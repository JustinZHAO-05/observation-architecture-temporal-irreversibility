"""Install the Fig. 3 mechanism's editable Office Math expressions."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
source = Path(__file__).resolve().parents[2]/"Fig1/reproduce/native_equations.py"
spec = importlib.util.spec_from_file_location("figure_math", source)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
run, script = native.run, native.script


def formulas(data):
    out = {}
    for example in data["examples"]:
        i = example["id"]
        size = 9.2
        theta = script("θ",str(i),size)
        out[f"Math - Phase {i}"] = theta+run(f" = {example['theta_rad']:.2f} rad",size)
        out[f"Math - Spectrum {i}"] = script("G",str(i),9.5)
        out[f"Math - u {i}"] = run("u",9.6,True)
        out[f"Math - v {i}"] = run("v",9.6,True)
        out[f"Math - Rotation {i}"] = (
            f"<m:sSup><m:e>{run('e',9.4)}</m:e>"
            f"<m:sup>{run('−',size)}{run('i',size,True)}{theta}</m:sup></m:sSup>")
        out[f"Math - Trace {i}"] = script("t","min",9.0)+run(f" ≈ {example['trace_ratio']:.4f}",9.0)
    ib = run("ib",8.5,True)
    out["Math - Cell 0"] = run("1",8.5)
    out["Math - Cell 1"] = ib
    out["Math - Cell 2"] = run("−",8.5)+ib
    out["Math - Cell 3"] = run("1",8.5)
    out["Math - Target"] = (run("S",8.9,True)+run("=",8.9)+script("I","2",8.9)+
                            run("+",8.9)+run("ibJ",8.9,True))
    out["Math - Strength"] = run("b",8.8,True)+run(f" = {data['b']:g}",8.8)
    out["Math - Trace axis"] = script("t","min",8.8)+run(" (log scale)",8.8)
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck",type=Path)
    parser.add_argument("data",type=Path)
    args=parser.parse_args()
    if args.deck.anchor or args.data.anchor:
        parser.error("Use paths relative to the handoff root.")
    native.apply(args.deck,formulas(json.loads(args.data.read_text(encoding="utf-8"))))
