"""Finite-record Gaussian confidence certificate with EXTERNAL class bounds."""
from pathlib import Path
import json,time
import numpy as np
import pandas as pd
from scipy.stats import beta
from concurrent.futures import ProcessPoolExecutor
from theory_round2 import ma_coeff,ma_spectrum
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def estimate(y,L,w,center=False):
 if center: y=y-y.mean(axis=0,keepdims=True)
 N,d=y.shape;g=y.T@y/N;S=np.broadcast_to(g,(len(w),d,d)).astype(complex).copy()
 for ell in range(1,L+1):
  g=y[ell:].T@y[:-ell]/(N-ell);z=np.exp(-1j*w*ell)[:,None,None];S+=z*g+z.conj()*g.T
 return S

def radius(N,L,d,F,B,alpha=.05,tail=0.,estimated_mean=False):
 if not 0<=L<N: raise ValueError('Require 0<=L<N')
 u=np.log(2*d*d*F/alpha);V=1/N+2*np.sum(1/(N-np.arange(1,L+1)))
 return float(2*B*(np.sqrt(V*u)+V*u)+tail+(3*B*V if estimated_mean else 0.))

def certificate(S,e):
 if np.asarray(S).ndim!=3 or np.asarray(S).shape[-2:]!=(3,3): raise ValueError('Use a frequency x 3 x 3 triangle spectrum; use multichannel_certificate for more channels')
 a,b,c=S[:,0,1],S[:,1,2],S[:,2,0];p=(a*b*c).imag
 er=e*(abs(a*b)+abs(b*c)+abs(c*a))+e*e*(abs(a)+abs(b)+abs(c))+e**3
 res=np.maximum(0.,abs(p)-er);up=np.diagonal(S,axis1=1,axis2=2).real+e;lo=up-2*e
 aa,bb,cc=abs(a)+e,abs(b)+e,abs(c)+e
 T=(aa*bb)**2*up[:,0]*up[:,2]+(bb*cc)**2*up[:,1]*up[:,0]+(cc*aa)**2*up[:,2]*up[:,1]
 lam=np.full(len(S),3.);good=np.all(lo>0,axis=1)
 if np.any(good):
  r1=np.minimum(1,aa[good]/np.sqrt(lo[good,0]*lo[good,1]));r2=np.minimum(1,bb[good]/np.sqrt(lo[good,1]*lo[good,2]));r3=np.minimum(1,cc[good]/np.sqrt(lo[good,2]*lo[good,0]))
  lam[good]=np.minimum(3,1+np.maximum.reduce([r1+r2,r2+r3,r3+r1]))
 return np.divide(2*res**2,lam*lam*T,out=np.zeros_like(res),where=np.all(up>0,axis=1)&(T>0)),p,er

def multichannel_certificate(S,e):
 """Maximum triangle lower bound at each frequency, valid for the full vector.
 The error radius must already cover ALL d channels and frequencies simultaneously.
 Dependent triangle lower bounds must not be added.
 """
 import itertools
 S=np.asarray(S)
 if S.ndim!=3 or S.shape[-1]!=S.shape[-2]: raise ValueError('Expected frequency x d x d')
 if S.shape[-1]<3:return np.zeros(len(S)),np.full((len(S),3),-1,dtype=int)
 best=np.zeros(len(S)); which=np.full((len(S),3),-1,dtype=int)
 for ids in itertools.combinations(range(S.shape[-1]),3):
  idx=np.asarray(ids);tri=S[:,idx[:,None],idx[None,:]];value,_,_=certificate(tri,e)
  improve=value>best;best[improve]=value[improve];which[improve]=idx
 return best,which

def exact_triangle_bound(S):
 p=np.diagonal(S,axis1=1,axis2=2).real;C=S/np.sqrt(p[:,:,None]*p[:,None,:]);a,b,c=C[:,0,1],C[:,1,2],C[:,2,0]
 D=abs(a*b)**2+abs(b*c)**2+abs(c*a)**2;la=np.linalg.eigvalsh(C)[:,-1]
 return np.divide(2*(a*b*c).imag**2,la**2*D,out=np.zeros_like(D),where=D>0)
W=np.array([np.pi/6,np.pi/3,np.pi/2,2*np.pi/3,5*np.pi/6]);NGRID=[2048,8192,32768,131072]
DELAY=[(0,0,0),(0,1,2),(0,4,8)];REPS=128

def one_group(spec):
 model,di,seed=spec;delay=DELAY[di];rng=np.random.default_rng(seed);ns=max(NGRID);d=3;maxd=max(delay);raw=[]
 if model.startswith('alternative'):
  b=float(model.split('_')[1]);A0,A1=ma_coeff(b);B=1+b;L=1+maxd;S0=np.array([ma_spectrum(b,w) for w in W])
 else:
  r=.6;R=(1-r)*np.eye(3)+r*np.ones((3,3));chol=np.linalg.cholesky(R);a=.5 if model=='null_colored' else 0.
  B=(1+a)**2/(1+a*a)*(1+2*r);L=int(a!=0)+maxd;S0=np.array([(1+a*a+2*a*np.cos(w))/(1+a*a)*R for w in W])
 H=np.exp(-1j*W[:,None]*np.array(delay)[None,:]);Strue=H[:,:,None]*S0*H[:,None,:].conj();exactL=exact_triangle_bound(Strue)
 for rep in range(REPS):
  z=rng.normal(size=(ns+maxd+2,d))
  x=z[1:]@A0.T+z[:-1]@A1.T if model.startswith('alternative') else (z[1:]+a*z[:-1])@chol.T/np.sqrt(1+a*a)
  y=np.column_stack([x[maxd-delay[j]:maxd-delay[j]+ns,j] for j in range(d)])
  for N in NGRID:
   Shat=estimate(y[:N],L,W);err=float(np.max(abs(Shat-Strue)));eps=radius(N,L,3,len(W),B);lower,p,er=certificate(Shat,eps)
   raw.append(dict(model=model,delay_group=di,max_delay=maxd,N=N,rep=rep,L=L,B=B,radius=eps,max_spectral_error=err,envelope_covers=err<=eps,rejects=bool(np.any(lower>0)),max_certified_lower=float(max(lower)),certificate_below_known_analytic_bound=bool(np.all(lower<=exactL+1e-12)),max_abs_raw_cycle=float(max(abs(p))),population_max_bound=float(max(exactL))))
 return raw

def main():
 start=time.perf_counter();models=['null_white','null_colored','alternative_0.35','alternative_0.65','alternative_0.9'];tasks=[(m,j,260207+1000*i+17*j) for i,m in enumerate(models) for j in range(3)];rows=[]
 with ProcessPoolExecutor(max_workers=3) as pool:
  for result in pool.map(one_group,tasks): rows.extend(result);print('completed',len(rows),'record analyses',flush=True)
 df=pd.DataFrame(rows);df.to_csv(OUT/'certificate_replicates.csv',index=False);group=[]
 for key,g in df.groupby(['model','delay_group','max_delay','N']):
  k=int(g.rejects.sum());n=len(g);cil=0 if k==0 else beta.ppf(.025,k,n-k+1);cih=1 if k==n else beta.ppf(.975,k+1,n-k)
  group.append(dict(zip(['model','delay_group','max_delay','N'],key),n=n,rejections=k,rejection_rate=k/n,rate_ci_low=cil,rate_ci_high=cih,coverage=g.envelope_covers.mean(),median_lower=g.max_certified_lower.median(),max_error_ratio=(g.max_spectral_error/g.radius).max(),radius=g.radius.iloc[0],population_max_bound=g.population_max_bound.iloc[0]))
 summary=pd.DataFrame(group);summary.to_csv(OUT/'certificate_summary.csv',index=False)
 res=dict(analyses=len(df),independent_long_trajectories=len(tasks)*REPS,all_envelopes_cover=bool(df.envelope_covers.all()),all_certificates_below_population_analytic_bound=bool(df.certificate_below_known_analytic_bound.all()),null_rejections=int(df[df.model.str.startswith('null')].rejects.sum()),seconds=time.perf_counter()-start)
 (OUT/'certificate_run.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2));print(summary[summary.model=='alternative_0.9'].to_string(index=False))
if __name__=='__main__':main()
