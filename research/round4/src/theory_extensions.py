"""Finite-order exact lifts and broadband trace optimum. Failed trial degrees are retained.
Grid positivity bounds include a derivative allowance; they use floating-point arithmetic.
"""
from pathlib import Path
import json,time
import numpy as np
import pandas as pd
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def rotational_optimum(w,beta,pole=0.):
 c=np.cos(w);s=np.sin(w);b=beta*s;t=(1+beta*beta*c*c)/(1+abs(c)*np.sqrt(1-b*b))
 q=(1-t)/(2*c) if abs(c)>1e-9 else 0.;j=beta/2;I=np.eye(2);J=np.array([[0.,1.],[-1.,0.]])
 G=np.block([[t/2*I,q*I+j*J],[q*I-j*J,t/2*I]])
 g=(1-pole*pole)/(1-2*pole*np.cos(w)+pole*pole)
 return G*g,g*(I+1j*b*J),np.c_[I,np.exp(-1j*w)*I],t,g

def broadband():
 rows=[];curve=[]
 for beta in [.2,.5,.8,.9,.99]:
  for pole in [0.,.4,.8]:
   def f(w):
    *_,t,g=rotational_optimum(w,beta,pole);return t*g
   val,err=quad(f,-np.pi,np.pi,points=[-np.pi/2,0,np.pi/2],epsabs=1e-11,epsrel=1e-11,limit=200)
   maxerr=0.;mineig=0.
   for w in np.linspace(-np.pi,np.pi,2049):
    G,S,H,t,g=rotational_optimum(w,beta,pole);maxerr=max(maxerr,float(np.max(abs(H@G@H.conj().T-S))));mineig=min(mineig,float(np.linalg.eigvalsh(G).min()))
    if pole==0:curve.append(dict(beta=beta,w=w,pointwise_trace_ratio=t))
   rows.append(dict(beta=beta,pole=pole,optimal_total_ratio=val/(2*np.pi),baseline_ratio=1.,power_reduction=1-val/(2*np.pi),quad_error=err/(2*np.pi),max_spectral_error=maxerr,min_eigenvalue=mineig))
 pd.DataFrame(rows).to_csv(OUT/'broadband_optima.csv',index=False);pd.DataFrame(curve).to_csv(OUT/'broadband_pointwise_curves.csv',index=False);return rows

def general_finite_support():
 rng=np.random.default_rng(2026110905);F=4096;w=2*np.pi*np.arange(F)/F;rows=[];attempts=[]
 for d in [2,3,6]:
  for q in [1,2,3]:
   for rep in range(8):
    A=rng.normal(size=(q+1,d,d))/np.sqrt(d*(q+1));A[0]+=1.2*np.eye(d)
    lags=[sum(A[j+l]@A[j].T for j in range(q+1-l)) for l in range(q+1)];lags[0]+=.5*np.eye(d)
    R=np.broadcast_to(lags[0],(F,d,d)).copy();Ys=np.zeros_like(R);u0=np.ones(F);um=np.zeros(F)
    for l in range(1,q+1):
     R+=np.cos(l*w)[:,None,None]*(lags[l]+lags[l].T)
     ul=np.ones(F) if l==1 else (2*np.cos(w) if l==2 else 2*np.cos(w)*u0-um)
     Ys-=ul[:,None,None]*(lags[l]-lags[l].T);um,u0=u0,ul
    ev,U=np.linalg.eigh(R);Ri=(U*(ev**-.5)[:,None,:])@U.transpose(0,2,1)
    aa=np.linalg.eigvalsh(1j*(Ri@Ys@Ri));a=np.max(abs(aa),axis=1);bsq=np.sin(w)**2*a*a
    assert bsq.max()<1
    Vfull=((a*a+(1-bsq)/2)/2)[:,None,None]*R;vc=np.fft.fft(Vfull,axis=0)/F;accepted=None
    for m in [2,4,8,16,32,64,128,256]:
     V=np.broadcast_to(vc[0].real,(F,d,d)).copy()
     for ell in range(1,m+1):V+=2*(1-ell/(m+1))*np.cos(ell*w)[:,None,None]*vc[ell].real
     c=np.cos(w)[:,None,None];ss=np.sin(w)[:,None,None];P=R+(2*c*c-1)*V;Q=-c*V+Ys/2
     G=np.concatenate([np.concatenate([P,Q],axis=2),np.concatenate([Q.transpose(0,2,1),V],axis=2)],axis=1)
     degree=max(q,m+2);gc=np.fft.fft(G,axis=0)/F;deriv=2*sum(ell*np.linalg.norm(gc[ell],2) for ell in range(1,degree+1))
     mingrid=float(np.linalg.eigvalsh(G).min());Fcheck=F;cert=mingrid-np.pi/F*deriv
     attempts.append(dict(d=d,target_order=q,rep=rep,approximation_degree=m,latent_order=degree,verification_grid=Fcheck,min_grid_eigenvalue=mingrid,derivative_bound=deriv,all_frequency_lower=cert))
     if mingrid>0 and cert<=0:
      need=int(2**np.ceil(np.log2(1.2*np.pi*deriv/mingrid)))
      if need<=32768:
       Fcheck=max(F*2,need);buf=np.zeros((Fcheck,2*d,2*d),complex);buf[:degree+1]=gc[:degree+1];buf[-degree:]=gc[-degree:]
       fine=np.fft.ifft(buf*Fcheck,axis=0).real;mingrid=float(np.linalg.eigvalsh(fine).min());cert=mingrid-np.pi/Fcheck*deriv
       attempts.append(dict(d=d,target_order=q,rep=rep,approximation_degree=m,latent_order=degree,verification_grid=Fcheck,min_grid_eigenvalue=mingrid,derivative_bound=deriv,all_frequency_lower=cert))
     if cert>1e-8:
      rec=P+V+c*(Q+Q.transpose(0,2,1))+1j*ss*(Q-Q.transpose(0,2,1));target=R+1j*ss*Ys
      err=float(np.linalg.norm(rec-target,axis=(1,2)).max()/np.linalg.norm(target,axis=(1,2)).max())
      accepted=dict(d=d,target_order=q,rep=rep,latent_order=degree,verification_grid=Fcheck,all_frequency_lower=cert,max_relative_error=err)
      if d==3 and q==3 and rep==0:np.savez_compressed(OUT/'finite_support_example.npz',target_lags=np.array(lags),latent_lags=gc[:degree+1].real,w=w,G=G,target=target)
      break
    if accepted is None:accepted=dict(d=d,target_order=q,rep=rep,latent_order=-1,verification_grid=Fcheck,all_frequency_lower=cert,max_relative_error=np.nan)
    rows.append(accepted)
   print('completed finite-support',d,q,flush=True)
 pd.DataFrame(rows).to_csv(OUT/'finite_support_lifts.csv',index=False);pd.DataFrame(attempts).to_csv(OUT/'finite_support_attempts.csv',index=False);return rows

def main():
 t=time.perf_counter();br=broadband();fs=general_finite_support()
 r=dict(broadband_settings=len(br),max_broadband_reconstruction_error=max(x['max_spectral_error'] for x in br),min_optimal_latent_eigenvalue=min(x['min_eigenvalue'] for x in br),finite_order_targets=len(fs),certified_positive=int(sum(x['all_frequency_lower']>0 for x in fs)),max_latent_order=int(max(x['latent_order'] for x in fs)),max_reconstruction_error=float(max(x['max_relative_error'] for x in fs)),seconds=time.perf_counter()-t)
 (OUT/'theory_extensions_summary.json').write_text(json.dumps(r,indent=2));print(r)
if __name__=='__main__':main()
