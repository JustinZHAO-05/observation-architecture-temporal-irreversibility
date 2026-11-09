"""Validate vector, print-size, and data deliverables for the eight supplements."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree as ET

import fitz
import numpy as np
import pandas as pd
from PIL import Image

SVG = "{http://www.w3.org/2000/svg}"
PT = 72 / 25.4


def check(root,i):
    name=f"FigS{i}"
    fig=root/"submission_figures"/name
    data=root/"generated_data"/name
    index=json.loads((fig/"panel_data.json").read_text(encoding="utf-8"))
    panels="ABC" if i==2 else "ABCD"
    assert set(index)==set(panels)
    entries={}
    for panel,files in index.items():
        outputs={}
        for file in files:
            path=data/file
            if path.suffix==".csv":
                n=len(pd.read_csv(path))
                assert n>0,path
                outputs[file]={"rows":n}
            else:
                with np.load(path,allow_pickle=False) as z:
                    assert z.files and all(z[k].size for k in z.files)
                    outputs[file]={"array_shapes":{k:list(z[k].shape) for k in z.files}}
            outputs[file]["sha256"]=sha256(path.read_bytes()).hexdigest()
        entries[panel]=outputs
    assert {p.stem for p in (fig/"panels").glob("*.svg")}==set(panels)
    for svg in [fig/f"{name}.svg",*(fig/"panels"/f"{key}.svg" for key in panels)]:
        tree=ET.parse(svg)
        ids=[item.get("id") for item in tree.iter() if item.get("id")]
        assert len(ids)==len(set(ids)) and not list(tree.iter(SVG+"image")),svg
    with fitz.open(fig/f"{name}.pdf") as doc:
        assert len(doc)==1 and not doc[0].get_images()
        w,h=doc[0].rect.width/PT,doc[0].rect.height/PT
        assert abs(w-178)<.03 and abs(h-126)<.03
    with Image.open(fig/f"{name}.png") as png:
        assert all(abs(d-600)<.1 for d in png.info["dpi"])
        assert all(abs(actual-mm/25.4*600)<2 for actual,mm in zip(png.size,[w,h],strict=True))
        pixels=list(png.size)
    report=dict(canvas_mm=[round(w,3),round(h,3)],vector_pdf=True,png_dpi=600,png_pixels=pixels,
                panels=entries,sha256={p.name:sha256(p.read_bytes()).hexdigest()
                                      for p in sorted(fig.glob(f"{name}.*"))})
    (fig/"validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"{name}: {len(panels)} panels, vector exports, 600 dpi, data links verified.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("03_FIGURE_PRODUCTION/supplement_rebuilt"))
    args=parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    for i in range(1,9):
        check(args.output,i)
