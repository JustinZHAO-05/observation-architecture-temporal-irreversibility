"""Independent full-matrix PSD cutting-plane optimization; no analytic optimum in solver."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from power_cost_and_coordinates import BAS,IJ,TRACE,unpack,analytic_ratio
ROOT=Path(__file__).resolve().parents[1]

def solve(b,t):
 s,c=np.sin(t),np.cos(t);J=np.array([[0.,1],[-1,0]])
 H=np.c_[np.eye(2),np.exp(-1j*t)*np.eye(2)];S=np.eye(2)+1j*b*J
 def feat(A): return np.array([A[0,0].real,A[1,1].real,A[0,1].real,A[0,1].imag])
 Aeq=np.stack([feat(H@X@H.conj().T) for X in BAS],axis=1);rhs=feat(S)
 k=((b/s)**2+(1-b*b)/2)/2;V=k*np.eye(2);Q=-c*V+b*J/(2*s);P=np.eye(2)+(2*c*c-1)*V
 G0=np.block([[P,Q],[Q.T,V]]);scale=max(1,np.trace(G0));G0/=scale;rhs/=scale
 directions=list(np.eye(4))
 for i in range(4):
  for j in range(i+1,4):
   for sign in [-1,1]:
    v=np.eye(4)[i]+sign*np.eye(4)[j];directions.append(v/np.linalg.norm(v))
 cuts=[-np.einsum('i,kij,j->k',v,BAS,v) for v in directions]
 for it in range(500):
  fit=linprog(TRACE,A_ub=np.array(cuts),b_ub=np.zeros(len(cuts)),A_eq=Aeq,b_eq=rhs,
      bounds=[(None,None)]*len(TRACE),method='highs',
      options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
  if not fit.success: raise RuntimeError(fit.message)
  G=unpack(fit.x);val,vec=np.linalg.eigh(G)
  if val[0]>=-2e-9: break
  for j in np.where(val<-1e-10)[0]:
   cuts.append(-np.einsum('i,kij,j->k',vec[:,j],BAS,vec[:,j]))
 # Convex blending with a strictly feasible covariance gives an attained PSD upper bound.
 delta=max(0,-np.linalg.eigvalsh(G)[0])+1e-12;gmin=np.linalg.eigvalsh(G0)[0]
 weight=delta/(gmin+delta);Gplus=(1-weight)*G+weight*G0
 return dict(b=b,theta=t,lower_ratio=fit.fun*scale/2,upper_ratio=np.trace(Gplus)*scale/2,
   analytic_ratio=analytic_ratio(b,t),min_upper_eigenvalue=np.linalg.eigvalsh(Gplus*scale)[0],
   constraint_error=np.max(abs(H@(Gplus*scale)@H.conj().T-S)),iterations=it+1,cuts=len(cuts))
rows=[solve(b,t) for b in [.2,.5,.8,.95] for t in [.1,.2,.4,.8,1.2,np.pi/2,2.2,2.8]]
df=pd.DataFrame(rows);df['relative_interval_width']=(df.upper_ratio-df.lower_ratio)/df.analytic_ratio
# LP solver tolerances make these numerical brackets, not interval-arithmetic proofs.
df.to_csv(ROOT/'results/latency_cost_lp_intervals.csv',index=False)
r=dict(cases=len(df),max_relative_interval_width=float(df.relative_interval_width.max()),
  max_lower_minus_analytic=float((df.lower_ratio-df.analytic_ratio).max()),
  max_analytic_minus_upper=float((df.analytic_ratio-df.upper_ratio).max()),
  min_upper_eigenvalue=float(df.min_upper_eigenvalue.min()),max_constraint_error=float(df.constraint_error.max()),
  max_iterations=int(df.iterations.max()))
(ROOT/'results/latency_cost_lp_summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
