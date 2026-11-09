"""Mechanism ablation in a positive-definite, frequency-localized 3-channel spectrum.
Frequency kernel uniform on [-h,h] about omega0; all plotted spectra PSD throughout support.
"""
from pathlib import Path
import numpy as np,pandas as pd
from numpy.polynomial.legendre import leggauss
O=Path(__file__).resolve().parents[1]/'results';O.mkdir(exist_ok=True)
rho=.13; ss=np.array([1.,-.6,.2]); qq=np.array([-2.,3.,-1.]); assert sum(qq)==0
xs,ws=leggauss(256);rows=[]
for h in [.005,.01,.02,.04,.06,.08,.12]:
 for scenario in ['both_active','flat_amplitudes','equal_phase_response']:
  a=ss if scenario!='flat_amplitudes' else np.zeros(3)
  q=qq if scenario!='equal_phase_response' else np.zeros(3)
  # exact (up to Gauss-Legendre quadrature): normalized uniform convolution
  delta=h*xs; z=[];mineig=1.
  for j in range(3): z.append(rho/2*np.dot(ws,(1+a[j]*delta)*np.exp(1j*q[j]*delta)))
  for f in delta:
   edge=rho*(1+a*f)*np.exp(1j*q*f)
   C=np.eye(3,dtype=complex)
   for (i,j),v in zip([(0,1),(1,2),(2,0)],edge):C[i,j]=v;C[j,i]=v.conjugate()
   mineig=min(mineig,np.linalg.eigvalsh(C)[0])
  im=np.prod(z).imag;leading=rho**3*(h*h/3)*np.dot(a,q)
  rows.append(dict(halfwidth=h,scenario=scenario,imaginary_windowed_cycle=im,leading_term=leading,
                   min_eigenvalue_in_kernel=mineig,positive_definite=mineig>0,
                   ratio_to_leading=(im/leading if abs(leading)>1e-15 else np.nan)))
df=pd.DataFrame(rows);df.to_csv(O/'compact_kernel_mechanism_ablation.csv',index=False)
print(df.to_string(index=False))
