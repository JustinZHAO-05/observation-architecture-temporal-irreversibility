"""Independent empirical audit. Imports no other project modules.

EDF decoding, linear projection, Hann taper, spectral matrices, triangle
products, and subject statistics are implemented here from the protocol.
Run from any directory: python src/empirical_audit_independent.py
"""
from pathlib import Path
from itertools import combinations
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import binomtest, ttest_1samp, pearsonr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reviews'
CHANNELS = ['F3','F4','FZ','C3','C4','CZ','P3','P4','PZ','O1','O2','OZ']
TRIPLES = np.array(list(combinations(range(12),3)))

def decode_edf(path):
    blob = path.read_bytes()
    nsignals = int(blob[252:256])
    nrecords = int(blob[236:244])
    record_seconds = float(blob[244:252])
    nheader = int(blob[184:192])
    fields = {}
    cursor = 256
    for name,width in [('labels',16),('transducers',80),('units',8),
                       ('pmin',8),('pmax',8),('dmin',8),('dmax',8),
                       ('prefilters',80),('nsamples',8),('reserved',32)]:
        block = blob[cursor:cursor+nsignals*width]
        fields[name] = [block[j*width:(j+1)*width].decode('ascii').strip()
                        for j in range(nsignals)]
        cursor += nsignals*width
    assert cursor == nheader
    ns = np.array(fields['nsamples'],int)
    data = np.frombuffer(blob[nheader:],'<i2').reshape(nrecords,int(ns.sum()))
    starts = np.cumsum(np.r_[0,ns[:-1]])
    ids = [next(i for i,s in enumerate(fields['labels'])
                if s.upper().rstrip('.') == label) for label in CHANNELS]
    x = []
    scaling = []
    for i in ids:
        assert fields['units'][i] == 'uV'
        digital = data[:,starts[i]:starts[i]+ns[i]].flatten().astype(float)
        p0,p1 = float(fields['pmin'][i]),float(fields['pmax'][i])
        d0,d1 = float(fields['dmin'][i]),float(fields['dmax'][i])
        slope = (p1-p0)/(d1-d0)
        intercept = p0-slope*d0
        x.append(digital*slope+intercept)
        scaling.append(dict(index0=i,label=fields['labels'][i],unit=fields['units'][i],
                            physical_min=p0,physical_max=p1,digital_min=d0,
                            digital_max=d1,microvolts_per_unit=slope,offset=intercept))
    fs = ns[ids]/record_seconds
    assert np.all(fs == 160)
    metadata = dict(nsignals=nsignals,nrecords=nrecords,record_seconds=record_seconds,
                    duration=nrecords*record_seconds,header_bytes=nheader,
                    file_bytes=len(blob),fs=float(fs[0]),selected=scaling,
                    prefilters=[fields['prefilters'][i] for i in ids],
                    sha256=hashlib.sha256(blob).hexdigest())
    return np.array(x).T,metadata

def independent_half(epochs):
    # Exact least-squares subtraction of intercept and linear trend.
    nt = epochs.shape[1]
    t = np.arange(nt,dtype=float)-(nt-1)/2
    centered = epochs-epochs.mean(axis=1,keepdims=True)
    slopes = np.sum(centered*t[None,:,None],axis=1)/(t@t)
    residual = centered-slopes[:,None,:]*t[None,:,None]
    hann = (1-np.cos(2*np.pi*np.arange(nt)/nt))/2
    z = np.fft.rfft(residual*hann[None,:,None],axis=1)
    # Matrix multiply frequency by frequency, independent of root einsum.
    spectra = np.stack([zf.T@zf.conj() for zf in z.transpose(1,0,2)])
    powers = np.diagonal(spectra,axis1=1,axis2=2).real
    c = spectra/np.sqrt(powers[:,:,None]*powers[:,None,:])
    i,j,k = TRIPLES.T
    v = (c[:,i,j]*c[:,j,k]*c[:,k,i]).imag
    return v

def score_record(x,metadata):
    output = dict(duration=metadata['duration'],fs=metadata['fs'])
    halves = []
    for name,starts in [('a',range(2,26,2)),('b',range(34,58,2))]:
        e = np.array([x[s*160:(s+2)*160] for s in starts])
        finite = np.isfinite(e).all(axis=(1,2))
        amp_bad = (np.ptp(e,axis=1)>500).any(axis=1)
        flat_bad = (np.std(e,axis=1)<.1).any(axis=1)
        good = finite & ~amp_bad & ~flat_bad
        output['n_epochs_'+name] = int(good.sum())
        output['good_mask_'+name] = ''.join('1' if z else '0' for z in good)
        output['amplitude_rejections_'+name] = int(amp_bad.sum())
        output['flat_rejections_'+name] = int(flat_bad.sum())
        output['nonfinite_rejections_'+name] = int((~finite).sum())
        halves.append(e[good])
    output['status'] = 'ok' if min(len(e) for e in halves)>=8 else 'insufficient_clean_epochs'
    if output['status'] == 'ok':
        va,vb = (independent_half(e) for e in halves)
        f = np.fft.rfftfreq(320,1/160)
        keep = (f>=2)&(f<=30)
        output['q_independent'] = float(np.mean(va[keep]*vb[keep]))
    return output

def monte_carlo_flip(values,seed,two_sided=False,n=99999):
    rng = np.random.default_rng(seed)
    vals = np.array(values,float)
    observed = np.sum(vals)
    exceed = 0
    for first in range(0,n,1000):
        ns = min(1000,n-first)
        signs = 2*rng.integers(0,2,(ns,len(vals)))-1
        null = signs@vals
        exceed += int(np.sum(np.abs(null)>=abs(observed) if two_sided else null>=observed))
    return (exceed+1)/(n+1)

def bootstrap_ci(values,seed,n=20000):
    v = np.asarray(values,float)
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0,len(v),(n,len(v)))].mean(axis=1)
    return [float(z) for z in np.quantile(means,[.025,.975])]

def main():
    OUT.mkdir(exist_ok=True)
    original = pd.read_csv(ROOT/'results/eeg_primary_original_subjects.csv')
    rows = []
    sampled_headers = {}
    for path in sorted((ROOT/'data/eegmmidb').glob('S*/S*R0[12].edf')):
        sid,run = int(path.stem[1:4]),int(path.stem[5:7])
        x,metadata = decode_edf(path)
        record = score_record(x,metadata)
        record.update(subject=sid,run=run)
        rows.append(record)
        if sid in (11,35):
            metadata['selected_sample_min_uv'] = float(x.min())
            metadata['selected_sample_max_uv'] = float(x.max())
            metadata['selected_sample_sd_uv'] = x.std(axis=0).tolist()
            sampled_headers[path.stem] = metadata
    audit = pd.DataFrame(rows)
    merged = original.merge(audit,on=['subject','run'],suffixes=('_root','_audit'),validate='one_to_one')
    assert len(merged)==218
    assert (merged.status_root==merged.status_audit).all()
    for h in ('a','b'):
        ok = merged['n_epochs_'+h+'_root'].notna()
        assert (merged.loc[ok,'n_epochs_'+h+'_root']==merged.loc[ok,'n_epochs_'+h+'_audit']).all()
    matched = merged[merged.status_root=='ok']
    max_q_error = float(np.max(np.abs(matched.q-matched.q_independent)))
    assert max_q_error<1e-15
    audit.to_csv(OUT/'empirical_audit_primary_recomputed.csv',index=False)
    pd.DataFrame([dict(subject=int(r.subject),run=int(r.run),q_reported=float(r.q),
                       q_independent=float(r.q_independent),absolute_error=float(abs(r.q-r.q_independent)))
                  for r in matched[matched.subject.isin([11,35])].itertuples()]).to_csv(
                      OUT/'empirical_audit_selected_scores.csv',index=False)
    tables = []
    paired = []
    sensitivity = []
    bases = ['primary_original','four_seconds_original','alternating_original',
             'primary_average','primary_original_filtered']
    for bi,base in enumerate(bases):
        data = pd.read_csv(ROOT/f'results/eeg_{base}_subjects.csv')
        valid = data[(data.cohort=='holdout') & (data.status=='ok')]
        for run in (1,2):
            g = valid[valid.run==run]
            q = g.q.to_numpy()
            if base=='primary_original':
                q = audit[(audit.subject>=11)&(audit.status=='ok')&(audit.run==run)].q_independent.to_numpy()
            ci = bootstrap_ci(q,81002+bi*10+run)
            tables.append(dict(analysis=base,run=run,n=len(q),positive=int(sum(q>0)),
                               mean=float(q.mean()),median=float(np.median(q)),sd=float(q.std(ddof=1)),
                               ci_low=ci[0],ci_high=ci[1],
                               sign_flip_p_independent=monte_carlo_flip(q,91002+bi*10+run),
                               binomial_sign_p=float(binomtest(int(sum(q>0)),len(q),.5,alternative='greater').pvalue)))
            if base!='primary_original':
                ref=original[(original.subject>=11)&(original.run==run)&(original.status=='ok')]
                common=ref.merge(g,on=['subject','run'],suffixes=('_original','_sensitivity'))
                sensitivity.append(dict(analysis=base,run=run,n_original=len(ref),n_sensitivity=len(g),
                    n_common=len(common),added_subjects=','.join(map(str,sorted(set(g.subject)-set(ref.subject)))),
                    removed_subjects=','.join(map(str,sorted(set(ref.subject)-set(g.subject)))),
                    original_mean_common=float(common.q_original.mean()),
                    sensitivity_mean_common=float(common.q_sensitivity.mean()),
                    correlation_common=float(pearsonr(common.q_original,common.q_sensitivity).statistic),
                    changed_epoch_counts_common=int(((common.n_epochs_a_original!=common.n_epochs_a_sensitivity)|
                                                     (common.n_epochs_b_original!=common.n_epochs_b_sensitivity)).sum())))
        pivot=valid.pivot(index='subject',columns='run',values='q').dropna()
        difference=(pivot[2]-pivot[1]).to_numpy()
        ci=bootstrap_ci(difference,101002+bi)
        paired.append(dict(analysis=base,n=len(difference),mean_difference=float(difference.mean()),
                           median_difference=float(np.median(difference)),
                           positive=int(sum(difference>0)),ci_low=ci[0],ci_high=ci[1],
                           sign_flip_p_independent=monte_carlo_flip(difference,111002+bi,True),
                           binomial_sign_p_two_sided=float(binomtest(int(sum(difference>0)),len(difference),.5).pvalue)))
    pd.DataFrame(tables).to_csv(OUT/'empirical_audit_group_table.csv',index=False)
    pd.DataFrame(paired).to_csv(OUT/'empirical_audit_paired_table.csv',index=False)
    pd.DataFrame(sensitivity).to_csv(OUT/'empirical_audit_sensitivity_table.csv',index=False)
    counts = {}
    h = audit[audit.subject>=11]
    for run in (1,2):
        g=h[h.run==run]
        counts[str(run)] = dict(total=len(g),retained=int((g.status=='ok').sum()),
            exclusions=sorted(g.loc[g.status!='ok','subject'].tolist()),
            amplitude_rejected_epochs=int(g.amplitude_rejections_a.sum()+g.amplitude_rejections_b.sum()),
            flat_rejected_epochs=int(g.flat_rejections_a.sum()+g.flat_rejections_b.sum()),
            nonfinite_rejected_epochs=int(g.nonfinite_rejections_a.sum()+g.nonfinite_rejections_b.sum()))
    summary=dict(max_q_absolute_error=max_q_error,n_records_audited=len(audit),
                 n_included_scores_audited=len(matched),all_statuses_match=True,
                 all_recorded_epoch_counts_match=True,holdout_qc=counts,
                 protocol_sha256=hashlib.sha256((ROOT/'protocols/protocol_v1.md').read_bytes()).hexdigest(),
                 sampled_headers=sampled_headers)
    (OUT/'empirical_audit_exact_outputs.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!='sampled_headers'},indent=2))
    print(pd.DataFrame(tables).to_string(index=False))
    print(pd.DataFrame(paired).to_string(index=False))
    print(pd.DataFrame(sensitivity).to_string(index=False))

if __name__=='__main__':
    main()
