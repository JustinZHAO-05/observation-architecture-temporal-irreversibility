"""Shared journal layout and reproducible exports. All CLI paths are relative."""
import argparse
import importlib.util
import json
import os
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.transforms import Bbox
import numpy as np
import pandas as pd

A = "#3973A5"
B = "#C66A3C"
TARGET = "#1B5C8C"
LATENT = "#6D7B8E"
GREEN = "#23886F"
GRAY = "#ADB5BD"
INK = "#172839"
EO = "#4E7CA3"
EC = "#D18A51"
SEED = 261108

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8,
    "axes.titlesize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.65, "lines.linewidth": 1.5, "lines.markersize": 3.8,
    "xtick.major.size": 2.8, "ytick.major.size": 2.8,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK,
    "svg.fonttype": "none", "svg.hashsalt": "PRE-temporal-figures",
    "pdf.fonttype": 42, "mathtext.fontset": "dejavusans",
})

TWO = [(0, .53, .48, .47), (.52, .53, .48, .47),
       (0, 0, .48, .47), (.52, 0, .48, .47)]
WIDE_TOP = [(0, .56, 1, .44), (0, 0, .48, .50), (.52, 0, .48, .50)]


class Panel:
    def __init__(self, figure, box, key, title):
        self.figure, self.box, self.key = figure, box, key
        x, y, w, h = box
        self.artists = [
            figure.text(x+.008,y+h-.024,f"({key.lower()})",va="top",
                        size=11,weight="semibold",gid=f"panel-{key}"),
            figure.text(x+.051,y+h-.030,title,va="top",weight="semibold"),
        ]

    def ax(self, x=.16, y=.19, w=.80, h=.64, *, diagram=False, tag=""):
        a, b, c, d = self.box
        ax = self.figure.add_axes((a+x*c, b+y*d, w*c, h*d))
        ax.set_gid(f"{self.key}-{tag or len(self.figure.axes)}")
        self.artists.append(ax)
        if diagram:
            ax.set(xlim=(0, 1), ylim=(0, 1))
            ax.set_axis_off()
        return ax


class Build:
    def __init__(self, root, production, name, height, boxes, titles):
        self.r1 = root / "01_RESEARCH/ROUND1/neural_time_arrow_study"
        self.r2 = root / "01_RESEARCH/ROUND2/PRE_round2"
        self.name = name
        self.out = production / "submission_figures" / name
        self.data = production / "generated_data" / name
        self.out.mkdir(parents=True, exist_ok=True)
        self.data.mkdir(parents=True, exist_ok=True)
        self.figure = plt.figure(figsize=(17.8/2.54, height/2.54), facecolor="white")
        self.panels = [Panel(self.figure, b, k, t)
                       for b, k, t in zip(boxes, "ABCD", titles, strict=False)]
        self.rng = np.random.default_rng(SEED)
        self.artifacts = {}

    def csv(self, key, table, suffix=""):
        p = self.data / f"{key}{suffix}.csv"
        pd.DataFrame(table).to_csv(p, index=False, float_format="%.17g")
        self.artifacts.setdefault(key, []).append(p.name)
        return table

    def npz(self, key, **arrays):
        p = self.data / f"{key}.npz"
        np.savez_compressed(p, **arrays)
        self.artifacts.setdefault(key, []).append(p.name)

    def archive_csv(self, round_number, name):
        return pd.read_csv((self.r1 if round_number == 1 else self.r2) / "results" / name)

    def finish(self, caption):
        expected = {p.key for p in self.panels}
        assert self.artifacts.keys() == expected, (self.name, self.artifacts)
        caption=caption.replace(r"\(", "$").replace(r"\)", "$")
        (self.out / "caption.md").write_text(caption.strip() + "\n", encoding="utf-8")
        (self.out / "panel_data.json").write_text(json.dumps(self.artifacts, indent=2)+"\n",
                                                  encoding="utf-8")
        for ax in self.figure.axes:
            for collection in ax.collections:
                collection.set_rasterized(False)
                if collection.get_label() == "colorbar-solids":
                    collection.set_edgecolor("face")
                    collection.set_linewidth(.26)
        for ext in ("svg", "pdf", "png"):
            metadata = {"Date": None} if ext == "svg" else (
                {"CreationDate": None, "ModDate": None} if ext == "pdf" else None)
            self.figure.savefig(self.out / f"{self.name}.{ext}", dpi=600, metadata=metadata)
        self.export_panels()
        plt.close(self.figure)

    def export_panels(self):
        # Save only the panel's artists, with its title and axis decorations.
        directory=self.out/"panels"
        directory.mkdir(exist_ok=True)
        for p in self.panels:
            for other in self.panels:
                for artist in other.artists:
                    artist.set_visible(other is p)
            self.figure.draw_without_rendering()
            renderer=self.figure._get_renderer()
            x,y,w,h=p.box
            fw,fh=self.figure.get_size_inches()
            box=Bbox.from_bounds(x*fw,y*fh,w*fw,h*fh)
            decoration_boxes=[artist.get_tightbbox(renderer).transformed(self.figure.dpi_scale_trans.inverted())
                              for artist in p.artists]
            bounds=Bbox.union([box,*decoration_boxes]).padded(.025)
            self.figure.savefig(directory/f"{p.key}.svg",bbox_inches=bounds,
                                metadata={"Date":None},dpi=600)
        for p in self.panels:
            for artist in p.artists:
                artist.set_visible(True)


def import_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def arrow(ax, start, end, color=LATENT, *, curve=0, style="-|>", lw=1.1):
    patch = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=8,
                            color=color, connectionstyle=f"arc3,rad={curve}",
                            linewidth=lw, shrinkA=0, shrinkB=0)
    ax.add_patch(patch)
    return patch


def block(ax, x, y, w, h, label, color=LATENT, fill="white"):
    ax.add_patch(Rectangle((x-w/2, y-h/2), w, h, facecolor=fill,
                           edgecolor=color, lw=1))
    ax.text(x, y, label, ha="center", va="center", color=color)


def tag(ax, x, y, label, **kwargs):
    ax.text(x, y, label, ha="center", va="center", **kwargs)


def math_sci(value, digits=2):
    coefficient, exponent = f"{value:.{digits}e}".split("e")
    return rf"${coefficient}\times10^{{{int(exponent)}}}$"


def vector_matrix(ax, matrix, lim):
    n, m = matrix.shape
    h = ax.pcolormesh(np.arange(m+1), np.arange(n+1), matrix,
                      cmap="RdBu_r", vmin=-lim, vmax=lim, antialiased=False,
                      edgecolors="face", linewidth=0.04)
    ax.set(xlim=(0, m), ylim=(n, 0), xticks=[], yticks=[], aspect="equal")
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(GRAY)
        spine.set_linewidth(.5)
    return h


def cli(builders):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("figures", nargs="*", help="Figure identifiers, e.g. Fig2 Fig1")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--production", type=Path, default=Path("03_FIGURE_PRODUCTION"),
                        help="Output directory relative to the handoff root")
    args = parser.parse_args()
    for option in (args.root, args.production):
        if option.anchor:
            parser.error("CLI paths must be relative")
    for name in args.figures or builders:
        if name not in builders:
            parser.error(f"Unknown figure: {name}")
        print(f"Building {name}", flush=True)
        builders[name](args.root, args.root / args.production)
