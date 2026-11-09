"""Combine the native Fig. 5 mechanism with vector scientific plots."""
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
TITLE="Finite-bandwidth mixing generates repeatable apparent closure"
BOXES={"a":LAYOUT["a-native"],"b":LAYOUT["b"],"c":LAYOUT["c"],"d":LAYOUT["d"]}


def svg_root(w,h):
    return ET.Element(f"{{{SVG}}}svg",{"width":f"{w}mm","height":f"{h}mm",
                     "viewBox":f"0 0 {w*PT} {h*PT}"})


def svg_add(root,source,key,box):
    x,y,w,h=box
    vectors.prefix_ids(source,key)
    x0,y0,pw,ph=map(float,source.attrib["viewBox"].split())
    assert x0==y0==0
    group=ET.SubElement(root,f"{{{SVG}}}g",{
        "id":key,"transform":f"translate({x*PT:.7f} {y*PT:.7f}) scale({w*PT/pw:.9f} {h*PT/ph:.9f})"})
    group.extend(source)


def mechanism(out,work):
    x,y,w,h=LAYOUT["a-native"]
    root=svg_root(w,h)
    with fitz.open(work/"Fig5_native.pdf") as native,fitz.open() as artwork,fitz.open() as combined:
        assert abs(native[0].rect.width/PT-178)<.1 and abs(native[0].rect.height/PT-133)<.1
        art=artwork.new_page(width=w*PT,height=h*PT)
        art.show_pdf_page(art.rect,native,0,clip=vectors.rect(x,y,w,h),keep_proportion=False)
        svg=ET.fromstring(art.get_svg_image(text_as_path=False))
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
        svg_add(root,svg,"native",(0,0,w,h))
        page=combined.new_page(width=w*PT,height=h*PT)
        page.show_pdf_page(page.rect,artwork,0,keep_proportion=False)
        for key in ("input","output"):
            xx,yy,ww,hh=LAYOUT[f"a-{key}"]
            box=(xx-x,yy-y,ww,hh)
            source=out/"panels"/f"Fig5a_{key}"
            with fitz.open(source.with_suffix(".pdf")) as plot:
                page.show_pdf_page(vectors.rect(*box),plot,0,keep_proportion=False)
            svg_add(root,ET.parse(source.with_suffix(".svg")).getroot(),key,box)
        assert not page.get_images()
        combined.save(out/"panels/Fig5a.pdf",garbage=4,deflate=True)
    ET.ElementTree(root).write(out/"panels/Fig5a.svg",encoding="utf-8",xml_declaration=True)


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
    assert groups==4 and shapes>=13 and math==3 and plots==5,(groups,shapes,math,plots)
    assert max(abs(a-b) for a,b in zip(dims,[178,133]))<.05
    return dict(native_groups=groups,native_shapes=shapes,editable_equations=math,vector_data_panels=plots,page_mm=dims)


def build(out):
    work=Path(gettempdir())/"PRE_Fig5_redraw"
    mechanism(out,work)
    root=svg_root(178,133)
    ET.SubElement(root,f"{{{SVG}}}title").text=f"Figure 5. {TITLE}"
    with fitz.open() as doc:
        page=doc.new_page(width=178*PT,height=133*PT)
        for letter,box in BOXES.items():
            path=out/"panels"/f"Fig5{letter}"
            with fitz.open(path.with_suffix(".pdf")) as part:
                page.show_pdf_page(vectors.rect(*box),part,0,keep_proportion=False)
            svg_add(root,ET.parse(path.with_suffix(".svg")).getroot(),f"panel-{letter}",box)
        assert not page.get_images()
        text=page.get_text()
        for label in ("Multiply first","Average first","Slopes within the window","Window-length scaling",
                      "Reversible latent counterexample","0.00008"):
            assert label in text,label
        doc.set_metadata({"title":f"Figure 5. {TITLE}","subject":"Physical Review E • main figure"})
        doc.save(out/"Fig5.pdf",garbage=4,deflate=True)
        page.get_pixmap(dpi=600,alpha=False).save(out/"Fig5.png")
        page.get_pixmap(dpi=144,alpha=False).save(work/"Fig5_print_proof.png")
    ids=[n.get("id") for n in root.iter() if "id" in n.attrib]
    assert len(ids)==len(set(ids)) and not list(root.iter(f"{{{SVG}}}image"))
    ET.ElementTree(root).write(out/"Fig5.svg",encoding="utf-8",xml_declaration=True)
    with fitz.open(out/"Fig5.svg") as doc:
        assert abs(doc[0].rect.width/PT-178)<.05 and abs(doc[0].rect.height/PT-133)<.05
        doc[0].get_pixmap(dpi=144,alpha=False).save(work/"Fig5_svg_proof.png")
    with Image.open(out/"Fig5.png") as raster:
        assert all(abs(dpi-600)<.1 for dpi in raster.info["dpi"])
        pixels=list(raster.size)
    result=dict(canvas_mm=[178,133],vector_pdf=True,png_dpi=600,png_pixels=pixels,
                pptx=verify_deck(out/"Fig5.pptx"),
                scientific=json.loads((out/"data/Fig5_checks.json").read_text(encoding="utf-8")),
                sha256={f"Fig5.{ext}":sha256((out/f"Fig5.{ext}").read_bytes()).hexdigest()
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
