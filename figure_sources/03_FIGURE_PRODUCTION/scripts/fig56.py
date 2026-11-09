"""External calibration and same-window EEG."""
import ast
import sys

import numpy as np
import pandas as pd
from matplotlib.patches import Circle, Rectangle
from scipy.stats import gaussian_kde
from common import A,B,EC,EO,GRAY,GREEN,INK,LATENT,TARGET,Build,arrow,tag


def calibration_example(f):
    sys.path.insert(0,str(f.r2/"src"))
    try:
        from theory_round2 import ma_coeff,ma_spectrum
        from continuous_rate_certificate import autocov,rate_bound
        from finite_certificate import certificate
    finally:
        sys.path.pop(0)
    N,b,L,bound,alpha=524288,.9,1,1.9,.05
    z=np.random.default_rng(713420).normal(size=(N+2,3))
    m0,m1=ma_coeff(b)
    y=(z[1:]@m0.T+z[:-1]@m1.T)[:N]
    rate,e,v,w,estimate=rate_bound(y,L,bound,alpha=alpha)
    lower,cycle,cycle_error=certificate(estimate,e+v)
    true=np.array([ma_spectrum(b,ww) for ww in w])
    archive=f.archive_csv(2,"continuous_rate_replicates.csv")
    row=archive[(archive.max_delay==0)&(archive.N==N)&(archive.rep==0)].iloc[0]
    assert np.allclose([rate,e,v,np.max(abs(estimate-true))],
                       row[["rate_lower","uniform_radius","cell_variation","dense_grid_max_error"]].astype(float),
                       rtol=1e-8,atol=5e-13)
    return dict(record_excerpt=y[:48],lag_covariances=autocov(y,L),omega_rad_sample=w,
                true_spectrum=true,estimated_spectrum=estimate,uniform_radius=e,cell_variation=v,
                certified_density=lower,raw_cycle=cycle,cycle_error=cycle_error,
                certified_rate=rate,alpha=alpha,N=N,b=b,L=L,B=bound,T_L=0.,seed=713420,rep=0)


def cert_tables(f):
    cert=f.archive_csv(2,"certificate_summary.csv")
    reps=f.archive_csv(2,"certificate_replicates.csv")
    groups=["model","max_delay","N"]
    counts=reps.groupby(groups).rejects.agg(["size","sum"]).reset_index()
    check=cert.merge(counts,on=groups,validate="one_to_one")
    assert len(reps)==7680 and len(check)==len(cert)==60
    assert check.n.eq(128).all() and check.rejections.eq(check["sum"]).all()
    assert check["size"].eq(check.n).all() and np.allclose(cert.rejection_rate,cert.rejections/cert.n)
    return cert,reps


def power_heatmaps(p,cert):
    table=cert[cert.model.str.startswith("alternative_")].copy()
    assert len(table)==36
    for i,(model,g) in enumerate(table.groupby("model")):
        ax=p.ax(.104+i*.268,.25,.249,.47)
        mat=g.pivot(index="max_delay",columns="N",values="rejections")
        image=ax.pcolormesh(np.arange(5)-.5,np.arange(4)-.5,mat.to_numpy()/128,
                            vmin=0,vmax=1,cmap="Greens",shading="flat")
        for (row,col),k in np.ndenumerate(mat.to_numpy()):
            tag(ax,col,row,str(k),color="white" if k>66 else INK,size=7.5)
        ax.set_title(rf"$b={float(model.split('_')[-1]):g}$",pad=3)
        ax.set_xticks(range(4),[f"$2^{{{int(np.log2(n))}}}$" for n in mat.columns],size=6.5)
        ax.set_yticks(range(3),mat.index if i==0 else [""]*3)
        ax.tick_params(length=0,pad=2)
        ax.set_xticks(np.arange(3)+.5,minor=True)
        ax.set_yticks(np.arange(2)+.5,minor=True)
        ax.grid(which="minor",color="white",lw=.6)
        ax.tick_params(which="minor",length=0)
        if i==0:
            ax.set_ylabel("Max. delay (samples)",labelpad=1)
    cax=p.ax(.914,.25,.023,.47)
    bar=p.figure.colorbar(image,cax=cax,ticks=[0,1])
    bar.ax.tick_params(labelsize=6.5,length=2,pad=2)
    bar.solids.set_label("colorbar-solids")
    note=p.ax(.11,.02,.80,.13,diagram=True)
    tag(note,.5,.73,r"Record length $N$ (samples)")
    tag(note,.5,.15,"Positive certificates out of 128",color=LATENT,size=7)
    return table


def rate_data(f):
    rates=f.archive_csv(2,"continuous_rate_replicates.csv")
    stats=f.archive_csv(2,"continuous_rate_summary.csv")
    assert len(rates)==384 and len(stats)==6
    assert rates.groupby(["max_delay","N"]).rep.nunique().eq(64).all()
    pos=rates.assign(positive=rates.rate_lower>0).groupby(["max_delay","N"]).positive.sum()
    assert np.array_equal(pos.to_numpy(),stats.positive) and (rates.rate_lower>=0).all()
    rates["log2_jitter"]=f.rng.uniform(-.075,.075,len(rates))
    return rates,stats


def rate_points(ax,rates):
    for i,(delay,group) in enumerate(rates.groupby("max_delay")):
        for j,(n,g) in enumerate(group.groupby("N")):
            x=np.log2(n)+[-.14,.14][i]
            vals=g.rate_lower.to_numpy()*1e3
            ax.scatter(x+g.log2_jitter,vals,s=11,marker=["o","s"][i],alpha=.35,
                       facecolors=[GREEN,"white"][i],edgecolors=GREEN,lw=.65,
                       label=f"{delay} samples" if j==0 else None,zorder=3)
            lo,med,hi=np.quantile(vals,[.025,.5,.975])
            ax.errorbar(x,med,yerr=[[med-lo],[hi-med]],color=INK,marker="_",
                        ms=9,mew=1.3,elinewidth=1,capsize=2,zorder=5)
    ax.axhline(0,color=GRAY,ls="--",lw=.8)
    ax.set(xticks=[15,17,19],xticklabels=[r"$2^{15}$",r"$2^{17}$",r"$2^{19}$"],
           xlim=(14.55,19.45),ylim=(-.27,9.15),xlabel=r"Record length $N$ (samples)",
           ylabel="Rate bound\n"+r"($10^{-3}$ nats/sample)")
    ax.legend(frameon=False,loc="upper left",title="Max. delay")


def fig5(root,out):
    f=Build(root,out,"Fig5",11.7,[(0,.56,1,.44),(0,0,.55,.51),(.58,0,.42,.51)],
            ["From one record to a certified lower sum","Fixed-grid detection",
             "Continuous-frequency rate"])
    a,b,c=f.panels
    ex=calibration_example(f)
    f.npz("A",**ex)
    omega=ex["omega_rad_sample"]/np.pi
    use=omega<1
    flow=a.ax(.02,.09,.96,.71,diagram=True)
    stages=["Record","Lag covariance","Spectral envelope","Cycle margin","Lower sum"]
    for i,stage in enumerate(stages):
        x=.038+i*.198
        ax=a.ax(x,.31,.139,.34)
        ax.set(xticks=[],yticks=[])
        ax.spines["left"].set_visible(False)
        if i==0:
            ax.plot(ex["record_excerpt"][:,0],color=TARGET,lw=.9)
        elif i==1:
            ax.axhline(0,color=GRAY,lw=.6)
            vals=ex["lag_covariances"][:,0,1]
            ax.scatter([0,1],vals,s=15,color=TARGET)
            ax.vlines([0,1],0,vals,color=TARGET,lw=1)
        elif i==2:
            y=ex["estimated_spectrum"][use,0,1].imag
            e=ex["uniform_radius"]
            ax.fill_between(omega[use],y-e,y+e,color=GREEN,alpha=.23)
            ax.plot(omega[use],y,color=TARGET,lw=.9)
        elif i==3:
            v,e=abs(ex["raw_cycle"][use]),ex["cycle_error"][use]
            ax.fill_between(omega[use],0,np.maximum(0,v-e),color=GREEN,alpha=.30)
            ax.plot(omega[use],v,color=TARGET,lw=.9)
            ax.plot(omega[use],e,color=GREEN,ls="--",lw=.9)
        else:
            v=ex["certified_density"][use]
            ax.fill_between(omega[use],0,v,step="mid",color=GREEN,alpha=.30)
            ax.step(omega[use],v,where="mid",color=GREEN,lw=.9)
        tag(flow,(x+.07-.02)/.96,.23,stage,color=TARGET if i<2 else GREEN)
        if i<4:
            x1=(x+.147-.02)/.96
            arrow(flow,(x1,.61),(x1+.047,.61),LATENT,lw=.9)
    flow.plot([.43,.96],[.115,.115],color=GREEN,lw=.9)
    tag(flow,.69,.015,r"External $B=1.9$, $T_L=0$; $\alpha=0.05$",color=GREEN)
    cert,_=cert_tables(f)
    f.csv("B",power_heatmaps(b,cert))
    rates,stats=rate_data(f)
    f.csv("C",rates)
    f.csv("C",stats,"_summary")
    rate_points(c.ax(.25,.17,.71,.67),rates)
    f.finish(r"""
**Figure 5. External calibration gives conditional lower confidence bounds in Model A.**
(a) The first archived delay-zero Gaussian MA(1) trajectory at its longest prefix
(\(N=524{,}288\), \(b=0.9\)). The stages show the first 48 samples of channel 1,
two estimated cross-covariance lags, the imaginary cross-spectrum with the
uniform radius, the positive imaginary-cycle margin, and the frequency-cell
density lower sum. The generating model supplies \(B=1.9\) and \(T_L=0\), with
\(\alpha=0.05\). (b) Positive fixed-grid certificates out of 128 trajectories per
cell. Within each signal-strength and delay combination, the four record
lengths are nested prefixes. (c) All 384 continuous-frequency bounds for
\(b=0.9\), including zeros. There are 64 independent long trajectories per
delay group and 128 in total. The three lengths within each group are nested
prefixes. Dark marks give the median and central 95% empirical quantiles.
""")


# Header labels from S001R01, with trailing periods removed. SHA-256
# 4743b736131a7e147c150e8b37711029b6cda5e356c4b3e8261a03cdcaaf8b0c.
EEG_LABELS = """Fc5 Fc3 Fc1 Fcz Fc2 Fc4 Fc6 C5 C3 C1 Cz C2 C4 C6 Cp5 Cp3 Cp1 Cpz Cp2 Cp4 Cp6
Fp1 Fpz Fp2 Af7 Af3 Afz Af4 Af8 F7 F5 F3 F1 Fz F2 F4 F6 F8 Ft7 Ft8 T7 T8 T9 T10 Tp7 Tp8
P7 P5 P3 P1 Pz P2 P4 P6 P8 Po7 Po3 Poz Po4 Po8 O1 Oz O2 Iz""".split()


def montage_data(f):
    import mne
    tree=ast.parse((f.r1/"src/eeg_study.py").read_text(encoding="utf-8"))
    decl=next(s for s in tree.body if isinstance(s,ast.Assign) and
              any(isinstance(t,ast.Name) and t.id=="CHANNELS" for t in s.targets))
    selected=ast.literal_eval(decl.value)
    positions=mne.channels.make_standard_montage("standard_1005").get_positions()["ch_pos"]
    labels={k.upper():k for k in positions}
    coords=np.array([positions[labels[ch.upper()]] for ch in EEG_LABELS])
    shifted=coords-np.array([0.,-.018,.003])
    rho=np.linalg.norm(shifted[:,:2],axis=1)
    xy=shifted[:,:2]/rho[:,None]*np.arctan2(rho,shifted[:,2])[:,None]
    xy*=.93/np.linalg.norm(xy,axis=1).max()
    chosen=np.array([ch.upper() in selected for ch in EEG_LABELS])
    assert len(EEG_LABELS)==len(set(EEG_LABELS))==64 and chosen.sum()==12
    return pd.DataFrame(dict(channel=[labels[ch.upper()] for ch in EEG_LABELS],
        selected=chosen,x_2d=xy[:,0],y_2d=xy[:,1],x_m=coords[:,0],y_m=coords[:,1],z_m=coords[:,2]))


def eeg_data(f):
    long=f.archive_csv(2,"eeg_complete_window_records.csv")
    assert len(long)==226 and long.subject.nunique()==71 and long.subject.min()>10
    assert long[["n_epochs_a","n_epochs_b"]].eq(12).all().all()
    assert np.allclose(long.q,long.amplitude_factor*long.alignment,rtol=1e-9,atol=2e-16)
    pairs=long.pivot(index=["subject","run"],columns="reference",values="q").reset_index()
    assert not pairs.isna().any().any() and len(pairs)==113
    assert pairs.groupby("run").subject.nunique().to_dict()=={1:52,2:61}
    pairs["average_minus_original"]=pairs.average-pairs.original
    wide=long.pivot(index="subject",columns=["reference","run"],values="q").dropna()
    condition=pd.DataFrame({r:wide[r][2]-wide[r][1] for r in ["original","average"]}).reset_index()
    assert len(condition)==42
    refs=f.archive_csv(2,"eeg_reference_paired.csv")
    conditions=f.archive_csv(2,"eeg_condition_paired.csv")
    for table in (refs,conditions):
        table["bootstrap_seed"]=743109
        table["bootstrap_draws"]=20000
    rng=np.random.default_rng(743109)
    def ci(values):
        values=np.asarray(values)
        return np.quantile(values[rng.integers(0,len(values),(20000,len(values)))].mean(axis=1),[.025,.975])
    for _,group in long.groupby(["run","reference"]):
        ci(group.q)
    for run,g in pairs.groupby("run"):
        row=refs[refs.run==run].iloc[0]
        assert np.isclose(row.mean_difference_average_minus_original,g.average_minus_original.mean())
        assert np.isclose(row.ratio_of_group_means,g.average.mean()/g.original.mean())
        assert np.allclose(ci(g.average_minus_original),row[["CI_low","CI_high"]].astype(float),atol=2e-16)
    for _,row in conditions.iterrows():
        v=condition[row.reference]
        assert np.isclose(row.mean_EC_minus_EO,v.mean(),atol=2e-16)
        assert np.allclose(ci(v),row[["CI_low","CI_high"]].astype(float),atol=2e-16)
    return long,pairs,condition,refs,conditions


def condition_plot(ax,condition,summary):
    values=condition[["original","average"]].to_numpy()*1e4
    for pair in values:
        ax.plot([0,1],pair,color=LATENT,alpha=.33,lw=.6,zorder=1)
    ax.scatter(np.broadcast_to([0,1],values.shape),values,color=LATENT,alpha=.55,s=10,zorder=2)
    for i,(ref,col) in enumerate([("original",TARGET),("average",B)]):
        row=summary[summary.reference==ref].iloc[0]
        m=row.mean_EC_minus_EO
        ax.errorbar(i+.10,m*1e4,yerr=[[1e4*(m-row.CI_low)],[1e4*(row.CI_high-m)]],
                    color=col,marker="D",ms=4.2,capsize=3,lw=1.2,zorder=5)
    ax.axhline(0,color=GRAY,ls="--",lw=.85)
    ax.set(xticks=[0,1],xticklabels=["Original","64-ch average"],xlim=(-.30,1.35),
           ylabel=r"Closed $-$ open $Q$ ($10^{-4}$)")
    ax.text(.47,.99,r"$n=42$ paired people",ha="center",va="top",
            transform=ax.transAxes,color=LATENT,size=7)


def fig6(root,out):
    f=Build(root,out,"Fig6",13.0,[(0,.50,.49,.50),(.51,.50,.49,.50),(0,0,.54,.46),(.58,0,.42,.46)],
            ["Same windows, two references","Reference changes the observed score",
             "Within-record reference differences","Within-person eye condition"])
    a,b,c,d=f.panels
    montage=montage_data(f)
    f.csv("A",montage)
    win=pd.DataFrame(dict(half=np.repeat(["A","B"],12),start_s=np.r_[np.arange(2,26,2),np.arange(34,58,2)]))
    win["stop_s"]=win.start_s+2
    f.csv("A",win,"_windows")
    ax=a.ax(.03,.21,.47,.61)
    ax.add_patch(Circle((0,0),1,fill=False,ec=INK,lw=1))
    ax.plot([-.11,0,.11],[.992,1.14,.992],color=INK,lw=1)
    for sign in [-1,1]:
        theta=np.linspace(-np.pi/2,np.pi/2,30)
        ax.plot(sign*(.996+.084*np.cos(theta)),.19*np.sin(theta),color=INK,lw=.9)
    bg,fg=montage[~montage.selected],montage[montage.selected]
    ax.scatter(bg.x_2d,bg.y_2d,s=8,color=GRAY)
    ax.scatter(fg.x_2d,fg.y_2d,s=18,color=TARGET)
    for row in fg.itertuples():
        shift={"O1":-4,"O2":4}.get(row.channel,0)
        ax.annotate(row.channel,(row.x_2d,row.y_2d),xytext=(shift,5),textcoords="offset points",
                    ha="center",size=6.5,color=TARGET)
    ax.set(xlim=(-1.13,1.13),ylim=(-1.04,1.17),aspect="equal")
    ax.set_axis_off()
    flow=a.ax(.44,.22,.54,.55,diagram=True)
    tag(flow,.46,.92,"64 acquired channels",color=LATENT)
    for y,label,col in ((.62,"Original reference",A),(.30,"64-channel average",B)):
        arrow(flow,(.45,.85),(.30,y+.07),col,curve=.13 if y>.4 else -.16)
        tag(flow,.42,y,label,color=col)
        arrow(flow,(.84,y),(.97,.45),col,lw=.85)
    arrow(flow,(.97,.42),(.80,.14),TARGET,curve=-.25,lw=.85)
    tag(flow,.57,.055,"Score the same 12 channels",color=TARGET,size=7)
    track=a.ax(.12,.103,.80,.084)
    for row in win.itertuples():
        track.add_patch(Rectangle((row.start_s,.16),2,.60,ec="white",fc=A if row.half=="A" else B,lw=.4))
    track.set(xlim=(0,60),ylim=(0,1),xticks=[0,26,34,60],yticks=[],xlabel="Accepted window times (s)")
    track.tick_params(length=2,pad=1)
    track.spines["left"].set_visible(False)

    _,pairs,condition,ref_summary,cond_summary=eeg_data(f)
    f.csv("B",pairs)
    f.csv("B",ref_summary,"_summary")
    ax=b.ax(.17,.20,.57,.60)
    limits=[pairs[["original","average"]].min().min()*1e4-.35,
            pairs[["original","average"]].max().max()*1e4+.45]
    ax.plot(limits,limits,color=GRAY,ls="--",lw=.85)
    for run,(col,m) in enumerate([(EO,"o"),(EC,"^")],1):
        g=pairs[pairs.run==run]
        ax.scatter(g.original*1e4,g.average*1e4,s=19,color=col,marker=m,alpha=.72,lw=.45,edgecolor="white")
    ax.set(xlim=limits,ylim=limits,aspect="equal",
           xlabel=r"Original $Q$ ($10^{-4}$)",ylabel=r"Average-ref. $Q$ ($10^{-4}$)")
    stats=b.ax(.71,.24,.29,.56,diagram=True)
    tag(stats,.5,.84,"Ratios of\ncondition means",color=LATENT,size=7)
    for i,(label,col,marker) in enumerate([("Eyes open",EO,"o"),("Eyes closed",EC,"^")]):
        stats.scatter(.07,.59-i*.32,s=14,color=col,marker=marker)
        tag(stats,.56,.59-i*.32,label,color=col,size=7)
        tag(stats,.54,.44-i*.32,f"{ref_summary.ratio_of_group_means.iloc[i]:.2f}×",color=col,weight="bold")

    f.csv("C",pairs)
    f.csv("C",ref_summary,"_summary")
    ax=c.ax(.19,.22,.76,.59)
    for i,(run,col) in enumerate([(1,EO),(2,EC)]):
        v=pairs[pairs.run==run].average_minus_original.to_numpy()*1e4
        xs=np.linspace(v.min(),v.max(),160)
        density=gaussian_kde(v)(xs)
        ax.fill_between(xs,i,i+.32*density/density.max(),color=col,alpha=.20)
        ax.scatter(v,i-f.rng.uniform(.025,.16,len(v)),s=12,color=col,alpha=.62,lw=0)
        row=ref_summary[ref_summary.run==run].iloc[0]
        mean=row.mean_difference_average_minus_original*1e4
        ax.errorbar(mean,i+.34,xerr=[[mean-row.CI_low*1e4],[row.CI_high*1e4-mean]],
                    marker="D",ms=4.3,color=col,capsize=3,lw=1.2)
    ax.axvline(0,color=GRAY,ls="--",lw=.9)
    ax.set(yticks=[0,1],yticklabels=["Open · 52","Closed · 61"],ylim=(-.25,1.51),
           xlabel=r"Average $-$ original $Q$ ($10^{-4}$)")
    f.csv("D",condition)
    f.csv("D",cond_summary,"_summary")
    condition_plot(d.ax(.22,.22,.74,.59),condition,cond_summary)
    f.finish(r"""
**Figure 6. EEG closure depends on the reference of the same recorded windows.**
(a) The 12 scored channels are highlighted within the 64 acquired channels.
Positions are a 2D projection of MNE's standard 10–05 montage for labels
verified against the [PhysioNet EEGMMIDB EDF header](https://doi.org/10.13026/C28G6P).
The common-average reference uses all 64 channels. Both scores use the same
12+12 accepted 2-s windows. (b) Scores for each of 113 matched records from
71 people (52 eyes open, 61 eyes closed). The dashed line is equality. The
ratios 5.16 and 2.63 use the condition-specific group means.
(c) Dots are matched records. Diamonds show mean within-record changes and
95% participant bootstrap intervals. Each person contributes at most one
record per condition. (d) Within-person closed-minus-open differences for
42 people under both references. Means and 95% participant bootstrap intervals
are shown. The means are \(1.3288\times10^{-4}\) (original) and
\(1.2634\times10^{-4}\) (average). This comparison is exploratory, with condition
associated with baseline run order.
""")
