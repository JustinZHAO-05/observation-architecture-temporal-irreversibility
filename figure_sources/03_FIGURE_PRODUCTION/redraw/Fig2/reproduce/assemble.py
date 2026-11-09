"""Assemble the vector PDF, PNG and SVG, and verify the native PowerPoint source."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import fitz
from PIL import Image

sys.dont_write_bytecode = True
from draw_data import LAYOUT

helper = Path(__file__).resolve().parents[2]/"Fig1/reproduce/assemble.py"
spec = importlib.util.spec_from_file_location("figure_vectors",helper)
vectors = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vectors)
PT, SVG, NS = vectors.PT,vectors.SVG,vectors.NS
TITLE = "Exact observational equivalence from a one-sample delay"


def export_a(native,out):
    page=fitz.open()
    a=page.new_page(width=178*PT,height=52*PT)
    source=native[0].rect
    assert abs(source.width/PT-178)<.3 and abs(source.height/PT-150)<.3
    a.show_pdf_page(a.rect,native,0,clip=fitz.Rect(0,0,source.x1,52*PT),keep_proportion=False)
    assert not a.get_images()
    assert "Reversible latent representation" in a.get_text()
    page.save(out/"panels/Fig2a.pdf",garbage=4,deflate=True)
    svg=ET.fromstring(a.get_svg_image(text_as_path=False))
    for element in svg.iter(f"{{{SVG}}}text"):
        font=element.get("font-family","")
        if font.startswith("CambriaMath"):
            element.set("font-family","Cambria Math")
        elif font.startswith("Arial"):
            element.set("font-family","Arial")
            if "Bold" in font:
                element.set("font-weight","bold")
            if "Italic" in font:
                element.set("font-style","italic")
        spans=list(element)
        if len(spans)==1 and spans[0].tag==f"{{{SVG}}}tspan":
            span=spans[0]
            for k in ("x","y"):
                element.set(k,span.get(k).split()[0])
            element.text=span.text
            element.remove(span)
    ET.ElementTree(svg).write(out/"panels/Fig2a.svg",encoding="utf-8",xml_declaration=True)


def assembled_svg(out):
    svg=ET.Element(f"{{{SVG}}}svg",{"width":"178mm","height":"150mm","viewBox":f"0 0 {178*PT} {150*PT}"})
    ET.SubElement(svg,f"{{{SVG}}}title").text=f"Figure 2. {TITLE}"
    for letter,(x,y,w,h) in LAYOUT.items():
        panel=ET.parse(out/f"panels/Fig2{letter}.svg").getroot()
        vectors.prefix_ids(panel,letter)
        x0,y0,pw,ph=map(float,panel.attrib["viewBox"].split())
        assert x0==y0==0
        group=ET.SubElement(svg,f"{{{SVG}}}g",{"id":f"panel-{letter}",
                             "transform":f"translate({x*PT:.7f} {y*PT:.7f}) scale({w*PT/pw:.9f} {h*PT/ph:.9f})"})
        group.extend(panel)
        assert len(list(group.iter(f"{{{SVG}}}text")))>=8
    ids=[n.attrib["id"] for n in svg.iter() if "id" in n.attrib]
    assert len(ids)==len(set(ids)) and not list(svg.iter(f"{{{SVG}}}image"))
    ET.ElementTree(svg).write(out/"Fig2.svg",encoding="utf-8",xml_declaration=True)


def check_deck(path):
    with ZipFile(path) as z:
        assert z.testzip() is None
        slide=ET.fromstring(z.read("ppt/slides/slide1.xml"))
        pres=ET.fromstring(z.read("ppt/presentation.xml"))
    groups=len(slide.findall(".//p:grpSp",NS))
    shapes=sum(len(slide.findall(f".//p:{kind}",NS)) for kind in ("sp","cxnSp"))
    shapes-=len(slide.findall(".//mc:Fallback/p:sp",NS))
    math=len(slide.findall(".//m:oMath",NS))
    plots=len(slide.findall(".//s:svgBlip",NS))
    size=pres.find("p:sldSz",NS)
    dims=[int(size.get(k))/36000 for k in ("cx","cy")]
    assert max(abs(a-b) for a,b in zip(dims,[178,150]))<.05
    assert groups>=10 and shapes>=60 and math==18 and plots==3,(groups,shapes,math,plots)
    return dict(native_shapes=shapes,native_groups=groups,editable_equations=math,
                vector_data_panels=plots,page_mm=dims)


def build(out):
    work=Path(tempfile.gettempdir())/"PRE_Fig2_redraw"
    with fitz.open(work/"Fig2a_powerpoint_full.pdf") as native:
        export_a(native,out)
    with fitz.open() as pdf:
        page=pdf.new_page(width=178*PT,height=150*PT)
        for letter,box in LAYOUT.items():
            with fitz.open(out/f"panels/Fig2{letter}.pdf") as part:
                page.show_pdf_page(vectors.rect(*box),part,0,keep_proportion=False)
        pdf.set_metadata({"title":f"Figure 2. {TITLE}","subject":"Physical Review E • main figure"})
        assert not page.get_images()
        text=page.get_text()
        for label in ("Reversible latent representation","Lag-one asymmetry",
                      "Exact covariance equality","Observed cycle and reversal rates","2.588315"):
            assert label in text,label
        pdf.save(out/"Fig2.pdf",garbage=4,deflate=True)
        page.get_pixmap(dpi=600,alpha=False).save(out/"Fig2.png")
        page.get_pixmap(dpi=144,alpha=False).save(work/"Fig2_print_proof.png")
    assembled_svg(out)
    with fitz.open(out/"Fig2.svg") as svg:
        assert abs(svg[0].rect.width/PT-178)<.05 and abs(svg[0].rect.height/PT-150)<.05
        svg[0].get_pixmap(dpi=144).save(work/"Fig2_svg_proof.png")
    with Image.open(out/"Fig2.png") as raster:
        assert all(abs(d-600)<.1 for d in raster.info["dpi"])
        pixels=list(raster.size)
    check=dict(canvas_mm=[178,150],vector_pdf=True,png_dpi=600,png_pixels=pixels,
               pptx=check_deck(out/"Fig2.pptx"),
               scientific=json.loads((out/"data/Fig2_scientific_checks.json").read_text()),
               sha256={f"Fig2.{ext}":hashlib.sha256((out/f"Fig2.{ext}").read_bytes()).hexdigest()
                       for ext in ("pdf","pptx","svg","png")})
    (out/"validation.json").write_text(json.dumps(check,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(check,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=Path("03_FIGURE_PRODUCTION/redraw/Fig2"))
    args=p.parse_args()
    if args.output.is_absolute():
        p.error("Use a relative path.")
    build(args.output)
