"""Verify the rotational-block optimum and draw the analytic Fig. 3 panels."""
import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
import numpy as np

INK, GRAY = "#181B20", "#555D69"
COLORS = ("#4C9787", "#007B6C", "#006053", "#193E42")
STYLES = ("-", (0, (4, 1.9)), (0, (5, 1.7, 1.2, 1.7)), (0, (1.25, 1.5)))
STRENGTHS = (0.2, 0.5, 0.8, 0.9)
EXAMPLE_B, EXAMPLE_THETA = .8, (.8, .05)
MARKERS = ("o", "D")
THETA_RANGE = (.01, 1.5)
LAYOUT = {"a": (2, 2, 61, 108), "b": (65, 2, 111, 50), "c": (65, 54, 111, 56)}
ARCHIVE = Path("01_RESEARCH/ROUND2/PRE_round2/results")
DEFAULT_OUTPUT = Path("03_FIGURE_PRODUCTION/redraw/Fig3")
DEFAULT_GRID = Path("03_FIGURE_PRODUCTION/generated_data/Fig3/redraw")

plt.rcParams.update({
    "font.family": "Arial", "font.size": 8.4, "axes.labelsize": 9,
    "mathtext.fontset": "custom", "mathtext.rm": "Cambria", "mathtext.it": "Cambria:italic",
    "axes.linewidth": .65, "svg.fonttype": "none", "svg.hashsalt": "pre-fig3-trace",
    "pdf.fonttype": 42,
})


def trace_ratio(b, theta):
    return (1 - abs(np.cos(theta)) * np.sqrt(1 - b**2)) / np.sin(theta)**2


def read_archive():
    curve = np.genfromtxt(ARCHIVE/"latency_power_curves.csv", delimiter=",", names=True)
    assert len(curve) == 400
    assert np.array_equal(np.unique(curve["b"]), [0.2, 0.5, 0.8, 0.95])
    assert np.allclose(curve["minimum_power_ratio"], trace_ratio(curve["b"], curve["theta"]), rtol=2e-13)
    assert np.allclose(curve["small_delay_coefficient"], 1-np.sqrt(1-curve["b"]**2))
    lp = np.genfromtxt(ARCHIVE/"latency_cost_lp_intervals.csv", delimiter=",", names=True)
    assert len(lp) == 32 and len(set(zip(lp["b"], lp["theta"]))) == 32
    assert np.allclose(lp["analytic_ratio"], trace_ratio(lp["b"], lp["theta"]), rtol=2e-13)
    assert np.all(lp["lower_ratio"]-1e-9 <= lp["analytic_ratio"])
    assert np.all(lp["analytic_ratio"] <= lp["upper_ratio"]+1e-9)
    return curve, lp


def save_examples(out):
    theta = np.array(EXAMPLE_THETA)
    eye = np.eye(2)
    skew = np.array([[0., 1.], [-1., 0.]])
    target = eye + 1j * EXAMPLE_B * skew
    cost = trace_ratio(EXAMPLE_B, theta)
    p = cost/2
    q = (1-cost)/(2*np.cos(theta))
    j = EXAMPLE_B/(2*np.sin(theta))
    spectra, transfers = [], []
    for tk, pk, qk, jk in zip(theta, p, q, j, strict=True):
        cross = qk*eye + jk*skew
        spectra.append(np.block([[pk*eye, cross], [cross.T, pk*eye]]))
        transfers.append(np.concatenate([eye, np.exp(-1j*tk)*eye], axis=1))
    g, h = np.array(spectra), np.array(transfers)
    reconstructed = h @ g @ h.conj().transpose(0, 2, 1)
    error = np.max(abs(reconstructed-target), axis=(1, 2))
    eigmin = np.linalg.eigvalsh(g)[:,0]
    assert np.max(error) < 1e-12 and np.min(eigmin) > -1e-12
    assert np.allclose(p, np.hypot(q, j), atol=1e-12)
    assert np.allclose(np.trace(g,axis1=1,axis2=2)/np.trace(target).real, cost)
    np.savez_compressed(out/"data/Fig3a_optima.npz", b=EXAMPLE_B, theta_rad=theta,
                       p=p, q=q, j=j, minimum_trace_ratio=cost, latent_spectrum=g,
                       transfer=h, target_spectrum=target, reconstructed_spectrum=reconstructed)
    examples = [dict(id=k, theta_rad=float(tk), trace_ratio=float(t), marker=marker)
                for k,(tk,t,marker) in enumerate(zip(theta,cost,MARKERS,strict=True),1)]
    (out/"data/Fig3a_mechanism.json").write_text(json.dumps(dict(b=EXAMPLE_B,examples=examples),indent=2)+"\n",
                                              encoding="utf-8")
    return cost, error, eigmin


def make_panel(letter, title):
    _, _, width, height = LAYOUT[letter]
    fig = plt.figure(figsize=(width/25.4,height/25.4), facecolor="white")
    fig.text(.015,1-2.3/height,letter,fontsize=12,fontweight="bold",va="top",color=INK)
    fig.text(.070,1-2.6/height,title,fontsize=10.4,fontweight="bold",va="top",color=INK)
    return fig


def format_phase(ax, label):
    ax.set_xscale("log")
    ax.set_xlim(*THETA_RANGE)
    ax.xaxis.set_major_locator(FixedLocator([.01,.03,.1,.3,1]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_: f"{x:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel(label, labelpad=1.7)
    for side in ("top","right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(which="major",length=2.5,width=.6,pad=1.75,color=INK)
    ax.tick_params(which="minor",length=1.3,width=.5,color=GRAY)


def save(fig,out,letter):
    path=out/"panels"/f"Fig3{letter}"
    fig.savefig(path.with_suffix(".svg"),metadata={"Date":None})
    fig.savefig(path.with_suffix(".pdf"),metadata={"CreationDate":None,"ModDate":None})
    plt.close(fig)


def draw_scaling(out, archive, cost):
    fig=make_panel("b","Small-phase scaling")
    ax=fig.add_axes((.135,.204,.840,.602))
    format_phase(ax,r"$|\theta|$ (rad)")
    ax.set_yscale("log")
    ax.set_ylim(.48,8500)
    ax.yaxis.set_major_locator(FixedLocator([1,10,100,1000]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_: f"{x:g}"))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_ylabel(r"$t_{\min}$",labelpad=3)
    ax.grid(axis="y",which="major",color="#D9E2DF",linewidth=.5)
    ax.set_axisbelow(True)

    rows=[]
    for b,color,style in zip(STRENGTHS,COLORS,STYLES,strict=True):
        data=archive[archive["b"]==b]
        if len(data):
            phase,ratio=data["theta"],data["minimum_power_ratio"]
            origin="archived_analytic"
        else:
            phase=archive[archive["b"]==EXAMPLE_B]["theta"]
            ratio=trace_ratio(b,phase)
            origin="theorem_2_on_archived_grid"
        assert len(phase)==100 and np.all(np.diff(phase)>0)
        rows.extend(("minimum",b,t,r,origin) for t,r in zip(phase,ratio,strict=True))
        ax.plot(phase,ratio,color=color,ls=style,lw=1.5,label=rf"$b={b:g}$")
    asym_phase=np.geomspace(.0104,.042,55)
    coefficient=1-np.sqrt(1-EXAMPLE_B**2)
    asym=coefficient/asym_phase**2
    assert np.max(abs(asym/trace_ratio(EXAMPLE_B,asym_phase)-1))<.003
    rows.extend(("asymptote",EXAMPLE_B,t,r,"theorem_2_small_phase") for t,r in zip(asym_phase,asym,strict=True))
    ax.plot(asym_phase,asym,color=INK,ls=(0,(2.5,2.1)),lw=.85,zorder=5)
    ax.annotate(r"$|\theta|^{-2}$",xy=(.030,coefficient/.030**2),xytext=(.063,830),
                color=INK,fontsize=8.5,arrowprops=dict(arrowstyle="-",lw=.58,color=GRAY))
    for phase,ratio,marker in zip(EXAMPLE_THETA,cost,MARKERS,strict=True):
        ax.plot(phase,ratio,marker=marker,ls="none",ms=4.9,mfc="white",mec=INK,mew=.9,zorder=6)
    ax.legend(loc="upper right",ncol=2,frameon=False,columnspacing=1.0,handlelength=2,
              handletextpad=.5,borderaxespad=.35,fontsize=8.15)
    with (out/"data/Fig3b_curves.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(["series","b","theta_rad","trace_ratio","provenance"])
        writer.writerows(rows)
    save(fig,out,"b")


def draw_map(out, grid_output, cost):
    theta=np.unique(np.r_[np.geomspace(*THETA_RANGE,301),EXAMPLE_THETA])
    b=np.unique(np.r_[np.linspace(0,.99,200),EXAMPLE_B])
    ratio=trace_ratio(b[:,None],theta[None,:])
    field=np.log10(ratio)
    for phase,minimum in zip(EXAMPLE_THETA,cost,strict=True):
        assert ratio[b==EXAMPLE_B,theta==phase][0]==minimum
    np.savez_compressed(grid_output/"Fig3c_grid.npz",theta_rad=theta,b=b,trace_ratio=ratio,log10_trace_ratio=field)
    fig=make_panel("c","Power-cost landscape")
    ax=fig.add_axes((.135,.187,.752,.643))
    format_phase(ax,r"$\theta$ (rad)")
    ax.set_ylim(b[0],b[-1])
    ax.set_yticks([0,.2,.4,.6,.8])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_: f"{x:g}"))
    ax.set_ylabel(r"$b$",labelpad=5)
    cmap=LinearSegmentedColormap.from_list("cost",["#F7FAF5","#D2E8DC","#96C9B8","#438F80","#225F59","#143D41"])
    levels=np.arange(-.4,4.01,.2)
    filled=ax.contourf(theta,b,field,levels=levels,cmap=cmap,norm=Normalize(-.4,4),antialiased=False)
    colors=("#3D615C","#355953","#173C3A","#F0F9F5")
    for k,(strength,color) in enumerate(zip((.34,.43,.54,.69),colors,strict=True)):
        contour=ax.contour(theta,b,field,levels=[k],colors=[color],linewidths=.75)
        values=np.log10(trace_ratio(strength,theta))
        idx=np.argmin(abs(values-k))
        ax.clabel(contour,fmt={k:str(10**k)},manual=[(theta[idx],strength)],
                  fontsize=8.3,inline=True,inline_spacing=3)
    for phase,marker in zip(EXAMPLE_THETA,MARKERS,strict=True):
        ax.plot(phase,EXAMPLE_B,marker=marker,ls="none",ms=5.3,mfc="white",mec=INK,mew=.95,zorder=7)
    ax.spines[["top","right"]].set_visible(True)
    cax=fig.add_axes((.907,.204,.016,.588))
    scale=fig.colorbar(filled,cax=cax,ticks=[0,1,2,3,4],drawedges=False)
    scale.solids.set_rasterized(False)
    scale.outline.set_linewidth(.6)
    scale.ax.tick_params(length=2.3,width=.6,pad=1.4,labelsize=8.25)
    scale.ax.set_title(r"$\log_{10}t_{\min}$",pad=10,fontsize=8.6)
    save(fig,out,"c")
    return list(ratio.shape)


def build(out, grid_output):
    (out/"panels").mkdir(parents=True,exist_ok=True)
    (out/"data").mkdir(exist_ok=True)
    grid_output.mkdir(parents=True,exist_ok=True)
    archive,lp=read_archive()
    cost,error,eigmin=save_examples(out)
    draw_scaling(out,archive,cost)
    shape=draw_map(out,grid_output,cost)
    checks=dict(strengths=list(STRENGTHS),analytic_curve_points_per_strength=100,
                archived_curve_rows=len(archive),example_b=EXAMPLE_B,example_theta_rad=list(EXAMPLE_THETA),
                example_trace_ratio=cost.tolist(),example_min_latent_eigenvalue=eigmin.tolist(),
                example_max_spectral_error=error.tolist(),map_shape=shape,
                independent_lp_settings=len(lp),lp_max_relative_width=float(lp["relative_interval_width"].max()),
                lp_max_equality_residual=float(lp["constraint_error"].max()))
    (out/"data/Fig3_checks.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(checks,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument("--grid-output",type=Path,default=DEFAULT_GRID)
    args=parser.parse_args()
    if args.output.anchor or args.grid_output.anchor:
        parser.error("Paths must be relative to the handoff root.")
    build(args.output,args.grid_output)
