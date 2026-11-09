"""Compose the editable SVG and vector PDF, then validate the Fig. 3 deliverables."""
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

sys.dont_write_bytecode = True
from draw_data import DEFAULT_OUTPUT, LAYOUT

source=Path(__file__).resolve().parents[2]/"Fig1/reproduce/assemble.py"
spec=importlib.util.spec_from_file_location("figure_vectors",source)
vectors=importlib.util.module_from_spec(spec)
spec.loader.exec_module(vectors)
PT, SVG, NS = vectors.PT, vectors.SVG, vectors.NS
TITLE="The spectral-power cost of observational equivalence"


def mechanism(out, work):
    with fitz.open(work/"Fig3a_powerpoint_full.pdf") as src, fitz.open() as doc:
        x,y,w,h=LAYOUT["a"]
        page=doc.new_page(width=w*PT,height=h*PT)
        assert abs(src[0].rect.width/PT-178)<.1 and abs(src[0].rect.height/PT-112)<.1
        page.show_pdf_page(page.rect,src,0,clip=vectors.rect(x,y,w,h),keep_proportion=False)
        assert "Same target, different costs" in page.get_text() and not page.get_images()
        doc.save(out/"panels/Fig3a.pdf",garbage=4,deflate=True)
        svg=ET.fromstring(page.get_svg_image(text_as_path=False))
    for item in svg.iter(f"{{{SVG}}}text"):
        font=item.get("font-family","")
        if font.startswith("CambriaMath"):
            item.set("font-family","Cambria Math")
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
    ET.ElementTree(svg).write(out/"panels/Fig3a.svg",encoding="utf-8",xml_declaration=True)


def compose_svg(out):
    root=ET.Element(f"{{{SVG}}}svg",{"width":"178mm","height":"112mm",
                    "viewBox":f"0 0 {178*PT} {112*PT}"})
    ET.SubElement(root,f"{{{SVG}}}title").text=f"Figure 3. {TITLE}"
    for letter,(x,y,w,h) in LAYOUT.items():
        panel=ET.parse(out/f"panels/Fig3{letter}.svg").getroot()
        vectors.prefix_ids(panel,letter)
        x0,y0,pw,ph=map(float,panel.attrib["viewBox"].split())
        assert x0==y0==0
        group=ET.SubElement(root,f"{{{SVG}}}g",{"id":f"panel-{letter}",
                            "transform":f"translate({x*PT:.7f} {y*PT:.7f}) scale({w*PT/pw:.9f} {h*PT/ph:.9f})"})
        group.extend(panel)
        assert len(list(group.iter(f"{{{SVG}}}text")))>=6
    ids=[n.get("id") for n in root.iter() if "id" in n.attrib]
    assert len(ids)==len(set(ids)) and not list(root.iter(f"{{{SVG}}}image"))
    ET.ElementTree(root).write(out/"Fig3.svg",encoding="utf-8",xml_declaration=True)


def verify_deck(path):
    with ZipFile(path) as deck:
        assert deck.testzip() is None
        slide=ET.fromstring(deck.read("ppt/slides/slide1.xml"))
        pres=ET.fromstring(deck.read("ppt/presentation.xml"))
    assert len(slide.findall(".//m:oMath",NS))==19
    assert len(slide.findall(".//s:svgBlip",NS))==2
    groups=len(slide.findall(".//p:grpSp",NS))
    shapes=sum(len(slide.findall(f".//p:{kind}",NS)) for kind in ("sp","cxnSp"))
    shapes-=len(slide.findall(".//mc:Fallback/p:sp",NS))
    size=pres.find("p:sldSz",NS)
    dims=[int(size.get(axis))/36000 for axis in ("cx","cy")]
    assert groups>=9 and shapes>=60 and max(abs(a-b) for a,b in zip(dims,[178,112]))<.05
    return dict(native_groups=groups,native_shapes=shapes,editable_equations=19,vector_data_panels=2,page_mm=dims)


def build(out):
    work=Path(gettempdir())/"PRE_Fig3_redraw"
    mechanism(out,work)
    with fitz.open() as doc:
        page=doc.new_page(width=178*PT,height=112*PT)
        for letter,box in LAYOUT.items():
            with fitz.open(out/f"panels/Fig3{letter}.pdf") as panel:
                page.show_pdf_page(vectors.rect(*box),panel,0,keep_proportion=False)
        assert not page.get_images()
        text=page.get_text()
        for label in ("Same target, different costs","Small-phase scaling","Power-cost landscape","160.4336"):
            assert label in text,label
        doc.set_metadata({"title":f"Figure 3. {TITLE}","subject":"Physical Review E • main figure"})
        doc.save(out/"Fig3.pdf",garbage=4,deflate=True)
        page.get_pixmap(dpi=600,alpha=False).save(out/"Fig3.png")
        page.get_pixmap(dpi=144,alpha=False).save(work/"Fig3_print_proof.png")
    compose_svg(out)
    with fitz.open(out/"Fig3.svg") as svg:
        assert abs(svg[0].rect.width/PT-178)<.05 and abs(svg[0].rect.height/PT-112)<.05
        svg[0].get_pixmap(dpi=144,alpha=False).save(work/"Fig3_svg_proof.png")
    with Image.open(out/"Fig3.png") as raster:
        assert all(abs(dpi-600)<.1 for dpi in raster.info["dpi"])
        pixels=list(raster.size)
    proof=dict(canvas_mm=[178,112],vector_pdf=True,png_dpi=600,png_pixels=pixels,
               pptx=verify_deck(out/"Fig3.pptx"),
               scientific=json.loads((out/"data/Fig3_checks.json").read_text(encoding="utf-8")),
               sha256={f"Fig3.{ext}":sha256((out/f"Fig3.{ext}").read_bytes()).hexdigest()
                       for ext in ("pdf","pptx","svg","png")})
    (out/"validation.json").write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(proof,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    build(args.output)
