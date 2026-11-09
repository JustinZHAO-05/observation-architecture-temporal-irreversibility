"""Verify every listed file and current figure/table index after extraction."""
import csv
from hashlib import sha256
import json
from pathlib import Path


def rows(root,path):
    with (root/path).open(encoding="utf-8-sig",newline="") as file:
        return list(csv.DictReader(file))


def check(root):
    root=root.resolve()
    manifest=rows(root,"MANIFEST_SHA256.csv")
    names={row["path"] for row in manifest}
    assert len(names)==len(manifest)
    for row in manifest:
        path=(root/row["path"]).resolve()
        assert path.is_relative_to(root) and path.stat().st_size==int(row["bytes"]),path
        assert sha256(path.read_bytes()).hexdigest()==row["sha256"],path

    panels=rows(root,"FIGURE_PANEL_INDEX.csv")
    assert len(panels)==len({(r["figure"],r["panel"]) for r in panels})==56
    assert len({r["figure"] for r in panels})==15
    for row in panels:
        for key in ("panel_svg","pdf","svg","png_600dpi","caption","reproduce","panel_data"):
            assert all(p in names for p in row[key].split(" | ")),(row["figure"],key)
        if row["pptx"]:
            assert row["pptx"] in names,row["pptx"]
    latest_s2=[r["panel"] for r in panels if r["figure"]=="FigS2"]
    assert set(latest_s2)==set("ABC")

    tables=rows(root,"tables/TABLE_SOURCE_INDEX.csv")
    assert len(tables)==11 and len({row["id"] for row in tables})==11
    for table in tables:
        name=f'tables/{table["csv"]}'
        assert name in names and len(rows(root,name))==int(table["rows"]),name
        assert all(p in names for p in table["sources"].split(" | ")),table["id"]

    collected=(root/"FIGURE_CAPTIONS_EN.md").read_text(encoding="utf-8")
    for path in {r["caption"] for r in panels}:
        lines=(root/path).read_text(encoding="utf-8-sig").strip().splitlines()
        text="\n".join(lines[1:] if lines[0].startswith("# ") else lines).strip()
        assert text and text in collected,path
    for name in ("FigS1","FigS2"):
        index=root/f"03_FIGURE_PRODUCTION/redraw/{name}/panel_data.json"
        assert set(json.loads(index.read_text(encoding="utf-8")))==set("ABCD" if name=="FigS1" else "ABC")
    print(f"Verified {len(manifest)} files, 15 figures, 56 panels, 15 captions and 11 tables.")


if __name__=="__main__":
    check(Path("."))
