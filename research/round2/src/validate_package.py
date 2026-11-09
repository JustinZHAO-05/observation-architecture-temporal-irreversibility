"""Consequential file, arithmetic, sample-unit and evidence consistency checks."""
from pathlib import Path
import hashlib, json, py_compile
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
def main():
    checks={}
    for script in (ROOT/'src').glob('*.py'):py_compile.compile(str(script),doraise=True)
    checks['python_sources_compile']=True
    d=pd.read_csv(R/'certificate_replicates.csv')
    checks['fixed_grid_count']=len(d)==7680
    checks['fixed_grid_independent_units']=d[['model','delay_group','rep']].drop_duplicates().shape[0]==1920
    checks['null_analysis_count']=len(d[d.model.str.startswith('null')])==3072
    checks['all_finite_envelopes_cover']=bool(d.envelope_covers.all())
    checks['all_fixed_bounds_below_population_bound']=bool(d.certificate_below_known_analytic_bound.all())
    summary=pd.read_csv(R/'certificate_summary.csv')
    merged=d.groupby(['model','delay_group','N']).rejects.mean().reset_index().merge(summary,on=['model','delay_group','N'])
    checks['power_summary_reconciles']=bool(np.allclose(merged.rejects,merged.rejection_rate))
    rate=pd.read_csv(R/'continuous_rate_replicates.csv')
    checks['rate_analysis_count']=len(rate)==384
    checks['rate_independent_units']=rate[['max_delay','rep']].drop_duplicates().shape[0]==128
    checks['rate_lower_sum_below_population_bound']=bool(rate.below_population_triangle_integral.all())
    z=np.load(R/'exact_short_memory_equivalence.npz')
    # Array names are stable in the delivered theory implementation.
    checks['exact_record_equality']=bool(np.max(abs(z['observed_covariance']-z['target_covariance']))<1e-12)
    e=pd.read_csv(R/'eeg_complete_window_records.csv')
    checks['EEG_pair_rows']=len(e)==226
    checks['EEG_matched_records']=len(e[['subject','run']].drop_duplicates())==113
    checks['EEG_unique_people']=e.subject.nunique()==71
    prov=json.loads((R/'eeg_followup_provenance.json').read_text())
    for ref,expected in prov['archive_sha256'].items():
        path=ROOT/'inputs/round1_results'/f'eeg_primary_{ref}_cycles.npz'
        checks[f'input_hash_{ref}']=hashlib.sha256(path.read_bytes()).hexdigest()==expected
    es=pd.read_csv(R/'eeg_reference_summary.csv')
    check=e.groupby(['run','reference']).q.mean().reset_index().merge(es,on=['run','reference'])
    checks['EEG_means_reconcile']=bool(np.allclose(check.q,check.mean_Q,rtol=1e-12,atol=1e-15))
    lp=pd.read_csv(R/'latency_cost_lp_intervals.csv')
    checks['LP_analytic_inside_numeric_bracket']=bool(np.all(lp.lower_ratio<=lp.analytic_ratio+1e-9) and np.all(lp.analytic_ratio<=lp.upper_ratio+1e-9))
    checks['LP_upper_covariances_PSD']=bool(np.all(lp.min_upper_eigenvalue>=-1e-9))
    checks['six_PNG_figures_exist']=len(list((ROOT/'figures').glob('*.png')))==6
    checks['no_font_files_bundled']=not any(p.suffix.lower() in ['.ttf','.otf','.woff','.woff2'] for p in ROOT.rglob('*'))
    record=dict(checks=checks,passed=sum(checks.values()),total=len(checks),all_passed=all(checks.values()))
    (R/'package_validation.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))
    if not record['all_passed']:raise SystemExit('Package consistency check failed')
if __name__=='__main__':main()
