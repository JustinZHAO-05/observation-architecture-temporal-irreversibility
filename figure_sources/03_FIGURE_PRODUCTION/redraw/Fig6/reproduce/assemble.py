"""Assemble Fig. 6's native PowerPoint routes and vector plots."""
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
PT,SVG,NS=vectors.PT,vectors.SVG,vectors.NS
TITLE="Calibrated inference of temporal irreversibility"
BOXES={"a":LAYOUT["a-native"],"b":LAYOUT["b"],"c":LAYOUT["c"]}


def root_svg(w,h):
    return ET.Element(f"{{{SVG}}}svg",{"width":f"{w}mm","height":f"{h}mm",
                     "viewBox":f"0 0 {w*PT} {h*PT}"})


def add_svg(root,source,key,box):
    x,y,w,h=box
    vectors.prefix_ids(source,key)
    x0,y0,pw,ph=map(float,source.attrib["viewBox"].split())
    assert x0==y0==0
    group=ET.SubElement(root,f"{{{SVG}}}g",{
        "id":key,"transform":f"translate({x*PT:.7f} {y*PT:.7f}) scale({w*PT/pw:.9f} {h*PT/ph:.9f})"})
    group.extend(source)


def mechanism(out,work):
    x,y,w,h=LAYOUT["a-native"]
    xx,yy,ww,hh=LAYOUT["a-data"]
    data_box=(xx-x,yy-y,ww,hh)
    root=root_svg(w,h)
    source=out/"panels/Fig6a_data"
    with fitz.open(work/"Fig6_native.pdf") as native,fitz.open() as art,fitz.open() as combined:
        assert abs(native[0].rect.width/PT-178)<.1 and abs(native[0].rect.height/PT-125)<.1
        top=art.new_page(width=w*PT,height=h*PT)
        top.show_pdf_page(top.rect,native,0,clip=vectors.rect(x,y,w,h),keep_proportion=False)
        svg=ET.fromstring(top.get_svg_image(text_as_path=False))
        # Preserve PowerPoint's accent glyphs, whose PDF character mappings do
        # not reproduce the hats when the equations are exported as SVG text.
        math_groups=[group for group in svg.iter(f"{{{SVG}}}g")
                     if any(child.get("font-family","").startswith("CambriaMath") for child in group)]
        outlined=ET.fromstring(top.get_svg_image(text_as_path=True))
        outlined_groups=[group for group in outlined.iter(f"{{{SVG}}}g")
                         if group.find(f"{{{SVG}}}use") is not None][-len(math_groups):]
        assert len(math_groups)==len(outlined_groups)==9
        for text_group,outline_group in zip(math_groups,outlined_groups,strict=True):
            assert "".join(text_group.itertext()).strip()=="".join(g.get("data-text","") for g in outline_group)
            text_group[:]=list(outline_group)
        svg.find(f"{{{SVG}}}defs").extend(outlined.find(f"{{{SVG}}}defs").findall(f"{{{SVG}}}path"))
        for item in svg.iter(f"{{{SVG}}}text"):
            font=item.get("font-family","")
            if font.startswith("Arial"):
                item.set("font-family","Arial")
                if "Bold" in font:
                    item.set("font-weight","bold")
            spans=list(item)
            if len(spans)==1 and spans[0].tag==f"{{{SVG}}}tspan":
                span=spans[0]
                for axis in ("x","y"):
                    item.set(axis,span.get(axis).split()[0])
                item.text=span.text
                item.remove(span)
        add_svg(root,svg,"native",(0,0,w,h))
        add_svg(root,ET.parse(source.with_suffix(".svg")).getroot(),"plots",data_box)
        page=combined.new_page(width=w*PT,height=h*PT)
        page.show_pdf_page(page.rect,art,0,keep_proportion=False)
        with fitz.open(source.with_suffix(".pdf")) as plots:
            page.show_pdf_page(vectors.rect(*data_box),plots,0,keep_proportion=False)
        assert not page.get_images()
        combined.save(out/"panels/Fig6a.pdf",garbage=4,deflate=True)
    ET.ElementTree(root).write(out/"panels/Fig6a.svg",encoding="utf-8",xml_declaration=True)


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
    assert groups==4 and shapes==13 and math==2 and plots==3,(groups,shapes,math,plots)
    assert max(abs(a-b) for a,b in zip(dims,[178,125]))<.05
    return dict(native_groups=groups,native_shapes=shapes,editable_equations=math,
                vector_data_panels=plots,page_mm=dims)


def build(out):
    work=Path(gettempdir())/"PRE_Fig6_redraw"
    mechanism(out,work)
    root=root_svg(178,125)
    ET.SubElement(root,f"{{{SVG}}}title").text=f"Figure 6. {TITLE}"
    with fitz.open() as doc:
        page=doc.new_page(width=178*PT,height=125*PT)
        for letter,box in BOXES.items():
            path=out/"panels"/f"Fig6{letter}"
            with fitz.open(path.with_suffix(".pdf")) as part:
                page.show_pdf_page(vectors.rect(*box),part,0,keep_proportion=False)
            add_svg(root,ET.parse(path.with_suffix(".svg")).getroot(),f"panel-{letter}",box)
        assert not page.get_images()
        text=page.get_text()
        for label in ("certified lower sum","Fixed-grid detection power","Continuous-frequency rate",
                      "Population triangle integral"):
            assert label in text,label
        for label in ("3,072","Vertical scale is linear near zero","Median and 10",
                      "524,288","Calibration","2,048 cells","29.77"):
            assert label not in text,label
        doc.set_metadata({"title":f"Figure 6. {TITLE}","subject":"Physical Review E • main figure"})
        doc.save(out/"Fig6.pdf",garbage=4,deflate=True)
        page.get_pixmap(dpi=600,alpha=False).save(out/"Fig6.png")
        page.get_pixmap(dpi=144,alpha=False).save(work/"Fig6_print_proof.png")
    ids=[n.get("id") for n in root.iter() if "id" in n.attrib]
    assert len(ids)==len(set(ids)) and not list(root.iter(f"{{{SVG}}}image"))
    ET.ElementTree(root).write(out/"Fig6.svg",encoding="utf-8",xml_declaration=True)
    with fitz.open(out/"Fig6.svg") as doc:
        assert abs(doc[0].rect.width/PT-178)<.05 and abs(doc[0].rect.height/PT-125)<.05
        doc[0].get_pixmap(dpi=144,alpha=False).save(work/"Fig6_svg_proof.png")
    with Image.open(out/"Fig6.png") as raster:
        assert all(abs(d-600)<.1 for d in raster.info["dpi"])
        pixels=list(raster.size)
    result=dict(canvas_mm=[178,125],vector_pdf=True,png_dpi=600,png_pixels=pixels,
                pptx=verify_deck(out/"Fig6.pptx"),
                scientific=json.loads((out/"data/Fig6_checks.json").read_text(encoding="utf-8")),
                sha256={f"Fig6.{ext}":sha256((out/f"Fig6.{ext}").read_bytes()).hexdigest()
                        for ext in ("pdf","pptx","svg","png")})
    (out/"validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    build(args.output)
