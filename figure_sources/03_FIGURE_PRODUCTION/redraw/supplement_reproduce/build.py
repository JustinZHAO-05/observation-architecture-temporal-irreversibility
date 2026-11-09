"""Rebuild the reorganized S1–S8 from the handoff root."""
import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from theory import s1, s2, s3, s4
from inference import s5, s6, s7, s8

BUILDERS = {f"FigS{i}": fn for i,fn in enumerate((s1,s2,s3,s4,s5,s6,s7,s8),1)}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("figures",nargs="*")
    parser.add_argument("--output",type=Path,default=Path("03_FIGURE_PRODUCTION/supplement_rebuilt"))
    args=parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    for figure in args.figures or BUILDERS:
        if figure not in BUILDERS:
            parser.error(f"Unknown supplement: {figure}")
        print(f"Building {figure}",flush=True)
        BUILDERS[figure](Path("."),args.output)
