"""Set the Fig. 4 mechanism's labels as editable PowerPoint math."""
import argparse
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode=True
source=Path(__file__).resolve().parents[2]/"Fig1/reproduce/native_equations.py"
spec=importlib.util.spec_from_file_location("figure_math",source)
native=importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
run,script=native.run,native.script


def formulas():
    s=9.15
    edge={n:script("C",n,s) for n in ("12","23","31")}
    out={f"Math - Edge {n}":script("C",n,8.9) for n in edge}
    out["Math - Phase update"]=(
        run("arg ",s)+script("C′","ij",s)+run(" = arg ",s)+script("C","ij",s)
        +run(" + ",s)+script("φ","i",s)+run(" − ",s)+script("φ","j",s))
    out["Math - Cycle invariant"]=(
        run("ψ′",s,True)+run(" = ",s)+run("ψ",s,True)+run(" = arg(",s)
        +"".join(edge.values())+run(")",s))
    out["Math - Frequency slice"]=run("ω",8.55,True)+run(" / π = 1/2",8.55)
    s=8.6
    out["Math - Share fraction"]=(
        f'<m:sSubSup><m:e>{run("θ",s,True)}</m:e><m:sub>{run("31",s)}</m:sub>'
        f'<m:sup>{run("∗",s)}</m:sup></m:sSubSup>'+run(" / ",s)+run("ψ",s,True))
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck",type=Path)
    args=parser.parse_args()
    if args.deck.anchor:
        parser.error("Use a path relative to the handoff root.")
    native.apply(args.deck,formulas())
