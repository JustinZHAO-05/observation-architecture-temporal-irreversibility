"""Fixed-gain trace optimization and the finite-window counterexample."""
import json

import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm

from common import A, B, EC, GRAY, GREEN, INK, LATENT, TARGET, TWO, Build, arrow, tag
from common import import_file


def power_min(b, theta):
    return (1-abs(np.cos(theta))*np.sqrt(1-b*b))/np.sin(theta)**2


def power_data(f):
    curves = f.archive_csv(2,"latency_power_curves.csv")
    lp = f.archive_csv(2,"latency_cost_lp_intervals.csv")
    assert len(curves)==400 and len(lp)==32
    assert np.allclose(curves.minimum_power_ratio,power_min(curves.b,curves.theta))
    assert np.allclose(lp.analytic_ratio,power_min(lp.b,lp.theta))
    assert (lp.lower_ratio <= lp.analytic_ratio+1e-10).all()
    assert (lp.upper_ratio >= lp.analytic_ratio-1e-10).all()
    assert np.isclose(power_min(.8,.05),160.4336,rtol=1e-6)
    assert np.isclose(lp.relative_interval_width.max(),2.31e-6,rtol=.003)
    return curves,lp


def draw_lp(ax,lp,relative=False):
    for i,(b,g) in enumerate(lp.groupby("b")):
        lo, hi, exact = g.lower_ratio,g.upper_ratio,g.analytic_ratio
        y = (lo+hi)/2
        err = (hi-lo)/2
        if relative:
            y,err = 1e6*(y/exact-1),1e6*err/exact
        ax.errorbar(exact,y,yerr=err,ls="none",marker=["o","s","^","D"][i],
                    mfc="white",mec=B,ecolor=B,ms=4,lw=.8,label=f"{b:g}")
    ax.set(xscale="log",xlabel=r"Analytic minimum $t_{\min}$")
    if relative:
        ax.axhline(0,color=GRAY,ls="--",lw=.9)
        ax.set_ylabel("LP deviation (ppm)")
    else:
        x=np.geomspace(lp.analytic_ratio.min()*.86,lp.analytic_ratio.max()*1.25,100)
        ax.plot(x,x,color=GRAY,ls="--",lw=.9,zorder=0)
        ax.set(yscale="log",ylabel="LP bracket midpoint",xlim=(x[0],x[-1]),ylim=(x[0],x[-1]))


def fig3(root,out):
    f=Build(root,out,"Fig3",12.4,
            [(0,.53,.43,.47),(.46,.53,.54,.47),(0,0,.56,.47),(.60,0,.40,.47)],
            ["Fixed imaginary projection","The cost of a short delay",
             "Minimum trace ratio","Full-matrix LP audit"])
    a,b,c,d=f.panels
    angles=np.array([.31,.85])
    signal=.55
    lengths=signal/np.sin(angles)
    f.csv("A",dict(theta_rad=angles,imaginary_target_b=signal,
                   two_j=lengths,real_projection=lengths*np.cos(angles)))
    ax=a.ax(.11,.15,.85,.64)
    ax.axhline(0,color=GRAY,lw=.7)
    ax.axhline(signal,color=GRAY,ls="--",lw=.8)
    for i,(theta,r,col) in enumerate(zip(angles,lengths,[B,LATENT])):
        x=r*np.cos(theta)
        arrow(ax,(0,0),(x,signal),col,lw=1.6)
        t=np.linspace(0,theta,42)
        ax.plot((.53-.28*i)*np.cos(t),(.53-.28*i)*np.sin(t),color=col,lw=.9)
        tag(ax,x*.73,signal*.73+.086,rf"$2j_{i+1}$",color=col)
        tag(ax,.63-.36*i,.07+.035*i,rf"$\theta_{i+1}$",color=col)
    ax.text(1.8,signal+.012,r"$b$",color=TARGET,ha="right",va="bottom")
    ax.set(xlim=(-.05,1.93),ylim=(-.10,.73),xticks=[],yticks=[],aspect="equal")
    ax.set_axis_off()
    ax.text(.02,.95,r"$2j\sin\theta=b$",transform=ax.transAxes,color=TARGET)
    ax.text(.02,-.01,"Unit observation gains",transform=ax.transAxes,color=LATENT)

    curves,lp=power_data(f)
    # The archive has b=.95. The main-figure contract calls for .9.
    grid=curves[curves.b==.95].theta.to_numpy()
    generated=pd.DataFrame(dict(b=.9,theta=grid,minimum_power_ratio=power_min(.9,grid),
                                small_delay_coefficient=1-np.sqrt(1-.9**2),source="Theorem 2"))
    curves=pd.concat([curves[curves.b!=.95].assign(source="archive"),generated],ignore_index=True)
    curves["theta2_trace"]=curves.theta**2*curves.minimum_power_ratio
    f.csv("B",curves)
    ax=b.ax(.16,.17,.80,.64)
    inset=b.ax(.56,.55,.34,.21)
    colors=["#9f5837","#b66541","#a14629","#632b1e"]
    for i,((strength,g),col) in enumerate(zip(curves.groupby("b"),colors)):
        ax.loglog(g.theta,g.minimum_power_ratio,color=col,ls=["-","--","-.",":"][i],
                  label=f"{strength:g}")
        early=g[g.theta<=.20]
        inset.semilogx(early.theta,early.theta2_trace,color=col,lw=1.0)
        inset.axhline(g.small_delay_coefficient.iloc[0],color=col,ls=":",lw=.7)
    ax.axvspan(.01,.05,color=B,alpha=.08)
    ax.set(xlabel=r"Phase delay $|\theta|$ (rad)",ylabel=r"Trace ratio $t_{\min}$")
    ax.legend(title=r"$b$",loc="lower left",frameon=False,ncol=2,borderpad=.2)
    inset.set(xlim=(.01,.2),xticks=[.01,.1],xticklabels=[".01",".1"],yticks=[0,.5])
    inset.set_title(r"$\theta^2 t_{\min}$",size=7,pad=2)
    inset.tick_params(length=2,labelsize=6.5,pad=1)

    theta=np.geomspace(.01,np.pi/2,129)
    strength=np.linspace(.02,.98,101)
    z=power_min(strength[:,None],theta[None,:])
    f.npz("C",theta_rad=theta,b=strength,minimum_trace_ratio=z)
    ax=c.ax(.14,.19,.70,.64)
    color=ax.pcolormesh(theta,strength,z,norm=LogNorm(vmin=.5,vmax=1e4),
                       cmap="YlOrBr",shading="nearest",edgecolors="face",linewidth=.20,antialiased=False)
    contours=ax.contour(theta,strength,z,levels=[1,10,100,1000],colors=INK,linewidths=.65)
    ax.clabel(contours,fmt="%g",fontsize=7)
    ax.scatter([.05],[.8],s=24,marker="D",edgecolor=INK,facecolor="white",zorder=6)
    ax.set(xscale="log",xlabel=r"Phase delay $|\theta|$ (rad)",ylabel=r"Target strength $b$")
    cax=c.ax(.865,.20,.034,.62)
    f.figure.colorbar(color,cax=cax,ticks=[1,10,100,1000,10000]).solids.set_label("colorbar-solids")

    f.csv("D",lp)
    ax=d.ax(.21,.19,.75,.64)
    draw_lp(ax,lp)
    ax.text(.04,.96,r"32 settings",transform=ax.transAxes,va="top",color=LATENT)
    inset=d.ax(.65,.27,.27,.19)
    inset.scatter(lp.analytic_ratio,lp.relative_interval_width*1e6,s=8,color=B)
    inset.set(xscale="log",xticks=[1,10],xticklabels=["1","10"],yticks=[0,2])
    inset.set_title("Bracket width (ppm)",size=7,pad=1)
    inset.tick_params(labelsize=6.5,length=2,pad=1)
    f.finish(r"""
**Figure 3. Fixed gains impose a spectral-trace cost on short differential delays.**
(a) The rotational covariance block must supply an imaginary projection
\(2j\sin\theta=b\). A shorter angle requires a larger magnitude of the off-diagonal
component at the same \(b\). The phasors visualize the constraint of Theorem 2.
(b) The analytic minimum for \(b=0.2,0.5,0.8,0.9\). The inset shows
\(\theta^2t_{\min}\) approaching \(1-\sqrt{1-b^2}\) (dotted lines).
(c) Theorem 2 evaluated on a deterministic grid. The marker at \(b=0.8\),
\(\theta=0.05\) rad gives 160.4336. Color encodes the dimensionless
latent-to-observed spectral trace ratio under unit gains.
(d) All 32 full-matrix PSD cutting-plane LP brackets against the analytic minimum.
The largest relative width is \(2.31\times10^{-6}\). The symbol encodes \(b\) in
ascending order (circle, square, triangle, diamond).
""")


def leakage_inputs(f):
    path=f.r1/"src"
    audit=import_file(path/"math_review_independent.py","r1_math_review")
    dur, fs, delay = 2,160,.125
    freq, avg, v = audit.expected_spectrum(dur,delay,fs=fs)
    w = np.linspace(8,12,801)
    a = np.exp(-2*np.pi*.15/fs)
    def psd(center):
        phase = 2*np.pi*(w[:,None]+np.array([-center,center]))/fs
        return ((1-a*a)/(1-2*a*np.cos(phase)+a*a)).mean(axis=1)
    p1,p2=psd(9.75),.4*psd(10.25)
    filters=np.exp(-2j*np.pi*w[:,None]*np.array([0,delay,0]))
    load=np.array([1,1,-1])
    cross=p1[:,None,None]*np.ones((3,3))+p2[:,None,None]*np.outer(load,load)
    true=cross*filters[:,:,None]*filters[:,None,:].conj()+.2*np.eye(3)
    power=np.diagonal(true,axis1=1,axis2=2).real
    coh=true/np.sqrt(power[:,:,None]*power[:,None,:])
    exact=(coh[:,0,1]*coh[:,1,2]*coh[:,2,0]).imag
    assert np.max(abs(exact)) < 1e-13
    # Fourier response of the same periodic Hann and linear detrending operator.
    t=np.arange(dur*fs)
    h=np.sin(np.pi*t/t.size)**2
    design=np.column_stack([np.ones(t.size),t-t.mean()])
    coefficient=h*np.exp(-2j*np.pi*10*t/fs)
    coefficient=coefficient-(coefficient@design)@np.linalg.solve(design.T@design,design.T)
    kernel=abs(np.exp(2j*np.pi*w[:,None]*t/fs)@coefficient)**2
    kernel/=kernel.max()
    return dict(frequency_hz=w,true_spectrum=true,true_coherency=coh,true_im_cycle=exact,
                frequency_hz_tapered=freq,tapered_spectrum=avg,tapered_im_cycle=v[:,0],
                peak1_psd=p1,peak2_psd=p2,kernel_relative=kernel,window_s=dur,delay_s=delay)


def leakage_scaling(f):
    d=pd.DataFrame(json.loads((f.r1/"reviews/math_review_v2_leakage_partial.json").read_text()))
    assert len(d)==18
    s=d[d.delay_s==.125].sort_values("T_s").copy()
    assert s.T_s.tolist()==[1,2,4,8,16,32]
    ratio=s.mean_v2_12channels.iloc[-2]/s.mean_v2_12channels.iloc[-1]
    assert np.isclose(ratio,15.48,rtol=.001)
    return d,s


def counterexample(f):
    path=f.r1/"reviews"
    scores=np.load(path/"adversarial_M0_60s_scores.npy")
    audit=json.loads((path/"math_review_exact_outputs.json").read_text())
    info=next(g for g in audit.values() if isinstance(g,dict) and
              "mean" in g and np.isclose(g["mean"],scores.mean()))
    assert scores.shape==(500,)
    return scores,info


def fig4(root,out):
    f=Build(root,out,"Fig4",11.6,
            [(0,.54,1,.46),(0,0,.51,.50),(.55,0,.45,.50)],
            ["Window averaging changes the order of operations",
             "Exact Hann-window scaling","Designed reversible counterexample"])
    a,b,c=f.panels
    data=leakage_inputs(f)
    f.npz("A",**data)
    w,coh=data["frequency_hz"],data["true_coherency"]
    pairs=[(0,1),(1,2),(2,0)]
    for i,((j,k),color) in enumerate(zip(pairs,[A,B,GREEN])):
        ax=a.ax(.035+i*.102,.36,.083,.36)
        ax.plot(w,coh[:,j,k].real,color=color,lw=1.1)
        ax.plot(w,coh[:,j,k].imag,color=color,ls="--",lw=.85)
        ax.fill_between(w,*ax.get_ylim(),where=data["kernel_relative"]>.5,
                        color=GRAY,alpha=.16,zorder=0)
        ax.set(xlim=(8,12),xticks=[8,10,12],yticks=[])
        ax.set_title(rf"$C_{{{j+1}{k+1}}}$",pad=2)
        ax.spines["left"].set_visible(False)
        if i==1:
            ax.set_xlabel("Frequency (Hz)",labelpad=1)
    flow=a.ax(.327,.23,.405,.51,diagram=True)
    for y,op1,op2,color in ((.78,"Multiply edges","Average product",LATENT),
                            (.27,"Average spectra","Normalize, multiply",B)):
        arrow(flow,(.00,y),(.10,y),color,lw=.9)
        tag(flow,.27,y,op1,color=color,size=7)
        arrow(flow,(.44,y),(.51,y),color,lw=.9)
        tag(flow,.718,y,op2,color=color,size=7)
        arrow(flow,(.89,y),(.97,y),color,lw=.9)
    tag(flow,.46,.02,"2-s Hann window",size=7,color=LATENT)
    ax=a.ax(.773,.23,.20,.52)
    ax.plot(w,np.zeros_like(w),color=LATENT,ls="--",lw=.9,label="Product first")
    ax.plot(data["frequency_hz_tapered"],data["tapered_im_cycle"],
            color=B,marker="o",ms=2.8,label="Window first")
    ax.set(xlim=(8,12),xticks=[8,10,12],xlabel="Frequency (Hz)",ylabel=r"$\mathrm{Im}\,P$")
    ax.legend(frameon=False,loc="lower center",bbox_to_anchor=(.5,.98),fontsize=6.5)

    all_scaling,s=leakage_scaling(f)
    f.csv("B",s)
    for i,(y,label,exponent) in enumerate(((abs(s.closure_at10Hz),r"$|\mathrm{Im}\,P(10\,\mathrm{Hz})|$",2),
                                         (s.mean_v2_12channels,"Expected score",4))):
        ax=b.ax(.14+i*.49,.22,.34,.59)
        x=s.T_s.to_numpy()
        ax.loglog(x,y,"o-",color=B)
        ax.loglog(x[-4:],y.iloc[-1]*(x[-4:]/x[-1])**(-exponent),ls="--",color=LATENT,lw=.9)
        ax.text(.95,.92,rf"$T^{{-{exponent}}}$",transform=ax.transAxes,
                color=LATENT,ha="right",va="top",size=7)
        ax.set(xticks=[1,4,16,32],xticklabels=["1","4","16","32"],xlabel="Window (s)",
               ylabel=label)
        ax.tick_params(axis="both",pad=1)

    q,info=counterexample(f)
    f.csv("C",dict(record=np.arange(1,501),Q=q,first_99=np.arange(500)<99))
    f.csv("C",[dict(info,first99_mean=float(q[:99].mean()))],"_audit")
    f.npz("C",frequency_hz=data["frequency_hz"],peak1_psd=data["peak1_psd"],
          peak2_psd=data["peak2_psd"],delay_s=data["delay_s"])
    ax=c.ax(.16,.21,.80,.60)
    ax.hist(q*1e5,bins=28,color="#e2b89f",edgecolor="white",linewidth=.5)
    ax.axvline(0,color=GRAY,ls="--",lw=.9)
    ax.axvline(q[:99].mean()*1e5,color=TARGET,lw=1.5)
    ax.set(xlabel=r"Cross-half score $Q$ ($10^{-5}$)",ylabel="Records")
    ax.text(.03,.96,"First 99 mean\n"+r"$p=8\times10^{-5}$",transform=ax.transAxes,
            color=TARGET,va="top",size=7)
    inset=c.ax(.65,.61,.27,.18)
    for field,col in (("peak1_psd",LATENT),("peak2_psd",B)):
        inset.plot(data["frequency_hz"],data[field],color=col,lw=1)
    inset.set(xlim=(9,11),xticks=[9,10,11],yticks=[])
    inset.set_title("Latent peaks",size=7,pad=1)
    inset.tick_params(labelsize=6.5,length=2,pad=1)
    f.finish(r"""
**Figure 4. Finite frequency resolution creates a closure artifact in Model A.**
(a) The three exact coherencies of the two-component reversible example with a
125-ms delay in channel 2. Solid and dashed microtraces are real and imaginary
parts. The shaded band shows the half-maximum region of the 2-s Hann response
at 10 Hz. Forming the cycle at each frequency gives a real product. Taking the
Hann-window expected spectra, normalizing and then forming the product gives
the nonzero imaginary closure shown at right.
(b) Six archived exact-window expectations, including detrending. The left axis
is the 10-Hz absolute closure, and the right axis is the expected cross-half
score averaged across the 2–30 Hz bins and the 220 triplets of the 12-channel
construction. Guides with slopes −2 and −4 are anchored to the 32-s values.
The expected score falls 15.48-fold between 16 and 32 s.
(c) One point of input per independent simulated 60-s record (500 records).
The mean over all 500 is \(1.0117\times10^{-5}\), with 95% Monte Carlo interval
\([0.8420,1.1815]\times10^{-5}\). The solid line is the mean of the frozen first
99 records, with one-sided sign-flip \(p=8\times10^{-5}\) (49,999 flips).
The latent spectra peak at 9.75 and 10.25 Hz.
""")
