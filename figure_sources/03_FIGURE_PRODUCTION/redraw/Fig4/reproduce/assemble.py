"""Compose the native mechanisms and vector plots at the PRE figure size."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import gettempdir
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import fitz
from PIL import Image

sys.dont_write_bytecode=True
from draw_data import DEFAULT_OUTPUT, LAYOUT

source=Path(__file__).resolve().parents[2]/"Fig1/reproduce/assemble.py"
spec=importlib.util.spec_from_file_location("figure_vectors",source)
vectors=importlib.util.module_from_spec(spec)
spec.loader.exec_module(vectors)
PT, SVG, NS = vectors.PT, vectors.SVG, vectors.NS
TITLE="Filter-invariant spectral cycles and quantitative reversal bounds"
BOXES={"a":(18,2,142,50.7),"b":LAYOUT["b"],"c":(108,55,68,59)}


def svg_root(w,h):
    return ET.Element(f"{{{SVG}}}svg",{"width":f"{w}mm","height":f"{h}mm",
                      "viewBox":f"0 0 {w*PT} {h*PT}"})


def svg_add(root, source, key, box):
    x,y,w,h=box
    vectors.prefix_ids(source,key)
    x0,y0,pw,ph=map(float,source.attrib["viewBox"].split())
    assert x0==y0==0
    group=ET.SubElement(root,f"{{{SVG}}}g",{
        "id":key,"transform":f"translate({x*PT:.7f} {y*PT:.7f}) scale({w*PT/pw:.9f} {h*PT/ph:.9f})"})
    group.extend(source)


def native_part(native,box):
    doc=fitz.open()
    x,y,w,h=box
    page=doc.new_page(width=w*PT,height=h*PT)
    page.show_pdf_page(page.rect,native,0,clip=vectors.rect(x,y,w,h),keep_proportion=False)
    svg=ET.fromstring(page.get_svg_image(text_as_path=False))
    for text in svg.iter(f"{{{SVG}}}text"):
        font=text.get("font-family","")
        if font.startswith("CambriaMath"):
            text.set("font-family","Cambria Math")
        elif font.startswith("Arial"):
            text.set("font-family","Arial")
            if "Bold" in font:
                text.set("font-weight","bold")
        spans=list(text)
        if len(spans)==1 and spans[0].tag==f"{{{SVG}}}tspan":
            span=spans[0]
            for axis in ("x","y"):
                text.set(axis,span.get(axis).split()[0])
            text.text=span.text
            text.remove(span)
    return doc,svg


def mixed_panel(native,out,letter):
    _,y,w,h=BOXES[letter]
    _,_,_,h_top=LAYOUT[f"{letter}-top"]
    _,data_y,data_w,data_h=LAYOUT[f"{letter}-data"]
    source=out/"panels"/f"Fig4{letter}_data"
    top_pdf,top_svg=native_part(native,LAYOUT[f"{letter}-top"])
    result=out/"panels"/f"Fig4{letter}"
    top_rect=(0,0,w,h_top)
    data_rect=(0,data_y-y,data_w,data_h)
    with top_pdf,fitz.open(source.with_suffix(".pdf")) as data,fitz.open() as combined:
        page=combined.new_page(width=w*PT,height=h*PT)
        page.show_pdf_page(vectors.rect(*top_rect),top_pdf,0,keep_proportion=False)
        page.show_pdf_page(vectors.rect(*data_rect),data,0,keep_proportion=False)
        assert not page.get_images()
        combined.save(result.with_suffix(".pdf"),garbage=4,deflate=True)
    svg=svg_root(w,h)
    svg_add(svg,top_svg,f"{letter}-geometry",top_rect)
    svg_add(svg,ET.parse(source.with_suffix(".svg")).getroot(),f"{letter}-plots",data_rect)
    ET.ElementTree(svg).write(result.with_suffix(".svg"),encoding="utf-8",xml_declaration=True)


def verify_deck(path):
    with ZipFile(path) as deck:
        assert deck.testzip() is None
        slide=ET.fromstring(deck.read("ppt/slides/slide1.xml"))
        pres=ET.fromstring(deck.read("ppt/presentation.xml"))
    math=len(slide.findall(".//m:oMath",NS))
    plots=len(slide.findall(".//s:svgBlip",NS))
    groups=len(slide.findall(".//p:grpSp",NS))
    shapes=sum(len(slide.findall(f".//p:{kind}",NS)) for kind in ("sp","cxnSp"))
    shapes-=len(slide.findall(".//mc:Fallback/p:sp",NS))
    size=pres.find("p:sldSz",NS)
    dims=[int(size.get(axis))/36000 for axis in ("cx","cy")]
    assert groups>=9 and shapes>=60 and math==7 and plots==3
    assert max(abs(a-b) for a,b in zip(dims,[178,116]))<.05
    return dict(native_groups=groups,native_shapes=shapes,editable_equations=math,vector_data_panels=plots,page_mm=dims)


def build(out):
    work=Path(gettempdir())/"PRE_Fig4_redraw"
    with fitz.open(work/"Fig4_native.pdf") as native:
        assert abs(native[0].rect.width/PT-178)<.1 and abs(native[0].rect.height/PT-116)<.1
        for letter in "ac":
            mixed_panel(native,out,letter)
    svg=svg_root(178,116)
    ET.SubElement(svg,f"{{{SVG}}}title").text=f"Figure 4. {TITLE}"
    with fitz.open() as doc:
        page=doc.new_page(width=178*PT,height=116*PT)
        for letter,box in BOXES.items():
            path=out/"panels"/f"Fig4{letter}"
            with fitz.open(path.with_suffix(".pdf")) as part:
                page.show_pdf_page(vectors.rect(*box),part,0,keep_proportion=False)
            svg_add(svg,ET.parse(path.with_suffix(".svg")).getroot(),f"panel-{letter}",box)
        assert not page.get_images()
        text=page.get_text()
        for label in ("Cycle invariance","Quantitative reversal bound","Weak edges absorb phase","97%"):
            assert label in text,label
        doc.set_metadata({"title":f"Figure 4. {TITLE}","subject":"Physical Review E • main figure"})
        doc.save(out/"Fig4.pdf",garbage=4,deflate=True)
        page.get_pixmap(dpi=600,alpha=False).save(out/"Fig4.png")
        page.get_pixmap(dpi=144,alpha=False).save(work/"Fig4_print_proof.png")
    ids=[n.get("id") for n in svg.iter() if "id" in n.attrib]
    assert len(ids)==len(set(ids)) and not list(svg.iter(f"{{{SVG}}}image"))
    ET.ElementTree(svg).write(out/"Fig4.svg",encoding="utf-8",xml_declaration=True)
    with fitz.open(out/"Fig4.svg") as doc:
        assert abs(doc[0].rect.width/PT-178)<.05 and abs(doc[0].rect.height/PT-116)<.05
        doc[0].get_pixmap(dpi=144,alpha=False).save(work/"Fig4_svg_proof.png")
    with Image.open(out/"Fig4.png") as raster:
        assert all(abs(d-600)<.1 for d in raster.info["dpi"])
        pixels=list(raster.size)
    report=dict(canvas_mm=[178,116],vector_pdf=True,png_dpi=600,png_pixels=pixels,
                pptx=verify_deck(out/"Fig4.pptx"),
                scientific=json.loads((out/"data/Fig4_checks.json").read_text(encoding="utf-8")),
                sha256={f"Fig4.{ext}":sha256((out/f"Fig4.{ext}").read_bytes()).hexdigest()
                        for ext in ("pdf","pptx","svg","png")})
    (out/"validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    build(args.output)
