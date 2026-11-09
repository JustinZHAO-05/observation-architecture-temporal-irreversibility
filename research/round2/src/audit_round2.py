"""Separate algebraic and implementation checks; no claim of external peer review."""
from pathlib import Path
import json
import numpy as np
from theory_round2 import ma_coeff,ma_spectrum
from finite_certificate import estimate,radius,certificate,exact_triangle_bound
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results';rng=np.random.default_rng(863902)
# Independent explicit time-kernel construction versus lag-loop implementation.
max_kernel_error=0;max_frobenius_error=0
for N in [9,17,40]:
 for L in [0,1,5]:
  if L>=N:continue
  y=rng.normal(size=(N,3));w=np.array([.2,.8,2.1]);pred=estimate(y,L,w)
  for j,omega in enumerate(w):
   D=np.arange(N)[:,None]-np.arange(N)[None,:]
   K=np.where(abs(D)<=L,np.exp(-1j*omega*D)/(N-abs(D)),0.)
   direct=y.T@K@y
   max_kernel_error=max(max_kernel_error,np.max(abs(direct-pred[j])))
   V=1/N+2*np.sum(1/(N-np.arange(1,L+1)))
   max_frobenius_error=max(max_frobenius_error,abs(np.linalg.norm(K,'fro')**2-V))
# Perturbations are general Hermitian, and need not yield a positive empirical spectrum.
max_excess=-np.inf;npositive=0;max_witness_excess=-np.inf
for rep in range(2500):
 z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3));S=z@z.conj().T+.2*np.eye(3)
 gain=10**rng.uniform(-1,1,size=3);S=gain[:,None]*S*gain[None,:]
 e=10**rng.uniform(-6,-1)*np.max(S.diagonal().real)
 D=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3));D=(D+D.conj().T)/2;D*=e/np.max(abs(D))
 hat=S+D;lb,p,err=certificate(hat[None],e);truth=exact_triangle_bound(S[None])[0]
 max_excess=max(max_excess,lb[0]-truth);npositive+=int(lb[0]>0)
 truep=(S[0,1]*S[1,2]*S[2,0]).imag
 max_witness_excess=max(max_witness_excess,abs(p[0]-truep)-err[0])
# Unknown constant means: global centering + proven deterministic mean-estimation allowance.
A0,A1=ma_coeff(.8);w=np.array([np.pi/6,np.pi/3,np.pi/2,2*np.pi/3,5*np.pi/6]);delays=np.array([0,1,2]);H=np.exp(-1j*w[:,None]*delays)
Strue=H[:,:,None]*np.array([ma_spectrum(.8,v) for v in w])*H[:,None,:].conj()
checks=[]
for N in [512,2048,8192]:
 for rep in range(100):
  z=rng.normal(size=(N+4,3));x=z[1:]@A0.T+z[:-1]@A1.T
  y=np.column_stack([x[2-delays[j]:2-delays[j]+N,j] for j in range(3)])+np.array([50,-10,2])
  hat=estimate(y,3,w,center=True);e=radius(N,3,3,len(w),1.8,estimated_mean=True)
  checks.append(float(np.max(abs(hat-Strue))/e))
# Exact large-N weak-signal separation check under bounded entrywise perturbations.
max_sep_failure=0
for r in [.03,.1,.25]:
 for psi in [.01,.1,.3]:
  S=np.eye(3,dtype=complex);S[0,1]=S[1,0]=r;S[1,2]=S[2,1]=r;S[2,0]=r*np.exp(1j*psi);S[0,2]=S[2,0].conjugate()
  e=.99*r/2*((1+abs(np.sin(psi)))**(1/3)-1)
  for j in range(50):
   D=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3));D=(D+D.conj().T)/2;D*=e/np.max(abs(D))
   lb,_,_=certificate((S+D)[None],e);max_sep_failure+=int(lb[0]<=0)
summary=dict(kernel_checks=27,max_kernel_error=float(max_kernel_error),max_Frobenius_identity_error=float(max_frobenius_error),
  perturbation_cases=2500,positive_certificates=npositive,max_certificate_minus_true_bound=float(max_excess),
  max_product_error_minus_envelope=float(max_witness_excess),unknown_mean_cases=len(checks),unknown_mean_all_covered=bool(max(checks)<=1),
  unknown_mean_max_error_over_radius=max(checks),weak_signal_separation_cases=450,separation_failures=max_sep_failure)
(OUT/'independent_formula_audit.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
