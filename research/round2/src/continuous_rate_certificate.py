"""Continuous-frequency lower confidence bound on Gaussian reversal KL rate.
A trigonometric-polynomial net bound plus interval-wise deterministic spectral variation
makes the frequency integral a lower sum, not an uncertified Riemann approximation.
"""
from pathlib import Path
import json,time
import numpy as np
import pandas as pd
from theory_round2 import ma_coeff,ma_spectrum
from finite_certificate import certificate,exact_triangle_bound
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'

def autocov(y,L):
 N=len(y);return np.array([y.T@y/N]+[y[k:].T@y[:-k]/(N-k) for k in range(1,L+1)])
def spectrum(g,w):
 S=np.broadcast_to(g[0],(len(w),3,3)).astype(complex).copy()
 for k in range(1,len(g)):
  z=np.exp(-1j*w*k)[:,None,None];S+=z*g[k]+z.conj()*g[k].T
 return S

def rate_bound(y,L,B,alpha=.05,cells=2048,estimated_mean=False,tail=0.):
 N=len(y)
 if estimated_mean:y=y-y.mean(axis=0)
 g=autocov(y,L);F=max(16,16*L);u=np.log(2*9*F/alpha)
 V=1/N+2*np.sum(1/(N-np.arange(1,L+1)))
 eps=2*B*(np.sqrt(V*u)+V*u)/(1-np.pi*L/F)
 if estimated_mean:eps+=3*B*V
 eps+=tail
 w=2*np.pi*(np.arange(cells)+.5)/cells
 Sh=spectrum(g,w)
 derivative=np.zeros((3,3))
 for k in range(1,L+1):derivative+=k*(abs(g[k])+abs(g[k].T))
 variation=np.pi/cells*np.max(derivative)
 lower,_,_=certificate(Sh,eps+variation)
 return float(np.mean(lower)),eps,variation,w,Sh

def main():
 rng=np.random.default_rng(713420);start=time.perf_counter();b=.9;A0,A1=ma_coeff(b);rows=[]
 for delay in [(0,0,0),(0,4,8)]:
  L=1+max(delay);Nmax=524288
  for rep in range(64):
   z=rng.normal(size=(Nmax+max(delay)+2,3));x=z[1:]@A0.T+z[:-1]@A1.T
   y=np.column_stack([x[max(delay)-delay[j]:max(delay)-delay[j]+Nmax,j] for j in range(3)])
   for N in [32768,131072,524288]:
    lb,e,v,w,Sh=rate_bound(y[:N],L,1+b)
    H=np.exp(-1j*w[:,None]*np.array(delay));St=H[:,:,None]*np.array([ma_spectrum(b,ww) for ww in w])*H[:,None,:].conj()
    poptri=np.mean(exact_triangle_bound(St))
    rows.append(dict(max_delay=max(delay),N=N,rep=rep,rate_lower=lb,uniform_radius=e,cell_variation=v,
      dense_grid_max_error=float(np.max(abs(Sh-St))),population_triangle_integral=float(poptri),
      below_population_triangle_integral=bool(lb<=poptri+1e-12)))
 df=pd.DataFrame(rows);df.to_csv(OUT/'continuous_rate_replicates.csv',index=False)
 su=df.groupby(['max_delay','N']).agg(n=('rep','count'),positive=('rate_lower',lambda x:int((x>0).sum())),
     median_rate_lower=('rate_lower','median'),max_rate_lower=('rate_lower','max'),uniform_radius=('uniform_radius','first'),
     population_triangle_integral=('population_triangle_integral','first')).reset_index()
 su.to_csv(OUT/'continuous_rate_summary.csv',index=False)
 res=dict(analyses=len(df),independent_long_trajectories=128,all_dense_grid_checks_covered=bool((df.dense_grid_max_error<=df.uniform_radius).all()),
   all_rate_bounds_below_population_triangle_integral=bool(df.below_population_triangle_integral.all()),
   exact_observed_KL_rate=2*(1/np.sqrt(1-b*b)-1),seconds=time.perf_counter()-start)
 (OUT/'continuous_rate_run.json').write_text(json.dumps(res,indent=2));print(su.to_string(index=False));print(json.dumps(res,indent=2))
if __name__=='__main__':main()
