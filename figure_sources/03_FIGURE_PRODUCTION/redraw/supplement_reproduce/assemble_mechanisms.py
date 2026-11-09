"""Merge the two native diagram slides with their vector chart exports."""
import argparse
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import fitz

PT = 72 / 25.4
SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", XLINK)

CROPS = {1: {"A": (0, 0, 86.0, 60.7), "B": (92.5, 0, 85.5, 60.7)},
         2: {"A": (0, 0, 86.0, 60.7)}}


def rect(box):
    x,y,w,h=box
    return fitz.Rect(x*PT,y*PT,(x+w)*PT,(y+h)*PT)


def namespace(source,prefix):
    mapping={n.get("id"):f"{prefix}-{n.get('id')}" for n in source.iter() if n.get("id")}
    for node in source.iter():
        if node.get("id"):
            node.set("id",mapping[node.get("id")])
        for key,val in node.attrib.copy().items():
            if key==f"{{{XLINK}}}href" and val.startswith("#"):
                node.set(key,"#"+mapping[val[1:]])
            if "url(#" in val:
                node.set(key,re.sub(r"url\(#([^)]+)\)",lambda m:f"url(#{mapping[m[1]]})",val))


def assemble(folder,number):
    name=f"FigS{number}"
    directory=folder/"submission_figures"/name
    final_pdf=directory/f"{name}.pdf"
    final_svg=directory/f"{name}.svg"
    temp_pdf=directory/"assembled.pdf"
    svg=ET.parse(final_svg)
    with fitz.open(final_pdf) as chart,fitz.open(directory/"native_mechanism.pdf") as native,fitz.open() as combined:
        page=combined.new_page(width=178*PT,height=126*PT)
        page.show_pdf_page(page.rect,chart,0,keep_proportion=False)
        for key,box in CROPS[number].items():
            x,y,w,h=box
            # Crop inside the heading so the chart's panel labels remain text.
            frame=rect((x,9 if y==0 else 74,w,(y+h)-(9 if y==0 else 74)))
            # Restrict white slide background to each mechanism panel.
            page.show_pdf_page(frame,native,0,clip=frame,keep_proportion=False)
        assert not page.get_images()
        page.get_pixmap(dpi=600,alpha=False).save(directory/f"{name}.png")
        combined.set_metadata({"title":f"Figure S{number}","subject":"Physical Review E supplementary figure"})
        combined.save(temp_pdf,garbage=4,deflate=True)
        for key,box in CROPS[number].items():
            region=rect(box)
            with fitz.open() as panel:
                p=panel.new_page(width=region.width,height=region.height)
                p.show_pdf_page(p.rect,combined,0,clip=region,keep_proportion=False)
                (directory/"panels"/f"{key}.svg").write_text(p.get_svg_image(text_as_path=True),encoding="utf-8")

        for key,box in CROPS[number].items():
            x,y,w,h=box
            y0=9 if y==0 else 74
            region=rect((x,y0,w,y+h-y0))
            with fitz.open() as mechanism:
                art=mechanism.new_page(width=region.width,height=region.height)
                art.show_pdf_page(art.rect,native,0,clip=region,keep_proportion=False)
                layer=ET.fromstring(art.get_svg_image(text_as_path=True))
                layer.set("x",f"{region.x0:.7f}")
                layer.set("y",f"{region.y0:.7f}")
                layer.set("width",f"{region.width:.7f}")
                layer.set("height",f"{region.height:.7f}")
                namespace(layer,f"ppt-{key}")
                svg.getroot().append(layer)
    svg.write(final_svg,encoding="utf-8",xml_declaration=True)
    temp_pdf.replace(final_pdf)
    with ZipFile(directory/f"{name}.pptx") as deck:
        assert deck.testzip() is None
        slide=deck.read("ppt/slides/slide1.xml")
        assert b"svgBlip" in slide and slide.count(b"<p:sp>")>=12
    (directory/"native_mechanism.pdf").unlink()


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("figures",nargs="*",type=int)
    parser.add_argument("--output",type=Path,default=Path("03_FIGURE_PRODUCTION/supplement_rebuilt"))
    args=parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    for i in args.figures or (1,2):
        if i not in (1,2):
            parser.error("Native diagrams are available for S1 and S2.")
        assemble(args.output,i)
