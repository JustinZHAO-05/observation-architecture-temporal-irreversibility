"""Independent algebraic audit: full Toeplitz records, polynomial convolution,
high-precision scalar optima, and saved-output consistency. No human peer review.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
rng=np.random.default_rng(2026110911);checks={}
# Full time-kernel formulation versus separately implemented lag loops.
errs=[]
for N,L,d in [(31,0,3),(64,1,3),(81,5,4),(113,12,3)]:
 y=rng.normal(size=(N,d));
 for w in [.0,.23,1.1,2.8,np.pi]:
  t=np.arange(N);delta=t[:,None]-t[None,:]
  K=np.where(abs(delta)<=L,np.exp(-1j*w*delta)/np.maximum(1,N-abs(delta)),0)
  full=y.T@K@y;lag=y.T@y/N+0j
  for l in range(1,L+1):
   g=y[l:].T@y[:-l]/(N-l);lag+=g*np.exp(-1j*w*l)+g.T*np.exp(1j*w*l)
  errs.append(np.max(abs(full-lag)))
checks['quadratic_form_checks']=len(errs);checks['quadratic_form_max_abs_error']=float(max(errs))
# Independent coefficient-domain H G H* check for saved finite-order example.
a=np.load(OUT/'finite_support_example.npz');g=a['latent_lags'];s=a['target_lags'];d=s.shape[1]
def gc(l):return g[l] if l>=0 and l<len(g) else (g[-l].T if l<0 and -l<len(g) else np.zeros_like(g[0]))
res=[]
for l in range(-len(g)-1,len(g)+2):
 # y_t = u_t + v_(t-1). Cross covariances: uv at l+1, vu at l-1.
 rec=gc(l)[:d,:d]+gc(l)[d:,d:]+gc(l+1)[:d,d:]+gc(l-1)[d:,:d]
 tar=s[l] if 0<=l<len(s) else (s[-l].T if -len(s)<l<0 else np.zeros((d,d)))
 res.append(np.max(abs(rec-tar)))
checks['coefficient_identity_max_abs_error']=float(max(res))
# Dense block covariance check independently from those coefficients.
T=20;dim=2*d;C=np.zeros(((T+1)*dim,(T+1)*dim));O=np.zeros((T*d,(T+1)*dim))
for t in range(T+1):
 for u in range(T+1):C[t*dim:(t+1)*dim,u*dim:(u+1)*dim]=gc(t-u)
for t in range(T):
 O[t*d:(t+1)*d,(t+1)*dim:(t+1)*dim+d]=np.eye(d);O[t*d:(t+1)*d,t*dim+d:(t+1)*dim]=np.eye(d)
Y=O@C@O.T;target=np.zeros_like(Y)
for t in range(T):
 for u in range(T):
  l=t-u
  if abs(l)<len(s):target[t*d:(t+1)*d,u*d:(u+1)*d]=s[l] if l>=0 else s[-l].T
checks['full_record_covariance_max_error']=float(np.max(abs(Y-target)))
# 70-digit cancellation-sensitive evaluation of the joint limiting formula.
mp.mp.dps=70;mx=mp.mpf('0');n=0
for beta in ['0.2','0.5','0.8','0.9']:
 for ws in ['0.01','0.00001','0.000000001']:
  w=mp.mpf(ws);be=mp.mpf(beta);b=be*mp.sin(w);c=mp.cos(w)
  direct=(1-abs(c)*mp.sqrt(1-b*b))/mp.sin(w)**2
  stable=(1+be*be*c*c)/(1+abs(c)*mp.sqrt(1-b*b))
  mx=max(mx,abs(direct-stable));n+=1
checks['high_precision_joint_checks']=n;checks['joint_identity_70digit_max_error']=str(mx)
# Reverse trace identity independently, without helper E().
errs=[];boundfail=0
for d in [3,5,9]:
 for rep in range(50):
  A=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));S=A@A.conj().T+.5*np.eye(d)
  E=.5*(np.trace(np.linalg.inv(S.T)@S).real-d)
  Q,_=np.linalg.qr(rng.normal(size=(d,d)));Z=Q@S@Q.T
  E2=.5*(np.trace(np.linalg.inv(Z.T)@Z).real-d);errs.append(abs(E2-E)/(1+abs(E)))
  Cc=S/np.sqrt(np.diag(S).real[:,None]*np.diag(S).real[None,:]);Tt=Cc[:3,:3];aa,bb,cc=Tt[0,1],Tt[1,2],Tt[2,0]
  D=abs(aa*bb)**2+abs(bb*cc)**2+abs(cc*aa)**2
  low=2*np.imag(aa*bb*cc)**2/(np.linalg.eigvalsh(Tt)[-1]**2*D)
  boundfail+=low>E+1e-10
checks['rotation_checks']=len(errs);checks['max_relative_rotation_error']=float(max(errs));checks['triangle_vs_full_violations']=int(boundfail)
# Count and source consistency, finite vs abstaining calibration.
f=pd.read_csv(OUT/'finite_support_lifts.csv');test=pd.read_csv(OUT/'unknown_shape_test_replicates.csv');cal=pd.read_csv(OUT/'unknown_shape_calibration_replicates.csv')
checks['finite_support_all_positive']=bool((f.all_frequency_lower>0).all());checks['finite_support_targets']=len(f)
checks['test_analyses']=len(test);checks['calibration_count']=len(cal);checks['finite_calibration_count']=int(np.isfinite(cal.B_upper).sum())
checks['invalid_certificates_under_calibrated_models']=int((~test[test.calibrated].valid).sum())
checks['all_pass']=bool(max(res)<1e-10 and checks['full_record_covariance_max_error']<1e-10 and max(errs)<1e-10 and not boundfail and checks['finite_support_all_positive'] and not checks['invalid_certificates_under_calibrated_models'])
(OUT/'independent_audit.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
