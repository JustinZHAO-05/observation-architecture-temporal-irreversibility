"""Quantitative panels from archived CSV/NPZ. No generated or illustrative data.
Each panel is drawn separately, then assembled as vector PDF pages.
"""
from pathlib import Path
import numpy as np,pandas as pd
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import beta as betadist
import fitz
R=Path(__file__).resolve().parents[1];O=R/'figures';O.mkdir(exist_ok=True);P=O/'panels';P.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'legend.fontsize':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'lines.linewidth':1.4})
COL=['#0072B2','#D55E00','#009E73','#555D69']
def panel(name,draw,w=3.3,h=2.6):
 fig,ax=plt.subplots(figsize=(w,h));draw(ax);fig.tight_layout(pad=.7)
 for ext in ['pdf','svg','png']:fig.savefig(P/(name+'.'+ext),dpi=240)
 plt.close(fig);return P/(name+'.pdf')
def combine(name,names,widths=None):
 docs=[fitz.open(P/(n+'.pdf')) for n in names];widths=widths or [d[0].rect.width for d in docs];height=max(d[0].rect.height for d in docs)+16
 out=fitz.open();page=out.new_page(width=sum(widths)+12*(len(names)-1),height=height);x=0
 for i,(d,w) in enumerate(zip(docs,widths)):
  page.show_pdf_page(fitz.Rect(x,16,x+w,height),d,0,keep_proportion=True)
  page.insert_text((x+3,11),chr(97+i),fontname='hebo',fontsize=11);x+=w+12
 out.save(O/(name+'.pdf'));page.get_pixmap(matrix=fitz.Matrix(2,2)).save(O/(name+'.png'));out.close()
 for d in docs:d.close()
 return O/(name+'.pdf')
ca=pd.read_csv(R/'results/unknown_shape_calibration_replicates.csv');df=pd.read_csv(R/'results/unknown_shape_test_replicates.csv')

def calratio(ax):
 g=ca[(ca.b==.9)&(ca.L==1)&np.isfinite(ca.B_upper)]
 for i,(m,z) in enumerate(g.groupby('m')):
  y=z.ratio;ax.scatter(np.full(len(y),i)+np.linspace(-.12,.12,len(y)),y,s=5,alpha=.23,color=COL[0]);q=y.quantile([.1,.5,.9]).values
  ax.errorbar(i,q[1],yerr=[[q[1]-q[0]],[q[2]-q[1]]],fmt='o',ms=5,capsize=3,color=COL[1])
 ax.axhline(1,ls='--',lw=1,color=COL[3]);ax.set(xticks=range(3),xticklabels=['4,096','16,384','65,536'],xlabel='Calibration length m',ylabel=r'Upper bound / true grid maximum')

panel('calibration_ratio',calratio)
def power(ax):
 g=df[(df.model=='MA1_unknown_shape')&(df.b==.9)];q=g.groupby(['N','m']).positive.mean().unstack()
 im=ax.imshow(q.values,vmin=0,vmax=1,cmap='Blues',aspect='auto')
 ax.set(xticks=range(4),xticklabels=['1,024','4,096','16,384','65,536'],yticks=range(3),yticklabels=['32,768','131,072','262,144'],xlabel='Calibration length m',ylabel='Test length N')
 ax.tick_params(axis='x',rotation=35)
 for i in range(3):
  for j in range(4):ax.text(j,i,'A' if j==0 else f'{q.values[i,j]:.0%}',ha='center',va='center',color='white' if q.values[i,j]>.5 else 'black',fontsize=8)
 # A is defined in the caption; avoid axis-label overlap.
panel('calibration_power',power)
def arpower(ax):
 g=df[(df.model=='ARMA_unknown_shape')&(df.b==.9)&(df.N==524288)]
 for i,(a,z) in enumerate(g.groupby('ar')):
  k=int(z.positive.sum());n=len(z);hi=betadist.ppf(.975,k+1,n-k) if k<n else 1;lo=betadist.ppf(.025,k,n-k+1) if k else 0
  ax.errorbar(i,k/n,yerr=[[k/n-lo],[hi-k/n]],fmt='o',capsize=5,color=COL[0])
 ax.set(xlim=(-.5,1.5),ylim=(-.008,.1),xticks=[0,1],xticklabels=['a = 0.3','a = 0.6'],ylabel='Positive-certificate fraction')

panel('long_correlation_power',arpower)
# Main assembly follows after all panels are available.
# Finite-order construction
f=pd.read_csv(R/'results/finite_support_lifts.csv')
def orders(ax):
 for k,d in enumerate([2,3,6]):
  z=f[f.d==d];ax.scatter(z.target_order+(k-1)*.10,z.latent_order,s=25,marker=['o','s','^'][k],color=COL[k],label=f'd = {d}',alpha=.75)
 ax.set(xticks=[1,2,3],xlabel='Target moving-average order',ylabel='Accepted latent covariance order');ax.legend(frameon=False)
panel('finite_orders',orders)
def margins(ax):
 for k,d in enumerate([2,3,6]):
  z=f[f.d==d];ax.scatter(z.all_frequency_lower,z.max_relative_error,s=25,marker=['o','s','^'][k],color=COL[k],label=f'd = {d}')
 ax.set(xscale='log',yscale='log',xlabel='All-frequency positivity margin',ylabel='Relative reconstruction error');ax.legend(frameon=False)
panel('finite_margins',margins)
combine('figS13',['finite_orders','finite_margins'])
# Broadband resource
b=pd.read_csv(R/'results/broadband_optima.csv');curve=pd.read_csv(R/'results/broadband_pointwise_curves.csv')
def costs(ax):
 for k,p in enumerate([0.,.4,.8]):
  z=b[b.pole==p];ax.plot(z.beta,z.optimal_total_ratio,marker=['o','s','^'][k],color=COL[k],label=f'color pole = {p:g}')
 ax.axhline(1,color=COL[3],ls='--',label='simple feasible baseline');ax.set(xlabel=r'Asymmetry parameter $\beta$',ylabel='Integrated minimum trace ratio');ax.legend(frameon=False,loc='lower right')
panel('broad_cost',costs)
def joint(ax):
 for k,be in enumerate([.2,.5,.8,.9]):
  z=curve[(curve.beta==be)&(curve.w>=0)];ax.plot(z.w/np.pi,z.pointwise_trace_ratio,color=COL[k],label=rf'$\beta={be}$')
 ax.set(xlabel=r'Frequency $\omega/\pi$',ylabel='Pointwise trace ratio');ax.legend(frameon=False,ncol=2)
panel('broad_joint',joint)
combine('figS14',['broad_cost','broad_joint'])
# Validity and misspecification
st=pd.read_csv(R/'results/misspecification_stress.csv')
def coverage(ax):
 vals=[1.,1.,float(st[st.condition=='misspecified_finite_support'].envelope_covers.mean()),float(st[st.condition=='valid_tail_envelope'].envelope_covers.mean())]
 labels=['MA(1)','AR--MA','Wrong tail','Valid tail'];ax.bar(range(4),vals,color=[COL[0],COL[0],COL[1],COL[0]],width=.6)
 ax.set(xticks=range(4),xticklabels=labels,ylim=(0,1.12),ylabel='Spectral-envelope coverage')
panel('coverage_conditions',coverage)
def lowerdist(ax):
 g=df[(df.model=='MA1_unknown_shape')&(df.b==.65)&(df.m==16384)]
 data=[z.lower.values for _,z in g.groupby('N')];ax.boxplot(data,tick_labels=['32,768','131,072','262,144'],showfliers=False,widths=.5)
 ax.set(xlabel='Test length N',ylabel='Maximum certified density');ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,-3));
panel('weaker_signal',lowerdist)
combine('figS15',['coverage_conditions','weaker_signal'])
# Exact transformations
ed=pd.read_csv(R/'results/eeg_known_transformations.csv')
def ecycle(ax):
 for i,name in enumerate(['diagonal_frequency_response','orthogonal_spatial_rotation']):
  z=ed[ed['transform']==name].max_cycle_change;ax.scatter(np.full(len(z),i)+np.linspace(-.1,.1,len(z)),np.maximum(z,1e-17),s=12,alpha=.5,color=COL[i])
 ax.set(xticks=[0,1],xticklabels=['Diagonal\nresponse','Orthogonal\nrotation'],yscale='log',ylabel='Maximum normalized-cycle change')
panel('eeg_cycle',ecycle)
def eraw(ax):
 for i,name in enumerate(['diagonal_frequency_response','orthogonal_spatial_rotation']):
  z=ed[ed['transform']==name].max_relative_raw_reversal_change;ax.scatter(np.full(len(z),i)+np.linspace(-.1,.1,len(z)),np.maximum(z,1e-17),s=12,alpha=.5,color=COL[i])
 ax.set(xticks=[0,1],xticklabels=['Diagonal\nresponse','Orthogonal\nrotation'],yscale='log',ylabel='Maximum relative raw-divergence change')
panel('eeg_raw',eraw)
combine('figS16',['eeg_cycle','eeg_raw'])
# Explicit wrong-tail limiting mechanism
lim=pd.read_csv(R/'results/misspecification_population_limit.csv')
def trunc(ax):
 good=lim.truncated_min_eigenvalue>0;z=lim;ax.plot(z.w/np.pi,np.where(good,z.true_cycle_imag,np.nan),'o-',label='full population cycle',color=COL[0]);ax.plot(z.w/np.pi,np.where(good,z.truncated_cycle_imag,np.nan),'s-',label='lag-1 truncated cycle',color=COL[1]);ax.set(xlabel=r'Frequency $\omega/\pi$',ylabel='Imaginary raw spectral cycle');ax.legend(frameon=False,fontsize=8)
panel('wrong_support_cycle',trunc)
def misslim(ax):
 z=lim;good=z.truncated_min_eigenvalue>0;ax.plot(z.w/np.pi,np.where(good,z.invalid_zero_error_lower,np.nan),'o-',color=COL[1]);ax.axhline(0,color=COL[3],ls='--');ax.set(xlabel=r'Frequency $\omega/\pi$',ylabel='Invalid zero-error density');
panel('wrong_support_limit',misslim)
combine('figS17',['wrong_support_cycle','wrong_support_limit'])
# Correct the R3 audit title without relabeling old data as new trials.
w=pd.read_csv(R/'results/white_latent_lift.csv')
def whiteeig(ax):
 z=w.groupby('b').latent_min_eigenvalue.min();ax.plot(z.index,z.values,'o-',color=COL[0]);ax.plot(z.index,(1-z.index)/2,'--',color=COL[3]);ax.set(xlabel='Asymmetry b',ylabel='Smallest latent eigenvalue')
def whiteerr(ax):
 z=w.groupby(['d','rep','b']).rel_error.max().reset_index()
 for i,b in enumerate(sorted(z.b.unique())):
  g=z[z.b==b];ax.scatter(g.d+(i-1.5)*.15,np.maximum(g.rel_error,1e-18),s=10,alpha=.5,label=f'b={b}',color=COL[i])
 ax.set(yscale='log',xlabel='Observed dimension',ylabel='Maximum relative spectral error');ax.legend(frameon=False,ncol=2)
panel('white_eigen',whiteeig);panel('white_error',whiteerr);combine('figS09_corrected',['white_eigen','white_error'])
# Two-by-two vector assembly at native 6.8-inch width, preserving readable type.
def combine_grid(name,names):
 docs=[fitz.open(P/(n+'.pdf')) for n in names];w=docs[0][0].rect.width;h=docs[0][0].rect.height
 out=fitz.open();page=out.new_page(width=2*w+12,height=2*h+44)
 for i,d in enumerate(docs):
  x=(i%2)*(w+12);y=(i//2)*(h+22)
  page.insert_text((x+3,y+12),chr(97+i),fontname='hebo',fontsize=11)
  page.show_pdf_page(fitz.Rect(x,y+18,x+w,y+18+h),d,0)
 out.save(O/(name+'.pdf'));page.get_pixmap(matrix=fitz.Matrix(2,2)).save(O/(name+'.png'));out.close()
 for d in docs:d.close()
combine_grid('fig_calibration_R4',['calibration_ratio','calibration_power','long_correlation_power','weaker_signal'])
# Install into manuscript tree.
import shutil
shutil.copy2(O/'fig_calibration_R4.pdf',R/'manuscript/figures/fig_calibration_R4.pdf')
for num in range(13,18):shutil.copy2(O/f'figS{num}.pdf',R/f'manuscript/supp_figures/figS{num}.pdf')
shutil.copy2(O/'figS09_corrected.pdf',R/'manuscript/supp_figures/figS09.pdf')
print('Created 7 assembled vector figures and component sources.')
