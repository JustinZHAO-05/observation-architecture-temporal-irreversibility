"""S5–S8: finite windows, confidence, sample complexity and EEG sensitivity."""
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from style import (BLUE, ORANGE, TEAL, GRAY, PURPLE, LIGHT, INK, COLORS, MARKERS,
                   supplement, legend, key_ticks, import_file)
from fig34 import leakage_inputs, leakage_scaling, counterexample
from fig56 import calibration_example, cert_tables, rate_data, eeg_data
from supp58 import audit_data


def s5(root,out):
    f=supplement(root,out,5,["Spectral smoothing across windows","Delay-dependent cycle bias",
                             "Approach to the asymptotic scaling","Sign-flip tests under reversible nulls"])
    a,b,c,d=f.panels
    exact=import_file(f.r1/"src/math_review_independent.py","supp_exact_window")
    scale,_=leakage_scaling(f)
    baseline=leakage_inputs(f)
    ax=a.ax(.17,.48,.79,.30)
    bx=a.ax(.17,.17,.79,.28)
    ax.plot(baseline["frequency_hz"],abs(baseline["true_spectrum"][:,0,1]),color=GRAY,
            lw=.83,ls="--",label="Population")
    bx.axhline(0,color=GRAY,lw=.73,ls="--")
    for i,T in enumerate((1,2,4,8)):
        freq,spectra,cycle=exact.expected_spectrum(T,delay_seconds=.125)
        v=cycle[:,0]
        expected=scale[np.isclose(scale.delay_s,.125)&(scale.T_s==T)].iloc[0]
        np.testing.assert_allclose([abs(v[freq==10])[0],np.mean(v*v)],
                                   [expected.closure_at10Hz,expected.mean_v2_3channels],rtol=2e-9,atol=1e-12)
        f.csv("A",dict(frequency_hz=freq,abs_cross_spectrum_12=abs(spectra[:,0,1]),
                       im_cycle=v,window_s=T,delay_s=.125),f"_{T}s")
        ax.plot(freq,abs(spectra[:,0,1]),color=COLORS[i],lw=1.12,label=f"{T} s")
        bx.plot(freq,v,color=COLORS[i],lw=1.12)
    f.csv("A",dict(frequency_hz=baseline["frequency_hz"],
                   abs_cross_spectrum_12=abs(baseline["true_spectrum"][:,0,1]),
                   im_cycle=baseline["true_im_cycle"]),"_population")
    ax.set(xlim=(8,12),ylabel=r"$|S_{12}|$")
    ax.tick_params(labelbottom=False)
    legend(ax,loc="lower left",bbox_to_anchor=(0,1.015),ncol=5,fontsize=7.15,columnspacing=.65)
    bx.set(xlim=(8,12),xlabel="Frequency (Hz)",ylabel=r"$\mathrm{Im}\,P$")

    f.csv("B",scale)
    ax=b.ax()
    for i,(delay,g) in enumerate(scale.groupby("delay_s")):
        g=g.sort_values("T_s")
        ax.loglog(g.T_s,abs(g.closure_at10Hz),color=COLORS[i],marker=MARKERS[i],ms=3.8,
                  lw=1.16,label=f"{delay*1000:g} ms")
    g=scale[np.isclose(scale.delay_s,.125)].sort_values("T_s")
    ax.loglog(g.T_s.iloc[-3:],g.asymptotic_T2_coefficient.iloc[0]*g.T_s.iloc[-3:].astype(float)**-2,
              color=GRAY,lw=.78,ls="--",label=r"$T^{-2}$ (125 ms)")
    key_ticks(ax,[1,2,4,8,16,32])
    ax.set(xlabel="Window length (s)",ylabel=r"$|\mathrm{Im}\,P(10\,\mathrm{Hz})|$")
    legend(ax,loc="lower left",ncol=2,fontsize=7.45)

    values=scale.sort_values(["delay_s","T_s"]).copy()
    values["T4_Q_bias"]=values.T_s**4*values.mean_v2_12channels
    values["T4_Q_over_32s"]=values.T4_Q_bias/values.groupby("delay_s").T4_Q_bias.transform("last")
    f.csv("C",values)
    ax=c.ax(.17,.49,.79,.32)
    bx=c.ax(.17,.18,.79,.27)
    for i,(delay,g) in enumerate(values.groupby("delay_s")):
        for p,key in [(ax,"observed_over_asymptotic"),(bx,"T4_Q_over_32s")]:
            p.semilogx(g.T_s,g[key],color=COLORS[i],marker=MARKERS[i],ms=3.5,lw=1.13)
    for p in (ax,bx):
        p.axhline(1,color=GRAY,ls="--",lw=.73)
        key_ticks(p,[1,2,4,8,16,32])
        p.set_ylim(0,1.19)
    ax.set_ylabel(r"$T^2|\mathrm{Im}\,P|/a_2$")
    ax.tick_params(labelbottom=False)
    bx.set(xlabel="Window length (s)",ylabel=r"$T^4Q_{\rm bias}$ / 32 s value")

    scores,info=counterexample(f)
    random=f.archive_csv(1,"time_domain_filter_null_summary.csv")
    reps=f.archive_csv(1,"time_domain_filter_null.csv")
    assert len(scores)==500 and len(reps)==960 and random.n.eq(240).all()
    assert np.isclose(scores[:99].mean(),info["first99_mean"]) and np.isclose(info["first99_signflip_p"],8e-5)
    structured=pd.DataFrame([dict(regime="Structured (first 99)",n=99,mean=info["first99_mean"],
                                  group_signflip_p=info["first99_signflip_p"])])
    f.csv("D",pd.concat([random,structured],ignore_index=True))
    f.csv("D",reps,"_randomized_records")
    f.csv("D",dict(rep=np.arange(1,501),score=scores,first99=np.arange(500)<99),"_structured_records")
    ax=d.ax(.32,.19,.64,.64)
    ax.axvline(.05,color=GRAY,lw=.85,ls="--")
    ax.scatter(random.group_signflip_p,range(4),marker="o",s=24,fc="white",ec=GRAY,lw=.86)
    ax.scatter([info["first99_signflip_p"]],[4],marker="D",s=25,c=ORANGE,lw=0)
    ax.set(xscale="log",xlim=(3.7e-5,1.18),ylim=(4.55,-.56),
           yticks=np.arange(5),yticklabels=["No filter","Mild","Moderate","Strong","Structured"],
           xlabel="Nominal sign-flip p value")
    ax.axhline(3.5,color=LIGHT,lw=.57)
    ax.text(.05,1.025,r"$0.05$",transform=ax.get_xaxis_transform(),ha="center",color=GRAY,fontsize=7.7)
    f.finish(r"""
**Figure S5. Finite-window mechanism and reversible-null behavior.**
(a) Exact expected detrended Hann spectra and imaginary coherency cycles for the 125-ms differential-delay example, at four window lengths. Dashed curves give the population cross-spectrum and zero imaginary cycle. Exact expectations are displayed on each window's discrete frequency grid.
(b) The magnitude of the expected 10-Hz imaginary cycle at six window lengths for delays of 25, 125 and 500 ms. The dashed line uses the analytic coefficient for the 125-ms delay.
(c) Top: the scaled cycle magnitude divided by the corresponding leading coefficient \(a_2\). Bottom: \(T^4Q_{\rm bias}\), divided by its numerical value at 32 s for each delay. Colors match (b). The archived 12-channel expected score is the mean squared expected imaginary cycle.
(d) Nominal one-sided sign-flip p values for four randomized reversible filter controls (240 records per regime) and the frozen first 99 records of the structured reversible model (\(p=8\times10^{-5}\)). The dashed line marks 0.05. Each point is one group test under its own simulation design. The 500 structured-record scores are included in the data.
""")


def s6(root,out):
    f=supplement(root,out,6,["Simultaneous spectral envelope","Unknown-mean correction",
                             "General Hermitian perturbations","Observed errors versus the radius"])
    a,b,c,d=f.panels
    ex=calibration_example(f)
    keys=("omega_rad_sample","true_spectrum","estimated_spectrum","uniform_radius","B","T_L","N","L","alpha","seed")
    f.npz("A",**{key:ex[key] for key in keys})
    w=ex["omega_rad_sample"]/np.pi
    keep=w<1
    x,y,z=w[keep],ex["estimated_spectrum"][keep,0,1].imag,ex["true_spectrum"][keep,0,1].imag
    e=ex["uniform_radius"]
    ax=a.ax()
    ax.fill_between(x,y-e,y+e,color=TEAL,alpha=.21,label=r"$\pm\epsilon$")
    ax.plot(x,y,color=BLUE,lw=1.13,label="Estimate")
    ax.plot(x,z,color=GRAY,lw=.9,ls="--",label="Population")
    ax.set(xlim=(0,1),xlabel=r"Normalized angular frequency $\omega/\pi$",ylabel=r"$\mathrm{Im}\,S_{12}$")
    legend(ax,loc="lower center",ncol=3,fontsize=7.5)

    centered,perturb=audit_data(f)
    centered["plot_jitter"]=f.rng.uniform(-.17,.17,len(centered))
    f.csv("B",centered)
    ax=b.ax()
    for i,(N,g) in enumerate(centered.groupby("N")):
        vals=g.error_over_radius
        ax.scatter(i+g.plot_jitter,vals,s=12,facecolor="none",edgecolor=TEAL,lw=.65)
        ax.hlines(vals.median(),i-.22,i+.22,color=INK,lw=1.12)
    ax.axhline(1,color=GRAY,lw=.8,ls="--")
    ax.set(xticks=[0,1,2],xticklabels=["512","2,048","8,192"],xlim=(-.48,2.48),ylim=(0,1.055),
           xlabel=r"Record length $N$ (samples)",ylabel="Maximum error / corrected radius")

    f.csv("C",perturb)
    ax=c.ax(.19,.19,.77,.64)
    for indefinite, g in perturb.groupby(perturb.min_empirical_eigenvalue<0):
        ax.scatter(g.true_bound,g.certificate,s=10 if indefinite else 7,c=ORANGE if indefinite else TEAL,
                   marker="x" if indefinite else "o",lw=.54 if indefinite else 0,alpha=.48,
                   label="Indefinite estimate" if indefinite else "PSD estimate")
    m=perturb.true_bound.max()*1.08
    ax.plot([0,m],[0,m],color=GRAY,lw=.76,ls="--",zorder=0)
    ax.set(xlim=(-1e-6,m),ylim=(-1e-6,m),xlabel="Population triangle bound (nats)",ylabel="Certificate (nats)")
    ax.set_xscale("symlog",linthresh=1e-5)
    ax.set_yscale("symlog",linthresh=1e-5)
    legend(ax,loc="upper left",fontsize=7.2)

    cert,reps=cert_tables(f)
    reps["error_over_radius"]=reps.max_spectral_error/reps.radius
    assert len(reps)==7680 and reps.envelope_covers.all() and reps.error_over_radius.max()<=1
    f.csv("D",reps)
    f.csv("D",cert,"_cells")
    ax=d.ax()
    labels=[r"$b=0.35$",r"$b=0.65$",r"$b=0.90$","Colored null","White null"]
    for k,(_,g) in enumerate(reps.groupby("model")):
        v=np.sort(g.error_over_radius.to_numpy())
        ax.step(np.r_[0,v,1],np.r_[0,np.arange(1,len(v)+1)/len(v),1],where="post",
                color=(*COLORS,GRAY)[k],lw=1.1,ls=("-","--","-.",":","-")[k],label=labels[k])
    ax.axvline(1,color=GRAY,lw=.8,ls="--")
    ax.set(xlim=(0,1.045),ylim=(-.015,1.035),xlabel="Maximum error / theoretical radius",ylabel="Empirical CDF")
    legend(ax,loc="lower right",fontsize=7.45)
    f.finish(r"""
**Figure S6. Confidence envelopes and their numerical validity.**
(a) Representative known-mean MA(1) spectrum, estimated from the same \(N=524{,}288\) trajectory as Fig. 6a. The band gives the simultaneous radius \(\epsilon\) for the imaginary cross-spectrum.
(b) Unknown-mean extension, checked by replaying 300 global-centering simulations (100 independent records per length). The largest normalized error is 0.284. The dashed line is the theoretical threshold.
(c) All 2,500 seeded Hermitian perturbations. The diagonal marks the population triangle bound. There were 1,713 positive certificates and all certificates were below their population bound, including trials with indefinite estimates. Both axes retain zero with symmetric-log scaling.
(d) Theoretical simultaneous coverage corresponds to an error-to-radius ratio at most one. Every one of the 7,680 fixed-grid analyses was within that threshold. They use 1,920 independent long trajectories, with nested lengths within each model–delay setting. The CDF pools lengths and delays descriptively. The nominal coverage level is 95%.
""")


def s7(root,out):
    f=supplement(root,out,7,["Weak-signal power","Power at longer delays",
                             "All continuous-rate certificates","Paired prefixes of each trajectory"])
    a,b,c,d=f.panels
    cert,reps=cert_tables(f)
    weak=cert[cert.model=="alternative_0.35"].copy()
    strong=cert[cert.model.isin(("alternative_0.65","alternative_0.9"))].copy()
    null=cert[cert.model.str.startswith("null")].copy()
    assert len(weak)==12 and len(strong)==24 and len(null)==24 and null.rejections.eq(0).all()
    f.csv("A",weak)
    f.csv("A",null,"_null_cells")
    f.csv("B",strong)
    f.csv("B",reps,"_replicates")
    ax=a.ax(.19,.20,.76,.61)
    mat=weak.pivot(index="max_delay",columns="N",values="rejections")
    ax.pcolormesh(np.arange(5)-.5,np.arange(4)-.5,mat/128,cmap="Greens",vmin=0,vmax=1,
                  edgecolor="white",lw=.7)
    for i,j in np.ndindex(mat.shape):
        count=mat.iloc[i,j]
        ax.text(j,i,str(count),ha="center",va="center",color="white" if count>66 else INK)
    ax.set(xticks=range(4),xticklabels=[r"$2^{11}$",r"$2^{13}$",r"$2^{15}$",r"$2^{17}$"],
           yticks=range(3),yticklabels=mat.index,xlabel=r"Record length $N$ (samples)",
           ylabel="Maximum delay (samples)")
    ax.set_title(r"$b=0.35$ · positive certificates out of 128",pad=5)
    ax.invert_yaxis()
    for k,(model,g) in enumerate(strong.groupby("model")):
        ax=b.ax(.16+.415*k,.20,.365,.55)
        for i,(delay,one) in enumerate(g.groupby("max_delay")):
            x=np.log2(one.N.to_numpy())
            ax.plot(x+(i-1)*.12,one.rejection_rate,color=COLORS[i],marker=MARKERS[i],
                    ms=3.6,lw=1.10,ls=["-","--",":"][i],label=f"{delay}")
        ax.set(xlim=(10.55,17.45),ylim=(-.045,1.07),yticks=[0,.5,1])
        key_ticks(ax,[11,13,15,17],[r"$2^{11}$",r"$2^{13}$",r"$2^{15}$",r"$2^{17}$"])
        ax.set_title(rf"$b={float(model.split('_')[-1]):g}$",pad=4.4)
        if k==0:
            ax.set_ylabel("Positive-certificate fraction")
        else:
            ax.tick_params(labelleft=False)
    key=b.ax(.10,.83,.88,.055,diagram=True)
    handles=[Line2D([],[],color=COLORS[i],ls=ls,marker=MARKERS[i],ms=3.4,lw=1.1,label=f"{n} samples")
             for i,(ls,n) in enumerate(zip(("-","--",":"),(0,2,8),strict=True))]
    legend(key,handles=handles,loc="center",ncol=3,fontsize=7.8,columnspacing=1.0)
    note=b.ax(.11,.03,.88,.06,diagram=True)
    note.text(.50,.46,r"Record length $N$ (samples)",ha="center")

    rates,stats=rate_data(f)
    assert rates.groupby(["max_delay","rep"]).N.nunique().eq(3).all()
    population=float(rates.population_triangle_integral.iloc[0])
    np.testing.assert_allclose(rates.population_triangle_integral,population,atol=1e-14)
    f.csv("C",rates)
    f.csv("C",stats,"_summary")
    ax=c.ax(.19,.19,.76,.64)
    for k,(delay,g) in enumerate(rates.groupby("max_delay")):
        for j,(_,one) in enumerate(g.groupby("N")):
            y=one.rate_lower.to_numpy()*1e3
            x=j+(-.15 if k==0 else .15)
            ax.scatter(x+one.log2_jitter,y,s=11,marker=MARKERS[k],alpha=.52,
                       fc="white",ec=(TEAL,PURPLE)[k],lw=.58,label=f"{delay} samples" if j==0 else None)
            lo,med,hi=np.quantile(y,[.025,.5,.975])
            ax.errorbar(x,med,yerr=[[med-lo],[hi-med]],color=INK,ls="none",marker="_",ms=7,capsize=2,lw=.86)
    ax.axhline(population*1e3,color=GRAY,lw=.79,ls="--")
    ax.set(xlim=(-.35,2.35),ylim=(-.018,37),xlabel=r"Record length $N$ (samples)",
           ylabel=r"Rate bound ($10^{-3}$ nats/sample)",xticks=[0,1,2],
           xticklabels=[r"$2^{15}$",r"$2^{17}$",r"$2^{19}$"])
    ax.set_yscale("symlog",linthresh=.07)
    ax.set_yticks([0,.1,1,10,30],["0","0.1","1","10","30"])
    legend(ax,loc="center left",fontsize=7.3)

    paths=rates.sort_values(["max_delay","rep","N"]).copy()
    paths["fraction_of_population"]=paths.rate_lower/paths.population_triangle_integral
    paths["deviation_from_prefix_median"]=(paths.rate_lower-
        paths.groupby(["max_delay","N"]).rate_lower.transform("median"))
    f.csv("D",paths)
    for k,(delay,g) in enumerate(paths.groupby("max_delay")):
        ax=d.ax(.18+.43*k,.19,.335,.62)
        mat=g.pivot(index="rep",columns="N",values="deviation_from_prefix_median")
        assert mat.shape==(64,3)
        vals=1e5*mat.to_numpy()
        ax.axhline(0,color=GRAY,ls="--",lw=.71)
        ax.plot([0,1,2],vals.T,color=(TEAL,PURPLE)[k],lw=.64,alpha=.28)
        ax.scatter(np.tile([0,1,2],64),vals.ravel(),color=(TEAL,PURPLE)[k],s=5,alpha=.35,lw=0)
        ax.set_title(f"{delay} samples",pad=4.4)
        ax.set(xticks=[0,1,2],xticklabels=[r"$2^{15}$",r"$2^{17}$",r"$2^{19}$"],xlim=(-.2,2.2))
        limit=abs(vals).max()*1.15
        ax.set_ylim(-limit,limit)
        if k==0:
            ax.set_ylabel(r"Deviation ($10^{-5}$ nats/sample)")
    note=d.ax(.11,.025,.88,.06,diagram=True)
    note.text(.50,.46,r"Record length $N$ (samples)",ha="center")
    f.finish(r"""
**Figure S7. Sample complexity at fixed and continuous frequencies.**
(a) All 12 fixed-grid cells at \(b=0.35\), with counts out of 128 independent trajectories per cell.
(b) Positive-certificate fractions at \(b=0.65\) and \(0.90\), stratified by maximum delay. The three series have small fixed horizontal offsets for visibility. All lengths within a model–delay setting use the same trajectories. The 24 null cells are supplied as a separate table, with zero positive certificates out of 128 in each cell.
(c) All 384 continuous-rate estimates, including zeros, from 128 independent long trajectories. Black marks give median and central 95% empirical quantiles. The dashed line gives the common population triangle integral.
(d) Each thin line links three prefixes of the same trajectory within one delay group (64 per group). Points show deviations from the median for their delay and prefix length, making individual variation visible. The two delay panels use the same units with different vertical limits. Panel (c) uses a symmetric-log scale with a linear region around zero.
""")


def s8(root,out):
    f=supplement(root,out,8,["Record selection and QC","Complete-window intersection",
                             "Participant-level reference effects","Alpha contribution to the full score"])
    a,b,c,d=f.panels
    long,pairs,_,_,_=eeg_data(f)
    original=f.archive_csv(1,"eeg_primary_original_subjects.csv")
    average=f.archive_csv(1,"eeg_primary_average_subjects.csv")
    raw=f.archive_csv(1,"raw_data_manifest.csv")
    keys=["subject","run"]
    assert len(raw)==len(original)==len(average)==218
    rows=original[keys+["status","n_epochs_a","n_epochs_b"]].merge(
        average[keys+["status","n_epochs_a","n_epochs_b"]],on=keys,validate="one_to_one",
        suffixes=("_original","_average"))
    for ref in ("original","average"):
        rows[f"complete_{ref}"]=rows[f"status_{ref}"].eq("ok") & rows[
            [f"n_epochs_a_{ref}",f"n_epochs_b_{ref}"]].eq(12).all(axis=1)
    rows["post_pilot"]=rows.subject>10
    rows["matched"]=rows.post_pilot & rows.complete_original & rows.complete_average
    observed=rows[rows.matched]
    assert len(observed)==113 and observed.subject.nunique()==71
    assert set(map(tuple,observed[keys].to_numpy()))==set(map(tuple,pairs[keys].to_numpy()))
    f.csv("A",rows)
    steps=[("Acquired",rows),("Pilot excluded",rows[rows.post_pilot]),
           ("Status OK in both",rows[rows.post_pilot & rows.status_original.eq("ok") & rows.status_average.eq("ok")]),
           ("Complete in both",observed)]
    stages=pd.DataFrame(dict(stage=[x[0] for x in steps],records=[len(x[1]) for x in steps],
                             participants=[x[1].subject.nunique() for x in steps]))
    f.csv("A",stages,"_stages")
    ax=a.ax(.30,.19,.66,.63)
    ax.barh(range(4),stages.records,color=[LIGHT,"#8FA8BA","#6389A3",BLUE],height=.56)
    for i,g in stages.iterrows():
        ax.text(g.records+3.2,i,f"{g.records} / {g.participants}",va="center",fontsize=7.9)
    ax.set(yticks=range(4),yticklabels=stages.stage,xlim=(0,277),ylim=(3.55,-.55),
           xticks=[0,100,200],xlabel="Record count")
    ax.text(.995,1.035,"Records / people",transform=ax.transAxes,ha="right",fontsize=7.8,color=GRAY)

    tab=(rows[rows.post_pilot].groupby(["run","complete_original","complete_average"]).size()
         .reindex(pd.MultiIndex.from_product([[1,2],[False,True],[False,True]],
                  names=["run","complete_original","complete_average"]),fill_value=0)
         .rename("n").reset_index())
    assert tab.groupby("run").n.sum().tolist()==[99,99]
    assert tab[tab.complete_original & tab.complete_average].n.tolist()==[52,61]
    f.csv("B",tab)
    f.csv("B",rows[rows.post_pilot],"_membership")
    for k,(run,g) in enumerate(tab.groupby("run")):
        ax=b.ax(.18+.43*k,.24,.36,.46)
        m=g.pivot(index="complete_original",columns="complete_average",values="n").to_numpy()
        ax.pcolormesh(np.arange(3)-.5,np.arange(3)-.5,m,cmap="Blues",vmin=0,vmax=65,
                      edgecolor="white",lw=.7)
        for i,j in np.ndindex(m.shape):
            ax.text(j,i,str(m[i,j]),ha="center",va="center",color="white" if m[i,j]>41 else INK,fontsize=9)
        ax.set(xticks=[0,1],xticklabels=["No","Yes"],yticks=[0,1],yticklabels=["No","Yes"] if k==0 else ["",""])
        ax.set_title("Eyes open" if run==1 else "Eyes closed",pad=6)
        ax.set_aspect("equal")
        if k==0:
            ax.set_ylabel("Original complete")
    note=b.ax(.14,.09,.86,.07,diagram=True)
    note.text(.5,.51,"64-ch average complete",ha="center")

    pairs["reference_effect"]=pairs.average-pairs.original
    people=pairs.groupby("subject").reference_effect.agg(effect="mean",matched_runs="size").reset_index()
    people=people.sort_values(["effect","subject"]).reset_index(drop=True)
    people["rank"]=np.arange(1,1+len(people))
    assert len(people)==71 and people.matched_runs.value_counts().to_dict()=={2:42,1:29}
    f.csv("C",people)
    f.csv("C",pairs,"_record_differences")
    ax=c.ax()
    ax.axhline(0,color=GRAY,ls="--",lw=.7)
    ax.vlines(people["rank"],0,people.effect*1e4,color=LIGHT,lw=.65)
    for k,(n,g) in enumerate(people.groupby("matched_runs")):
        ax.scatter(g["rank"],g.effect*1e4,s=15,marker=MARKERS[k],color=(GRAY,BLUE)[k],lw=0,
                   label=f"{n} matched {'run' if n==1 else 'runs'}")
    ax.set(xlim=(-1,73),xlabel="Participant rank by effect",ylabel=r"$Q_{\rm average}-Q_{\rm original}$ ($10^{-4}$)")
    legend(ax,loc="upper left",fontsize=7.7)

    q=long[["subject","run","reference","q","q_alpha","alpha_contribution_to_full_Q"]].copy()
    assert len(q)==226
    np.testing.assert_allclose(q.alpha_contribution_to_full_Q,q.q_alpha*10/57,atol=2e-16,rtol=0)
    f.csv("D",q)
    ax=d.ax(.19,.19,.77,.64)
    ax.axhline(0,color=LIGHT,lw=.65)
    ax.axvline(0,color=LIGHT,lw=.65)
    grid=np.array([-2.2,11.5])
    ax.plot(grid,grid,color=GRAY,ls="--",lw=.73)
    for i,ref in enumerate(("original","average")):
        g=q[q.reference==ref]
        ax.scatter(g.q*1e4,g.alpha_contribution_to_full_Q*1e4,s=12,marker=MARKERS[i],
                   facecolor="white" if i==0 else BLUE,edgecolor=GRAY if i==0 else BLUE,lw=.63,alpha=.73,
                   label=["Original","64-ch average"][i])
    ax.set(xlim=(-2.2,11.5),xlabel=r"Full $Q$ ($10^{-4}$)",ylabel=r"Alpha contribution ($10^{-4}$)")
    legend(ax,loc="upper left",fontsize=7.45)
    f.finish(r"""
**Figure S8. EEG selection and observation-coordinate sensitivity.**
(a) The archived acquisition and QC funnel, counting records and distinct participants at each step. Status OK under both references precedes the restriction to complete windows.
(b) Observed complete-window membership among the 99 post-pilot participants per eye condition. A complete record has status OK and all 12 predefined windows in each half. The joint cells contain 52 eyes-open and 61 eyes-closed records.
(c) The mean within-record reference difference for each of the 71 participants, using the matched runs available to that participant. Markers distinguish 29 participants with one matched run and 42 with both.
(d) The signed contribution of alpha (8 to below 13 Hz) versus full \(Q\), across all 226 record–reference combinations. The band contribution uses the full frequency–triplet denominator and equals \(10/57\) times the alpha-band mean. The diagonal marks equality with full \(Q\). The comparison is exploratory and eye condition follows the source recording order.
""")
