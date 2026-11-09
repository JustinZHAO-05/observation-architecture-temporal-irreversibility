"""Prepare R5 plot scripts from exact R4/R3 data. No numeric data changed."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
p=R/'src/make_r5_figures.py'
s=p.read_text(encoding='utf-8')
# Panel-level prose titles move into figure captions: measured axes, symbols and group labels remain.
s,n=re.subn(r",title='[^']*'",'',s)
print('Removed subplot titles:',n)
# Auxiliary inscriptions move into captions. Keep numerical heatmap-cell labels.
parts=[
 " ax.text(.97,.95,'120 pairs per length\\nm = 1,024: abstain',transform=ax.transAxes,va='top',ha='right',fontsize=8)",
 "  ax.errorbar(i,k/n,yerr=[[k/n-lo],[hi-k/n]],fmt='o',capsize=5,color=COL[0]);ax.text(i,hi+.01,f'{k}/{n}',ha='center',fontsize=9)",
 " ax.text(.04,.96,'N = 524,288\\nm = 131,072\\nExact 95% binomial intervals',va='top',transform=ax.transAxes,fontsize=8)",
 "ax.text(.04,.95,'m = 16,384; 120 pairs\\nNested record lengths',va='top',transform=ax.transAxes,fontsize=8)",
 "ax.text(.04,.95,'Only positive-definite truncated spectra\\nTrue phase-relaxed density = 0',va='top',transform=ax.transAxes,fontsize=8)",
]
for old in parts:
 if old not in s:
  print('MISSING',repr(old))
 else:
  if old.startswith('  ax.errorbar'):
   s=s.replace(old,"  ax.errorbar(i,k/n,yerr=[[k/n-lo],[hi-k/n]],fmt='o',capsize=5,color=COL[0])")
  else: s=s.replace(old,'')
# Make panel labels slightly larger, but avoid title bands.
# Allow a little higher axis whitespace to prevent marker clipping.
s=s.replace("height=max(d[0].rect.height for d in docs)+16", "height=max(d[0].rect.height for d in docs)+16")
p.write_text(s,encoding='utf-8')
