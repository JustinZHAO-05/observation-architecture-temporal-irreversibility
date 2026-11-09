"""Insert editable PowerPoint math for the calibrated example."""
import argparse
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode=True
source=Path(__file__).resolve().parents[2]/"Fig1/reproduce/native_equations.py"
spec=importlib.util.spec_from_file_location("figure_math",source)
native=importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
run=native.run


def formulas():
    label_size=8.2
    def hat(letter):
        return ('<m:acc><m:accPr><m:chr m:val="&#x0302;"/></m:accPr>'
                f'<m:e>{run(letter,label_size,True)}</m:e></m:acc>')
    return {
        "Math - Spectral readout":(
            run("Im ",label_size)+f'<m:sSub><m:e>{hat("S")}</m:e>'
            f'<m:sub>{run("12",label_size)}</m:sub></m:sSub>'),
        "Math - Cycle readout":run("|Im ",label_size)+hat("P")+run("|",label_size),
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck",type=Path)
    args=parser.parse_args()
    if args.deck.anchor:
        parser.error("Use paths relative to the handoff root.")
    native.apply(args.deck,formulas())
