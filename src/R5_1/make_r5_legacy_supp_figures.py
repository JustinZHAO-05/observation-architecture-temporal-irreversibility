"""Regenerate R3-added Supplementary Figs. S10-S12 from archived numeric results.
All scientific parameters, plotted values, source CSVs, and formulae are preserved.
Only redundant plot headers are removed and placed in captions.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];D=R/'results'; O=R/'manuscript'/'supp_figures'; F=R/'figures';F.mkdir(exist_ok=True)
COL=['#0072B2','#D55E00','#009E73','#CC79A7']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,'legend.fontsize':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'lines.linewidth':1.3})
def base():
 fig,ax=plt.subplots(1,2,figsize=(8.0,3.0));
 for i,letter in enumerate('ab'): ax[i].text(-.13,1.06,letter,transform=ax[i].transAxes,fontweight='bold',fontsize=12,va='top',ha='left')
 return fig,ax
def finish(fig,name):
 fig.subplots_adjust(left=.10,right=.985,bottom=.22,top=.93,wspace=.36)
 for ext in ['pdf','png','svg']: fig.savefig(F/f'{name}.{ext}',dpi=280)
 fig.savefig(O/f'{name}.pdf');plt.close(fig)
low=pd.read_csv(D/'joint_low_frequency.csv');fig,ax=base()
for i,(beta,g) in enumerate(low.groupby('beta')):
 ax[0].plot(g.theta,g.exact_cost,color=COL[i],lw=1.5,label=rf'$\beta={beta:g}$')
 ax[1].plot(g.theta,g.exact_cost/g.low_freq_limit,color=COL[i],lw=1.5)
ax[0].set(xscale='log',xlabel=r'Delay phase $\theta$ (rad)',ylabel='Minimum spectral-trace ratio')
ax[1].axhline(1,ls='--',color='#666666',lw=.9)
ax[1].set(xscale='log',xlabel=r'Delay phase $\theta$ (rad)',ylabel=r'Ratio to $(1+\beta^2)/2$')
ax[0].legend(frameon=False,fontsize=8)
finish(fig,'figS10')

ab=pd.read_csv(D/'compact_kernel_mechanism_ablation.csv');fig,ax=base()
names={'both_active':'Both active','flat_amplitudes':'Flat amplitudes','equal_phase_response':'Equal phase response'}
for i,(scenario,g) in enumerate(ab.groupby('scenario')):
 ax[0].plot(g.halfwidth,g.imaginary_windowed_cycle,marker='o',markersize=2.8,color=COL[i],label=names.get(scenario,scenario.replace('_',' ').capitalize()))
g=ab[ab.scenario=='both_active'];ax[0].plot(g.halfwidth,g.leading_term,ls='--',lw=1,color='#444444',label='Leading term')
ax[0].set(xlabel=r'Kernel halfwidth $h$',ylabel='Imaginary averaged cycle');ax[0].legend(frameon=False,fontsize=7.2)
ax[1].plot(g.halfwidth,g.ratio_to_leading,color=COL[0],marker='o',markersize=3)
ax[1].axhline(1,color='#666666',lw=.8,ls='--');ax[1].set(xlabel=r'Kernel halfwidth $h$',ylabel='Exact / leading term')
finish(fig,'figS11')

ca=pd.read_csv(D/'independent_scale_calibration.csv');fig,ax=base()
for i,(b,g) in enumerate(ca.groupby('b')):
 p=g.groupby('m').positive_certificate.mean();ax[0].plot(p.index,p.values,color=COL[i],marker='o',markersize=4,label=f'b={b:g}')
ax[0].set(xlabel='Independent calibration length (samples)',ylabel='Positive-certificate fraction',ylim=(-.04,1.04));ax[0].legend(frameon=False,fontsize=8)
g=ca[ca.b==.9]
for m,gm in g.groupby('m'):ax[1].scatter(np.full(len(gm),m),gm.sigma2_upper,s=8,alpha=.20,color=COL[0])
ax[1].plot(g.groupby('m').sigma2_upper.median(),marker='o',lw=1.5,color=COL[1],label='Median')
ax[1].axhline(1,ls='--',lw=.9,color='#555555',label='True scale')
ax[1].set(xlabel='Independent calibration length (samples)',ylabel='Upper confidence bound on scale');ax[1].legend(frameon=False,fontsize=8)
finish(fig,'figS12')
print('Regenerated supplemental figures S10, S11, S12.')
