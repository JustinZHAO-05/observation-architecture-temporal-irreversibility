"""Filter robustness holding the original QC epochs and participants fixed."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import signal,stats
from closure_core import periodogram_replicates,split_cycle_statistic
from eeg_study import ROOT,DATA,OUT,load_selected

rng=np.random.default_rng(90273)
primary=pd.read_csv(OUT/'eeg_primary_original_subjects.csv')
rows=[]
starts=list(range(2,26,2))+list(range(34,58,2))
for _,record in primary[(primary.status=='ok')&(primary.cohort=='holdout')].iterrows():
    s,r=int(record.subject),int(record.run)
    path=DATA/f'S{s:03d}'/f'S{s:03d}R{r:02d}.edf'
    x,fs,_=load_selected(path)
    ep=np.stack([x[int(t*fs):int((t+2)*fs)] for t in starts])
    good=np.isfinite(ep).all(axis=(1,2))&(np.ptp(ep,axis=1)<=500).all(axis=1)&(ep.std(axis=1)>=.1).all(axis=1)
    f,za=periodogram_replicates(ep[:12][good[:12]],fs)
    _,zb=periodogram_replicates(ep[12:][good[12:]],fs)
    keep=(f>=2)&(f<=30)
    q,va,vb=split_cycle_statistic(za,zb)
    # Exact Fourier-domain transformation is an implementation/algebra check.
    gain=np.exp(rng.uniform(-2,2,(len(f),12)))
    phase=rng.uniform(-np.pi,np.pi,(len(f),12))
    h=gain*np.exp(1j*phase)
    qf,vaf,vbf=split_cycle_statistic(za*h[None,:,:],zb*h[None,:,:])
    exact_error=max(float(abs(vaf-va).max()),float(abs(vbf-vb).max()))
    # Physical causal filtering before fixed segmentation tests approximation.
    rf=np.random.default_rng(s*10+r)
    y=np.empty_like(x)
    for i in range(x.shape[1]):
        tau=rf.uniform(.004,.025);pole=np.exp(-1/(fs*tau));d=int(rf.integers(0,5))
        v=signal.lfilter([1-pole],[1,-pole],x[:,i])
        y[:,i]=np.r_[np.zeros(d),v[:len(v)-d]] if d else v
    ef=np.stack([y[int(t*fs):int((t+2)*fs)] for t in starts])
    _,zaf=periodogram_replicates(ef[:12][good[:12]],fs)
    _,zbf=periodogram_replicates(ef[12:][good[12:]],fs)
    qtime,vat,vbt=split_cycle_statistic(zaf,zbf)
    original=float(q[keep].mean());filtered=float(qtime[keep].mean())
    assert abs(original-float(record.q))<1e-12
    rows.append(dict(subject=s,run=r,q_original=original,q_filtered_fixed_mask=filtered,
        q_change=filtered-original,exact_fourier_cycle_error=exact_error,
        median_abs_cycle_change=float(np.median(np.r_[abs(vat[keep]-va[keep]).ravel(),abs(vbt[keep]-vb[keep]).ravel()])),
        relative_cycle_l2_change=float(np.sqrt((np.sum((vat[keep]-va[keep])**2)+np.sum((vbt[keep]-vb[keep])**2))/
           (np.sum(va[keep]**2)+np.sum(vb[keep]**2))))))
df=pd.DataFrame(rows);df.to_csv(OUT/'matched_filter_robustness.csv',index=False)
summary=[]
for run,g in df.groupby('run'):
    summary.append(dict(run=int(run),n=len(g),q_pearson=float(stats.pearsonr(g.q_original,g.q_filtered_fixed_mask).statistic),
       q_spearman=float(stats.spearmanr(g.q_original,g.q_filtered_fixed_mask).statistic),
       original_mean=float(g.q_original.mean()),filtered_mean=float(g.q_filtered_fixed_mask.mean()),
       relative_mean_change=float((g.q_filtered_fixed_mask.mean()-g.q_original.mean())/g.q_original.mean()),
       median_relative_cycle_l2_change=float(g.relative_cycle_l2_change.median()),
       max_exact_fourier_error=float(g.exact_fourier_cycle_error.max())))
(OUT/'matched_filter_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
