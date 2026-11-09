"""Follow-up analysis of archived first-round EEG spectra-derived arrays.
No re-download or raw-EDF claim. Complete-window intersection removes mask changes.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'inputs/round1_results'
OUT=ROOT/'results'
rng=np.random.default_rng(743109)

def ci(x,draws=20000):
 x=np.asarray(x);v=x[rng.integers(0,len(x),(draws,len(x)))].mean(axis=1)
 return list(map(float,np.quantile(v,[.025,.975])))

def main():
 refs=['original','average'];tables={r:pd.read_csv(OLD/f'eeg_primary_{r}_subjects.csv') for r in refs}
 keys=[]
 for r in refs:
  d=tables[r]; keys.append(set(map(tuple,d[(d.status=='ok')&(d.n_epochs_a==12)&(d.n_epochs_b==12)&(d.subject>10)][['subject','run']].to_numpy())))
 selected=sorted(set.intersection(*keys));rows=[];archive={};maxerr=0
 for ref in refs:
  path=OLD/f'eeg_primary_{ref}_cycles.npz';z=np.load(path);freq=z['f'];archive[ref]=hashlib.sha256(path.read_bytes()).hexdigest()
  table=tables[ref].set_index(['subject','run'])
  for subject,run in selected:
   key=f'S{subject:03d}R{run:02d}';a=z[key+'_a'].astype(float);b=z[key+'_b'].astype(float)
   q=float(np.mean(a*b));rmsa=np.sqrt(np.mean(a*a));rmsb=np.sqrt(np.mean(b*b));amp=rmsa*rmsb;alignment=q/amp
   maxerr=max(maxerr,abs(q-float(table.loc[(subject,run),'q'])))
   alpha=(freq>=8)&(freq<13)
   rows.append(dict(subject=subject,run=run,reference=ref,q=q,amplitude_factor=amp,alignment=alignment,
     q_alpha=float(np.mean((a*b)[alpha])),alpha_contribution_to_full_Q=float(np.sum((a*b)[alpha])/a.size),
     n_epochs_a=12,n_epochs_b=12))
 df=pd.DataFrame(rows);df.to_csv(OUT/'eeg_complete_window_records.csv',index=False)
 group=[];paired=[]
 for (run,ref),g in df.groupby(['run','reference']):
  lo,hi=ci(g.q.to_numpy());group.append(dict(run=run,reference=ref,n=len(g),mean_Q=g.q.mean(),median_Q=g.q.median(),CI_low=lo,CI_high=hi,
   mean_amplitude=g.amplitude_factor.mean(),mean_alignment=g.alignment.mean(),positive=int((g.q>0).sum())))
 for run,g in df.groupby('run'):
  p=g.pivot(index='subject',columns='reference',values='q');delta=p.average-p.original;lo,hi=ci(delta)
  paired.append(dict(run=run,n=len(delta),mean_difference_average_minus_original=delta.mean(),CI_low=lo,CI_high=hi,
      ratio_of_group_means=p.average.mean()/p.original.mean(),pearson_r=stats.pearsonr(p.average,p.original).statistic,
      t_paired_p=stats.ttest_rel(p.average,p.original).pvalue))
 pd.DataFrame(group).to_csv(OUT/'eeg_reference_summary.csv',index=False)
 pd.DataFrame(paired).to_csv(OUT/'eeg_reference_paired.csv',index=False)
 cond=[]
 for ref,g in df.groupby('reference'):
  pivot=g.pivot(index='subject',columns='run',values='q').dropna();diff=pivot[2]-pivot[1];lo,hi=ci(diff)
  cond.append(dict(reference=ref,n=len(pivot),mean_EC_minus_EO=diff.mean(),CI_low=lo,CI_high=hi,
      paired_t_p=stats.ttest_rel(pivot[2],pivot[1]).pvalue))
 pd.DataFrame(cond).to_csv(OUT/'eeg_condition_paired.csv',index=False)
 summary=dict(matched_complete_window_records=len(selected),matched_subjects=len(set(s for s,r in selected)),
   original_EO_records=int(sum(r==1 for s,r in selected)),original_EC_records=int(sum(r==2 for s,r in selected)),
   max_float32_archive_score_difference=maxerr,archive_sha256=archive,
   scope='Exploratory post-holdout analysis of archived imaginary-cycle arrays; same 12+12 windows under both references; no raw EDF recomputation.')
 (OUT/'eeg_followup_provenance.json').write_text(json.dumps(summary,indent=2))
 print(pd.DataFrame(group).to_string(index=False));print(pd.DataFrame(paired).to_string(index=False));print(pd.DataFrame(cond).to_string(index=False));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
