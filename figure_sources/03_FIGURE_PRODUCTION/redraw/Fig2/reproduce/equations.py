"""Native PowerPoint math zones for the one-sample delay mechanism."""
import argparse
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
helper = Path(__file__).resolve().parents[2]/"Fig1/reproduce/native_equations.py"
spec = importlib.util.spec_from_file_location("figure_math",helper)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
run = native.run
script = native.script


def formulas():
    size = 9.4
    out = {}
    for i in "123":
        for letter in "uvy":
            out[f"Labels - {letter}{i}"] = script(letter,i,size)
        out[f"Labels - delay{i}"] = script("z","−1",size,upper=True)
    s = 9.1
    out["Labels - real-spectrum"] = (run("G",s,True)+run("(",s)+run("ω",s,True)+
        run(")∈",s)+script("ℝ","6×6",s,upper=True))
    def call(letter,time,s=9.2):
        return script(letter,"i",s)+run("(",s)+run("t",s,True)+(run(time,s) if time else "")+run(")",s)
    out["Timing labels - minus-one"] = run("t",8.6,True)+run("−1",8.6)
    out["Timing labels - current"] = run("t",8.6,True)
    out["Timing labels - selected-v"] = call("v","−1")
    out["Timing labels - selected-u"] = call("u","")
    out["Labels - observation"] = call("y","")+run("=",9.2)+call("u","")+run("+",9.2)+call("v","−1")
    return out


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("deck",type=Path)
    args=p.parse_args()
    if args.deck.is_absolute():
        p.error("Use a relative deck path.")
    native.apply(args.deck,formulas())
