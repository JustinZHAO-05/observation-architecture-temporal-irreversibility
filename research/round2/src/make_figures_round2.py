"""Standalone, reproducible figures; no data are refitted while plotting."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from theory_round2 import exact_latent_lags,ma_spectrum
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results';F=ROOT/'figures';F.mkdir(exist_ok=True)
def save(fig,name):
 fig.tight_layout()
 for ext in ['png','pdf','svg']:fig.savefig(F/(name+'.'+ext),dpi=200,bbox_inches='tight')
 plt.close(fig)

def main():
 w=np.linspace(0,np.pi,401);g,k=exact_latent_lags(.9);p=[];lifted=[]
 for omega in w:
  S=ma_spectrum(.9,omega);G=g[0]+2*np.cos(omega)*g[1]+2*np.cos(2*omega)*g[2]
  H=np.c_[np.eye(3),np.exp(-1j*omega)*np.eye(3)];T=H@G@H.conj().T
  p.append((S[0,1]*S[1,2]*S[2,0]).imag);lifted.append((T[0,1]*T[1,2]*T[2,0]).imag)
 fig,ax=plt.subplots(figsize=(7.4,4.4));ax.plot(w/np.pi,p,label='Irreversible target')
 ax.plot(w[::16]/np.pi,np.array(lifted)[::16],ls='none',marker='o',fillstyle='none',label='Reversible latent + one-step delay + mixing')
 ax.axhline(0,ls=':',label='Real-spectrum latent process');ax.set(xlabel='Frequency / pi (rad per sample)',ylabel='Imaginary spectral triangle',title='Identical observations from different latent time symmetries')
 ax.legend(fontsize=8,loc='lower center');ax.grid(alpha=.2);save(fig,'01_exact_observational_equivalence')
 d=pd.read_csv(R/'latency_power_curves.csv');num=pd.read_csv(R/'latency_cost_lp_intervals.csv')
 fig,ax=plt.subplots(figsize=(7.4,4.5))
 for b,g in d.groupby('b'):
  ax.loglog(g.theta,g.minimum_power_ratio,label=f'Antisymmetric strength b={b:g}')
 ax.set(xlabel='Observation phase delay theta (rad)',ylabel='Minimum latent / observed spectral trace',title='Smaller latency requires larger hidden signal power')
 ax.legend(fontsize=8);ax.grid(alpha=.2,which='both');save(fig,'02_latency_power_tradeoff')
 d=pd.read_csv(R/'certificate_summary.csv');sub=d[d.model.str.startswith('alternative')]
 labels=[];mat=[]
 for (model,delay),g in sub.groupby(['model','max_delay']):
  labels.append(f"b={model.split('_')[1]}, delay={delay}");mat.append(g.sort_values('N').rejection_rate.to_numpy())
 fig,ax=plt.subplots(figsize=(7.4,5.4));im=ax.imshow(mat,vmin=0,vmax=1,aspect='auto')
 ax.set_xticks(range(4),['2,048','8,192','32,768','131,072']);ax.set_yticks(range(len(labels)),labels)
 ax.set(xlabel='Record length (samples)',title='Positive finite-grid lower bounds: all alternatives retained')
 fig.colorbar(im,ax=ax,label='Detection fraction');save(fig,'03_finite_record_power')
 d=pd.read_csv(R/'continuous_rate_replicates.csv');fig,ax=plt.subplots(figsize=(7.4,4.5))
 for delay,g in d.groupby('max_delay'):
  z=g.groupby('N').rate_lower;med=z.median();q1=z.quantile(.25);q3=z.quantile(.75)
  ax.errorbar(med.index,med,yerr=np.vstack([med-q1,q3-med]),marker='o',capsize=4,label=f'Max. channel delay {delay} samples')
 ax.set_xscale('log',base=2);ax.set_xticks([32768,131072,524288],['32,768','131,072','524,288'])
 ax.set(xlabel='Record length (samples)',ylabel='Certified rate lower bound (nats/sample)',title='Continuous-frequency certification becomes informative')
 ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.legend(fontsize=8);ax.grid(alpha=.2)
 ax.text(.02,.96,'Medians and interquartile ranges over 64 simulations',transform=ax.transAxes,va='top',fontsize=8)
 save(fig,'04_certified_rate')
 d=pd.read_csv(R/'eeg_complete_window_records.csv');fig,ax=plt.subplots(figsize=(6.6,5.6));allv=[]
 for run,g in d.groupby('run'):
  p=g.pivot(index='subject',columns='reference',values='q');allv.extend(p.to_numpy().ravel())
  ax.scatter(p.original,p.average,marker='o' if run==1 else '^',s=28,alpha=.75,label=f"{'Eyes open' if run==1 else 'Eyes closed'} (n={len(p)})")
 pad=.04*(max(allv)-min(0,min(allv)));lo=min(0,min(allv))-pad;hi=max(allv)+pad;ax.plot([lo,hi],[lo,hi],ls='--',label='Equal score')
 ax.set(xlabel='Original-reference Q',ylabel='Average-reference Q',title='Same subjects and windows, different EEG reference',xlim=(lo,hi),ylim=(lo,hi))
 ax.ticklabel_format(style='sci',scilimits=(0,0));ax.legend(fontsize=8);ax.grid(alpha=.2);save(fig,'05_eeg_same_window_reference')
 d=pd.read_csv(R/'coordinate_validation.csv');fig,ax=plt.subplots(figsize=(7.2,4.4));ratio=d.triangle_bound_after/d.triangle_bound_before
 ax.hist(ratio,bins=30);ax.set(xlabel='Triangle bound after / before real orthogonal mixing',ylabel='Number of rotations',title='The phase-relaxed bound depends on the spatial basis')
 ax.text(.97,.95,'Raw Gaussian reversal density is unchanged\n600 random orthogonal transformations',transform=ax.transAxes,ha='right',va='top',fontsize=9)
 save(fig,'06_coordinate_dependence')
if __name__=='__main__':main()
