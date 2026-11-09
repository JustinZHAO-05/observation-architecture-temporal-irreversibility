"""Prespecified EEGMMIDB baseline analysis. Public data, no trained model."""
from __future__ import annotations
import argparse
import concurrent.futures
import json
from pathlib import Path
import shutil
import time
import urllib.request
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats, signal

from closure_core import (read_edf,periodogram_replicates,split_cycle_statistic,
                         bootstrap_mean_ci,sign_flip_test)

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'eegmmidb'
OUT=ROOT/'results'
CHANNELS=['F3','F4','FZ','C3','C4','CZ','P3','P4','PZ','O1','O2','OZ']


def fetch_one(subject,run):
    name=f'S{subject:03d}R{run:02d}.edf'
    target=DATA/f'S{subject:03d}'/name
    if target.exists():
        return subject,run,str(target),'cached'
    target.parent.mkdir(parents=True,exist_ok=True)
    pilot=ROOT/'data'/'pilot'/name
    if pilot.exists():
        shutil.copy2(pilot,target)
        return subject,run,str(target),'pilot_copy'
    url=f'https://physionet.org/files/eegmmidb/1.0.0/S{subject:03d}/{name}'
    for attempt in range(3):
        try:
            data=urllib.request.urlopen(url,timeout=40).read()
            if data[:8].strip()!=b'0':
                raise ValueError('Response is not EDF')
            tmp=target.with_suffix('.part');tmp.write_bytes(data);tmp.replace(target)
            return subject,run,str(target),'downloaded'
        except Exception as error:
            message=f'{type(error).__name__}: {error}'
    return subject,run,str(target),message


def load_selected(path,reference='original'):
    arrays,rates,labels,meta=read_edf(path)
    ids=[labels.index(c) for c in CHANNELS]
    if len(set(rates[ids]))!=1:
        raise ValueError('Selected channels have different sample rates')
    if any(meta['units'][i] not in ['uV','µV'] for i in ids):
        raise ValueError('Unexpected amplitude units')
    x=np.column_stack([arrays[i] for i in ids]);fs=float(rates[ids[0]])
    if reference=='average':
        eeg=[i for i in range(len(labels)) if meta['units'][i] in ['uV','µV']]
        average=np.column_stack([arrays[i] for i in eeg]).mean(axis=1)
        x=x-average[:,None]
    return x,fs,meta


def analyze_record(path,subject,run,mode='primary',reference='original',filter_seed=None):
    x,fs,meta=load_selected(path,reference)
    row=dict(subject=subject,run=run,mode=mode,reference=reference,
             cohort='pilot' if subject<=10 else 'holdout',
             duration=meta['duration'],fs=fs,status='ok')
    if meta['duration']<58:
        row['status']='too_short';return row,None
    if fs!=160:
        row['status']='unexpected_sample_rate';return row,None
    if filter_seed is not None:
        rng=np.random.default_rng(filter_seed)
        for i in range(x.shape[1]):
            tau=rng.uniform(.004,.025);pole=np.exp(-1/(fs*tau))
            d=int(rng.integers(0,5))
            v=signal.lfilter([1-pole],[1,-pole],x[:,i])
            # Deterministic causal zero padding, with 2s burn-in before analysis.
            x[:,i]=np.r_[np.zeros(d),v[:len(v)-d]] if d else v
    if mode=='primary':
        length=2;starts_a=list(range(2,26,2));starts_b=list(range(34,58,2));min_epochs=8
    elif mode=='four_seconds':
        length=4;starts_a=list(range(2,26,4));starts_b=list(range(34,58,4));min_epochs=4
    elif mode=='alternating':
        length=2;starts=list(range(2,58,2));starts_a=starts[::2];starts_b=starts[1::2];min_epochs=8
    else:
        raise ValueError(mode)
    zz=[]
    for suffix,starts in [('a',starts_a),('b',starts_b)]:
        epochs=np.stack([x[int(s*fs):int((s+length)*fs)] for s in starts])
        good=np.isfinite(epochs).all(axis=(1,2))
        good &= (np.ptp(epochs,axis=1)<=500).all(axis=1)
        good &= (epochs.std(axis=1)>=.1).all(axis=1)
        row[f'n_epochs_{suffix}']=int(good.sum())
        row[f'rejected_epochs_{suffix}']=int((~good).sum())
        if good.sum()<min_epochs:
            row['status']='insufficient_clean_epochs';return row,None
        f,z=periodogram_replicates(epochs[good],fs);zz.append(z)
    q,va,vb=split_cycle_statistic(zz[0],zz[1])
    keep=(f>=2)&(f<=30)
    row['q']=float(q[keep].mean())
    row['naive_square']=float(.5*(np.mean(va[keep]**2)+np.mean(vb[keep]**2)))
    row['closure_similarity']=float(np.sum(va[keep]*vb[keep])/
        np.sqrt(np.sum(va[keep]**2)*np.sum(vb[keep]**2)))
    # Fixed bands are descriptive, not additional confirmatory tests.
    for label,low,high in [('delta',2,4),('theta',4,8),('alpha',8,13),('beta',13,30)]:
        k=(f>=low)&(f<high)
        row[f'q_{label}']=float(q[k].mean())
    extras={'f':f[keep],'va':va[keep].astype('float32'),'vb':vb[keep].astype('float32')}
    return row,extras


def summarize(df,seed=73491):
    rng=np.random.default_rng(seed);summ=[]
    for (cohort,run),g in df[df.status=='ok'].groupby(['cohort','run']):
        q=g.q.to_numpy();ci=bootstrap_mean_ci(q,rng)
        p=sign_flip_test(q,rng,49999)
        summ.append(dict(cohort=cohort,run=int(run),n=len(q),mean=float(q.mean()),
            median=float(np.median(q)),sd=float(q.std(ddof=1)),positive=int(np.sum(q>0)),
            ci_low=float(ci[0]),ci_high=float(ci[1]),sign_flip_p=p,
            t_p=float(stats.ttest_1samp(q,0,alternative='greater').pvalue),
            standardized_mean=float(q.mean()/q.std(ddof=1))))
    res=pd.DataFrame(summ)
    res['holm_p']=np.nan
    for cohort in res.cohort.unique():
        ii=res.index[res.cohort==cohort].to_numpy()
        order=ii[np.argsort(res.loc[ii,'sign_flip_p'].to_numpy())]
        running=0.
        for rank,idx in enumerate(order):
            running=max(running,min(1.,(len(order)-rank)*res.loc[idx,'sign_flip_p']))
            res.loc[idx,'holm_p']=running
    paired=[]
    for cohort,g in df[df.status=='ok'].groupby('cohort'):
        pivot=g.pivot(index='subject',columns='run',values='q').dropna()
        if 1 not in pivot or 2 not in pivot:continue
        d=(pivot[2]-pivot[1]).to_numpy();ci=bootstrap_mean_ci(d,rng)
        paired.append(dict(cohort=cohort,n=len(d),mean_difference=float(d.mean()),
            ci_low=float(ci[0]),ci_high=float(ci[1]),
            p=sign_flip_test(d,rng,49999,alternative='two-sided'),
            status='exploratory_condition_difference'))
    return res,pd.DataFrame(paired)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--subjects',default='1-109')
    ap.add_argument('--mode',default='primary',choices=['primary','four_seconds','alternating'])
    ap.add_argument('--reference',default='original',choices=['original','average'])
    ap.add_argument('--causal-filters',action='store_true')
    ap.add_argument('--download-only',action='store_true')
    args=ap.parse_args()
    lo,hi=map(int,args.subjects.split('-'));subjects=range(lo,hi+1)
    suffix=f'{args.mode}_{args.reference}' + ('_filtered' if args.causal_filters else '')
    if lo==1 and hi==10:suffix+='_pilot'
    started=datetime.now(timezone.utc).isoformat();start=time.perf_counter()
    items=[(s,r) for s in subjects for r in [1,2]]
    download=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(fetch_one,*item) for item in items]
        for i,fut in enumerate(concurrent.futures.as_completed(futures)):
            item=fut.result();download.append(item)
            if (i+1)%20==0:print('downloads',i+1,'/',len(items),flush=True)
    pd.DataFrame(download,columns=['subject','run','path','download_status']).sort_values(
        ['subject','run']).to_csv(OUT/f'download_{suffix}.csv',index=False)
    if args.download_only:return
    rows=[];extra={};frequencies=None
    for i,(s,r,p,status) in enumerate(sorted(download)):
        if not Path(p).exists():
            rows.append(dict(subject=s,run=r,status='download_failed'));continue
        try:
            row,ex=analyze_record(p,s,r,args.mode,args.reference,
                                 s*10+r if args.causal_filters else None)
        except Exception as error:
            row=dict(subject=s,run=r,status=f'{type(error).__name__}: {error}')
            ex=None
        rows.append(row)
        if ex is not None:
            extra[f'S{s:03d}R{r:02d}_a']=ex['va'];extra[f'S{s:03d}R{r:02d}_b']=ex['vb'];frequencies=ex['f']
        if (i+1)%20==0:print('analyzed',i+1,'/',len(items),flush=True)
    df=pd.DataFrame(rows)
    df.to_csv(OUT/f'eeg_{suffix}_subjects.csv',index=False)
    if frequencies is not None:np.savez_compressed(OUT/f'eeg_{suffix}_cycles.npz',f=frequencies,**extra)
    res,pair=summarize(df)
    res.to_csv(OUT/f'eeg_{suffix}_summary.csv',index=False)
    pair.to_csv(OUT/f'eeg_{suffix}_paired.csv',index=False)
    metadata=dict(started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),
        wall_seconds=time.perf_counter()-start,arguments=vars(args),n_records=len(df),
        status_counts=df.status.value_counts().to_dict())
    (OUT/f'eeg_{suffix}_run.json').write_text(json.dumps(metadata,indent=2))
    print(res.to_string(index=False),flush=True)
    print(pair.to_string(index=False),flush=True)
    print(metadata,flush=True)


if __name__=='__main__':main()
