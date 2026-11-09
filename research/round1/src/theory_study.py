"""Reproducible analytic stress tests and network-family experiments."""
from pathlib import Path
import json
import time
import itertools

import numpy as np
import pandas as pd
from scipy import linalg

from closure_core import (coherency, cycle_product, triangles,
    diagonal_congruence, spectral_reversal_density, triangle_lower_bound,
    minimize_reversal_density, complex_gaussian_replicates)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results'
OUT.mkdir(exist_ok=True)


def stress_tests(seed=18472):
    rng = np.random.default_rng(seed)
    records = []
    for n, count in [(3, 300), (8, 120), (24, 80), (64, 40)]:
        tri = triangles(n)
        if len(tri) > 300:
            tri = tri[rng.choice(len(tri), 300, replace=False)]
        for case in range(count):
            z = (rng.normal(size=(n, n+2)) + 1j*rng.normal(size=(n,n+2)))
            s = z@z.conj().T + .5*np.eye(n)
            c = coherency(s)
            h = np.exp(rng.uniform(-2, 2, n) + 1j*rng.uniform(-np.pi,np.pi,n))
            cf = coherency(diagonal_congruence(s,h))
            p, pf = cycle_product(c,tri),cycle_product(cf,tri)
            err = float(np.max(abs(p-pf)))
            rev_err = float(np.max(abs(cycle_product(c.T,tri)-p.conj())))
            row = dict(n=n,case=case,filter_invariance_error=err,
                       reversal_conjugation_error=rev_err)
            if n == 3:
                lb = float(triangle_lower_bound(c))
                opt, _ = minimize_reversal_density(c,rng,starts=5)
                row.update(lower_bound=lb,attained_minimum=opt,
                           analytic_bound_margin=opt-lb,
                           unfiltered_density=float(spectral_reversal_density(c)))
            records.append(row)
    df = pd.DataFrame(records)
    df.to_csv(OUT/'matrix_stress_tests.csv',index=False)
    assert df.filter_invariance_error.max() < 1e-10
    assert df.reversal_conjugation_error.max() < 1e-10
    assert df.analytic_bound_margin.dropna().min() > -1e-8
    return dict(n_cases=len(df),max_invariance_error=df.filter_invariance_error.max(),
                min_analytic_bound_margin=df.analytic_bound_margin.min())


def var_spectrum(a, omega, q=None):
    q = np.eye(a.shape[0]) if q is None else q
    g = np.linalg.inv(np.eye(a.shape[0])[None,:,:]-
                      np.exp(-1j*omega)[:,None,None]*a[None,:,:])
    return g@q@np.swapaxes(g.conj(),-1,-2)


def network_families(seed=24170):
    rng = np.random.default_rng(seed)
    omega = np.linspace(.08,2.9,24)
    rows = []
    spectra_examples = {}
    for n in [3,8,24,64]:
        for network in range(12):
            raw = rng.normal(size=(n,n))/np.sqrt(n)
            sym = .5*(raw+raw.T)
            sym /= np.linalg.norm(sym,2)
            raw2 = rng.normal(size=(n,n))/np.sqrt(n)
            skew = .5*(raw2-raw2.T)
            skew /= np.linalg.norm(skew,2)
            tri = triangles(n)
            if len(tri)>300:
                tri = tri[rng.choice(len(tri),300,replace=False)]
            for asymmetry in [0.,.1,.3,.6]:
                a = .72*(sym+asymmetry*skew)/(1+asymmetry)
                s = var_spectrum(a,omega)
                c = coherency(s)
                pole = rng.uniform(.05,.92,n)
                delay = rng.integers(0,6,n)
                gain = np.exp(rng.uniform(-1.,1.,n))
                h = gain[None,:]*(1-pole)[None,:]/(
                    1-pole[None,:]*np.exp(-1j*omega[:,None]))
                h *= np.exp(-1j*omega[:,None]*delay)
                sf = diagonal_congruence(s,h)
                cf = coherency(sf)
                cp = cycle_product(c,tri).imag
                cpf = cycle_product(cf,tri).imag
                upper = np.triu_indices(n,1)
                rows.append(dict(n=n,network=network,asymmetry=asymmetry,
                    cycle_rms=float(np.sqrt(np.mean(cp**2))),
                    cycle_rms_filtered=float(np.sqrt(np.mean(cpf**2))),
                    pair_imag_rms=float(np.sqrt(np.mean(c[:,upper[0],upper[1]].imag**2))),
                    pair_imag_rms_filtered=float(np.sqrt(np.mean(cf[:,upper[0],upper[1]].imag**2))),
                    reversal_density=float(np.mean(spectral_reversal_density(s))),
                    reversal_density_filtered=float(np.mean(spectral_reversal_density(sf))),
                    max_cycle_change=float(np.max(abs(cp-cpf))),
                    spectral_radius=float(max(abs(np.linalg.eigvals(a))))))
                if n==8 and network==0:
                    spectra_examples[f'c_{asymmetry}']=c
                    spectra_examples[f'cf_{asymmetry}']=cf
    df=pd.DataFrame(rows);df.to_csv(OUT/'network_families.csv',index=False)
    np.savez_compressed(OUT/'network_examples.npz',omega=omega,**spectra_examples)
    assert df.spectral_radius.max() < 1
    assert df.loc[df.asymmetry==0,'cycle_rms_filtered'].max() < 1e-12
    assert df.max_cycle_change.max() < 1e-10
    return dict(n_conditions=len(df),max_cycle_change=df.max_cycle_change.max(),
                reversible_filtered_pair_mean=df.loc[df.asymmetry==0,'pair_imag_rms_filtered'].mean(),
                reversible_filtered_cycle_max=df.loc[df.asymmetry==0,'cycle_rms_filtered'].max())


def explicit_counterexamples():
    omega=np.linspace(.05,3.,128)
    # Directional feedforward chain with independent innovations: nonzero
    # pairwise asymmetry but all spectral triangle products real.
    a=np.array([[.0,.0,.0],[.65,.0,.0],[.0,.65,.0]])
    c=coherency(var_spectrum(a,omega))
    chain=dict(max_closure_imag=float(abs(cycle_product(c).imag).max()),
               mean_reversal_density=float(spectral_reversal_density(c).mean()))
    # Reversible, correlated real source spectrum; distinct source filters
    # followed by instantaneous spatial mixing creates nonzero sensor closure.
    r=np.array([[1.,.6,.2],[.6,1.,.4],[.2,.4,1.]])
    h=np.exp(-1j*omega[:,None]*np.array([0,1,3])[None,:])
    sf=diagonal_congruence(np.broadcast_to(r,(len(omega),3,3)),h)
    m=np.array([[1.,.2,.1],[.1,1.,.3],[.3,.2,1.]])
    mixed=m@sf@m.T
    cm=coherency(mixed)
    mixing=dict(max_source_closure_imag=float(abs(cycle_product(coherency(sf)).imag).max()),
        max_sensor_closure_imag=float(abs(cycle_product(cm).imag).max()),
        max_lower_bound=float(triangle_lower_bound(cm).max()))
    # Incomplete support: all triangles zero, but a four-edge cycle is complex.
    s4=np.eye(4,dtype=complex)
    for i,j,v in [(0,1,.15),(1,2,.15),(2,3,.15),(3,0,.15j)]:
        s4[i,j]=v;s4[j,i]=np.conj(v)
    sparse=dict(max_triangle_imag=float(abs(cycle_product(s4).imag).max()),
        four_cycle_imag=float((s4[0,1]*s4[1,2]*s4[2,3]*s4[3,0]).imag),
        min_eigenvalue=float(np.linalg.eigvalsh(s4).min()))
    out=dict(feedforward_chain=chain,filter_then_mix=mixing,sparse_four_cycle=sparse)
    (OUT/'counterexamples.json').write_text(json.dumps(out,indent=2))
    np.savez_compressed(OUT/'counterexample_spectra.npz',omega=omega,chain=c,mixing=cm)
    assert chain['max_closure_imag']<1e-12
    assert chain['mean_reversal_density']>0
    assert mixing['max_sensor_closure_imag']>0.001
    assert sparse['min_eigenvalue']>0
    return out


if __name__=='__main__':
    t=time.perf_counter()
    summary={}
    summary['matrix_tests']=stress_tests();print('matrix tests',summary['matrix_tests'],flush=True)
    summary['networks']=network_families();print('networks',summary['networks'],flush=True)
    summary['counterexamples']=explicit_counterexamples();print('counterexamples',summary['counterexamples'],flush=True)
    summary['wall_seconds']=time.perf_counter()-t
    (OUT/'theory_summary.json').write_text(json.dumps(summary,indent=2))
