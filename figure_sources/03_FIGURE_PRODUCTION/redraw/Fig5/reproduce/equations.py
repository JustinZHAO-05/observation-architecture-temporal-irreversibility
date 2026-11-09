"""Insert the two averaging operations as editable Office Math."""
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


def average(expr,size):
    return (f'<m:sSub><m:e>{run("⟨",size)}{expr}{run("⟩",size)}</m:e>'
            f'<m:sub>{run("w",size,True)}</m:sub></m:sSub>')


def formulas():
    s=9.0
    product=script("∏","e",s)
    edge=script("C","e",s)
    return {
        "Math - Product first":average(product+edge,s),
        "Math - Average first":product+average(edge,s),
        "Math - Kernel key":(run("w",8.4,True)+run(" ∝ ",8.4)
                             +script("K","Hann",8.4)+script("S","ii",8.4)),
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck",type=Path)
    args=parser.parse_args()
    if args.deck.anchor:
        parser.error("Use a path relative to the handoff root.")
    native.apply(args.deck,formulas())
