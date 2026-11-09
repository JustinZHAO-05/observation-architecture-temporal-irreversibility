"""Journal style and paths for the revised supplementary figures."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from common import Build, TWO, import_file, vector_matrix
import matplotlib as mpl
import numpy as np

BLUE, ORANGE, TEAL, GRAY = "#0072B2", "#D55E00", "#009E73", "#555D69"
PURPLE, LIGHT, INK = "#A05A8A", "#AAB5C1", "#181B20"
COLORS = (BLUE, ORANGE, TEAL, PURPLE)
MARKERS = ("o", "s", "^", "D")
SEED = 261109
PROD = Path("03_FIGURE_PRODUCTION")

mpl.rcParams.update({
    "font.family": "Arial", "font.size": 8.6, "axes.labelsize": 8.55, "axes.titlesize": 8.55,
    "legend.fontsize": 7.9, "xtick.labelsize": 8, "ytick.labelsize": 8, "text.color": INK,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "axes.linewidth": .64,
    "mathtext.fontset": "custom", "mathtext.rm": "Cambria", "mathtext.it": "Cambria:italic",
    "svg.hashsalt": "PRE-supplement-revised",
})


def supplement(root, out, number, titles, boxes=TWO, height=12.6):
    f = Build(root, out, f"FigS{number}", height, boxes, titles)
    f.rng = np.random.default_rng(SEED + number)
    for p in f.panels:
        label, title = p.artists
        label.set_text(p.key.lower())
        label.set_fontweight("bold")
        label.set_fontsize(11.6)
        title.set_fontsize(10.25)
    return f


def key_ticks(ax, x, symbols=None):
    ax.set_xticks(x, symbols if symbols is not None else [f"{v:g}" for v in x])
    ax.tick_params(axis="x", which="minor", labelbottom=False)


def legend(ax, **kwargs):
    return ax.legend(frameon=False, handlelength=1.45, handletextpad=.45, borderaxespad=.35, **kwargs)
