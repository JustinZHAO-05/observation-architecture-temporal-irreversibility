"""Supplementary window, confidence, power and EEG diagnostics."""
import json
import sys

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from common import A,B,EC,EO,GRAY,GREEN,INK,LATENT,TARGET,TWO,Build,arrow,tag
from fig34 import counterexample,leakage_inputs,leakage_scaling
from fig56 import calibration_example,cert_tables,eeg_data,power_heatmaps,rate_data,rate_points


def sup5(root,out):
    f=Build(root,out,"FigS5",12.0,TWO,["Cross-spectra and Hann response","Exact window expectations",
        "Designed reversible null","Randomized filter controls"])
    a,b,c,d=f.panels
    ex=leakage_inputs(f)
    f.npz("A",**ex)
    w, spec=ex["frequency_hz"],ex["true_spectrum"]
    ax=a.ax(.18,.47,.78,.34)
    for (i,j),col,ls in zip(((0,1),(1,2),(2,0)),[TARGET,B,GREEN],["-","-","--"]):
        ax.plot(w,abs(spec[:,i,j]),color=col,ls=ls,lw=1.1,label=rf"$|S_{{{i+1}{j+1}}}|$")
    ax.set(xlim=(8,12),xticks=[8,9,10,11,12],ylabel="Cross-spectrum")
    ax.tick_params(labelbottom=False)
    ax.legend(frameon=False,ncol=2,loc="upper right",fontsize=6.5)
    low=a.ax(.18,.17,.78,.24)
    low.fill_between(w,0,ex["kernel_relative"],color=LATENT,alpha=.19)
    low.plot(w,ex["kernel_relative"],color=LATENT,lw=1.2)
    low.set(xlim=(8,12),xticks=[8,9,10,11,12],yticks=[0,1],
            ylabel="Hann response",xlabel="Frequency (Hz)")

    scale,_=leakage_scaling(f)
    f.csv("B",scale)
    for k,(key,label,order) in enumerate([
            ("closure_at10Hz",r"$|\mathrm{Im}\,P(10\,\mathrm{Hz})|$",2),
            ("mean_v2_12channels","Expected score",4)]):
        ax=b.ax(.16+.49*k,.19,.32,.61)
        for i,(delay,g) in enumerate(scale.groupby("delay_s")):
            ax.loglog(g.T_s,abs(g[key]),marker=["o","s","^"][i],ms=3,color=[A,B,LATENT][i],
                      lw=1.0,label=f"{1000*delay:g}")
        g=scale[scale.delay_s==.125]
        x=g.T_s.to_numpy()[-4:]
        ax.loglog(x,abs(g[key].iloc[-1])*(x/x[-1])**(-order),ls="--",color=INK,lw=.8)
        ax.set(xticks=[1,4,16,32],xticklabels=["1","4","16","32"],xlabel="Window (s)",ylabel=label)
        if k==1:
            ax.legend(frameon=False,loc="lower left",title="Delay (ms)",fontsize=6.5)

    q,info=counterexample(f)
    f.csv("C",dict(record=np.arange(1,501),Q=q,first_99=np.arange(500)<99))
    f.csv("C",[info],"_audit")
    ax=c.ax(.18,.19,.78,.62)
    ax.hist(q*1e5,bins=28,color="#e2b89f",edgecolor="white",linewidth=.5)
    ax.axvline(0,color=GRAY,ls="--",lw=.85)
    ax.axvline(info["first99_mean"]*1e5,color=TARGET,lw=1.5,label="First 99 mean")
    ax.set(xlabel=r"Cross-half score $Q$ ($10^{-5}$)",ylabel="Records")
    ax.legend(frameon=False,loc="upper right")
    ax.text(.04,.90,r"$p=8\times10^{-5}$",color=TARGET,transform=ax.transAxes)

    summary=f.archive_csv(1,"time_domain_filter_null_summary.csv")
    reps=f.archive_csv(1,"time_domain_filter_null.csv")
    assert len(reps)==960 and summary.n.eq(240).all()
    for row in summary.itertuples(index=False):
        assert np.isclose(row.mean,reps[reps.regime==row.regime].score.mean())
    f.csv("D",summary)
    f.csv("D",reps,"_replicates")
    ax=d.ax(.25,.19,.71,.62)
    y=np.arange(4)
    mean=summary["mean"]*1e5
    ax.axvline(0,color=GRAY,ls="--",lw=.85)
    ax.errorbar(mean,y,xerr=[mean-summary.ci_low*1e5,summary.ci_high*1e5-mean],
                marker="o",ls="none",color=TARGET,capsize=3,lw=1.1)
    ax.set(yticks=y,yticklabels=["No filter","Mild","Moderate","Strong"],ylim=(3.55,-.55),
           xlabel=r"Mean score $Q$ ($10^{-5}$)")
    f.finish(r"""
**Figure S5. Exact-window bias and distinct reversible-null experiments.**
(a) Magnitudes of the three exact delayed cross-spectra and the relative
squared response of the 2-s detrended Hann operator centered at 10 Hz.
\(S_{23}\) and \(S_{31}\) have the same magnitude here. (b) All six window
lengths for each of three delays. Dashed slopes are −2 and −4, anchored to
the 32-s value for the 125-ms delay. (c) The designed reversible example
has 500 independent 60-s records. The frozen first-99 mean is marked
(\(p=8\times10^{-5}\), one-sided sign flip). (d) The separate randomized
filter experiment has 240 independent records per regime (960 total).
Points and bars give archived means and 95% intervals.
""")


def audit_data(f):
    # Replays the random-number order in audit_round2.py and captures the
    # individual outputs omitted from the archived aggregate JSON.
    sys.path.insert(0,str(f.r2/"src"))
    try:
        from theory_round2 import ma_coeff,ma_spectrum
        from finite_certificate import certificate,estimate,exact_triangle_bound,radius
    finally:
        sys.path.pop(0)
    reference=json.loads((f.r2/"results/independent_formula_audit.json").read_text())
    rng=np.random.default_rng(863902)
    for n in (9,17,40):
        for _ in (0,1,5):
            rng.normal(size=(n,3))
    rows=[]
    for rep in range(reference["perturbation_cases"]):
        z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        s=z@z.conj().T+.2*np.eye(3)
        gain=10**rng.uniform(-1,1,size=3)
        s=gain[:,None]*s*gain[None,:]
        e=10**rng.uniform(-6,-1)*np.max(s.diagonal().real)
        d=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        d=(d+d.conj().T)/2
        d*=e/np.max(abs(d))
        hat=s+d
        lb,p,err=certificate(hat[None],e)
        truth=exact_triangle_bound(s[None])[0]
        true_cycle=(s[0,1]*s[1,2]*s[2,0]).imag
        rows.append(dict(rep=rep,epsilon=e,min_empirical_eigenvalue=np.linalg.eigvalsh(hat)[0],
                         certificate=lb[0],true_bound=truth,certificate_excess=lb[0]-truth,
                         witness_excess=abs(p[0]-true_cycle)-err[0]))
    perturb=pd.DataFrame(rows)
    assert len(perturb)==2500 and (perturb.certificate>0).sum()==reference["positive_certificates"]
    assert np.isclose(perturb.certificate_excess.max(),reference["max_certificate_minus_true_bound"],atol=1e-13)
    assert np.isclose(perturb.witness_excess.max(),reference["max_product_error_minus_envelope"],atol=1e-13)

    a0,a1=ma_coeff(.8)
    w=np.arange(1,6)*np.pi/6
    delays=np.array([0,1,2])
    h=np.exp(-1j*w[:,None]*delays)
    s=h[:,:,None]*np.array([ma_spectrum(.8,v) for v in w])*h[:,None,:].conj()
    rows=[]
    for n in [512,2048,8192]:
        for rep in range(100):
            z=rng.normal(size=(n+4,3))
            x=z[1:]@a0.T+z[:-1]@a1.T
            y=np.column_stack([x[2-j:2-j+n,j] for j in range(3)])+np.array([50,-10,2])
            sh=estimate(y,3,w,center=True)
            e=radius(n,3,3,len(w),1.8,estimated_mean=True)
            error=np.max(abs(sh-s))
            rows.append(dict(N=n,rep=rep,radius=e,max_spectral_error=error,
                             error_over_radius=error/e))
    centered=pd.DataFrame(rows)
    assert len(centered)==300 and centered.error_over_radius.max()<1
    assert np.isclose(centered.error_over_radius.max(),reference["unknown_mean_max_error_over_radius"])
    return centered,perturb


def sup6(root,out):
    f=Build(root,out,"FigS6",11.9,TWO,["A simultaneous spectral envelope","Observed errors within the radius",
        "Global centering audit","Hermitian perturbation audit"])
    a,b,c,d=f.panels
    ex=calibration_example(f)
    keys=["omega_rad_sample","true_spectrum","estimated_spectrum","uniform_radius","B","T_L","N","L","alpha","seed"]
    f.npz("A",**{k:ex[k] for k in keys})
    w=ex["omega_rad_sample"]/np.pi
    keep=w<1
    w=w[keep]
    y=ex["estimated_spectrum"][keep,0,1].imag
    z=ex["true_spectrum"][keep,0,1].imag
    e=ex["uniform_radius"]
    ax=a.ax(.19,.19,.77,.63)
    ax.fill_between(w,y-e,y+e,color=GREEN,alpha=.20,label=r"$\pm\epsilon$")
    ax.plot(w,z,color=LATENT,ls="--",lw=1.5,label="Population")
    ax.plot(w,y,color=TARGET,lw=.8,marker="o",markevery=100,ms=2.8,label="Estimate")
    ax.set(xlim=(0,1),xlabel=r"Normalized angular frequency $\omega/\pi$",ylabel=r"$\mathrm{Im}\,S_{12}$")
    ax.legend(frameon=False,loc="lower center",ncol=3)

    _,reps=cert_tables(f)
    reps["error_over_radius"]=reps.max_spectral_error/reps.radius
    assert reps.error_over_radius.max()<1
    f.csv("B",reps)
    ax=b.ax(.17,.19,.79,.63)
    colors=[TARGET,A,B,LATENT,GREEN]
    labels={"alternative_0.35":r"$b=0.35$","alternative_0.65":r"$b=0.65$",
            "alternative_0.9":r"$b=0.90$","null_colored":"MA(1) null","null_white":"White null"}
    for i,(model,g) in enumerate(reps.groupby("model")):
        v=np.sort(g.error_over_radius.to_numpy())
        ax.step(v,np.arange(1,len(v)+1)/len(v),where="post",color=colors[i],lw=1.1,
                ls=["-","--","-.",":","-"][i],label=labels[model])
    ax.axvline(1,color=GRAY,ls="--",lw=.9)
    ax.set(xlim=(0,1.02),ylim=(0,1.02),xlabel="Maximum error / radius",ylabel="Empirical CDF")
    ax.legend(loc="lower right",frameon=False,ncol=1)

    centered,perturb=audit_data(f)
    centered["x_jitter"]=f.rng.uniform(-.18,.18,len(centered))
    f.csv("C",centered)
    ax=c.ax(.17,.19,.79,.63)
    for i,(n,g) in enumerate(centered.groupby("N")):
        ax.scatter(i+g.x_jitter,g.error_over_radius,s=12,facecolor="none",edgecolor=GREEN,lw=.65)
        ax.hlines(g.error_over_radius.median(),i-.23,i+.23,color=INK,lw=1.3)
    ax.axhline(1,color=GRAY,ls="--",lw=.9)
    ax.set(ylim=(0,1.06),xlim=(-.5,2.5),xticks=[0,1,2],xticklabels=["512","2,048","8,192"],
           xlabel=r"Record length $N$ (samples)",ylabel="Maximum error / radius")
    ax.text(.94,.75,"300 / 300 covered",color=GREEN,ha="right",transform=ax.transAxes)

    f.csv("D",perturb)
    ax=d.ax(.18,.19,.78,.63)
    indefinite=perturb.min_empirical_eigenvalue<0
    ax.scatter(perturb.true_bound[~indefinite],perturb.certificate[~indefinite],
               s=7,color=GREEN,alpha=.34,lw=0,label="PSD estimate")
    ax.scatter(perturb.true_bound[indefinite],perturb.certificate[indefinite],
               s=10,marker="x",color=B,alpha=.46,lw=.6,label="Indefinite estimate")
    m=perturb.true_bound.max()*1.07
    ax.plot([0,m],[0,m],color=GRAY,ls="--",lw=.9,zorder=0)
    ax.set(xlim=(-.005,m),ylim=(-.005,m),xlabel="True triangle bound (nats)",
           ylabel="Certificate (nats)")
    ax.legend(frameon=False,loc="upper left")
    f.finish(r"""
**Figure S6. Simultaneous spectral uncertainty and implementation audits.**
(a) Imaginary cross-spectrum and uniform radius from the same known-mean
MA(1) example as Fig. 5(a). (b) Empirical CDFs for the realized maximum
error divided by its simultaneous radius in the fixed-grid study.
Each model pools three delay groups and four nested lengths. The unit
reference marks coverage. (c) Replay of the 300 archived global-centering
checks at unknown constant mean (100 trajectories per length). The maximum
error-to-radius ratio is 0.284. (d) Replay of the 2,500 archived Hermitian
perturbations. Each certificate is at or below the true bound, including
cases in which the estimated matrix is indefinite. The horizontal
zero values are retained. In (c,d) the frozen RNG and summary statistics
were used to verify replay.
""")


def sup7(root,out):
    f=Build(root,out,"FigS7",11.9,[(0,.53,.37,.47),(.40,.53,.60,.47),(0,0,.51,.47),(.55,0,.45,.47)],
            ["Reversible nulls","All alternative cells","All rate replicates","From grid center to full cell"])
    a,b,c,d=f.panels
    cert,_=cert_tables(f)
    null=cert[cert.model.str.startswith("null")].copy().reset_index(drop=True)
    assert len(null)==24 and (null.rejections==0).all()
    assert np.allclose(null.rate_ci_high,1-.025**(1/128))
    f.csv("A",null)
    ax=a.ax(.21,.21,.75,.58)
    for i,(model,g) in enumerate(null.groupby("model")):
        x=np.arange(len(g))+i*.23
        ax.vlines(x,0,100*g.rate_ci_high,color=[A,LATENT][i],lw=.9,alpha=.85)
        ax.scatter(x,np.zeros(len(g)),color=[A,LATENT][i],s=13,
                   marker=["o","s"][i],label=["MA(1) null","White null"][i],zorder=4)
    for x in [3.6,7.6]:
        ax.axvline(x,color=GRAY,lw=.65,ls=":")
    ax.axhline(2.840805,color=GRAY,ls="--",lw=.7)
    ax.set(xlim=(-.55,11.65),ylim=(-.18,4.5),xticks=[1.5,5.5,9.5],xticklabels=["0","2","8"],
           xlabel="Maximum delay (samples)",ylabel="Rejections (%)")
    ax.legend(frameon=False,ncol=2,loc="upper center",fontsize=6.5)
    ax.text(.98,.73,"0 / 128 per cell",transform=ax.transAxes,ha="right",size=7,color=LATENT)
    f.csv("B",power_heatmaps(b,cert))
    rate,summary=rate_data(f)
    f.csv("C",rate)
    f.csv("C",summary,"_summary")
    rate_points(c.ax(.23,.18,.73,.65),rate)

    # Deterministic cell envelope based on the verified representative record.
    ex=calibration_example(f)
    center=ex["omega_rad_sample"][345]
    h=np.pi/len(ex["omega_rad_sample"])
    w=np.linspace(center-h,center+h,121)
    cov=ex["lag_covariances"]
    z=np.exp(-1j*w)
    estimate=(cov[0,0,1]+z*cov[1,0,1]+z.conj()*cov[1,1,0]).imag
    midpoint=estimate[len(w)//2]
    m=ex["cell_variation"]
    e=ex["uniform_radius"]
    assert np.max(abs(estimate-midpoint))<=m
    f.npz("D",omega_rad_sample=w,center=center,cell_halfwidth=h,
          estimate=estimate,estimate_center=midpoint,derivative_margin=m,uniform_radius=e)
    ax=d.ax(.23,.20,.73,.62)
    x=(w-center)/h
    ax.axhspan(-1,1,color=GREEN,alpha=.16)
    ax.plot(x,(estimate-midpoint)/m,color=TARGET,label="Within-cell change")
    ax.scatter(0,0,s=24,color=TARGET,zorder=4)
    ax.axhline(0,color=GRAY,lw=.75,ls="--")
    ax.set(ylim=(-1.4,1.4),xlim=(-1,1),xticks=[-1,0,1],xticklabels=[r"$-h$","0",r"$+h$"],
           yticks=[-1,0,1],xlabel="Offset from cell center",ylabel="Change / derivative margin")
    ax.legend(frameon=False,loc="upper center",fontsize=6.5)
    ax.text(.97,.04,r"Cell radius $=\epsilon+\Delta_{\rm cell}$",
            transform=ax.transAxes,color=GREEN,ha="right",size=7)
    f.finish(r"""
**Figure S7. Detection power and continuous-frequency propagation.**
(a) Zero positive certificates out of 128 trajectories in every null
cell. Within each delay block the four positions represent increasing
nested record lengths. Lines reach the two-sided exact 95% binomial
upper endpoint (2.84%); the interval applies to each cell.
(b) All 36 alternative cells, with counts per 128 trajectories. (c) All
384 rate bounds (128 independent long trajectories). Markers indicate
nested lengths, and dark marks give medians and central 95% empirical
quantiles. (d) An actual cell of the Fig. 5(a) example, showing the
estimated imaginary cross-spectrum variation relative to its center and
scaled by the deterministic derivative margin \(\Delta_{\rm cell}\).
Adding that margin to the uniform \(\epsilon\) gives an error radius
that applies throughout the cell of half-width \(h\).
""")


def sup8(root,out):
    f=Build(root,out,"FigS8",11.9,[(0,.57,1,.43),(0,0,.305,.52),(.32,0,.31,.52),(.64,0,.36,.52)],
            ["From acquired baselines to matched windows","Scores by condition",
             "Amplitude and alignment","Paired eye condition"])
    a,b,c,d=f.panels
    long,pairs,condition,ref_ci,cond_ci=eeg_data(f)
    orig=f.archive_csv(1,"eeg_primary_original_subjects.csv")
    avg=f.archive_csv(1,"eeg_primary_average_subjects.csv")
    raw=f.archive_csv(1,"raw_data_manifest.csv")
    assert len(raw)==len(orig)==len(avg)==218
    keys=["subject","run"]
    rows=orig[keys+["status","n_epochs_a","n_epochs_b"]].merge(
        avg[keys+["status","n_epochs_a","n_epochs_b"]],on=keys,
        validate="one_to_one",suffixes=("_orig","_avg"))
    rows["after_pilot"]=rows.subject>10
    window_fields=[k for k in rows if k.startswith("n_epochs_")]
    rows["both_complete"]=rows.after_pilot & rows[window_fields].eq(12).all(axis=1) & \
        rows[["status_orig","status_avg"]].eq("ok").all(axis=1)
    observed=rows[rows.both_complete]
    assert len(observed)==113 and observed.subject.nunique()==71
    assert set(map(tuple,observed[keys].to_numpy()))==set(map(tuple,pairs[keys].to_numpy()))
    f.csv("A",rows)
    counts=[len(rows),int(rows.after_pilot.sum()),len(observed)]
    people=[rows.subject.nunique(),rows[rows.after_pilot].subject.nunique(),observed.subject.nunique()]
    stages=["Acquired baselines","After 10 pilot people","Both references complete"]
    f.csv("A",dict(stage=stages,records=counts,people=people),"_stages")
    ax=a.ax(.026,.07,.95,.73,diagram=True)
    for i,(title,n,k) in enumerate(zip(stages,counts,people)):
        x=.04+i*.325
        tag(ax,x+.112,.87,title,color=INK,weight="semibold")
        ax.add_patch(Rectangle((x,.47),.224*n/218,.16,color=[LATENT,A,TARGET][i],lw=0))
        tag(ax,x+.112,.31,f"{n} records / {k} people",color=[LATENT,A,TARGET][i])
        if i<2:
            arrow(ax,(x+.237,.55),(x+.306,.55),LATENT)
    tag(ax,.80,.07,"52 open · 61 closed · 42 paired people",color=TARGET,size=7.5)

    f.csv("B",long)
    ax=b.ax(.22,.20,.73,.61)
    for i,((run,ref),g) in enumerate(long.groupby(["run","reference"])):
        col=EO if run==1 else EC
        v=g.q.to_numpy()*1e4
        x=[-.16,.16,.84,1.16][i]
        ax.scatter(x+f.rng.uniform(-.10,.10,len(g)),v,s=13,color=col,alpha=.57,
                   marker="s" if ref=="average" else "o",
                   facecolors=col if ref=="average" else "none",edgecolors=col,lw=.55)
        ax.hlines(np.mean(v),x-.11,x+.11,color=INK,lw=1.25)
    ax.axhline(0,color=GRAY,ls="--",lw=.8)
    ax.set(xlim=(-.39,1.38),xticks=[0,1],xticklabels=["Open","Closed"],
           ylabel=r"Score $Q$ ($10^{-4}$)")
    ax.text(.02,.97,"□ Average\n○ Original",transform=ax.transAxes,va="top",size=6.5,color=LATENT)

    f.csv("C",long)
    ax=c.ax(.24,.20,.72,.61)
    for ref,g in long.groupby("reference"):
        ax.scatter(g.amplitude_factor*1e3,g.alignment,s=13,alpha=.57,
                   marker="s" if ref=="average" else "o",color=B if ref=="average" else A,
                   edgecolors="white",lw=.35,label=ref.capitalize())
    ax.axhline(0,color=GRAY,ls="--",lw=.8)
    ax.set(xlabel=r"Amplitude factor ($10^{-3}$)",ylabel="Alignment")
    ax.legend(frameon=False,loc="upper right",fontsize=6.5)

    paired=long[long.subject.isin(condition.subject)].copy()
    assert len(paired)==168
    f.csv("D",paired)
    f.csv("D",cond_ci,"_summary")
    ax=d.ax(.18,.20,.78,.61)
    for i,(ref,col) in enumerate([("original",A),("average",B)]):
        g=paired[paired.reference==ref].pivot(index="subject",columns="run",values="q")
        x=np.array([0,1])+2.42*i
        for values in g.to_numpy()*1e4:
            ax.plot(x,values,color=col if values[1]>=values[0] else GRAY,lw=.7,alpha=.55)
        ax.scatter(np.broadcast_to(x,g.shape),g.to_numpy()*1e4,s=10,color=col,alpha=.55,lw=0)
        ax.plot(x,g.mean().to_numpy()*1e4,color=col,lw=1.6,marker="D",ms=4.2,zorder=5)
        ax.text(x.mean(),.97,["Original","64-ch average"][i],ha="center",va="top",
                transform=ax.get_xaxis_transform(),color=col,size=6.8)
    ax.axhline(0,color=GRAY,ls="--",lw=.8)
    ax.set(xticks=[0,1,2.42,3.42],xticklabels=["Open","Closed","Open","Closed"],
           xlim=(-.38,3.80),ylabel=r"Score $Q$ ($10^{-4}$)")
    ax.set_ylim(top=ax.get_ylim()[1]*1.17)
    f.finish(r"""
**Figure S8. Provenance and paired EEG score decompositions.**
(a) The archive contains two baseline records per person. Excluding 10
pilot participants and intersecting the complete-window masks across
references leaves 113 records from 71 people. (b) Each dot is one person
within a condition and reference; the same records appear at both references.
Horizontal marks give condition means. (c) For split-half imaginary cycles
\(v_A,v_B\), \(Q=\langle v_Av_B\rangle=A_Q\,r_Q\), where
\(A_Q=\mathrm{RMS}(v_A)\mathrm{RMS}(v_B)\) and \(r_Q=Q/A_Q\) is signed
alignment. Averages are over the analyzed frequency–triplet grid.
Each record contributes one point per reference. (d) For 42 people with
both eye conditions, each line links their two scores within reference.
Colored and gray lines denote nonnegative and negative closed-minus-open
differences, respectively. Diamonds give means. All same-window comparisons
are exploratory, with eye condition associated with baseline run order.
""")
