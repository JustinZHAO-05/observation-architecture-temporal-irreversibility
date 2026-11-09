"""Latency-power cost and coordinate tests; constrained optimization is independent of formula."""
from pathlib import Path
import json,time,sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize, LinearConstraint, NonlinearConstraint
from theory_round2 import ma_spectrum,K3,E
from finite_certificate import exact_triangle_bound
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'

# Full symmetric 4x4 real covariance parameterization, not a symmetry-reduced fit.
IJ=list(zip(*np.triu_indices(4)))
BAS=[]
for i,j in IJ:
 A=np.zeros((4,4)); A[i,j]=1.;A[j,i]=1.; BAS.append(A)
BAS=np.array(BAS)
TRACE=np.array([np.trace(A) for A in BAS])
def unpack(z): return np.einsum('k,kij->ij',z,BAS)
def analytic_ratio(b,theta):
 return (1-abs(np.cos(theta))*np.sqrt(1-b*b))/np.sin(theta)**2

def numeric_cost(b,theta):
 c,s=np.cos(theta),np.sin(theta)
 H=np.c_[np.eye(2),np.exp(-1j*theta)*np.eye(2)]
 J=np.array([[0.,1],[-1,0]])
 target=np.eye(2)+1j*b*J
 def features(S): return np.array([S[0,0].real,S[1,1].real,S[0,1].real,S[0,1].imag])
 A=np.stack([features(H@X@H.conj().T) for X in BAS],axis=1)
 rhs=features(target)
 # Strictly feasible starting point from the constructive lift, NOT the optimal cost formula.
 eta=(1-b*b)/2;k=((b/s)**2+eta)/2;V=k*np.eye(2)
 Q=-c*V+b*J/(2*s);P=np.eye(2)+(2*c*c-1)*V
 G=np.block([[P,Q],[Q.T,V]])
 scale=max(1.,np.trace(G));z0=np.array([G[i,j] for i,j in IJ])/scale
 eq=LinearConstraint(A,rhs/scale,rhs/scale)
 fit=minimize(lambda z: TRACE@z,z0,jac=lambda z:TRACE,method='SLSQP',
    constraints=[eq,{'type':'ineq','fun':lambda z:np.linalg.eigvalsh(unpack(z))}],
    options={'ftol':1e-12,'maxiter':250})
 Gfit=unpack(fit.x)*scale
 return dict(b=b,theta=theta,analytic_ratio=analytic_ratio(b,theta),
   numerical_ratio=np.trace(Gfit)/2,success=bool(fit.success),message=fit.message,
   minimum_eigenvalue=np.linalg.eigvalsh(Gfit)[0],
   max_constraint_error=np.max(abs(H@Gfit@H.conj().T-target)),iterations=fit.nit)

def main():
 start=time.perf_counter();rows=[]
 for b in [.2,.5,.8,.95]:
  for theta in [.1,.2,.4,.8,1.2,np.pi/2,2.2,2.8]:
   rows.append(numeric_cost(b,theta)); print('cost',b,theta,rows[-1]['success'],flush=True)
 df=pd.DataFrame(rows);df['relative_error']=abs(df.numerical_ratio-df.analytic_ratio)/df.analytic_ratio
 df.to_csv(OUT/'latency_power_optimization.csv',index=False)
 curves=[]
 for b in [.2,.5,.8,.95]:
  for theta in np.geomspace(.01,np.pi/2,100):
   curves.append(dict(b=b,theta=theta,minimum_power_ratio=analytic_ratio(b,theta),
       small_delay_coefficient=1-np.sqrt(1-b*b)))
 pd.DataFrame(curves).to_csv(OUT/'latency_power_curves.csv',index=False)
 # Exact real change of coordinates reduces the 3-cycle to a two-coordinate plane.
 O=np.array([[1,-1,0],[1,1,-2],[1,1,1]],float)
 O/=np.linalg.norm(O,axis=1)[:,None]
 S=ma_spectrum(.9,np.pi/2);Srot=O@S@O.T
 output=dict(cost_cases=len(df),optimizer_successes=int(df.success.sum()),
      max_relative_cost_error=float(df.relative_error.max()),
      min_fitted_eigenvalue=float(df.minimum_eigenvalue.min()),
      max_constraint_error=float(df.max_constraint_error.max()),
      power_ratio_b08_theta005=analytic_ratio(.8,.05),
      exact_coordinate_example=dict(raw_E_original=E(S),raw_E_rotated=E(Srot),
         triangle_lower_original=float(exact_triangle_bound(S[None])[0]),
         triangle_lower_rotated=float(exact_triangle_bound(Srot[None])[0]),
         imaginary_cycle_original=float((S[0,1]*S[1,2]*S[2,0]).imag),
         imaginary_cycle_rotated=float((Srot[0,1]*Srot[1,2]*Srot[2,0]).imag),
         orthogonality_error=float(np.max(abs(O@O.T-np.eye(3))))),
      seconds=time.perf_counter()-start)
 rng=np.random.default_rng(341903);coord=[]
 for rep in range(600):
  b=rng.uniform(.05,.95);w=rng.uniform(.01,np.pi-.01)
  S=ma_spectrum(b,w);Q,_=np.linalg.qr(rng.normal(size=(3,3)));R=Q@S@Q.T
  coord.append(dict(rep=rep,b=b,w=w,raw_E_before=E(S),raw_E_after=E(R),
     triangle_bound_before=exact_triangle_bound(S[None])[0],triangle_bound_after=exact_triangle_bound(R[None])[0]))
 cd=pd.DataFrame(coord);cd.to_csv(OUT/'coordinate_validation.csv',index=False)
 output['random_rotations']=len(cd);output['max_raw_E_rotation_error']=float(abs(cd.raw_E_before-cd.raw_E_after).max())
 (OUT/'power_coordinate_summary.json').write_text(json.dumps(output,indent=2))
 print(json.dumps(output,indent=2))
if __name__=='__main__':main()
