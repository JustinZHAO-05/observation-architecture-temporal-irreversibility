"""Unknown-shape Gaussian spectral calibration; all randomness is seeded.
An external relative covariance-tail envelope defines the admissible class.
Calibration and test records are independent; record lengths reuse nested prefixes.
"""
from pathlib import Path
import json,time
import numpy as np
import pandas as pd
from scipy.signal import lfilter
from finite_certificate import estimate,radius,certificate,exact_triangle_bound
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
K=np.array([[0,-1,1],[1,0,-1],[-1,1,0]],float)/np.sqrt(3)
M=np.array([[1.,0.,0.],[.12,1.05,0.],[0.,-.10,.95]])
W=np.array([np.pi/6,np.pi/3,np.pi/2,2*np.pi/3,5*np.pi/6])
def model_spectrum(w,b,ar=0.,scale=1.,mix=M):
 s=np.eye(3)[None,:,:]-1j*b*np.sin(w)[:,None,None]*K
 s=np.einsum('ij,fjk,lk->fil',mix,s,mix)
 return s*((1-ar*ar)/(1-2*ar*np.cos(w)+ar*ar))[:,None,None]*scale

def sim(rng,n,b,ar=0.,scale=1.,mix=M):
 a=0. if b==0 else b/(1+np.sqrt(1-b*b));v,U=np.linalg.eigh(np.eye(3)+a*a*K@K.T)
 A0=(U*v**-.5)@U.T;A1=a*A0@K;burn=256 if ar else 0
 z=rng.standard_normal((n+burn+1,3));x=z[1:]@A0.T+z[:-1]@A1.T
 if ar:x=lfilter([np.sqrt(1-ar*ar)],[1.,-ar],x,axis=0)
 return (x[burn:]@mix.T)*np.sqrt(scale)

def relative_tail(L,rho):
 return 0. if rho==0 else float((2*rho/(1-rho)+1+rho)*rho**L)

def calibrate(z,L,F=128,alpha=.025,tau=0.,center=False):
 """No true spectrum or B is used here. Infinity means calibration abstention."""
 n,d=z.shape;c=1-np.pi*L/F
 if c<=0:raise ValueError('F must exceed pi L')
 V=1/n+2*np.sum(1/(n-np.arange(1,L+1)));v=np.log(2*d*d*F/alpha)
 r=2*(np.sqrt(V*v)+V*v);meanbias=3*V if center else 0.
 den=c-d*r-d*c*(tau+meanbias)
 if den<=0:return float('inf'),float(den),0.
 Sh=estimate(z,L,np.linspace(-np.pi,np.pi,F,endpoint=False),center=center)
 A=float(np.max(abs(np.linalg.eigvalsh(Sh))))
 return A/den,float(den),A

def analyze_one(y,N,L,B,tau,Strue):
 Sh=estimate(y[:N],L,W)
 if not np.isfinite(B):return dict(positive=False,lower=0.,radius=np.inf,envelope=True,valid=True)
 eps=radius(N,L,3,len(W),B,alpha=.025,tail=B*tau);lo,_,_=certificate(Sh,eps)
 return dict(positive=bool(np.any(lo>0)),lower=float(np.max(lo)),radius=eps,envelope=bool(np.max(abs(Sh-Strue))<=eps),valid=bool(np.all(lo<=exact_triangle_bound(Strue)+1e-12)))

def main():
 t=time.perf_counter();rows=[];ca=[];rng=np.random.default_rng(2026110904)
 ms=[1024,4096,16384,65536];ns=[32768,131072,262144]
 for b in [0.,.65,.9]:
  truth=model_spectrum(W,b);Bstar=float(np.linalg.eigvalsh(model_spectrum(np.linspace(-np.pi,np.pi,4097),b)).max());Bo=float(np.linalg.norm(M,2)**2*(1+b))
  for rep in range(120):
   scale=float(np.exp(rng.uniform(-.5,.5)));z=sim(rng,max(ms),b,scale=scale);y=sim(rng,max(ns),b,scale=scale)
   for m in ms:
    U,den,A=calibrate(z[:m],1)
    ca.append(dict(b=b,rep=rep,m=m,L=1,tau=0.,B_upper=U,B_true=Bstar*scale,ratio=U/(Bstar*scale),covers=U>=Bstar*scale,denominator=den))
    for N in ns:rows.append(dict(model='MA1_unknown_shape',b=b,rep=rep,m=m,N=N,ar=0.,rho=0.,calibrated=True,**analyze_one(y,N,1,U,0.,truth*scale)))
   for N in ns:
    for mult in [.5,1.,2.]:rows.append(dict(model='oracle_multiplier',b=b,rep=rep,m=0,N=N,ar=0.,rho=0.,calibrated=False,multiplier=mult,**analyze_one(y,N,1,Bo*scale*mult,0.,truth*scale)))
  print('completed MA1 b',b,flush=True)
 for ar,rho,L in [(.3,.4,10),(.6,.65,24)]:
  tau=relative_tail(L,rho);Bsafe=np.linalg.norm(M,2)**2*1.9*(1+rho)/(1-rho)
  for b in [0.,.9]:
   truth=model_spectrum(W,b,ar);Bstar=float(np.linalg.eigvalsh(model_spectrum(np.linspace(-np.pi,np.pi,4097),b,ar)).max())
   for rep in range(60):
    z=sim(rng,131072,b,ar);y=sim(rng,524288,b,ar);U,den,A=calibrate(z,L,F=max(128,16*L),tau=tau)
    ca.append(dict(b=b,rep=rep,m=len(z),L=L,tau=tau,ar=ar,B_upper=U,B_true=Bstar,ratio=U/Bstar,covers=U>=Bstar,denominator=den))
    for N in [131072,524288]:
     for name,B in [('unknown_shape',U),('external_safe',Bsafe)]:rows.append(dict(model='ARMA_'+name,b=b,rep=rep,m=len(z),N=N,ar=ar,rho=rho,calibrated=name=='unknown_shape',**analyze_one(y,N,L,B,tau,truth)))
   print('completed ARMA',ar,b,flush=True)
 df=pd.DataFrame(rows);cf=pd.DataFrame(ca);df.to_csv(OUT/'unknown_shape_test_replicates.csv',index=False);cf.to_csv(OUT/'unknown_shape_calibration_replicates.csv',index=False)
 df.groupby(['model','b','ar','m','N'],dropna=False).agg(n=('positive','size'),positive=('positive','sum'),power=('positive','mean'),median_lower=('lower','median'),coverage=('envelope','mean'),valid=('valid','mean')).reset_index().to_csv(OUT/'unknown_shape_summary.csv',index=False)
 cf.groupby(['b','L','m']).agg(n=('covers','size'),cover=('covers','mean'),median_ratio=('ratio','median'),max_ratio=('ratio','max')).reset_index().to_csv(OUT/'calibration_coverage_summary.csv',index=False)
 r=dict(seed=2026110904,test_analyses=len(df),calibration_analyses=len(cf),finite_calibrations=int(np.isfinite(cf.B_upper).sum()),independent_calibration_test_pairs=600,nested_lengths=True,calibration_failures=int((~cf.covers).sum()),calibrated_certificate_violations=int((~df[df.calibrated].valid).sum()),calibrated_null_positives=int(df[df.calibrated&(df.b==0)].positive.sum()),runtime_seconds=time.perf_counter()-t)
 (OUT/'calibration_run.json').write_text(json.dumps(r,indent=2));print(r)
if __name__=='__main__':main()
