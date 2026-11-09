"""Build a compact reporting table from frozen empirical output files.

No new tests, models, or confidence intervals are computed. All score units
are dimensionless Q. Matched comparisons are descriptive participant subsets.
"""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'

def csv(name):
    return pd.read_csv(RESULTS/name,float_precision='round_trip')

def main():
    rows=[]
    for base,analysis in [('primary_original','primary_2s'),('four_seconds_original','sensitivity_4s')]:
        summary_name=f'eeg_{base}_summary.csv'
        for r in csv(summary_name).query("cohort == 'holdout'").itertuples():
            rows.append(dict(analysis=analysis,condition='eyes_open' if r.run==1 else 'eyes_closed',
                n_participants=r.n,n_positive=r.positive,mean_q=r.mean,median_q=r.median,
                ci_low=r.ci_low,ci_high=r.ci_high,ci_target='mean_q',
                conditional_sign_flip_p=r.sign_flip_p,holm_p=r.holm_p,
                sample_definition='Branch-specific retained holdout participants',
                source_files='results/'+summary_name,
                notes='Dimensionless Q; percentile subject-bootstrap 95% CI; sign-flip null assumes finite-window sign symmetry; sensitivity rows are descriptive'))
        paired_name=f'eeg_{base}_paired.csv'
        r=csv(paired_name).query("cohort == 'holdout'").iloc[0]
        rows.append(dict(analysis='paired_'+analysis,condition='eyes_closed_minus_open',
            n_participants=int(r.n),mean_difference=r.mean_difference,
            ci_low=r.ci_low,ci_high=r.ci_high,ci_target='mean_difference',
            conditional_sign_flip_p=r.p,
            sample_definition='Holdout participants retained in both baseline conditions',
            source_files='results/'+paired_name,
            notes='Exploratory paired baseline-condition association; percentile subject-bootstrap 95% CI; no Holm value assigned to this secondary contrast'))
    original=csv('eeg_primary_original_subjects.csv').query("cohort == 'holdout' and status == 'ok'")
    four=csv('eeg_four_seconds_original_subjects.csv').query("cohort == 'holdout' and status == 'ok'")
    for run in (1,2):
        common=original[original.run==run].merge(four[four.run==run],on=['subject','run'],
                                               suffixes=('_2s','_4s'),validate='one_to_one')
        before=float(common.q_2s.mean());after=float(common.q_4s.mean())
        rows.append(dict(analysis='matched_window_2s_to_4s',condition='eyes_open' if run==1 else 'eyes_closed',
            n_participants=len(common),reference_mean_q=before,mean_q=after,
            mean_difference=float((common.q_4s-common.q_2s).mean()),
            relative_mean_change=(after-before)/before,
            sample_definition='Intersection of primary and four-second retained participants for this condition',
            source_files='results/eeg_primary_original_subjects.csv;results/eeg_four_seconds_original_subjects.csv',
            notes='Descriptive matched-participant comparison; original and four-second epoch definitions differ; no new test'))
    filtered=csv('matched_filter_robustness.csv')
    saved=json.loads((RESULTS/'matched_filter_summary.json').read_text())
    for r in saved:
        run=int(r['run']);g=filtered[filtered.run==run]
        assert len(g)==int(r['n'])
        assert abs(float(g.q_original.mean())-r['original_mean'])<1e-16
        assert abs(float(g.q_filtered_fixed_mask.mean())-r['filtered_mean'])<1e-16
        rows.append(dict(analysis='matched_causal_filter_fixed_mask',condition='eyes_open' if run==1 else 'eyes_closed',
            n_participants=int(r['n']),reference_mean_q=r['original_mean'],mean_q=r['filtered_mean'],
            mean_difference=r['filtered_mean']-r['original_mean'],
            relative_mean_change=r['relative_mean_change'],pearson_r=r['q_pearson'],
            sample_definition='Same primary holdout participants and same original accepted-epoch masks',
            source_files='results/matched_filter_summary.json;results/matched_filter_robustness.csv',
            notes='Descriptive mild causal-filter perturbation; no new test; original QC mask preserved'))
    columns=['analysis','condition','n_participants','n_positive','mean_q','reference_mean_q',
             'mean_difference','median_q','ci_low','ci_high','ci_target','conditional_sign_flip_p',
             'holm_p','pearson_r','relative_mean_change','sample_definition','source_files','notes']
    frame=pd.DataFrame(rows).reindex(columns=columns)
    target=ROOT/'output/scientific_results_table.csv'
    frame.to_csv(target,index=False,float_format='%.17g')
    print(frame[['analysis','condition','n_participants','mean_q','reference_mean_q','mean_difference','conditional_sign_flip_p','holm_p','pearson_r']].to_string(index=False))
    print('Saved',target)

if __name__=='__main__':main()
