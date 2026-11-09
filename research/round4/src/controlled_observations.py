"""Known-transform tests on ONE real EEG record and covariance-tail misspecification.
Transform realizations are numerical controls, not independent biological observations.
"""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
from scipy.signal import lfilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
sys.path.insert(0,str(ROOT/'inputs/01_RESEARCH/ROUND1/neural_time_arrow_study/src'))
from closure_core import read_edf,periodogram_replicates,spectrum_from_replicates,coherency,cycle_product
from calibration_unknown_shape import calibrate
from finite_certificate import estimate,radius,certificate

def reversal(S):return np.array([.5*(np.trace(np.linalg.solve(s.T,s)).real-len(s)) for s in S])
def cycles(S):return cycle_product(coherency(S))
def eeg():
 f=ROOT/'inputs/03_FIGURE_PRODUCTION/redraw/Fig7/inputs/S011R01.edf'
 arr,rates,labels,meta=read_edf(f);names=['F3','F4','FZ','C3','C4','CZ','P3','P4','PZ','O1','O2','OZ']
 ids=[labels.index(c) for c in names];x=np.column_stack([arr[i] for i in ids]);fs=rates[ids[0]]
 starts=list(range(2,26,2))+list(range(34,58,2));epochs=np.stack([x[int(s*fs):int((s+2)*fs)] for s in starts])
 freq,z=periodogram_replicates(epochs,fs);keep=(freq>=2)&(freq<=30);z=z[:,keep];freq=freq[keep]
 S=spectrum_from_replicates(z);raw=reversal(S);C=cycles(S);rng=np.random.default_rng(2026110907);rows=[]
 for rep in range(80):
  delay=rng.integers(0,9,size=12);gain=np.exp(rng.uniform(-.7,.7,size=12));pole=rng.uniform(.1,.8,size=12)
  H=gain[None,:]*np.exp(-2j*np.pi*freq[:,None]/fs*delay[None,:])*(1-pole)[None,:]/(1-pole[None,:]*np.exp(-2j*np.pi*freq[:,None]/fs))
  Sh=H[:,:,None]*S*H[:,None,:].conj()
  rows.append(dict(transform='diagonal_frequency_response',rep=rep,max_cycle_change=float(np.max(abs(cycles(Sh)-C))),max_relative_raw_reversal_change=float(np.max(abs(reversal(Sh)-raw)/(1+abs(raw))))))
  Q,_=np.linalg.qr(rng.normal(size=(12,12)));So=np.einsum('ij,fjk,lk->fil',Q,S,Q)
  rows.append(dict(transform='orthogonal_spatial_rotation',rep=rep,max_cycle_change=float(np.max(abs(cycles(So)-C))),max_relative_raw_reversal_change=float(np.max(abs(reversal(So)-raw)/(1+abs(raw))))))
 eegids=[i for i in range(len(labels)) if meta['units'][i] in ['uV','µV']];common=np.column_stack([arr[i] for i in eegids]).mean(axis=1)
 xa=x-common[:,None];ep=np.stack([xa[int(s*fs):int((s+2)*fs)] for s in starts]);_,za=periodogram_replicates(ep,fs);Sa=spectrum_from_replicates(za[:,keep])
 rows.append(dict(transform='64_channel_average_reference',rep=0,max_cycle_change=float(np.max(abs(cycles(Sa)-C))),max_relative_raw_reversal_change=float(np.max(abs(reversal(Sa)-raw)/(1+abs(raw))))))
 pd.DataFrame(rows).to_csv(OUT/'eeg_known_transformations.csv',index=False);np.savez_compressed(OUT/'eeg_transform_source.npz',f=freq,S_original=S,S_average=Sa)
 return dict(record='S011R01',n_biological_records=1,windows=len(starts),channels=names,frequencies=len(freq),transform_realizations=len(rows),max_original_condition=float(np.linalg.cond(S).max()),diagonal_max_cycle_error=max(r['max_cycle_change'] for r in rows if r['transform']=='diagonal_frequency_response'),orthogonal_max_relative_raw_error=max(r['max_relative_raw_reversal_change'] for r in rows if r['transform']=='orthogonal_spatial_rotation'))

def stress():
 rng=np.random.default_rng(2026110908);cov=np.array([[1.,.65,.5],[.65,1.,.7],[.5,.7,1.]])
 ch=np.linalg.cholesky(cov);a=.8;delays=np.array([0,1,3]);m=65536;N=131072
 W=np.array([np.pi/6,np.pi/3,np.pi/2,2*np.pi/3,5*np.pi/6]);D=np.exp(-1j*W[:,None]*delays)
 S0=cov[None,:,:]*((1-a*a)/(1-2*a*np.cos(W)+a*a))[:,None,None];Strue=D[:,:,None]*S0*D[:,None,:].conj()
 def gen(n):
  z=rng.standard_normal((n+3+256,3))@ch.T;u=lfilter([np.sqrt(1-a*a)],[1.,-a],z,axis=0)[256:]
  return np.column_stack([u[3-d:3-d+n,j] for j,d in enumerate(delays)])
 rows=[]
 for rep in range(80):
  z=gen(m);y=gen(N)
  for name,L,tau in [('misspecified_finite_support',1,0.),('valid_tail_envelope',48,2*.8**(49-3)/(1-.8))]:
   U,den,_=calibrate(z,L,F=max(128,16*L),tau=tau);Sh=estimate(y,L,W)
   if np.isfinite(U):eps=radius(N,L,3,len(W),U,alpha=.025,tail=U*tau);lo,_,_=certificate(Sh,eps);coverage=np.max(abs(Sh-Strue))<=eps
   else:eps=np.inf;lo=np.zeros(len(W));coverage=True
   rows.append(dict(rep=rep,condition=name,L=L,tau=tau,B_upper=U,positive=bool(np.any(lo>1e-14)),lower=float(max(lo)),envelope_covers=bool(coverage)))
 pd.DataFrame(rows).to_csv(OUT/'misspecification_stress.csv',index=False)
 # Population truncated-spectrum limit: demonstrates the omitted deterministic bias.
 lags=[]
 for ell in [0,1]:lags.append(np.array([[cov[i,j]*a**abs(ell-delays[i]+delays[j]) for j in range(3)] for i in range(3)]))
 trunc=lags[0][None]+np.exp(-1j*W)[:,None,None]*lags[1]+np.exp(1j*W)[:,None,None]*lags[1].T
 low,_,_=certificate(trunc,0.)
 pd.DataFrame(dict(w=W,true_cycle_imag=(Strue[:,0,1]*Strue[:,1,2]*Strue[:,2,0]).imag,truncated_cycle_imag=(trunc[:,0,1]*trunc[:,1,2]*trunc[:,2,0]).imag,truncated_min_eigenvalue=np.linalg.eigvalsh(trunc)[:,0],invalid_zero_error_lower=low)).to_csv(OUT/'misspecification_population_limit.csv',index=False)
 return pd.DataFrame(rows).groupby('condition').agg(n=('positive','size'),positive=('positive','sum'),coverage=('envelope_covers','mean'),median_lower=('lower','median')).reset_index().to_dict('records')
if __name__=='__main__':
 r={'eeg':eeg(),'stress':stress()};(OUT/'observation_controls_summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
