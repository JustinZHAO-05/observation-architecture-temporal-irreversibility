"""Build Fig. 5 from the archived reversible counterexample and exact windows."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
import numpy as np

sys.dont_write_bytecode=True
ROUND1=Path("01_RESEARCH/ROUND1/neural_time_arrow_study")
DEFAULT_OUTPUT=Path("03_FIGURE_PRODUCTION/redraw/Fig5")
DEFAULT_GRID=Path("03_FIGURE_PRODUCTION/generated_data/Fig5/redraw")
LAYOUT={"a-native":(2,2,104,54),"a-input":(2,11,39,45),"a-output":(72,11,34,45),
        "b":(109,2,67,54),"c":(2,60,78,71),"d":(83,60,93,71)}
INK,GRAY,BLUE,ORANGE,PURPLE="#181B20","#555D69","#0072B2","#D55E00","#8E5385"
EDGE_COLORS=(BLUE,PURPLE,GRAY)
FS,T,DELAY=160,2,.125
I,J=np.array([(0,1),(1,2),(2,0)]).T
NFFT=16384

plt.rcParams.update({
    "font.family":"Arial","font.size":8.4,"axes.labelsize":8.7,"axes.linewidth":.62,
    "mathtext.fontset":"custom","mathtext.rm":"Cambria","mathtext.it":"Cambria:italic",
    "svg.fonttype":"none","svg.hashsalt":"pre-fig5-bandwidth","pdf.fonttype":42,
})


def load_audit():
    spec=importlib.util.spec_from_file_location("window_audit",ROUND1/"src/math_review_independent.py")
    audit=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    return audit


def components(f):
    pole=np.exp(-2*np.pi*.15/FS)
    phase=2*np.pi*(f[:,None,None]+np.array([[-9.75,9.75],[-10.25,10.25]]))/FS
    return ((1-pole*pole)/(1-2*pole*np.cos(phase)+pole*pole)).mean(axis=-1)*np.array([1,.4])


def exact_inputs(f):
    p1,p2=components(f).T
    signed=p1[:,None]+p2[:,None]*np.array([1,-1,-1])
    power=p1+p2+.2
    phase=2*np.pi*f[:,None]*np.array([DELAY,-DELAY,0])
    return power,signed*np.exp(1j*phase)


def taper_coefficients(centers):
    time=np.arange(T*FS)
    window=np.sin(np.pi*time/len(time))**2
    design=np.column_stack((np.ones(len(time)),time-time.mean()))
    weights=window*np.exp(-2j*np.pi*centers[:,None]*time/FS)
    weights-=(weights@design)@np.linalg.solve(design.T@design,design.T)
    return weights,float(window@window)


def frequency_calculation(audit,grid):
    freq=np.linspace(8.5,11.5,601)
    power,edge=exact_inputs(freq)
    c=edge/power[:,None]
    assert np.max(abs(np.prod(c,axis=1).imag))<1e-14

    center=np.linspace(8.5,11.5,61)
    weights,window_energy=taper_coefficients(center)
    quadrature=np.fft.fftfreq(NFFT,1/FS)
    psd,cross=exact_inputs(quadrature)
    response=np.fft.ifft(weights,n=NFFT,axis=1)*NFFT
    kernel=abs(response)**2/(window_energy*NFFT)
    denominator=kernel@psd
    coherent=kernel@cross/denominator[:,None]
    first=kernel@(np.prod(cross/psd[:,None],axis=1)*psd)/denominator
    last=np.prod(coherent,axis=1)

    bins,s,archived=audit.expected_spectrum(T,delay_seconds=DELAY,fs=FS)
    keep=(bins>=center[0])&(bins<=center[-1])
    display_bins=bins[keep]
    matches=np.searchsorted(center,display_bins)
    assert np.array_equal(center[matches],display_bins)
    expected=s[keep]
    errors=abs(last[matches].imag-archived[keep,0])
    assert np.max(errors)<2e-11 and np.max(abs(first.imag))<1e-14
    assert np.allclose(denominator[matches,None],np.diagonal(expected,axis1=1,axis2=2).real,rtol=1e-10)
    assert np.allclose((kernel@cross)[matches],expected[:,I,J],rtol=1e-10,atol=1e-10)
    at10=float(last[center==10].imag[0])

    at_center,_=taper_coefficients(np.array([10.]))
    local_response=abs(np.exp(2j*np.pi*freq[:,None]*np.arange(T*FS)/FS)@at_center[0])**2
    kernel_display=local_response/local_response.max()
    phase_increment=2*np.pi*(freq[:,None]-10)*np.array([DELAY,-DELAY,0.])
    peak=components(freq)
    np.savez_compressed(grid/"Fig5a_window_order.npz",frequency_hz=freq,exact_coherency=c,
                        evaluation_hz=center,product_then_average=first,average_then_product=last,
                        windowed_coherency=coherent,archived_bins_hz=display_bins,
                        archived_im_cycle=archived[keep,0],power_denominator=denominator,
                        quadrature_points=NFFT,window_s=T,sampling_hz=FS)
    np.savez_compressed(grid/"Fig5b_peaks_and_kernel.npz",frequency_hz=freq,source_power=peak,
                        peak_relative_kernel=kernel_display,delay_phase_rad=phase_increment,
                        source_centers_hz=[9.75,10.25],reference_frequency_hz=10.,delay_s=DELAY)
    return dict(freq=freq,c=c,center=center,first=first,last=last,bins=display_bins,
                bin_cycle=archived[keep,0],kernel=kernel_display,phase=phase_increment,
                peak=peak,at10=at10,max_error=float(np.max(errors)))


def frozen_scaling(out):
    archive=json.loads((ROUND1/"reviews/math_review_v2_leakage_partial.json").read_text())
    rows=sorted((r for r in archive if r["delay_s"]==DELAY),key=lambda r:r["T_s"])
    assert len(archive)==18 and [r["T_s"] for r in rows]==[1,2,4,8,16,32]
    with (out/"data/Fig5c_exact_windows.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def frozen_scores(audit,out,replay):
    path=ROUND1/"reviews"
    score=np.load(path/"adversarial_M0_60s_scores.npy",allow_pickle=False)
    summary=json.loads((path/"math_review_exact_outputs.json").read_text())["finite_record_counterexample"]
    assert score.shape==(500,) and np.isfinite(score).all()
    assert np.isclose(score.mean(),summary["mean"],rtol=1e-13)
    assert np.isclose(score[:99].mean(),summary["first99_mean"],rtol=1e-13)
    assert np.mean(score>0)==summary["proportion_positive"] and summary["first99_signflip_p"]==.00008
    replay_error=None
    if replay:
        with TemporaryDirectory(prefix="fig5_replay_") as temp:
            audit.OUT=Path(temp)
            result=audit.finite_record_counterexample()
            replayed=np.load(Path(temp)/summary["score_file"],allow_pickle=False)
            replay_error=float(np.max(abs(score-replayed)))
        assert replay_error<1e-16
        assert result["first99_signflip_p"]==summary["first99_signflip_p"]
    selected=np.argsort(score,kind="stable")[np.round(np.linspace(0,len(score)-1,42)).astype(int)]
    with (out/"data/Fig5d_records.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(["record","Q","first_99","rug_point"])
        writer.writerows((i+1,q,i<99,i in selected) for i,q in enumerate(score))
    (out/"data/Fig5d_frozen_test.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return score,summary,selected,replay_error


def panel(key,title=None):
    _,_,w,h=LAYOUT[key]
    f=plt.figure(figsize=(w/25.4,h/25.4),facecolor="white")
    if title:
        f.text(.013,.973,key,fontsize=12,fontweight="bold",va="top",color=INK)
        f.text(.075,.969,title,fontsize=10.4,fontweight="bold",va="top",color=INK)
    return f


def save(f,out,name):
    path=out/"panels"/name
    f.savefig(path.with_suffix(".svg"),metadata={"Date":None})
    f.savefig(path.with_suffix(".pdf"),metadata={"CreationDate":None,"ModDate":None})
    plt.close(f)


def polish(ax):
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(length=2.35,width=.56,pad=1.6)
    ax.set_axisbelow(True)


def frequency_axis(ax):
    ax.set(xlim=(8.5,11.5),xticks=[9,10,11])
    ax.axvline(10,color="#ACB7BF",ls=(0,(2,2)),lw=.56,zorder=0)


def plot_inputs(data,out):
    f=panel("a-input")
    for x,text in [( .352,r"$|C_e|$"),(.727,r"$\arg C_e$ (rad)")]:
        f.text(x,.956,text,ha="center",va="top",color=INK,fontsize=8.6)
    for k,(edge,color) in enumerate(zip(("12","23","31"),EDGE_COLORS,strict=True)):
        y=.702-.252*k
        left=f.add_axes((.221,y,.260,.182))
        right=f.add_axes((.591,y,.272,.182))
        f.text(.054,y+.091,r"$C_{"+edge+"}$",va="center",color=color,fontsize=8.5)
        for ax in (left,right):
            polish(ax)
            frequency_axis(ax)
            ax.set_xticks([9,11])
            ax.tick_params(labelsize=7.9)
            if k!=2:
                ax.tick_params(labelbottom=False)
        c=data["c"][:,k]
        left.plot(data["freq"],abs(c),color=color,lw=1.1)
        left.set(ylim=(0,1.03),yticks=[0,1])
        phase=np.angle(c)
        phase[1:][abs(np.diff(phase))>np.pi/2]=np.nan
        right.plot(data["freq"],phase,color=color,lw=1.06)
        right.axhline(0,color="#D4DCE1",lw=.54,zorder=0)
        right.set(ylim=(-3.25,3.25),yticks=[-np.pi,0,np.pi],
                  yticklabels=[r"$-\pi$",r"$0$",r"$\pi$"])
        right.yaxis.tick_right()
        right.spines["left"].set_visible(False)
        right.spines["right"].set_visible(True)
    f.text(.53,.035,"Frequency (Hz)",ha="center",va="bottom",fontsize=8.45)
    save(f,out,"Fig5a_input")


def plot_outputs(data,out):
    f=panel("a-output")
    axes=[f.add_axes((.285,y,.660,.223)) for y in (.620,.221)]
    f.text(.042,.532,r"$\mathrm{Im}\,P$",ha="center",va="center",rotation=90,fontsize=8.4)
    for ax in axes:
        polish(ax)
        frequency_axis(ax)
        ax.set(ylim=(-.021,.052),yticks=[-.02,0,.04],
               yticklabels=[r"$-0.02$","0","0.04"])
        ax.tick_params(labelsize=8)
        ax.axhline(0,color="#BBC6CC",lw=.55,zorder=0)
    axes[0].plot(data["center"],data["first"].imag,color=GRAY,lw=1.16)
    axes[0].tick_params(labelbottom=False)
    axes[1].plot(data["center"],data["last"].imag,color=ORANGE,lw=1.28)
    axes[1].plot(data["bins"],data["bin_cycle"],ls="none",marker="o",ms=3.15,
                 mfc="white",mec=ORANGE,mew=.72)
    f.text(.606,.035,"Frequency (Hz)",ha="center",va="bottom",fontsize=8.45)
    save(f,out,"Fig5a_output")


def plot_b(data,out):
    f=panel("b","Slopes within the window")
    top=f.add_axes((.157,.469,.804,.322))
    low=f.add_axes((.157,.163,.804,.208),sharex=top)
    freq=data["freq"]
    for ax in (top,low):
        polish(ax)
        frequency_axis(ax)
    top.tick_params(labelbottom=False)
    top.set_ylabel("Relative height",labelpad=2)
    top.set(ylim=(-.015,1.12),yticks=[0,.5,1])
    top.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:g}"))
    scale=data["peak"][:,0].max()
    top.fill_between(freq,data["kernel"],color="#E9EDF0",lw=0)
    for k,(col,f0) in enumerate(zip((BLUE,PURPLE),(9.75,10.25),strict=True)):
        top.plot(freq,data["peak"][:,k]/scale,color=col,lw=1.31,label=f"{f0:g} Hz")
        top.axvline(f0,color="#B6C3CB",ls=(0,(2,2)),lw=.53,zorder=1)
    top.plot(freq,data["kernel"],color=GRAY,lw=.96,ls=(0,(4,2)),label="Hann (2 s)")
    top.legend(loc="lower center",bbox_to_anchor=(.5,1.035),ncol=3,frameon=False,
               fontsize=8.1,handlelength=1.35,handletextpad=.38,columnspacing=.72,borderaxespad=0)
    for k,(col,edge) in enumerate(zip(EDGE_COLORS,("Edge 12","23","31"),strict=True)):
        low.plot(freq,data["phase"][:,k],color=col,lw=1.12,label=edge)
    low.set(ylim=(-1.23,1.23),yticks=[-1,0,1])
    low.set_ylabel(r"$\Delta d_e$ (rad)",labelpad=2)
    low.set_xlabel("Frequency (Hz)",labelpad=1.2,loc="left")
    low.legend(loc="lower right",bbox_to_anchor=(1,1.018),ncol=3,frameon=False,
               fontsize=8.0,handlelength=1.10,handletextpad=.38,columnspacing=.72,borderaxespad=0)
    f.text(.170,.399,r"$\Delta\tau=125$ ms",color=GRAY,fontsize=8.25)
    f.text(.958,.015,r"$\mathrm{Bias}\ \propto\ \mu_2\,r'_e d'_e$",ha="right",va="bottom",fontsize=8.7)
    save(f,out,"Fig5b")


def plot_c(rows,out):
    f=panel("c","Window-length scaling")
    t=np.array([r["T_s"] for r in rows])
    closure=abs(np.array([r["closure_at10Hz"] for r in rows]))
    q=np.array([r["mean_v2_12channels"] for r in rows])
    assert np.isclose(q[-2]/q[-1],15.48,rtol=.001)
    axes=[f.add_axes((.183,y,.762,.305)) for y in (.548,.137)]
    for ax in axes:
        polish(ax)
        ax.set(xscale="log",yscale="log",xlim=(.85,37))
        ax.xaxis.set_major_locator(FixedLocator(t))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:g}"))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.grid(axis="y",color="#DEE5E8",lw=.53)
    axes[0].set(ylim=(3.2e-4,.12),yticks=[1e-3,1e-2,1e-1])
    axes[0].set_ylabel(r"$|\mathrm{Im}\,P_T(10\,\mathrm{Hz})|$",labelpad=2.5)
    axes[0].tick_params(labelbottom=False)
    axes[1].set(ylim=(4e-10,8e-5),yticks=[1e-9,1e-7,1e-5])
    axes[1].set_ylabel(r"$Q_{\mathrm{bias}}$",labelpad=2.5)
    axes[1].set_xlabel(r"Window length $T$ (s)",labelpad=1.7)
    tt=np.geomspace(4,32,100)
    reference=[rows[-1]["asymptotic_T2_coefficient"]/tt**2,q[-1]*(32/tt)**4]
    for ax,value,line,power in zip(axes,(closure,q),reference,(2,4),strict=True):
        ax.plot(tt,line,color=GRAY,lw=1.0,ls=(0,(3.5,2.5)),zorder=1)
        ax.plot(t,value,ls="none",marker="o",ms=3.7,mfc="white",mec=ORANGE,mew=1.04,zorder=2)
        ax.text(.815,.83,rf"$T^{{-{power}}}$",transform=ax.transAxes,color=GRAY,fontsize=9)
    save(f,out,"Fig5c")


def plot_d(scores,summary,selected,out):
    f=panel("d","Reversible latent counterexample")
    ax=f.add_axes((.133,.184,.822,.585))
    polish(ax)
    scaled=scores*1e5
    bins=np.arange(-5,8.5,.5)
    heights,_,_=ax.hist(scaled,bins=bins,density=True,color="#D6DCE0",edgecolor="white",linewidth=.65)
    assert scaled.min()>=bins[0] and scaled.max()<=bins[-1]
    ax.axvline(0,color=GRAY,ls=(0,(3,2)),lw=.85,zorder=2)
    ax.axvline(summary["mean"]*1e5,ymax=.88,color=ORANGE,lw=1.42,zorder=3,label="Mean of 500")
    rug_y=-.011-.0044*(np.arange(len(selected))%3)
    ax.plot(scaled[selected],rug_y,ls="none",marker="o",ms=2.85,mfc=GRAY,mec="white",mew=.31,zorder=3)
    ymax=heights.max()
    ax.set(xlim=(-5.2,8.2),ylim=(-.027,ymax*1.22),xticks=[-4,0,4,8])
    first99=(summary["first99_mean"]*1e5,ymax*1.105)
    ax.plot(*first99,marker="D",ms=3.45,mfc=GRAY,mec="white",mew=.45,zorder=4)
    ax.annotate("",xy=first99,xytext=(.69,1.055),textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-",color="#87939B",lw=.6,shrinkA=0,shrinkB=3.1))
    ax.set_xlabel(r"Cross-half score $Q$ ($10^{-5}$)",labelpad=2)
    ax.set_ylabel("Density",labelpad=2)
    ax.legend(loc="upper left",frameon=False,fontsize=8.35,handlelength=1.55,
              borderaxespad=.25,handletextpad=.4)
    f.text(.954,.877,"Nominal sign-flip test",ha="right",fontsize=8.35,color=INK)
    f.text(.954,.824,rf"First 99   $p={summary['first99_signflip_p']:.5f}$",ha="right",
           fontsize=8.6,color=INK)
    save(f,out,"Fig5d")


def build(out,grid,replay):
    (out/"data").mkdir(parents=True,exist_ok=True)
    (out/"panels").mkdir(exist_ok=True)
    grid.mkdir(parents=True,exist_ok=True)
    audit=load_audit()
    data=frequency_calculation(audit,grid)
    scaling=frozen_scaling(out)
    scores,summary,selected,replay_error=frozen_scores(audit,out,replay)
    assert np.isclose(data["at10"],scaling[1]["closure_at10Hz"],rtol=1e-10)
    plot_inputs(data,out)
    plot_outputs(data,out)
    plot_b(data,out)
    plot_c(scaling,out)
    plot_d(scores,summary,selected,out)
    result=dict(delay_s=DELAY,window_s=T,sampling_hz=FS,window_quadrature_points=NFFT,
                maximum_error_vs_exact_lag_sum=data["max_error"],cycle_at10_hz=data["at10"],
                exact_window_lengths_s=[r["T_s"] for r in scaling],
                ratio_Qbias_16_over_32=scaling[-2]["mean_v2_12channels"]/scaling[-1]["mean_v2_12channels"],
                replay_seed=732419,replay_max_abs_score_error=replay_error,rug_points=len(selected),
                frozen_counterexample=summary)
    (out/"data/Fig5_checks.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument("--grid-output",type=Path,default=DEFAULT_GRID)
    parser.add_argument("--replay",action="store_true",help="rerun the frozen 500-record simulation")
    args=parser.parse_args()
    if args.output.anchor or args.grid_output.anchor:
        parser.error("Use paths relative to the handoff root.")
    build(args.output,args.grid_output,args.replay)
