"""Verify the EEG pairings and prepare the vector data layers for Figure 7."""
import argparse
from hashlib import md5, sha256
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
PROD = Path("03_FIGURE_PRODUCTION")
DEFAULT = PROD / "redraw/Fig7"
GRID = PROD / "generated_data/Fig7/redraw"
ROUND1 = Path("01_RESEARCH/ROUND1/neural_time_arrow_study")
ROUND2 = Path("01_RESEARCH/ROUND2/PRE_round2")
LAYOUT = {"a": (2, 2, 65, 46), "b": (70, 2, 106, 46), "c": (2, 50, 85, 63),
          "d": (90, 50, 86, 63), "e": (2, 115, 174, 41)}
INK, GRAY, BLUE = "#181B20", "#555D69", "#0072B2"
PALE = "#AAB4BE"
REFS = ("original", "average")
REF_LABELS = ("Original", "64-ch average")
SEED, DRAWS = 743109, 20000
EDF_SHA = "374dfa06c6df18e3bd324f4c8aefa462bacb6bf9dcbfe8d58ae6e84ed2bbc443"
ASSET_MD5 = "d2a0637fb2064d7065354d012f377fcc"

plt.rcParams.update({
    "font.family": "Arial", "font.size": 8.45, "axes.labelsize": 8.65, "axes.linewidth": .66,
    "mathtext.fontset": "custom", "mathtext.rm": "Cambria", "mathtext.it": "Cambria:italic",
    "svg.fonttype": "none", "svg.hashsalt": "pre-fig7-eeg", "pdf.fonttype": 42,
})


def table(name):
    return pd.read_csv(ROUND2 / "results" / f"eeg_{name}.csv", float_precision="round_trip")


def check_archives(records):
    provenance = json.loads((ROUND2 / "results/eeg_followup_provenance.json").read_text(encoding="utf-8"))
    for ref, rows in records.groupby("reference"):
        name = f"eeg_primary_{ref}_cycles.npz"
        path = ROUND2 / "inputs/round1_results" / name
        assert sha256(path.read_bytes()).hexdigest() == provenance["archive_sha256"][ref]
        with np.load(path) as archive:
            np.testing.assert_array_equal(archive["f"], np.arange(2, 30.1, .5))
            for row in rows.itertuples(index=False):
                key = f"S{row.subject:03d}R{row.run:02d}"
                a, b = (archive[f"{key}_{half}"].astype(float) for half in "ab")
                q = np.mean(a * b)
                amp = np.sqrt(np.mean(a * a)) * np.sqrt(np.mean(b * b))
                assert a.shape == b.shape == (57, 220)
                np.testing.assert_allclose([q, amp, q / amp],
                                           [row.q, row.amplitude_factor, row.alignment], rtol=0, atol=4e-16)


def statistics(out, verify_archive):
    records = table("complete_window_records")
    assert len(records) == 226 and records.subject.nunique() == 71 and records.subject.min() > 10
    assert set(records.reference) == set(REFS)
    assert records[["n_epochs_a", "n_epochs_b"]].eq(12).all().all()
    assert records.amplitude_factor.gt(0).all() and records.alignment.abs().le(1).all()
    residual = float((records.q - records.amplitude_factor * records.alignment).abs().max())
    assert residual < 1e-16
    if verify_archive:
        check_archives(records)
    pairs = records.pivot(index=["subject", "run"], columns="reference", values="q").reset_index()
    assert len(pairs) == 113 and not pairs.isna().any().any()
    assert pairs.groupby("run").size().to_dict() == {1: 52, 2: 61}
    pairs["condition"] = pairs.run.map({1: "eyes open", 2: "eyes closed"})
    wide = records.pivot(index="subject", columns=["reference", "run"], values="q").dropna()
    contrast = pd.DataFrame({ref: wide[ref][2] - wide[ref][1] for ref in REFS}).reset_index()
    assert len(contrast) == 42

    rng = np.random.default_rng(SEED)

    def interval(values):
        values = np.asarray(values)
        boot = values[rng.integers(len(values), size=(DRAWS, len(values)))].mean(axis=1)
        return np.quantile(boot, [.025, .975])

    for _, group in records.groupby(["run", "reference"]):
        interval(group.q)
    ratio, ref_stats = {}, table("reference_paired").set_index("run")
    for run, group in pairs.groupby("run"):
        observed = ref_stats.loc[run]
        ratio[run] = float(group.average.mean() / group.original.mean())
        np.testing.assert_allclose(ratio[run], observed.ratio_of_group_means, rtol=1e-13)
        np.testing.assert_allclose(interval(group.average - group.original),
                                   observed[["CI_low", "CI_high"]], rtol=0, atol=2e-16)
    condition = table("condition_paired")
    for row in condition.itertuples():
        delta = contrast[row.reference]
        np.testing.assert_allclose([delta.mean(), *interval(delta)],
                                   [row.mean_EC_minus_EO, row.CI_low, row.CI_high], rtol=0, atol=2e-16)
    condition["bootstrap_seed"], condition["bootstrap_draws"] = SEED, DRAWS
    group_stats = (records.groupby(["run", "reference"])[["q", "amplitude_factor", "alignment"]]
                   .mean().reset_index())
    for name, data in (("c_pairs", pairs), ("d_factors", records), ("d_group_means", group_stats),
                       ("e_participant_deltas", contrast), ("e_bootstrap", condition)):
        data.to_csv(out / "data" / f"Fig7{name}.csv", index=False)
    return records, pairs, contrast, condition, ratio, residual


def example(out, grid, edf, records):
    sys.path.insert(0, str(ROUND1 / "src"))
    try:
        from closure_core import read_edf
        from eeg_study import CHANNELS, analyze_record
    finally:
        sys.path.pop(0)
    manifest = pd.read_csv(ROUND1 / "results/raw_data_manifest.csv").set_index("relative_path")
    expected = manifest.loc["S011/S011R01.edf"]
    assert edf.stat().st_size == expected.size_bytes
    assert sha256(edf.read_bytes()).hexdigest() == EDF_SHA == expected.sha256
    signals, rates, labels, meta = read_edf(edf)
    eeg = [i for i, unit in enumerate(meta["units"]) if unit in ("uV", "µV")]
    assert len(eeg) == 64 and np.all(rates[eeg] == 160) and meta["duration"] == 61
    montage = pd.read_csv(PROD / "generated_data/Fig6/A.csv")
    assert montage.channel.nunique() == 64 and montage.selected.sum() == 12
    assert set(montage.channel.str.upper()) == {labels[i] for i in eeg}
    assert set(montage.loc[montage.selected, "channel"].str.upper()) == set(CHANNELS)
    montage.to_csv(out / "data/Fig7a_montage.csv", index=False)
    sample = np.arange(320, 481)
    time = sample / 160
    channel_uv = np.column_stack([signals[i][sample] for i in eeg])
    original = signals[labels.index("FZ")][sample]
    mean64 = channel_uv.mean(axis=1)
    average = original - mean64
    np.savez_compressed(grid / "Fig7a_Fz_excerpt.npz", time_s=time, samples=sample,
                        channels=np.array([labels[i] for i in eeg]), channel_uv=channel_uv,
                        fz_original_uv=original, mean64_uv=mean64, fz_average_uv=average,
                        edf_sha256=EDF_SHA, subject=11, run=1, sampling_hz=160)
    windows = pd.read_csv(PROD / "generated_data/Fig6/A_windows.csv")
    assert windows.start_s.to_list() == [*range(2, 26, 2), *range(34, 58, 2)]
    assert windows.groupby("half").size().to_dict() == {"A": 12, "B": 12}
    assert (windows.stop_s - windows.start_s).eq(2).all()
    windows = windows.assign(subject=11, run=1, duration_s=meta["duration"],
                             accepted_original=True, accepted_average=True)
    windows.to_csv(out / "data/Fig7b_windows.csv", index=False)

    # Validate the selected record against the original estimator and use its
    # genuine two-half vectors to scale the diagram.
    for ref in REFS:
        result, extras = analyze_record(edf, 11, 1, reference=ref)
        assert result["status"] == "ok" and result["n_epochs_a"] == result["n_epochs_b"] == 12
        a, b = (extras[f"v{half}"].astype(float) for half in "ab")
        assert a.shape == b.shape == (57, 220)
        q, rms_a, rms_b = np.mean(a*b), np.sqrt(np.mean(a*a)), np.sqrt(np.mean(b*b))
        amp = rms_a*rms_b
        alignment = q/amp
        archived = records.query("subject==11 and run==1 and reference==@ref").iloc[0]
        np.testing.assert_allclose([q, amp, alignment], archived[["q", "amplitude_factor", "alignment"]].astype(float),
                                   atol=2e-14, rtol=0)
    theta = np.arccos(alignment)
    first_angle = np.deg2rad(-24.)
    angles = np.array([first_angle, first_angle + theta])
    lengths = np.array([rms_a, rms_b])
    radii_mm = 10.6 * lengths / lengths.max()
    origin = np.array([15.2, 17.5])
    xy = origin + radii_mm[:, None] * np.stack((np.cos(angles), -np.sin(angles)), axis=-1)
    np.savez_compressed(grid / "Fig7d_example_vectors.npz", v_A=a, v_B=b, frequency_hz=extras["f"],
                        subject=11, run=1, reference="average", amplitude_factor=amp,
                        alignment=alignment, theta_rad=theta, q=q)
    geometry = pd.DataFrame({"half": list("AB"), "origin_x_mm": origin[0], "origin_y_mm": origin[1],
                             "end_x_mm": xy[:, 0], "end_y_mm": xy[:, 1], "angle_rad": angles,
                             "norm": lengths*np.sqrt(a.size), "angle_between_rad": theta})
    geometry.to_csv(out / "data/Fig7d_geometry.csv", index=False)
    return montage, time, original, average, float(theta)


def panel(key):
    _, _, w, h = LAYOUT[key]
    return plt.figure(figsize=(w / 25.4, h / 25.4), facecolor="none")


def axes(fig, box, key):
    _, _, w, h = LAYOUT[key]
    x, y, aw, ah = box
    return fig.add_axes((x/w, 1-(y+ah)/h, aw/w, ah/h), facecolor="none")


def polish(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=2.4, width=.58, pad=2.1, labelsize=8.05)


def save(fig, out, suffix):
    for ext, meta in (("svg", {"Date": None}), ("pdf", {"CreationDate": None, "ModDate": None})):
        fig.savefig(out / "panels" / f"Fig7{suffix}.{ext}", metadata=meta, transparent=True)
    plt.close(fig)


def outline(svg):
    assert md5(svg.read_bytes()).hexdigest() == ASSET_MD5
    head = next(node for node in ET.parse(svg).iter() if node.get("id") == "Head")
    assert len(head) == 4
    for node in head:
        pen = RecordingPen()
        parse_path(node.get("d"), pen)
        vertices, codes = [], []
        for command, points in pen.value:
            if command == "closePath":
                vertices.append(vertices[0])
                codes.append(PlotPath.CLOSEPOLY)
            elif command != "endPath":
                code = {"moveTo": PlotPath.MOVETO, "lineTo": PlotPath.LINETO,
                        "curveTo": PlotPath.CURVE4}[command]
                vertices.extend(((x-299.010)/244.2, (403.608-y)/244.2) for x, y in points)
                codes.extend([code]*len(points))
        yield PlotPath(vertices, codes)


def draw_a(out, montage, time, original, average, source):
    f = panel("a")
    m = axes(f, (1.4, 7.2, 29.9, 31.9), "a")
    for i, path in enumerate(outline(source)):
        m.add_patch(PathPatch(path, facecolor="#F5F8FA" if i == 0 else "none",
                              edgecolor=GRAY, linewidth=.65, capstyle="round"))
    for selected, color, size in ((False, "#AAB7C2", 4.6), (True, BLUE, 9.0)):
        group = montage[montage.selected == selected]
        m.scatter(group.x_2d, group.y_2d, s=size, color=color, lw=0, zorder=3)
    m.set(xlim=(-1.14, 1.14), ylim=(-1.04, 1.20), aspect="equal")
    m.set_axis_off()
    series = [(original, GRAY, 12.35), (average, BLUE, 25.6)]
    span = max(abs(np.r_[original, average]))
    extent = max(20, int(np.ceil(span/10))*10)
    for i, (value, color, y) in enumerate(series):
        ax = axes(f, (38.5, y, 25, 8.4), "a")
        polish(ax)
        ax.plot(time, value, color=color, lw=.67)
        ax.axhline(0, color="#D6DEE5", lw=.53, zorder=0)
        ax.set(xlim=(2, 3), ylim=(-extent, extent), yticks=[-extent, extent], xticks=[2, 3])
        ax.tick_params(axis="y", length=0, pad=1.3, labelsize=7.8)
        if i == 0:
            ax.spines["bottom"].set_visible(False)
            ax.set_xticks([])
        else:
            ax.set_xlabel("Time (s)", labelpad=1.1, fontsize=8.0)
    save(f, out, "a_data")


def heading(fig, key, name):
    _, _, w, h = LAYOUT[key]
    fig.text(1/w, 1-1.15/h, key, fontsize=12, weight="bold", va="top", color=INK)
    fig.text(7/w, 1-1.35/h, name, fontsize=10.35, weight="bold", va="top", color=INK)


def draw_c(out, pairs):
    f = panel("c")
    heading(f, "c", "Rereferencing effect")
    ax = axes(f, (16.8, 8.0, 46.0, 46.0), "c")
    polish(ax)
    limits = [-2.0, 11.4]
    assert pairs[["original", "average"]].to_numpy().min()*1e4 > limits[0]
    assert pairs[["original", "average"]].to_numpy().max()*1e4 < limits[1]
    ax.plot(limits, limits, color=PALE, lw=.78, ls=(0, (4, 2.3)), zorder=0)
    for run, marker, filled in ((1, "o", False), (2, "^", True)):
        g = pairs[pairs.run == run]
        ax.scatter(g.original*1e4, g.average*1e4, s=11 if run == 1 else 14, marker=marker,
                   facecolor=GRAY if filled else "white", edgecolor=GRAY, linewidth=.6, alpha=.88)
    ax.set(xlim=limits, ylim=limits, xticks=[-2, 0, 4, 8], yticks=[-2, 0, 4, 8], aspect="equal",
           xlabel=r"$Q_{\mathrm{original}}\ (10^{-4})$", ylabel=r"$Q_{\mathrm{average}}\ (10^{-4})$")
    markers = [Line2D([], [], ls="", marker=m, color=GRAY, markerfacecolor=fill, ms=3.9,
                      markeredgewidth=.65, label=text)
               for m, fill, text in (("o", "white", "Eyes open"), ("^", GRAY, "Eyes closed"))]
    ax.legend(handles=markers, loc="upper left", bbox_to_anchor=(1.022, .99), fontsize=8.0,
              frameon=False, handlelength=1.0, handletextpad=.45, labelspacing=.31, borderaxespad=0)
    save(f, out, "c")


def draw_d(out, grid, records):
    f = panel("d")
    ax = axes(f, (14, 28.5, 69, 25.7), "d")
    polish(ax)
    xa, ya = np.meshgrid(np.linspace(.72, 3.34, 160), np.linspace(-.13, .425, 160))
    z = 10*xa*ya
    levels = [-1, 2, 5, 8]
    ax.contour(xa, ya, z, levels=levels, colors="#BDC8D0", linewidths=.59,
               linestyles="dotted", zorder=0)
    # Label the analytical iso-score curves at the same amplitude.
    for q in levels:
        ax.text(3.245, q/(10*3.245), f"{q:g}", va="center", ha="left",
                fontsize=7.55, color=GRAY, bbox=dict(fc="white", ec="none", pad=.3))
    ax.text(3.28, .371, r"$Q\ (10^{-4})$", ha="right", va="center", fontsize=7.75, color=GRAY)
    np.savez_compressed(grid / "Fig7d_isoscore_grid.npz", amplitude=xa/1e3, alignment=ya,
                        q=z/1e4, levels=np.array(levels)/1e4)
    pairs = records.pivot(index=["subject", "run"], columns="reference",
                          values=["amplitude_factor", "alignment"])
    ax.plot(pairs["amplitude_factor"][list(REFS)].to_numpy().T*1e3,
            pairs["alignment"][list(REFS)].to_numpy().T, color="#A3ADB6", alpha=.28, lw=.55, zorder=1)
    for ref, color, fill, marker in (("original", GRAY, "white", "o"), ("average", BLUE, BLUE, "s")):
        r = records[records.reference == ref]
        ax.scatter(r.amplitude_factor*1e3, r.alignment, s=8.2, color=fill, edgecolor=color,
                   alpha=.84, linewidth=.56, marker=marker, zorder=2)
    ax.set(xlim=(.72, 3.34), ylim=(-.13, .42), xticks=[1, 2, 3], yticks=[-.1, 0, .2, .4],
           xlabel=r"Amplitude factor $(10^{-3})$", ylabel="Alignment")
    handles = [Line2D([], [], ls="", marker=m, markerfacecolor=f, color=c, ms=3.7,
                      markeredgewidth=.62, label=l)
               for m, f, c, l in (("o", "white", GRAY, REF_LABELS[0]), ("s", BLUE, BLUE, REF_LABELS[1]))]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.06), frameon=False, fontsize=8.0,
              ncol=2, columnspacing=1.25, handlelength=1, handletextpad=.48, borderaxespad=0)
    save(f, out, "d_data")


def draw_e(out, contrast, condition):
    f = panel("e")
    heading(f, "e", "Within-participant condition contrast")
    ax = axes(f, (24.5, 8.5, 127.0, 24.8), "e")
    polish(ax)
    y = contrast[list(REFS)].to_numpy()*1e4
    ax.axhline(0, color=PALE, lw=.75, ls=(0, (4, 2)), zorder=0)
    ax.plot([0, 1], y.T, color="#929FAB", lw=.61, alpha=.42, zorder=1)
    for i, (ref, color) in enumerate(zip(REFS, (GRAY, BLUE), strict=True)):
        ax.scatter(np.full(len(y), i), y[:, i], s=9.5, color=color, linewidth=0, alpha=.72, zorder=2)
        row = condition[condition.reference == ref].iloc[0]
        mean, low, high = row[["mean_EC_minus_EO", "CI_low", "CI_high"]]*1e4
        ax.errorbar(i + (-.13 if i == 0 else .13), mean, yerr=[[mean-low], [high-mean]],
                    color=INK, marker="D", markersize=4.25, capsize=2.8, lw=1.0, zorder=5)
    ax.set(xlim=(-.49, 1.49), ylim=(-2.6, 5.65), xticks=[0, 1], xticklabels=REF_LABELS,
           ylabel=r"$\Delta Q\ (10^{-4})$")
    ax.yaxis.set_major_locator(MaxNLocator(4, integer=True))
    handles = [Line2D([], [], color="#929FAB", lw=.7, marker="o", ms=2.5, label="Participant"),
               Line2D([], [], color=INK, ls="", marker="D", ms=4.1, label="Mean, 95% CI")]
    ax.legend(handles=handles, loc="upper right", fontsize=8.0, frameon=False, handlelength=1.25,
              handletextpad=.44, labelspacing=.33, borderaxespad=.32)
    save(f, out, "e")


def build(out, grid, edf, asset, verify_archive):
    (out / "data").mkdir(parents=True, exist_ok=True)
    (out / "panels").mkdir(exist_ok=True)
    grid.mkdir(parents=True, exist_ok=True)
    records, pairs, contrast, ci, ratio, residual = statistics(out, verify_archive)
    montage, time, orig, avg, theta = example(out, grid, edf, records)
    draw_a(out, montage, time, orig, avg, asset)
    draw_c(out, pairs)
    draw_d(out, grid, records)
    draw_e(out, contrast, ci)
    checks = dict(matched_records=len(pairs), unique_participants=71, eyes_open=52, eyes_closed=61,
                  paired_participants=len(contrast), reference_records=len(records),
                  ratio_of_group_means=ratio, max_q_product_error=residual, edf_sha256=EDF_SHA,
                  asset_md5=ASSET_MD5, example_angle_deg=float(np.rad2deg(theta)), sampling_hz=160,
                  analysis_channels=12, car_channels=64, windows_per_half=12,
                  bootstrap_seed=SEED, bootstrap_draws=DRAWS, full_cycle_archive_checked=verify_archive)
    (out / "data/Fig7_checks.json").write_text(json.dumps(checks, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--grid-output", type=Path, default=GRID)
    parser.add_argument("--edf", type=Path, default=DEFAULT/"inputs/S011R01.edf")
    parser.add_argument("--asset", type=Path, default=DEFAULT/"inputs/Kraemer_EEG_10_20.svg")
    parser.add_argument("--verify-archive", action="store_true")
    args = parser.parse_args()
    if any(path.anchor for path in (args.output, args.grid_output, args.edf, args.asset)):
        parser.error("Run from the handoff root with relative paths.")
    build(args.output, args.grid_output, args.edf, args.asset, args.verify_archive)
