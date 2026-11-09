from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'results';F=R/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
def save(fig,name):
 fig.tight_layout()
 fig.savefig(F/(name+'.pdf'))
 fig.savefig(F/(name+'.png'),dpi=240)
 plt.close(fig)

w=pd.read_csv(O/'white_latent_lift.csv')
fig,ax=plt.subplots(1,2,figsize=(8.0,3))
for b,g in w[w.d==3].groupby('b'):
 ax[0].scatter(g.w.iloc[::4]/np.pi,g.latent_min_eigenvalue.iloc[::4],s=8,label=f'b={b}')
ax[0].set(xlabel=r'Frequency / $\pi$',ylabel='Smallest latent covariance eigenvalue',title='Temporally white latent representation')
ax[0].legend(frameon=False,fontsize=7)
for d,g in w.groupby('d'):
 ax[1].scatter(np.full(len(g)//100+1,d)[:len(g.iloc[::100])],g.rel_error.iloc[::100],s=12,alpha=.65,label=f'd={d}')
ax[1].set(xlabel='Observed dimension',ylabel='Relative spectral reconstruction error',yscale='log',title='23,520 independent checks')
ax[1].set_ylim(1e-18,1e-13);save(fig,'R3_S9_white_latent')

low=pd.read_csv(O/'joint_low_frequency.csv')
fig,ax=plt.subplots(1,2,figsize=(8.2,3.1))
for beta,g in low.groupby('beta'):
 ax[0].plot(g.theta,g.exact_cost,label=f'β={beta:g}')
 ax[1].plot(g.theta,g.exact_cost/g.low_freq_limit,label=f'β={beta:g}')
ax[0].set(xscale='log',xlabel='Delay phase θ (rad)',ylabel='Minimum spectral trace ratio',title='Physical joint limit: b=β sin θ')
ax[1].axhline(1,ls='--',lw=.9)
ax[1].set(xscale='log',xlabel='Delay phase θ (rad)',ylabel='Ratio to (1+β²)/2',title='Finite low-frequency limit')
ax[0].legend(frameon=False,fontsize=7);save(fig,'R3_S10_joint_limit')

ab=pd.read_csv(O/'compact_kernel_mechanism_ablation.csv')
fig,ax=plt.subplots(1,2,figsize=(8.2,3.1))
for scenario,g in ab.groupby('scenario'):
 ax[0].plot(g.halfwidth,g.imaginary_windowed_cycle,marker='o',markersize=3,label=scenario.replace('_',' '))
g=ab[ab.scenario=='both_active']
ax[0].plot(g.halfwidth,g.leading_term,ls='--',label='leading theory')
ax[0].set(xlabel='Frequency-kernel halfwidth h',ylabel='Imaginary cycle after averaging',title='Positive-definite spectral mechanism controls')
ax[0].legend(frameon=False,fontsize=7)
ax[1].plot(g.halfwidth,g.ratio_to_leading,marker='o',markersize=3)
ax[1].axhline(1,ls='--',lw=.9)
ax[1].set(xlabel='Frequency-kernel halfwidth h',ylabel='Exact / leading term',title='Approach to the local expansion')
save(fig,'R3_S11_window_ablation')

ca=pd.read_csv(O/'independent_scale_calibration.csv')
fig,ax=plt.subplots(1,2,figsize=(8.2,3.1))
for b,g in ca.groupby('b'):
 p=g.groupby('m').positive_certificate.mean()
 ax[0].plot(p.index,p.values,marker='o',label=f'b={b:g}')
g=ca[ca.b==.9]
for m,gm in g.groupby('m'):
 ax[1].scatter(np.full(len(gm),m),gm.sigma2_upper,s=6,alpha=.25)
ax[1].plot(g.groupby('m').sigma2_upper.median(),marker='o',label='median')
ax[1].axhline(1,ls='--',label='true scale')
ax[0].set(xlabel='Independent calibration length (samples)',ylabel='Positive certificate frequency',ylim=(-.05,1.05),title='Finite-record, separately calibrated detection')
ax[0].legend(frameon=False,fontsize=7)
ax[1].set(xlabel='Independent calibration length (samples)',ylabel='One-sided upper scale bound',title='Calibration uncertainty and conservatism')
ax[1].legend(frameon=False,fontsize=7)
save(fig,'R3_S12_independent_calibration')
print('figures generated',len(list(F.glob('*.pdf'))))
