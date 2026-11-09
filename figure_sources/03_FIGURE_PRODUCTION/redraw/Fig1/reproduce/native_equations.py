"""Replace the named Fig. 1c label paragraphs with editable Office Math zones."""
import argparse
from pathlib import Path
import re
from xml.sax.saxutils import escape
from zipfile import ZipFile

A14 = "http://schemas.microsoft.com/office/drawing/2010/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
SLIDE = "ppt/slides/slide1.xml"


def run(text, size, italic=False):
    style = "i" if italic else "p"
    return (
        f'<m:r><m:rPr><m:sty m:val="{style}"/></m:rPr>'
        f'<a:rPr sz="{round(size*100)}"><a:solidFill><a:srgbClr val="181B20"/>'
        '</a:solidFill><a:latin typeface="Cambria Math"/></a:rPr>'
        f'<m:t xml:space="preserve">{escape(text)}</m:t></m:r>'
    )


def script(base, idx, size, *, upper=False):
    tag, slot = ("sSup","sup") if upper else ("sSub","sub")
    return (f'<m:{tag}><m:e>{run(base,size,True)}</m:e>'
            f'<m:{slot}>{run(idx,size)}</m:{slot}></m:{tag}>')


def formula_map():
    formulas = {}
    for j in "123":
        for letter,size in [("x",9.25),("h",9.7),("y",9.25)]:
            formulas[f"A Labels - {letter}{j}"] = script(letter,j,size)
        for letter,size in [("u",8.7),("v",8.7),("y",9.25)]:
            formulas[f"B Labels - {letter}{j}"] = script(letter,j,size)
    formulas["B Labels - Identity"] = script("I","3",9.8)
    formulas["B Labels - Delay"] = script("z","−1",9.8,upper=True)
    formulas["B Labels - Mixer"] = run("M",10,True)
    i = script("I","3",8.8)
    formulas["B Labels - Mixing matrix"] = run("[",8.8)+i+run("\u2002",8.8)+i+run("]",8.8)
    return formulas


def apply(path, formulas=None):
    if formulas is None:
        formulas = formula_map()
    done = set()
    def update(match):
        shape = match[0]
        name = re.search(r'<p:cNvPr\b[^>]*\bname="([^"]+)"',shape)
        if not name or name[1] not in formulas:
            return shape
        name = name[1]
        assert name not in done,name
        done.add(name)
        def paragraph(p):
            props=re.search(r"<a:pPr\b[^>]*/>|<a:pPr\b.*?</a:pPr>",p[0],flags=re.S)
            return (f'<a:p>{props[0] if props else ""}<a14:m><m:oMath xmlns:m="{M}">'
                    f'{formulas[name]}</m:oMath></a14:m></a:p>')
        math,n = re.subn(r"<a:p>.*?</a:p>",paragraph,shape,flags=re.S)
        assert n==1,(name,n)
        return (f'<mc:AlternateContent xmlns:mc="{MC}">'
                f'<mc:Choice xmlns:a14="{A14}" Requires="a14">{math}</mc:Choice>'
                f'<mc:Fallback>{shape}</mc:Fallback></mc:AlternateContent>')
    temp=path.with_suffix(".math.tmp")
    with ZipFile(path) as source:
        original=source.read(SLIDE).decode("utf-8")
        modified=re.sub(r"<p:sp>.*?</p:sp>",update,original,flags=re.S)
        assert done==formulas.keys(),sorted(set(formulas)-done)
        with ZipFile(temp,"w") as result:
            for entry in source.infolist():
                result.writestr(entry,modified.encode("utf-8") if entry.filename==SLIDE else source.read(entry))
    temp.replace(path)
    print(f"Added {len(done)} editable equations.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck",type=Path)
    args=parser.parse_args()
    if args.deck.is_absolute():
        parser.error("Use a relative deck path.")
    apply(args.deck)
