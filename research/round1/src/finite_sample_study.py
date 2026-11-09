"""Finite-sample calibration, power, and temporal-filter leakage probes."""
from pathlib import Path
import json
import time
import numpy as np
import pandas as pd
from scipy import signal, stats
from closure_core import (coherency, cycle_product, diagonal_congruence,
    periodogram_replicates, split_cycle_statistic, sign_flip_test)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'


def gaussian_half_scores(s, k, count, rng):
    n=s.shape[0]
    l=np.linalg.cholesky(s)
    out=[]
    for _ in range(2):
        z=(rng.normal(size=(count,k,n))+1j*rng.normal(size=(count,k,n)))/np.sqrt(2)
        z=z@l.T
        sh=np.einsum('rki,rkj->rij',z,z.conj())/k
        out.append(cycle_product(coherency(sh)).imag)
    return np.mean(out[0]*out[1],axis=-1)


def spectral_null_and_power(seed=51279):
    rng=np.random.default_rng(seed)
    rows=[]
    n_groups=300
    group_n=40
    count=n_groups*group_n
    for k in [6,12,24]:
        for coherence in [.2,.5,.8]:
            for phase in [0.,.25,.5]:
                # Equal edge magnitude, signed closure angle phase. Only retain
                # positive-definite spectra; report skipped invalid combinations.
                s=np.full((3,3),coherence,dtype=complex);np.fill_diagonal(s,1)
                s[2,0]*=np.exp(1j*phase);s[0,2]=s[2,0].conjugate()
                if np.linalg.eigvalsh(s).min()<=.005:
                    rows.append(dict(k=k,coherence=coherence,phase=phase,status='invalid_covariance'))
                    continue
                # Arbitrary phases mimic unknown individual-channel filters.
                h=np.exp(1j*rng.uniform(-np.pi,np.pi,3))
                s=diagonal_congruence(s,h)
                values=gaussian_half_scores(s,k,count,rng).reshape(n_groups,group_n)
                pvals=[]
                # 1,999 permutations per synthetic study gives a direct
                # Monte Carlo check of the proposed group sign-flip procedure.
                for value in values:
                    pvals.append(sign_flip_test(value,rng,n_perm=1999))
                rate=float(np.mean(np.asarray(pvals)<=.05))
                ci=stats.binomtest(int(round(rate*n_groups)),n_groups).proportion_ci()
                rows.append(dict(k=k,coherence=coherence,phase=phase,status='ok',
                    n_studies=n_groups,subjects_per_study=group_n,rejection_rate=rate,
                    rejection_ci_low=ci.low,rejection_ci_high=ci.high,
                    mean_score=float(values.mean()),score_sd=float(values.std()),
                    population_cycle_imag=float(cycle_product(s).imag[0])))
    df=pd.DataFrame(rows);df.to_csv(OUT/'finite_spectral_calibration.csv',index=False)
    return df


def time_domain_calibration(seed=87691, n_subjects=240):
    rng=np.random.default_rng(seed)
    fs=160; n=12; total=int(65*fs); burn=int(8*fs)
    starts=list(range(2,26,2))+list(range(34,58,2))
    rows=[]
    for regime,max_delay,max_tau in [('no_filter',0.,0.),
                                      ('mild',.025,.025),
                                      ('moderate',.125,.125),
                                      ('strong',.5,.5)]:
        for subject in range(n_subjects):
            frequencies=rng.uniform(3.,28.,n)
            damping=rng.uniform(.86,.98,n)
            eps=rng.normal(size=(total+burn,n))
            latent=np.empty_like(eps)
            for i in range(n):
                den=[1.,-2*damping[i]*np.cos(2*np.pi*frequencies[i]/fs),damping[i]**2]
                z=signal.lfilter([1.],den,eps[:,i])
                latent[:,i]=z/z[burn:].std()
            # Fixed real spatial mixing of independent scalar reversible modes.
            mix=rng.normal(size=(n,n))/np.sqrt(n)+.7*np.eye(n)
            x=latent@mix.T
            y=np.empty_like(x)
            for i in range(n):
                if max_tau:
                    tau=rng.uniform(.002,max_tau)
                    pole=np.exp(-1/(fs*tau))
                    v=signal.lfilter([1-pole],[1,-pole],x[:,i])
                    delay=int(round(rng.uniform(0,max_delay)*fs))
                    y[:,i]=np.roll(v,delay)
                else:
                    y[:,i]=x[:,i]
            y=y[burn:]
            epochs=np.stack([y[int(s*fs):int((s+2)*fs)] for s in starts])
            f,z=periodogram_replicates(epochs,fs)
            q,_,_=split_cycle_statistic(z[:12],z[12:])
            keep=(f>=2)&(f<=30)
            rows.append(dict(regime=regime,subject=subject,
                             score=float(q[keep].mean())))
        print('time-domain null',regime,flush=True)
    df=pd.DataFrame(rows);df.to_csv(OUT/'time_domain_filter_null.csv',index=False)
    summ=[]
    for regime,g in df.groupby('regime',sort=False):
        q=g.score.to_numpy();sem=stats.sem(q)
        summ.append(dict(regime=regime,n=len(q),mean=float(q.mean()),sd=float(q.std(ddof=1)),
            ci_low=float(q.mean()-1.96*sem),ci_high=float(q.mean()+1.96*sem),
            group_signflip_p=sign_flip_test(q,rng,9999),
            group_t_p=float(stats.ttest_1samp(q,0,alternative='greater').pvalue)))
    pd.DataFrame(summ).to_csv(OUT/'time_domain_filter_null_summary.csv',index=False)
    return summ


if __name__=='__main__':
    start=time.perf_counter()
    cal=spectral_null_and_power()
    print(cal.to_string(index=False),flush=True)
    td=time_domain_calibration()
    print(td,flush=True)
    (OUT/'finite_sample_summary.json').write_text(json.dumps({
        'wall_seconds':time.perf_counter()-start,'time_domain_null':td},indent=2))
