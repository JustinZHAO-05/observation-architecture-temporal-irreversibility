"""PRE revised analyses: exact memoryless lift, joint delay limits,
frequency-averaging mechanism ablations and independently calibrated confidence.
Python 3.13, NumPy/SciPy/pandas/matplotlib; no random non-determinism.
"""
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
from scipy.stats import chi2
from scipy.linalg import solve_triangular
sys.path.insert(0,str(Path(__file__).parent))
from theory_round2 import K3, ma_coeff, ma_spectrum, E
from finite_certificate import estimate, radius, certificate, exact_triangle_bound
R=Path(__file__).resolve().parents[1]
OUT=R/'results';OUT.mkdir(exist_ok=True)
RNG=np.random.default_rng(20261109)

def memoryless():
 rows=[]
 for d in [3,6,12,24]:
  for rep in range(30):
   z=RNG.standard_normal((d,d));K=z-z.T;K=K/max(np.linalg.norm(K,2),1e-12)
   for b in [0.2,0.5,0.8,0.9]:
    G=.5*np.block([[np.eye(d),-b*K],[b*K,np.eye(d)]])
    mineig=np.linalg.eigvalsh(G)[0]
    for w in np.linspace(0,np.pi,49):
     H=np.concatenate([np.eye(d),np.exp(-1j*w)*np.eye(d)],axis=1)
     Sy=H@G@H.conj().T;tar=np.eye(d)-1j*b*np.sin(w)*K
     err=np.linalg.norm(Sy-tar,'fro')/np.linalg.norm(tar,'fro')
     rows.append(dict(d=d,rep=rep,b=b,w=w,rel_error=err,latent_min_eigenvalue=mineig))
 df=pd.DataFrame(rows);df.to_csv(OUT/'white_latent_lift.csv',index=False)
 return dict(cases=len(df),max_rel_error=float(df.rel_error.max()),min_latent_eigenvalue=float(df.latent_min_eigenvalue.min()),distinct_d=[int(x) for x in sorted(df.d.unique())])

def low_frequency():
 rows=[]
 for beta in [.2,.5,.8,.95]:
  for theta in np.logspace(-5,-.2,110):
   b=beta*np.sin(theta);c=abs(np.cos(theta));s=np.sin(theta)
   # stable expression: rationalized numerator avoids cancellation
   val=(1+(c*b/s)**2)/(1+c*np.sqrt(1-b*b))
   lim=(1+beta*beta)/2
   rows.append(dict(beta=beta,theta=theta,b=b,exact_cost=val,low_freq_limit=lim,relative_error=abs(val-lim)/lim))
 df=pd.DataFrame(rows);df.to_csv(OUT/'joint_low_frequency.csv',index=False)
 return dict(points=len(df),max_relative_error_at_theta_le_1e_3=float(df[df.theta<1e-3].relative_error.max()))

def bandwidth_ablation():
 # Local spectral edges, all derived from a common node-phase gauge. Two independent causal/smooth mechanisms.
 # Exact Gaussian-bandwidth integral is analytic; numerical quadrature independently checks the expression.
 rr=.13
 slopes=np.array([1.0,-.6,.2]);phase_deriv=np.array([-2.,3.,-1.]);assert abs(phase_deriv.sum())<1e-12
 rows=[]
 from numpy.polynomial.hermite import hermgauss
 X,W=hermgauss(80)
 for h in [.005,.01,.02,.03,.04,.05,.065,.08]:
  for case in ['joint','zero_amplitude_slope','zero_delay_slope']:
   ss=slopes if case!='zero_amplitude_slope' else np.zeros(3)
   qq=phase_deriv if case!='zero_delay_slope' else np.zeros(3)
   # E[(1+s d)e^{i q d}] = exp(-q²h²/2)*(1+i s q h²)
   zz=rr*np.exp(-.5*(qq*h)**2)*(1+1j*ss*qq*h*h)
   analytic=np.prod(zz).imag
   d=np.sqrt(2)*h*X
   z_quad=[]
   for s,q in zip(ss,qq):
    z_quad.append((rr/np.sqrt(np.pi))*np.dot(W,(1+s*d)*np.exp(1j*q*d)))
   numeric=np.prod(z_quad).imag
   predicted=rr**3*h*h*np.dot(ss,qq)
   rows.append(dict(h=h,case=case,exact_imag=analytic,quadrature_imag=numeric,leading_prediction=predicted,
                    abs_quad_error=abs(analytic-numeric)))
 df=pd.DataFrame(rows);df.to_csv(OUT/'finite_bandwidth_ablation.csv',index=False)
 return dict(rows=len(df),max_analytic_quadrature_diff=float(df.abs_quad_error.max()),
             max_abs_control_signal=float(df[df.case!='joint'].exact_imag.abs().max()),
             leading_ratio_at_h005=float(df[(df.case=='joint')&(df.h==.005)].exact_imag.iloc[0]/df[(df.case=='joint')&(df.h==.005)].leading_prediction.iloc[0]))

def block_covariance(b,m):
 # Temporal MA(1) with Γ(0)=I and Γ(1)=bK/2; indexing in time-major order.
 d=3;M=np.eye(d*m)
 g=b*K3()/2
 for t in range(1,m):
  M[t*d:(t+1)*d,(t-1)*d:t*d]=g
  M[(t-1)*d:t*d,t*d:(t+1)*d]=g.T
 return M

def independent_calibration():
 # Calibrated unknown scale sigma² in a specified/validated MA(1) spectral shape.
 # Independent calibration record z ~ N(0, sigma² Σ_b), Σ_b known shape.
 # U = (zᵀ Σ_b^-1 z)/chi2.ppf(alpha_cal, dm) is exact one-sided upper CI for sigma².
 # Use alpha_cal+alpha_test=.05 and no re-use of test trajectory in calibration.
 N=32768;W=np.array([np.pi/6,np.pi/3,np.pi/2,2*np.pi/3,5*np.pi/6]);ac=.025;at=.025
 reps=90;ms=[16,64,128]
 C={}
 for b in [0.0,.9]:
  for m in ms: C[(b,m)]=np.linalg.cholesky(block_covariance(b,m))
 rows=[]
 for b in [0.0,.9]:
  A0,A1=ma_coeff(b)
  Strue=np.array([ma_spectrum(b,w) for w in W]);exact=exact_triangle_bound(Strue)
  for rep in range(reps):
   z=RNG.standard_normal((N+1,3));y=z[1:]@A0.T+z[:-1]@A1.T
   Shat=estimate(y,1,W);err=np.max(abs(Shat-Strue))
   oracle_B=1+b
   cert_oracle,_,_=certificate(Shat,radius(N,1,3,len(W),oracle_B,alpha=at))
   for m in ms:
    e=RNG.standard_normal(3*m)
    calib=C[(b,m)]@e # independent calibration recording with exact target shape
    w=solve_triangular(C[(b,m)],calib,lower=True)
    Q=np.dot(w,w)
    U=Q/chi2.ppf(ac,3*m)
    eps=radius(N,1,3,len(W),U*oracle_B,alpha=at)
    cert,_,_=certificate(Shat,eps)
    rows.append(dict(b=b,rep=rep,m=m,N=N,sigma2_upper=U,sigma2_upper_covers=(U>=1.),
                     spectral_bound=U*oracle_B,spectral_error=err,eps=eps,spectral_envelope_covers=err<=eps,
                     positive_certificate=bool(np.any(cert>0)),oracle_positive=bool(np.any(cert_oracle>0)),
                     max_certificate=float(np.max(cert)),certificate_below_analytic=bool(np.all(cert<=exact+1e-12))))
 df=pd.DataFrame(rows);df.to_csv(OUT/'independent_scale_calibration.csv',index=False)
 return {f'b{b}_m{m}':{'replications':int(len(g)),'calibration_coverage':float(g.sigma2_upper_covers.mean()),
                     'simultaneous_spectral_coverage':float(g.spectral_envelope_covers.mean()),
                     'positive_certificate_rate':float(g.positive_certificate.mean()),
                     'oracle_positive_rate':float(g.oracle_positive.mean()),
                     'median_calibration_upper_factor':float(g.sigma2_upper.median()),
                     'all_certificates_below_population_analytic':bool(g.certificate_below_analytic.all())}
         for (b,m),g in df.groupby(['b','m'])}

if __name__=='__main__':
 res={}
 for name,fn in [('memoryless',memoryless),('joint_low_frequency',low_frequency),('bandwidth_ablation',bandwidth_ablation),('independent_calibration',independent_calibration)]:
  print('running',name,flush=True);res[name]=fn();print(json.dumps(res[name],indent=2),flush=True)
 (OUT/'R3_summary.json').write_text(json.dumps(res,indent=2))
