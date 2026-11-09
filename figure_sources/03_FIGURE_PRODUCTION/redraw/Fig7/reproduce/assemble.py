"""Assemble the native PowerPoint mechanisms with vector EEG data panels."""
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
from draw_data import DEFAULT, LAYOUT

source = Path(__file__).resolve().parents[2] / "Fig1/reproduce/assemble.py"
spec = importlib.util.spec_from_file_location("figure_vectors", source)
vectors = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vectors)
SVG, PT, NS = vectors.SVG, vectors.PT, vectors.NS
TITLE = "Observation-coordinate dependence of spectral-cycle structure in human EEG"


def svg_root(w, h):
    return ET.Element(f"{{{SVG}}}svg", {"width": f"{w}mm", "height": f"{h}mm",
                                        "viewBox": f"0 0 {w*PT} {h*PT}"})


def add_layer(root, source, key, box):
    x, y, w, h = box
    vectors.prefix_ids(source, key)
    x0, y0, pw, ph = map(float, source.get("viewBox").split())
    assert x0 == y0 == 0
    layer = ET.SubElement(root, f"{{{SVG}}}g", {
        "id": key, "transform": f"translate({x*PT:.7f} {y*PT:.7f}) scale({w*PT/pw:.9f} {h*PT/ph:.9f})"})
    layer.extend(source)


def mechanism(panels, native, key):
    x, y, w, h = LAYOUT[key]
    box = (0, 0, w, h)
    root = svg_root(w, h)
    with fitz.open() as mech, fitz.open() as combined:
        part = mech.new_page(width=w*PT, height=h*PT)
        part.show_pdf_page(part.rect, native, 0, clip=vectors.rect(x, y, w, h), keep_proportion=False)
        # Mechanism text is kept as PowerPoint objects in the deck and as
        # editable outlines in SVG to preserve the equations' exact shapes.
        add_layer(root, ET.fromstring(part.get_svg_image(text_as_path=True)), "mechanism", box)
        page = combined.new_page(width=w*PT, height=h*PT)
        page.show_pdf_page(page.rect, mech, 0, keep_proportion=False)
        if key != "b":
            data = panels/f"Fig7{key}_data"
            with fitz.open(data.with_suffix(".pdf")) as plots:
                page.show_pdf_page(page.rect, plots, 0, keep_proportion=False)
            add_layer(root, ET.parse(data.with_suffix(".svg")).getroot(), "data", box)
        assert not page.get_images()
        combined.save(panels/f"Fig7{key}.pdf", garbage=4, deflate=True)
    ET.ElementTree(root).write(panels/f"Fig7{key}.svg", encoding="utf-8", xml_declaration=True)


def verify_deck(path):
    with ZipFile(path) as deck:
        assert deck.testzip() is None
        slide = ET.fromstring(deck.read("ppt/slides/slide1.xml"))
        size = ET.fromstring(deck.read("ppt/presentation.xml")).find("p:sldSz", NS)
    dims = [int(size.get(axis))/36000 for axis in ("cx", "cy")]
    groups, math, plots = (len(slide.findall(xpath, NS))
                           for xpath in (".//p:grpSp", ".//m:oMath", ".//s:svgBlip"))
    names = [n.get("name", "") for n in slide.findall(".//p:cNvPr", NS)]
    assert (groups, math, plots) == (3, 8, 4), (groups, math, plots)
    assert sum(name.startswith("b - Accepted window") for name in names) == 48
    assert max(abs(a-b) for a, b in zip(dims, (178, 158))) < .06
    return dict(native_groups=groups, editable_equations=math, vector_data_layers=plots,
                native_window_marks=48, page_mm=dims)


def build(out):
    work = Path(gettempdir())/"PRE_Fig7_redraw"
    panels = out/"panels"
    with fitz.open(work/"Fig7_native.pdf") as native:
        assert abs(native[0].rect.width/PT-178) < .15 and abs(native[0].rect.height/PT-158) < .15
        for key in "abd":
            mechanism(panels, native, key)
    root = svg_root(178, 158)
    ET.SubElement(root, f"{{{SVG}}}title").text = f"Figure 7. {TITLE}"
    with fitz.open() as doc:
        page = doc.new_page(width=178*PT, height=158*PT)
        for key, box in LAYOUT.items():
            stem = panels/f"Fig7{key}"
            with fitz.open(stem.with_suffix(".pdf")) as part:
                page.show_pdf_page(vectors.rect(*box), part, 0, keep_proportion=False)
            add_layer(root, ET.parse(stem.with_suffix(".svg")).getroot(), f"panel-{key}", box)
        assert not page.get_images()
        text = page.get_text()
        for label in ("EEG montage and reference", "Matched recordings and windows", "Rereferencing effect",
                      "Amplitude and alignment", "Within-participant condition contrast",
                      "Eyes closed", "Eyes open", "Mean, 95% CI"):
            assert label in text, label
        doc.set_metadata({"title": f"Figure 7. {TITLE}", "subject": "Physical Review E • main figure"})
        doc.save(out/"Fig7.pdf", garbage=4, deflate=True)
        page.get_pixmap(dpi=600, alpha=False).save(out/"Fig7.png")
        page.get_pixmap(dpi=144, alpha=False).save(work/"Fig7_print_proof.png")
    ids = [n.get("id") for n in root.iter() if n.get("id")]
    hrefs = [n.get(f"{{{vectors.XLINK}}}href", "") for n in root.iter(f"{{{SVG}}}use")]
    assert len(ids) == len(set(ids)) and not list(root.iter(f"{{{SVG}}}image"))
    assert all(h.startswith("#") and h[1:] in set(ids) for h in hrefs)
    ET.ElementTree(root).write(out/"Fig7.svg", encoding="utf-8", xml_declaration=True)
    with fitz.open(out/"Fig7.svg") as doc:
        assert abs(doc[0].rect.width/PT-178) < .05 and abs(doc[0].rect.height/PT-158) < .05
        doc[0].get_pixmap(dpi=144, alpha=False).save(work/"Fig7_svg_proof.png")
    with Image.open(out/"Fig7.png") as raster:
        assert all(abs(d-600) < .1 for d in raster.info["dpi"])
        pixels = list(raster.size)
    report = dict(canvas_mm=[178, 158], vector_pdf=True, png_dpi=600, png_pixels=pixels,
                  pptx=verify_deck(out/"Fig7.pptx"),
                  scientific=json.loads((out/"data/Fig7_checks.json").read_text(encoding="utf-8")),
                  sha256={f"Fig7.{ext}": sha256((out/f"Fig7.{ext}").read_bytes()).hexdigest()
                          for ext in ("pdf", "pptx", "svg", "png")})
    (out/"validation.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT)
    args = parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    build(args.output)
