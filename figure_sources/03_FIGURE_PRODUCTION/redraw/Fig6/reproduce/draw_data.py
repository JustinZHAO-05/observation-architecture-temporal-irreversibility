"""Replay the representative calibrated trajectory and draw the Fig. 6 data."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter, NullLocator
import numpy as np
import pandas as pd

sys.dont_write_bytecode=True
ROUND2=Path("01_RESEARCH/ROUND2/PRE_round2")
ARCHIVE=ROUND2/"results"
DEFAULT_OUTPUT=Path("03_FIGURE_PRODUCTION/redraw/Fig6")
DEFAULT_GRID=Path("03_FIGURE_PRODUCTION/generated_data/Fig6/redraw")
LAYOUT={"a-native":(2,2,174,38),"a-data":(2,11.6,174,25.6),
        "b":(2,42,92,81),"c":(97,42,79,81)}
INK,GRAY,BLUE,ORANGE,TEAL,PURPLE="#181B20","#555D69","#0072B2","#D55E00","#009E73","#8E5385"
NGRID=(2048,8192,32768,131072)
RATE_N=(32768,131072,524288)
STRENGTHS=(.35,.65,.9)
REPLAY_SEED=713420
JITTER_SEED=26110906

plt.rcParams.update({
    "font.family":"Arial","font.size":8.4,"axes.labelsize":8.65,"axes.linewidth":.62,
    "mathtext.fontset":"custom","mathtext.rm":"Cambria","mathtext.it":"Cambria:italic",
    "svg.fonttype":"none","svg.hashsalt":"pre-fig6-calibration","pdf.fonttype":42,
})


def replay(grid,archive_rates):
    sys.path.insert(0,str(ROUND2/"src"))
    try:
        from theory_round2 import ma_coeff,ma_spectrum
        from continuous_rate_certificate import autocov,rate_bound
        from finite_certificate import certificate,exact_triangle_bound
    finally:
        sys.path.pop(0)
    n,b,L,B,tail,alpha,cells=524288,.9,1,1.9,0.,.05,2048
    z=np.random.default_rng(REPLAY_SEED).normal(size=(n+2,3))
    m0,m1=ma_coeff(b)
    y=(z[1:]@m0.T+z[:-1]@m1.T)[:n]
    rate,radius,variation,w,estimate=rate_bound(y,L,B,alpha=alpha,cells=cells,tail=tail)
    lower,cycle,error=certificate(estimate,radius+variation)
    true=np.array([ma_spectrum(b,wi) for wi in w])
    population=exact_triangle_bound(true)
    row=archive_rates.query("max_delay == 0 and N == @n and rep == 0")
    assert len(row)==1 and w.size==cells and np.isclose(rate,lower.mean(),rtol=1e-13)
    compared=[rate,radius,variation,np.max(abs(estimate-true)),population.mean()]
    keys=["rate_lower","uniform_radius","cell_variation","dense_grid_max_error","population_triangle_integral"]
    assert np.allclose(compared,row[keys].iloc[0].to_numpy(dtype=float),rtol=1e-8,atol=5e-13)
    assert np.max(abs(estimate-true))<=radius
    assert np.all(lower<=population+1e-12) and rate>0
    assert np.allclose(lower[:cells//2],lower[cells//2:][::-1],atol=2e-14)
    delta=abs(cycle)-error
    ex=dict(record_excerpt=y[:48],lag_covariances=autocov(y,5),omega_rad_sample=w,
            cell_edges_rad_sample=np.linspace(0,2*np.pi,cells+1),true_spectrum=true,
            estimated_spectrum=estimate,spectrum_lower_imag=estimate.imag-radius,
            spectrum_upper_imag=estimate.imag+radius,uniform_radius=radius,
            cell_variation=variation,cell_radius=radius+variation,raw_cycle=cycle,
            cycle_error=error,cycle_positive_margin=np.maximum(0,delta),
            certified_density=lower,population_triangle_density=population,
            certified_rate=rate,seed=REPLAY_SEED,rep=0,b=b,N=n,B=B,T_L=tail,L=L,
            alpha=alpha,net_points=16,integral_cells=cells,max_delay=0)
    np.savez_compressed(grid/"Fig6a_representative_trajectory.npz",**ex)
    return ex


def read_power(out):
    reps=pd.read_csv(ARCHIVE/"certificate_replicates.csv")
    summary=pd.read_csv(ARCHIVE/"certificate_summary.csv")
    keys=["model","max_delay","N"]
    counts=reps.groupby(keys).rejects.agg(n="size",rejections="sum").reset_index()
    check=counts.merge(summary,on=keys,validate="one_to_one",suffixes=("","_archive"))
    assert len(reps)==7680 and len(check)==len(counts)==len(summary)==60
    assert check.n.eq(128).all() and check.n.eq(check.n_archive).all()
    assert check.rejections.eq(check.rejections_archive).all()
    assert np.allclose(check.rejection_rate,check.rejections/check.n)
    assert not reps.duplicated(keys+["rep"]).any()
    assert reps.groupby(["model","max_delay","rep"]).N.nunique().eq(4).all()
    n_long=len(reps[["model","max_delay","rep"]].drop_duplicates())
    null=reps[reps.model.str.startswith("null")]
    assert n_long==1920 and len(null)==3072 and not null.rejects.any()
    assert len(null[["model","max_delay","rep"]].drop_duplicates())==768
    assert reps.envelope_covers.all() and reps.certificate_below_known_analytic_bound.all()
    assert len(counts[counts.model.str.startswith("alternative")])==36
    counts["positive_fraction"]=counts.rejections/counts.n
    counts.to_csv(out/"data/Fig6b_cell_counts.csv",index=False)
    shutil.copyfile(ARCHIVE/"certificate_replicates.csv",out/"data/Fig6b_replicates.csv")
    return counts


def read_rates(out):
    reps=pd.read_csv(ARCHIVE/"continuous_rate_replicates.csv")
    archived=pd.read_csv(ARCHIVE/"continuous_rate_summary.csv")
    assert len(reps)==384 and len(archived)==6
    assert reps.groupby(["max_delay","rep"]).N.nunique().eq(3).all()
    assert len(reps[["max_delay","rep"]].drop_duplicates())==128
    assert reps.groupby(["max_delay","N"]).rep.nunique().eq(64).all()
    assert not reps.duplicated(["max_delay","N","rep"]).any()
    assert (reps.rate_lower>=0).all() and reps.below_population_triangle_integral.all()
    assert (reps.dense_grid_max_error<=reps.uniform_radius).all()
    population=reps.population_triangle_integral.iloc[0]
    assert np.allclose(reps.population_triangle_integral,population,rtol=1e-13)
    rows=[]
    for (delay,n),g in reps.groupby(["max_delay","N"]):
        q10,med,q90=np.quantile(g.rate_lower,[.10,.50,.90])
        prior=archived[(archived.max_delay==delay)&(archived.N==n)].iloc[0]
        positive=int((g.rate_lower>0).sum())
        assert len(g)==64 and positive==prior.positive
        assert np.isclose(med,prior.median_rate_lower,atol=1e-15)
        rows.append(dict(max_delay=delay,N=n,n=64,positive=positive,q10=q10,median=med,q90=q90,
                         population_triangle_integral=population))
    stats=pd.DataFrame(rows)
    rng=np.random.default_rng(JITTER_SEED)
    jitter=rng.uniform(-.104,.104,(2,64))
    group=reps.max_delay.map({0:0,8:1}).to_numpy()
    reps["prefix_paired_jitter"]=jitter[group,reps.rep.to_numpy()]
    reps.to_csv(out/"data/Fig6c_replicates.csv",index=False)
    stats.to_csv(out/"data/Fig6c_quantiles.csv",index=False)
    return reps,stats,population


def panel(key,title=None):
    _,_,w,h=LAYOUT[key]
    f=plt.figure(figsize=(w/25.4,h/25.4),facecolor="white")
    if title:
        f.text(.014,.969,key,fontsize=12,fontweight="bold",va="top",color=INK)
        f.text(.079,.966,title,fontsize=10.4,fontweight="bold",va="top",color=INK)
    return f


def save(f,out,name):
    path=out/"panels"/name
    f.savefig(path.with_suffix(".svg"),metadata={"Date":None})
    f.savefig(path.with_suffix(".pdf"),metadata={"CreationDate":None,"ModDate":None})
    plt.close(f)


def polish(ax,small=False):
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(length=2.3,width=.55,pad=1.3,labelsize=7.9 if small else 8.4)
    ax.set_axisbelow(True)


def compact(x,_):
    return f"{x:g}"


def plot_pipeline(ex,out):
    f=panel("a-data")
    f.patch.set_visible(False)
    left,top,width,height=LAYOUT["a-data"]
    plot_top,plot_bottom,plot_width=15.25,29.15,25.5
    axs=[f.add_axes(((x-left)/width,(top+height-plot_bottom)/height,
                    plot_width/width,(plot_bottom-plot_top)/height))
         for x in (8.75,42.75,76.75,110.75,144.75)]
    for ax in axs:
        ax.patch.set_visible(False)
        polish(ax,small=True)
        ax.yaxis.set_major_formatter(FuncFormatter(compact))

    record=ex["record_excerpt"]
    axs[0].spines["left"].set_visible(False)
    for i,color in enumerate((BLUE,GRAY,PURPLE)):
        level=(2-i)*5.6
        axs[0].axhline(level,color="#DCE3E7",lw=.5)
        axs[0].plot(np.arange(len(record)),record[:,i]+level,color=color,lw=.80)
        axs[0].text(-2.8,level,r"$y_"+str(i+1)+"$",ha="right",va="center",fontsize=8.1,color=color)
    axs[0].set(xlim=(-1,48),xticks=[0,24,47],yticks=[])
    axs[0].set_xlabel(r"$t$ (samples)",labelpad=.85)

    lag=ex["lag_covariances"]
    m=np.max(abs(lag),axis=(1,2))
    keep=np.arange(len(lag))<=ex["L"]
    for selection,col in ((keep,BLUE),(~keep,"#A5B1B8")):
        ids=np.flatnonzero(selection)
        axs[1].vlines(ids,0,m[selection],color=col,lw=.86)
        axs[1].plot(ids,m[selection],ls="none",marker="o",ms=3.0,mfc=col,mec=col)
    axs[1].axvline(1,color=GRAY,ls=(0,(2,2)),lw=.56,zorder=0)
    axs[1].set(xlim=(-.3,5.35),ylim=(-.05,1.13),xticks=[0,1,5],yticks=[0,1])
    axs[1].text(.25,.83,r"$L=1$",transform=axs[1].transAxes,fontsize=8.0,color=GRAY)
    axs[1].set_xlabel(r"Lag $\ell$",labelpad=.85)

    w=ex["omega_rad_sample"]/np.pi
    half=w<1
    x=w[half]
    y=ex["estimated_spectrum"][half,0,1].imag
    radius=ex["uniform_radius"]
    axs[2].fill_between(x,y-radius,y+radius,color="#CDE9E0",lw=0)
    axs[2].plot(x,y,color=BLUE,lw=.90)
    axs[2].plot(x,ex["true_spectrum"][half,0,1].imag,color=GRAY,lw=.80,ls=(0,(3,2)))
    axs[2].set(xlim=(0,1),ylim=(-.06,.63),xticks=[0,.5,1],yticks=[0,.5])

    p=abs(ex["raw_cycle"][half])
    error=ex["cycle_error"][half]
    axs[3].fill_between(x,error,p,where=p>error,color="#C7E8DB",lw=0)
    axs[3].plot(x,p,color=ORANGE,lw=1.04)
    axs[3].plot(x,error,color=GRAY,lw=.77,ls=(0,(3,2)))
    axs[3].set(xlim=(0,1),ylim=(-.005,.176),xticks=[0,.5,1],yticks=[0,.15])

    axs[4].stairs(ex["certified_density"],ex["cell_edges_rad_sample"]/np.pi,baseline=0,
                  fill=True,facecolor="#C7E8DB",edgecolor=TEAL,lw=.84)
    axs[4].plot(w,ex["population_triangle_density"],color=GRAY,lw=.72,ls=(0,(3,2)))
    axs[4].set(xlim=(0,2),ylim=(-.002,.057),xticks=[0,1,2],yticks=[0,.05])
    for ax in axs[2:]:
        ax.xaxis.set_major_formatter(FuncFormatter(compact))
        ax.set_xlabel(r"$\omega/\pi$",labelpad=.85)
    save(f,out,"Fig6a_data")


def plot_power(counts,out):
    f=panel("b","Fixed-grid detection power")
    cmap=LinearSegmentedColormap.from_list("certificate_fraction",["#F1F6F3","#BFE2D2","#52AD90","#007659"])
    norm=Normalize(0,1)
    for k,b in enumerate(STRENGTHS):
        x=.150+k*.271
        ax=f.add_axes((x,.362,.252,.416))
        group=counts[counts.model==f"alternative_{b:g}"].pivot(index="max_delay",columns="N",values="positive_fraction")
        assert tuple(group.index)==(0,2,8) and tuple(group.columns)==NGRID
        for i,j in np.ndindex(3,4):
            value=group.iat[i,j]
            ax.add_patch(Rectangle((j-.5,i-.5),1,1,fc=cmap(norm(value)),ec="white",lw=.66))
            if k==2 and (i,j) in ((0,2),(2,2),(2,3)):
                ax.text(j,i,f"{value:g}",ha="center",va="center",
                        fontsize=8.0,color="white" if value>.58 else GRAY)
        ax.set(xlim=(-.5,3.5),ylim=(2.5,-.5),xticks=range(4),
               xticklabels=[r"$2^{11}$",r"$2^{13}$",r"$2^{15}$",r"$2^{17}$"],
               yticks=range(3),yticklabels=["0","2","8"] if k==0 else ["","",""])
        ax.set_title(rf"$b={b:g}$",fontsize=9.0,pad=4)
        ax.tick_params(length=0,pad=3,labelsize=7.95)
        if k==0:
            ax.set_ylabel("Max. delay (samples)",labelpad=2.8)
        for spine in ax.spines.values():
            spine.set_color("#ADB9B3")
            spine.set_linewidth(.55)
    f.text(.550,.260,r"Record length $N$ (samples)",ha="center",fontsize=8.65)
    bar=f.add_axes((.315,.161,.466,.033))
    for i in range(100):
        bar.add_patch(Rectangle((i/100,0),.0104,1,fc=cmap((i+.5)/100),ec="none"))
    bar.set(xlim=(0,1),ylim=(0,1),xticks=[0,.5,1],yticks=[])
    bar.xaxis.set_major_formatter(FuncFormatter(compact))
    bar.tick_params(length=2.4,width=.56,labelsize=8.1,pad=1.45)
    f.text(.548,.208,"Positive certificate fraction",ha="center",fontsize=8.2,color=GRAY)
    save(f,out,"Fig6b")


def plot_rates(reps,stats,population,out):
    f=panel("c","Continuous-frequency rate")
    ax=f.add_axes((.190,.201,.769,.625))
    polish(ax)
    ax.set_yscale("symlog",linthresh=.08,linscale=.55)
    ax.set(xlim=(-.39,2.39),ylim=(-.046,39),xticks=range(3),
           xticklabels=[r"$2^{15}$",r"$2^{17}$",r"$2^{19}$"],yticks=[0,.1,1,10,30])
    ax.yaxis.set_major_formatter(FuncFormatter(compact))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlabel(r"Record length $N$ (samples)",labelpad=2.0)
    ax.set_ylabel(r"Rate bound ($10^{-3}$ nats/sample)",labelpad=3.1)
    ax.axhline(0,color="#C5CFD4",lw=.55,zorder=0)
    reference=population*1e3
    ax.axhline(reference,color=GRAY,lw=.83,ls=(0,(4,2)),zorder=0)
    ax.text(.012,reference*1.095,"Population triangle integral",ha="left",va="bottom",
            transform=ax.get_yaxis_transform(),color=GRAY,fontsize=8.0)
    markers=("o","s")
    colors=("#347D65","#936483")
    fills=("#C7E4D7","#EDDEEA")
    for i,delay in enumerate((0,8)):
        for j,n in enumerate(RATE_N):
            group=reps[(reps.max_delay==delay)&(reps.N==n)]
            row=stats[(stats.max_delay==delay)&(stats.N==n)].iloc[0]
            x=j+(-.144 if i==0 else .144)
            ax.plot(x+group.prefix_paired_jitter,group.rate_lower*1e3,ls="none",marker=markers[i],
                    mfc=fills[i],mec=colors[i],mew=.54,ms=3.0,zorder=2)
            lo,med,hi=np.array([row.q10,row["median"],row.q90])*1e3
            ax.errorbar(x,med,yerr=[[med-lo],[hi-med]],color=INK,marker="_",
                        ms=7.3,mew=1.05,elinewidth=.86,capsize=2,zorder=4)
    handles=[Line2D([],[],ls="none",marker=marker,mfc=fill,mec=color,mew=.75,ms=4.1,
                    label=f"{delay} samples")
             for marker,fill,color,delay in zip(markers,fills,colors,(0,8),strict=True)]
    f.legend(handles=handles,loc="upper right",bbox_to_anchor=(.971,.901),frameon=False,
             fontsize=8.25,ncol=2,columnspacing=.9,handlelength=1.2,handletextpad=.38,borderaxespad=0)
    save(f,out,"Fig6c")


def build(out,grid):
    (out/"data").mkdir(parents=True,exist_ok=True)
    (out/"panels").mkdir(exist_ok=True)
    grid.mkdir(parents=True,exist_ok=True)
    counts=read_power(out)
    rates,stats,population=read_rates(out)
    ex=replay(grid,rates)
    plot_pipeline(ex,out)
    plot_power(counts,out)
    plot_rates(rates,stats,population,out)
    summary=dict(power_analyses=7680,power_independent_long_trajectories=1920,
                 null_analyses=3072,null_independent_long_trajectories=768,null_positive=0,
                 rate_analyses=384,rate_independent_long_trajectories=128,
                 rate_replicates_per_cell=64,rate_quantiles=[.10,.50,.90],jitter_seed=JITTER_SEED,
                 population_triangle_integral=float(population),replay_seed=REPLAY_SEED,
                 replay_N=ex["N"],replay_L=ex["L"],replay_B=ex["B"],replay_T_L=ex["T_L"],
                 replay_alpha=ex["alpha"],replay_integral_cells=ex["integral_cells"],
                 replay_uniform_radius=float(ex["uniform_radius"]),replay_cell_variation=float(ex["cell_variation"]),
                 replay_rate=float(ex["certified_rate"]))
    (out/"data/Fig6_checks.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument("--grid-output",type=Path,default=DEFAULT_GRID)
    args=parser.parse_args()
    if args.output.anchor or args.grid_output.anchor:
        parser.error("Use paths relative to the handoff root.")
    build(args.output,args.grid_output)
