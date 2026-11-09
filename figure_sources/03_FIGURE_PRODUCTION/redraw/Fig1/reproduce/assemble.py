"""Assemble the Python vector panels and the native PowerPoint vector export."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import fitz
from PIL import Image

SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", XLINK)
PT = 72 / 25.4
LAYOUT = {"a": (2, 0, 86, 52), "b": (90, 0, 86, 52), "c": (0, 52.7, 178, 59.3)}
NS = {"p":"http://schemas.openxmlformats.org/presentationml/2006/main",
      "a":"http://schemas.openxmlformats.org/drawingml/2006/main",
      "s":"http://schemas.microsoft.com/office/drawing/2016/SVG/main",
      "m":"http://schemas.openxmlformats.org/officeDocument/2006/math",
      "mc":"http://schemas.openxmlformats.org/markup-compatibility/2006"}


def rect(x, y, w, h):
    return fitz.Rect(x*PT, y*PT, (x+w)*PT, (y+h)*PT)


def vector_clip(native, output):
    shape = LAYOUT["c"]
    _, y, w, h = shape
    c = fitz.open()
    cpage = c.new_page(width=w*PT, height=h*PT)
    source = native[0].rect
    assert abs(source.width/PT-178)<.5 and abs(source.height/PT-112)<.5
    clip = fitz.Rect(0,y*PT,source.x1,source.y1)
    cpage.show_pdf_page(cpage.rect,native,0,clip=clip,keep_proportion=False)
    assert not cpage.get_images()
    c.save(output/"panels/Fig1c.pdf", garbage=4, deflate=True)
    c_svg = ET.fromstring(cpage.get_svg_image(text_as_path=False))
    # PDF font names can include PostScript suffixes that are not family names.
    for item in c_svg.iter():
        font = item.get("font-family","")
        if font.startswith("CambriaMath"):
            item.set("font-family","Cambria Math")
        if font.startswith("Arial"):
            item.set("font-family","Arial")
            if "Bold" in font:
                item.set("font-weight","bold")
            if "Italic" in font:
                item.set("font-style","italic")
    for text in c_svg.iter(f"{{{SVG}}}text"):
        spans = list(text)
        if len(spans) == 1 and spans[0].tag == f"{{{SVG}}}tspan":
            # Plain positioned text also works in editors that lack x-coordinate arrays.
            span = spans[0]
            for axis in ("x","y"):
                text.set(axis,span.get(axis).split()[0])
            text.text = span.text
            text.remove(span)
    ET.ElementTree(c_svg).write(output/"panels/Fig1c.svg",encoding="utf-8",xml_declaration=True)
    return c


def prefix_ids(svg, prefix):
    mapping = {node.get("id"):f"{prefix}-{node.get('id')}" for node in svg.iter() if node.get("id")}
    for node in svg.iter():
        if node.get("id"):
            node.set("id",mapping[node.get("id")])
        for key,val in node.attrib.copy().items():
            if key == f"{{{XLINK}}}href" and val.startswith("#") and val[1:] in mapping:
                node.set(key,"#"+mapping[val[1:]])
            elif "url(#" in val:
                node.set(key,re.sub(r"url\(#([^)]+)\)",lambda m:f"url(#{mapping[m[1]]})",val))


def merged_svg(output):
    root=ET.Element(f"{{{SVG}}}svg",{"width":"178mm","height":"112mm",
                                      "viewBox":f"0 0 {178*PT:.7f} {112*PT:.7f}"})
    title=ET.SubElement(root,f"{{{SVG}}}title")
    title.text="Figure 1. From observed temporal asymmetry to observation architecture"
    # The PowerPoint export carries a white page background under the mechanism.
    for letter in ("c", "a", "b"):
        x,y,w,h=LAYOUT[letter]
        layer=ET.parse(output/f"panels/Fig1{letter}.svg").getroot()
        prefix_ids(layer,letter)
        x0,y0,layer_w,layer_h=map(float,layer.attrib["viewBox"].split())
        assert x0 == y0 == 0
        group=ET.SubElement(root,f"{{{SVG}}}g",
                           {"id":f"panel-{letter}",
                            "transform":f"translate({x*PT:.7f} {y*PT:.7f}) scale({w*PT/layer_w:.9f} {h*PT/layer_h:.9f})"})
        group.extend(layer)
    ids=[n.attrib["id"] for n in root.iter() if "id" in n.attrib]
    assert len(ids)==len(set(ids))
    assert not list(root.iter(f"{{{SVG}}}image"))
    assert all(len(list(layer.iter(f"{{{SVG}}}text")))>=8 for layer in list(root)[1:])
    ET.ElementTree(root).write(output/"Fig1.svg",encoding="utf-8",xml_declaration=True)


def pptx_checks(path):
    with ZipFile(path) as archive:
        xml=ET.fromstring(archive.read("ppt/slides/slide1.xml"))
        ppt=ET.fromstring(archive.read("ppt/presentation.xml"))
    shape_count=sum(len(xml.findall(f".//p:{name}",NS)) for name in ("sp","cxnSp"))
    # Count each Office Math shape once, excluding its legacy fallback.
    shape_count-=len(xml.findall(".//mc:Fallback/p:sp",NS))
    group_count=len(xml.findall(".//p:grpSp",NS))
    svg_count=len(xml.findall(".//s:svgBlip",NS))
    size=ppt.find("p:sldSz",NS)
    page_mm=[int(size.attrib[key])/36000 for key in ("cx","cy")]
    equation_count=len(xml.findall(".//m:oMath",NS))
    assert shape_count>=65 and group_count>=10 and svg_count==2 and equation_count==22
    assert max(abs(a-b) for a,b in zip(page_mm,[178,112]))<.05
    return {"native_shapes":shape_count,"native_groups":group_count,
            "editable_equations":equation_count,"svg_data_panels":svg_count,"page_mm":page_mm}


def build(output, deck_name):
    work=Path(tempfile.gettempdir())/"PRE_Fig1_redraw"
    with fitz.open(work/"Fig1c_powerpoint_full.pdf") as native:
        with vector_clip(native,output) as c, fitz.open() as doc:
            page=doc.new_page(width=178*PT,height=112*PT)
            for letter in ("a","b"):
                with fitz.open(output/f"panels/Fig1{letter}.pdf") as part:
                    page.show_pdf_page(rect(*LAYOUT[letter]),part,0,keep_proportion=False)
            page.show_pdf_page(rect(*LAYOUT["c"]),c,0,keep_proportion=False)
            doc.set_metadata({"title":"Figure 1. From observed temporal asymmetry to observation architecture",
                              "subject":"Physical Review E • main figure"})
            assert not page.get_images(), "Expected vector content throughout."
            text=page.get_text()
            for label in ("Temporal structure","Spectral structure","Channelwise filters","Source filters + mixing","Amplitude (SD)"):
                assert label in text,label
            doc.save(output/"Fig1.pdf",garbage=4,deflate=True)
            page.get_pixmap(dpi=600,alpha=False).save(output/"Fig1.png")
            page.get_pixmap(dpi=144,alpha=False).save(work/"Fig1_print_proof.png")
    merged_svg(output)
    with Image.open(output/"Fig1.png") as image:
        assert all(abs(dpi-600)<.1 for dpi in image.info["dpi"])
        size=list(image.size)
    deck = output/deck_name
    validation=dict(figure="Fig1 redraw",vector_pdf=True,canvas_mm=[178,112],
                    png_dpi=600,png_pixels=size,pptx=pptx_checks(deck),
                    sha256={file.name:hashlib.sha256(file.read_bytes()).hexdigest()
                            for file in (output/"Fig1.svg",output/"Fig1.pdf",output/"Fig1.png",deck)})
    (output/"validation.json").write_text(json.dumps(validation,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(validation,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("03_FIGURE_PRODUCTION/redraw/Fig1"))
    parser.add_argument("--deck-name",default="Fig1.pptx")
    args=parser.parse_args()
    if args.output.is_absolute() or Path(args.deck_name).name!=args.deck_name:
        parser.error("Provide a relative output directory and a deck filename.")
    build(args.output,args.deck_name)
