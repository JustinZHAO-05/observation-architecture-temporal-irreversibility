"""Exact reversible lift for source filtering before spatial mixing."""
from pathlib import Path
import json,time
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
def root(A,inverse=False):
 v,q=np.linalg.eigh(A)
 if v.min()<=0: raise ValueError('Not positive definite')
 return (q*(1/np.sqrt(v) if inverse else np.sqrt(v)))@q.T

def lift(S,w):
 R=S.real;Y=S.imag;d=len(R);s=np.sin(w);c=np.cos(w)
 if abs(s)<1e-12: raise ValueError('Use continuous endpoint limit')
 Ri=root(R,True);beta=np.linalg.norm(Ri@Y@Ri,2)
 if beta>=1: raise ValueError('Not positive definite')
 eta=(1-beta*beta)/2;k=((beta/s)**2+eta)/2
 V=k*R;Q=-c*V+Y/(2*s);P=R+(2*c*c-1)*V
 G=np.block([[P,Q],[Q.T,V]])
 H=np.concatenate([np.eye(d),np.exp(-1j*w)*np.eye(d)],axis=1)
 return G,H,k,beta

def K3(): return np.array([[0.,-1,1],[1,0,-1],[-1,1,0]])/np.sqrt(3)
def ma_coeff(b):
 a=b/(1+np.sqrt(1-b*b));K=K3();R=np.eye(3)+a*a*K@K.T;A0=root(R,True)
 return A0,a*A0@K

def ma_spectrum(b,w): return np.eye(3)-1j*b*np.sin(w)*K3()
def exact_latent_lags(b):
 k=(b*b+(1-b*b)/2)/2;I=np.eye(3);Z=np.zeros((3,3));J=-b*K3()/2
 return [np.block([[I,J],[J.T,k*I]]),np.block([[Z,-k*I/2],[-k*I/2,Z]]),np.block([[k*I/2,Z],[Z,Z]])],k

def block_cov(lags,N):
 d=len(lags[0]);ans=np.zeros((N*d,N*d))
 for t in range(N):
  for u in range(N):
   k=t-u
   if abs(k)<len(lags): ans[t*d:(t+1)*d,u*d:(u+1)*d]=lags[k] if k>=0 else lags[-k].T
 return ans

def E(S): return .5*(np.trace(np.linalg.solve(S.T,S)).real-len(S))
def main():
 start=time.perf_counter();rng=np.random.default_rng(2601107);rows=[]
 grid=np.r_[1e-5,np.linspace(.01,np.pi-.01,81),np.pi-1e-5]
 for d in [3,6,12]:
  for rep in range(30):
   A=rng.normal(size=(d,d));A*=rng.uniform(.2,.9)/max(abs(np.linalg.eigvals(A)))
   Z=rng.normal(size=(d,d));Q=Z@Z.T/d+.4*np.eye(d)
   maxerr=0.;mineig=np.inf;maxE=0.;maxk=0.
   for w in grid:
    H=np.linalg.inv(np.eye(d)-A*np.exp(-1j*w));S=H@Q@H.conj().T
    G,F,k,beta=lift(S,w);rec=F@G@F.conj().T
    maxerr=max(maxerr,np.linalg.norm(rec-S,'fro')/np.linalg.norm(S,'fro'))
    mineig=min(mineig,np.linalg.eigvalsh(G)[0]);maxE=max(maxE,E(S));maxk=max(maxk,k)
   rows.append(dict(dimension=d,network=rep,max_relative_error=maxerr,min_latent_eigenvalue=mineig,max_observed_reversal=maxE,max_k=maxk))
 pd.DataFrame(rows).to_csv(OUT/'general_lift_validation.csv',index=False)
 b=.9;lags,k=exact_latent_lags(b);N=32;latent=block_cov(lags,N+1);O=np.zeros((N*3,(N+1)*6))
 for t in range(N):
  O[t*3:(t+1)*3,(t+1)*6:(t+1)*6+3]=np.eye(3);O[t*3:(t+1)*3,t*6+3:t*6+6]=np.eye(3)
 target=block_cov([np.eye(3),b*K3()/2],N);observed=O@latent@O.T
 ws=np.linspace(0,np.pi,513);errs=[];ev=[];rev=[]
 for w in ws:
  G=lags[0]+2*np.cos(w)*lags[1]+2*np.cos(2*w)*lags[2]
  F=np.concatenate([np.eye(3),np.exp(-1j*w)*np.eye(3)],axis=1);S=ma_spectrum(b,w)
  errs.append(np.max(abs(F@G@F.conj().T-S)));ev.append(np.linalg.eigvalsh(G)[0]);rev.append(E(S))
 S=ma_spectrum(b,np.pi/2);cyc=(S[0,1]*S[1,2]*S[2,0]).imag
 np.savez_compressed(OUT/'exact_short_memory_equivalence.npz',latent_lags=np.array(lags),latent_covariance=latent,target_covariance=target,observation_matrix=O,observed_covariance=observed,w=ws,reversal=rev)
 summary=dict(networks=len(rows),frequency_points_per_network=len(grid),max_general_relative_error=max(x['max_relative_error'] for x in rows),min_general_latent_eigenvalue=min(x['min_latent_eigenvalue'] for x in rows),exact_example=dict(b=b,observed_channels=3,latent_channels=6,latent_covariance_support=2,observation_delay=1,record_length=N,k=k,max_full_record_covariance_difference=float(np.max(abs(observed-target))),max_spectral_difference=float(max(errs)),min_latent_spectral_eigenvalue=float(min(ev)),max_abs_imaginary_cycle=float(abs(cyc)),max_observed_reversal=float(max(rev))),seconds=time.perf_counter()-start)
 (OUT/'theory_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
