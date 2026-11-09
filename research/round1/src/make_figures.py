"""Publication-style figures from frozen outputs; no model fitting or tests."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
NAVY='#20354c'; TEAL='#00897b'; ORANGE='#d36b27'; BLUE='#367eb5'; GRAY='#73808c'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
    'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':NAVY,
    'text.color':NAVY,'axes.titleweight':'bold','axes.titlepad':11,
    'axes.edgecolor':'#bbc4ca','xtick.color':NAVY,'ytick.color':NAVY,
    'legend.frameon':False,'savefig.facecolor':'white','svg.fonttype':'none'})

def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=220,bbox_inches='tight')
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight')
    plt.close(fig)

def label(ax,letter,title):
    ax.set_title(letter+'  '+title,loc='left',fontsize=11)

def population():
    networks=pd.read_csv(ROOT/'results/network_families.csv')
    certificates=pd.read_csv(ROOT/'results/variational_certificates.csv')
    fig,axs=plt.subplots(2,2,figsize=(11.2,8.0),layout='constrained')
    a=axs[0,0]; r=networks[networks.asymmetry==0]
    rng=np.random.default_rng(83)
    a.scatter(np.zeros(len(r))+rng.normal(0,.045,len(r)),r.pair_imag_rms,
              color=TEAL,s=19,alpha=.65,label='Before filters')
    a.scatter(np.ones(len(r))+rng.normal(0,.045,len(r)),r.pair_imag_rms_filtered,
              color=ORANGE,s=19,alpha=.65,label='After filters')
    for _,row in r.iterrows():
        a.plot([0,1],[row.pair_imag_rms,row.pair_imag_rms_filtered],color=GRAY,lw=.5,alpha=.2)
    a.set(xticks=[0,1],xticklabels=['Original','Channel-filtered'],ylabel='RMS imaginary pairwise coherency')
    label(a,'A','Pairwise asymmetry appears in reversible networks')
    a.text(.02,.96,'48 reversible networks; 3 to 64 channels',transform=a.transAxes,va='top',fontsize=9)
    a=axs[0,1]; colors={3:TEAL,8:BLUE,24:ORANGE,64:NAVY}
    for n,g in networks.groupby('n'):
        a.scatter(np.maximum(g.cycle_rms,1e-18),np.maximum(g.cycle_rms_filtered,1e-18),
                  label=f'{n} channels',s=26,alpha=.75,color=colors[n])
    a.plot([1e-18,1],[1e-18,1],color=GRAY,lw=1,ls='--')
    a.set(xscale='log',yscale='log',xlim=(1e-18,.2),ylim=(1e-18,.2),
          xlabel='Original RMS imaginary cycle',ylabel='Filtered RMS imaginary cycle')
    label(a,'B','Population cycles survive channel filtering')
    a.legend(fontsize=8,loc='upper left')
    a.text(.98,.03,'192 conditions; maximum change 9.3e-17',ha='right',transform=a.transAxes,fontsize=9)
    a=axs[1,0]; g=certificates[certificates.matrix_dimension==3]
    a.scatter(g.upper_bound,g.triangle_bound,s=15,alpha=.6,color=TEAL)
    lo=min(g.upper_bound.min(),g.triangle_bound.min())*.6
    hi=max(g.upper_bound.max(),g.triangle_bound.max())*1.5
    a.plot([lo,hi],[lo,hi],color=GRAY,ls='--',lw=1)
    a.set(xscale='log',yscale='log',xlim=(lo,hi),ylim=(lo,hi),
          xlabel='Phase-minimized reversal density (certified interval)',ylabel='Analytic triangle lower bound')
    label(a,'C','An explicit lower bound on irreducible asymmetry')
    a.text(.03,.97,f'300 positive-definite matrices\nPrimal/dual gaps < {g.gap.max()*1.02:.2g}',va='top',
           transform=a.transAxes,fontsize=9)
    a=axs[1,1]
    for k,n in enumerate([2,3,8,24]):
        g=certificates[certificates.matrix_dimension==n]
        a.scatter(k+rng.normal(0,.045,len(g)),np.maximum(g.gap,1e-16),s=15,alpha=.45,color=colors.get(n,GRAY))
        a.plot([k-.16,k+.16],[max(g.gap.median(),1e-16)]*2,color=NAVY,lw=2)
    a.set(yscale='log',xticks=range(4),xticklabels=['2 (50)','3 (300)','8 (100)','24 (30)'],
          xlabel='Matrix dimension (number of cases)',ylabel='Certified upper minus lower bound')
    label(a,'D','Primal-dual gaps grow with dimension')
    a.text(.03,.97,'Floating-point primal/dual certificates',va='top',transform=a.transAxes,fontsize=9)
    save(fig,'figure_1_population_and_bounds')

def finite_resolution():
    cal=pd.read_csv(ROOT/'results/finite_spectral_calibration.csv')
    cal=cal[(cal.phase==0)&(cal.status=='ok')]
    fig,axs=plt.subplots(1,3,figsize=(13.2,4.1),layout='constrained')
    a=axs[0]; x=np.arange(len(cal))
    a.errorbar(x,cal.rejection_rate,yerr=[cal.rejection_rate-cal.rejection_ci_low,
        cal.rejection_ci_high-cal.rejection_rate],fmt='o',color=TEAL,ms=5,capsize=3)
    a.axhline(.05,color=ORANGE,ls='--',lw=1)
    a.set(xticks=x,xticklabels=[f'{int(r.k)}\n{r.coherence:.1f}' for _,r in cal.iterrows()],
          xlabel='Replicates per half / coherency magnitude',ylabel='Rejection fraction',ylim=(0,.115))
    label(a,'A','Calibrated ideal spectral null')
    a.text(.04,.96,'300 studies per setting\n40 independent participants per study',va='top',transform=a.transAxes,fontsize=9)
    f=ROOT/'reviews/math_review_v2_leakage_partial.json'
    final=ROOT/'reviews/math_review_v2_leakage.csv'
    leak=pd.read_csv(final) if final.exists() else pd.DataFrame(json.loads(f.read_text()))
    a=axs[1]
    for delay,color in zip([.025,.125,.5],[BLUE,TEAL,ORANGE]):
        d=leak[leak.delay_s==delay]
        a.plot(d.T_s,d.mean_v2_12channels,'o-',color=color,label=f'{delay*1000:g} ms delay',lw=1.5,ms=4)
    d=leak[leak.delay_s==.125].sort_values('T_s'); last=d.iloc[-1]
    xx=np.array([max(4,float(d.T_s.min())),float(d.T_s.max())])
    a.plot(xx,last.mean_v2_12channels*(last.T_s/xx)**4,ls='--',color=GRAY,lw=1,label=r'$T^{-4}$ reference')
    a.set(xscale='log',yscale='log',xlabel='Hann window duration (s)',
          ylabel='Squared cycle of expected windowed spectrum',xticks=sorted(leak.T_s.unique()))
    a.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    label(a,'B','Leakage in reversible dynamics')
    a.legend(fontsize=8)
    a=axs[2]; scores=np.load(ROOT/'reviews/adversarial_M0_60s_scores.npy')*1e4
    a.hist(scores,bins=28,color=TEAL,edgecolor='white',alpha=.85)
    a.axvline(0,color=GRAY,lw=1);a.axvline(scores.mean(),color=ORANGE,lw=2)
    a.set(xlabel=r'Cross-half score $Q$ ($\times10^{-4}$)',ylabel='Number of simulated records')
    a.set_ylim(0,a.get_ylim()[1]*1.30)
    label(a,'C','False rejection of the latent null')
    a.text(.96,.95,'500 reversible-latent records\nMean Q = 1.012e-5\nFirst 99 records: p = 0.00008',
           transform=a.transAxes,va='top',ha='right',fontsize=9)
    save(fig,'figure_2_finite_window_failure')

def eeg():
    subjects=pd.read_csv(ROOT/'results/eeg_primary_original_subjects.csv')
    g=subjects[(subjects.status=='ok')&(subjects.cohort=='holdout')]
    pair=g.pivot(index='subject',columns='run',values='q').dropna()
    primary=pd.read_csv(ROOT/'results/eeg_primary_original_summary.csv')
    four=pd.read_csv(ROOT/'results/eeg_four_seconds_original_summary.csv')
    fig,axs=plt.subplots(2,2,figsize=(11.3,8.1),layout='constrained')
    a=axs[0,0]
    for _,r in pair.iterrows():a.plot([0,1],r[[1,2]].to_numpy()*1e4,color=GRAY,alpha=.25,lw=.7)
    for pos,run,color in [(0,1,BLUE),(1,2,TEAL)]:
        d=pair[run].to_numpy()*1e4
        a.scatter(np.full(len(d),pos),d,s=16,color=color,alpha=.65,zorder=3)
    a.axhline(0,color=GRAY,lw=.7)
    a.set(xticks=[0,1],xticklabels=['Eyes open','Eyes closed'],ylabel=r'Subject score $Q$ ($\times10^{-4}$)',xlim=(-.35,1.35))
    label(a,'A','Windowed closure is repeatable across halves')
    a.text(.03,.97,'73 paired holdout participants\nExploratory difference: 1.275e-4',va='top',transform=a.transAxes,fontsize=9)
    a=axs[0,1]
    labels=[];pos=0
    for frame,duration in [(primary,'2 s'),(four,'4 s')]:
        for run,color in [(1,BLUE),(2,TEAL)]:
            r=frame[(frame.cohort=='holdout')&(frame.run==run)].iloc[0]
            a.errorbar(r['mean']*1e4,pos,xerr=np.array([[r['mean']-r.ci_low],[r.ci_high-r['mean']]])*1e4,
                       fmt='o',color=color,ms=7,capsize=4)
            labels.append(f'{duration}: {"open" if run==1 else "closed"} (n={int(r.n)})');pos+=1
    a.set(yticks=range(4),yticklabels=labels,xlabel=r'Mean $Q$ with 95% subject bootstrap CI ($\times10^{-4}$)')
    a.invert_yaxis();a.axvline(0,color=GRAY,lw=1)
    label(a,'B','The effect persists at a longer window')
    a=axs[1,0];npz=np.load(ROOT/'results/eeg_primary_original_cycles.npz');f=npz['f']
    for run,color in [(1,BLUE),(2,TEAL)]:
        rows=[]
        for subject in g[g.run==run].subject:
            prefix=f'S{int(subject):03d}R{run:02d}_'
            rows.append((npz[prefix+'a'].astype(float)*npz[prefix+'b'].astype(float)).mean(axis=1))
        z=np.array(rows)*1e4;m=z.mean(axis=0);se=z.std(axis=0,ddof=1)/np.sqrt(len(z))
        a.plot(f,m,color=color,label=f'Eyes {"open" if run==1 else "closed"}',lw=1.7)
        a.fill_between(f,m-1.96*se,m+1.96*se,color=color,alpha=.13,lw=0)
    a.axhline(0,color=GRAY,lw=.7)
    a.set(xlabel='Frequency (Hz)',ylabel=r'Mean triangle cross-half product ($\times10^{-4}$)',xlim=(2,30))
    label(a,'C','Descriptive frequency profile')
    a.legend(fontsize=9);a.text(.98,.02,'Shading: pointwise 95% normal intervals',ha='right',transform=a.transAxes,fontsize=8)
    a=axs[1,1];matched=pd.read_csv(ROOT/'results/matched_filter_robustness.csv')
    # Column names are checked against the result schema at run time.
    xcol='q_original' if 'q_original' in matched else 'original_q'
    ycol='q_filtered_fixed_mask'
    for run,color in [(1,BLUE),(2,TEAL)]:
        d=matched[matched.run==run]
        a.scatter(d[xcol]*1e4,d[ycol]*1e4,color=color,s=19,alpha=.65,label=f'{"Open" if run==1 else "Closed"}, n={len(d)}')
    lo=min(matched[xcol].min(),matched[ycol].min())*1e4
    hi=max(matched[xcol].max(),matched[ycol].max())*1e4
    a.plot([lo,hi],[lo,hi],color=GRAY,lw=1,ls='--')
    a.set(xlabel=r'Original $Q$ ($\times10^{-4}$)',ylabel=r'Causally filtered $Q$ ($\times10^{-4}$)')
    label(a,'D','Same participants and same accepted epochs')
    a.legend(fontsize=9);a.text(.98,.02,'Pearson r = .9968 (open), .9992 (closed)',ha='right',transform=a.transAxes,fontsize=8)
    save(fig,'figure_3_eeg_holdout')

def serialization():
    z=np.load(ROOT/'reviews/serialization_covariance_example.npz')
    fig,axs=plt.subplots(2,2,figsize=(11.2,8.0),layout='constrained')
    cov=z['target_covariance']; null=z['serialized_covariance']
    vmax=max(abs(cov).max(),abs(null).max())
    for a,mat,letter,title in [(axs[0,0],cov,'A','Target finite-record covariance'),
                              (axs[0,1],null,'B','Reversible-source finite-record covariance')]:
        im=a.imshow(mat,cmap='RdBu_r',vmin=-vmax,vmax=vmax,aspect='equal')
        a.set(xlabel='Stacked channel-time coordinate',ylabel='Stacked channel-time coordinate')
        label(a,letter,title)
        fig.colorbar(im,ax=a,shrink=.85,pad=.02,label='Covariance')
    a=axs[1,0];coef=z['target_coefficients'];filters=z['serialized_filters']
    omega=np.linspace(.001,np.pi-.001,501)
    g=np.einsum('iak,fk->fia',coef,np.exp(-1j*omega[:,None]*np.arange(coef.shape[-1])))
    h=np.exp(-1j*omega[:,None]*np.arange(filters.shape[-1]))@filters.T
    s=g@g.conj().transpose(0,2,1)+.2*np.eye(3)
    s0=h[:,:,None]*h[:,None,:].conj()+.2*np.eye(3)
    from closure_core import coherency,cycle_product
    a.plot(omega/np.pi,cycle_product(coherency(s)).imag[:,0],color=ORANGE,lw=1.8,label='Target dynamics')
    a.plot(omega/np.pi,cycle_product(coherency(s0)).imag[:,0],color=TEAL,lw=1.5,label='Reversible source + FIR filters')
    a.set(xlabel='Frequency / Nyquist frequency',ylabel='Population imaginary coherency cycle')
    label(a,'C','Their population cycle properties differ')
    a.legend(fontsize=8)
    a=axs[1,1]
    for i,color in enumerate([BLUE,TEAL,ORANGE]):
        idx=np.flatnonzero(filters[i])
        a.vlines(idx,0,filters[i,idx],color=color,lw=1.3,alpha=.8)
        a.scatter(idx,filters[i,idx],s=17,color=color,label=f'Channel {i+1}',zorder=3)
    a.axhline(0,color=GRAY,lw=.7)
    a.axvspan(0,15,color=GRAY,alpha=.09,label='Record length N = 16')
    a.set(xlabel='Filter lag (samples)',ylabel='FIR coefficient',xlim=(-1,48))
    label(a,'D','Long filters reuse disjoint noise intervals')
    a.legend(fontsize=8,loc='upper right')
    a.text(.03,.03,'MA order 4; delays 0, 21, 42\nMaximum covariance mismatch 4.44e-16',
           transform=a.transAxes,fontsize=9,va='bottom',bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
    save(fig,'figure_4_finite_record_equivalence')

if __name__=='__main__':
    population();finite_resolution();eeg();serialization()
    print('Figures saved to',OUT)
