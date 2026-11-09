"""Install the Figure 7 native PowerPoint equations."""
import argparse
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
source = Path(__file__).resolve().parents[2] / "Fig1/reproduce/native_equations.py"
spec = importlib.util.spec_from_file_location("figure_math", source)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
run, script = native.run, native.script


def car():
    size = 8.85
    base = script("y", "i", size)
    average = (f'<m:sSup><m:e>{base}</m:e><m:sup>{run("CAR", size)}</m:sup></m:sSup>')
    time = run("(", size) + run("t", size, True) + run(")", size)
    fraction = run("(1/64)", size)
    summation = (
        f'<m:sSubSup><m:e>{run("∑", size)}</m:e>'
        f'<m:sub>{run("j", size, True)}{run("=1", size)}</m:sub>'
        f'<m:sup>{run("64", size)}</m:sup></m:sSubSup>{script("y", "j", size)}{time}'
    )
    return average + time + run(" = ", size) + base + time + run(" − ", size) + fraction + summation


def formulas():
    size = 8.65
    score = script("P", "A", 8.3) + run(", ", 8.3) + script("P", "B", 8.3) + run(" → ", 8.3) + run("Q", 8.3, True)
    return {
        "a - CAR formula": car(),
        "b - Score 0": score,
        "b - Score 1": score,
        "d - Vector label A": script("𝐯", "A", 8.75),
        "d - Vector label B": script("𝐯", "B", 8.75),
        "d - Angle label": run("φ", 8.7, True),
        "d - Score identity": run("Q", 9, True) + run(" = ", 9) + run("A", 9, True) + run(" cos ", 9) + run("φ", 9, True),
        "d - Amplitude factor": run("A", size, True) + run(" = RMS(", size) + script("𝐯", "A", size)
        + run(") RMS(", size) + script("𝐯", "B", size) + run(")", size),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    args = parser.parse_args()
    if args.deck.anchor:
        parser.error("Use a path relative to the handoff root.")
    native.apply(args.deck, formulas())
