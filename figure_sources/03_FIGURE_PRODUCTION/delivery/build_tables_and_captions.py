"""Collect the current figure captions and regenerate the manuscript tables."""
import argparse
import csv
import json
import math
from pathlib import Path
import re


P = Path("03_FIGURE_PRODUCTION")
REDRAW = P / "redraw"
R1 = Path("01_RESEARCH/ROUND1/neural_time_arrow_study")
R2 = Path("01_RESEARCH/ROUND2/PRE_round2")
MAIN = Path("02_MANUSCRIPT/Manuscript_Integrated_Working_Draft_EN.md")
SUPP = Path("02_MANUSCRIPT/Supplement_Expanded_Scientific_Working_Draft_EN.md")
FIGURES = [f"Fig{i}" for i in range(1,8)] + [f"FigS{i}" for i in range(1,9)]


def csv_rows(path):
    with path.open(encoding="utf-8-sig",newline="") as file:
        return list(csv.DictReader(file))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def draft_tables(path):
    lines=path.read_text(encoding="utf-8-sig").splitlines()
    for i in range(len(lines)-1):
        if not lines[i].startswith("|") or not re.fullmatch(r"[\s|:\-]+",lines[i+1]):
            continue
        split=lambda line:[cell.strip() for cell in line.strip().strip("|").split("|")]
        head=split(lines[i])
        data=[]
        for row in lines[i+2:]:
            if not row.startswith("|"):
                break
            cells=split(row)
            assert len(cells)==len(head),(path,row)
            data.append(cells)
        assert data
        yield head,data


def number(value):
    value=str(value).strip("$").replace(",","").strip()
    value=re.sub(r"\\times\s*10\^\{([+-]?\d+)\}",r"e\1",value)
    return float(value)


def matches(printed,actual,*,rel=7e-5,abs_tol=0):
    assert math.isclose(number(printed),float(actual),rel_tol=rel,abs_tol=abs_tol),(printed,actual)


def verify_manuscript_tables(main,supp):
    t1=main["Observation regime"][1]
    assert len(t1)==4
    exact=read_json(R2/"results/theory_summary.json")["exact_example"]
    one=dict(main["Quantity"][1])
    assert one["Observed / latent dimensions"]==f"{exact['observed_channels']} / {exact['latent_channels']}"
    assert one["Observation delay"]==f"{exact['observation_delay']} sample"
    assert one["Maximum covariance difference for the complete 32-point record"].startswith("0.0")
    assert exact["max_full_record_covariance_difference"]==0
    for key,field in [("Maximum spectral difference on 513 frequencies","max_spectral_difference"),
                      ("Minimum latent spectral eigenvalue on that grid","min_latent_spectral_eigenvalue"),
                      ("Maximum absolute imaginary triangle","max_abs_imaginary_cycle"),
                      ("Maximum observed reversal density","max_observed_reversal")]:
        matches(one[key],exact[field],rel=.005)
    rate=csv_rows(R2/"results/continuous_rate_summary.csv")
    assert len(rate)==len(main["Maximum delay"][1])==6
    for printed,row in zip(main["Maximum delay"][1],rate,strict=True):
        for field,value in zip(("max_delay","N","positive","median_rate_lower"),printed,strict=True):
            matches(value,row[field],rel=0,abs_tol=5e-7 if field=="median_rate_lower" else 0)
    eeg={(int(r["run"]),r["reference"]):r for r in csv_rows(R2/"results/eeg_reference_summary.csv")}
    ratios={int(r["run"]):r for r in csv_rows(R2/"results/eeg_reference_paired.csv")}
    for run,row in enumerate(main["Condition"][1],1):
        assert int(eeg[run,"original"]["n"])==int(eeg[run,"average"]["n"])==int(row[1])
        matches(row[2],eeg[run,"original"]["mean_Q"])
        matches(row[3],eeg[run,"average"]["mean_Q"])
        matches(row[4],ratios[run]["ratio_of_group_means"])
    for first in ("Quantity","Maximum delay"):
        assert main[first]==supp[first]
    assert main["Condition"]==supp["Matched EEG"]

    r1theory=read_json(R1/"results/theory_summary.json")
    independent=read_json(R1/"reviews/math_review_exact_outputs.json")
    checks=supp["Validation"][1]
    assert len(checks)==6
    assert checks[0][1].startswith(str(r1theory["matrix_tests"]["n_cases"]))
    assert checks[1][1].startswith(str(r1theory["networks"]["n_conditions"]))
    assert checks[3][1].startswith(str(independent["matrices"]["n_optimized_3x3"]))
    assert checks[4][1].startswith(str(len(csv_rows(R1/"results/variational_certificates.csv"))))
    assert len(independent["wishart"])==5
    for name,table,primary in [("eeg_primary_original_summary","Primary EEG",True),
                               ("eeg_four_seconds_original_summary","Sensitivity",False)]:
        archived=[r for r in csv_rows(R1/"results"/f"{name}.csv") if r["cohort"]=="holdout"]
        assert len(archived)==2
        for printed,row in zip(supp[table][1],archived,strict=True):
            assert int(printed[1 if primary else 2])==int(row["n"])
            if primary:
                assert int(printed[2])==int(row["positive"])
            matches(printed[3],row["mean"])
            for val,field in zip(printed[4].strip("[]").split(","),("ci_low","ci_high"),strict=True):
                matches(val.strip(),row[field])
            matches(printed[5],row["holm_p"])
    masked=read_json(R1/"results/matched_filter_summary.json")
    mask_table=supp["Same-mask perturbation"][1]
    for run,row in enumerate(masked,1):
        assert row["run"]==run and int(mask_table[0][run])==row["n"]
        matches(mask_table[1][run],row["q_pearson"])
        matches(mask_table[2][run],row["q_spearman"])
        matches(mask_table[3][run].strip("%"),100*row["relative_mean_change"],rel=.002)
        matches(mask_table[4][run],row["max_exact_fourier_error"],rel=.001)


def gaussian_rows():
    theory=read_json(R2/"results/theory_summary.json")
    ex=theory["exact_example"]
    serial=read_json(R1/"reviews/math_review_v2_outputs.json")["serialization"]
    finite=read_json(R2/"results/certificate_run.json")
    cont=read_json(R2/"results/continuous_rate_run.json")
    assert (finite["analyses"],finite["independent_long_trajectories"])==(7680,1920)
    assert (cont["analyses"],cont["independent_long_trajectories"])==(384,128)
    return [
        ("Finite-record serialization","Gaussian MA(4)",serial["channels"],"0; 21; 42",
         serial["record_length"],"4 (target); 46 (serialized)","501 points on the Fig. S2 grid",
         "801242",1,1,(R1/"src/math_review_v2_calculations.py").as_posix()),
        ("Exact population example","Three-channel Gaussian MA(1)",ex["observed_channels"],ex["observation_delay"],
         ex["record_length"],f"1 (observed); {ex['latent_covariance_support']} (latent)",
         "513 frequencies","deterministic",1,1,(R2/"src/theory_round2.py").as_posix()),
        ("General population lift","Gaussian VAR(1)","3; 6; 12",1,"population","VAR(1)",
         f"{theory['frequency_points_per_network']} frequencies per network","2601107",
         theory["networks"],theory["networks"],(R2/"src/theory_round2.py").as_posix()),
        ("Fixed-grid spectral certificate","Two reversible nulls; alternatives b=0.35, 0.65, 0.9",
         3,"(0,0,0); (0,1,2); (0,4,8)","2048; 8192; 32768; 131072",
         "lag cutoff: base support plus maximum channel delay",
         "π/6; π/3; π/2; 2π/3; 5π/6","260207 + 1000×model index + 17×delay index",
         finite["independent_long_trajectories"],finite["analyses"],(R2/"src/finite_certificate.py").as_posix()),
        ("Continuous-rate certificate","Gaussian MA(1), b=0.9",3,"(0,0,0); (0,4,8)","32768; 131072; 524288",
         "1 (no delay); 9 (maximum delay 8)","2,048 cells; deterministic net size max(16,16L)","713420",
         cont["independent_long_trajectories"],cont["analyses"],(R2/"src/continuous_rate_certificate.py").as_posix()),
    ]


def inclusion_rows():
    table=csv_rows(P/"generated_data/FigS8/redraw/A.csv")
    assert len(table)==218 and len({(r["subject"],r["run"]) for r in table})==218
    selected={(r["subject"],r["run"]) for r in table if r["matched"]=="True"}
    match=csv_rows(R2/"results/eeg_complete_window_records.csv")
    assert len(selected)==113 and len({s for s,_ in selected})==71
    assert selected=={(r["subject"],r["run"]) for r in match} and len(match)==226
    return list(table[0]),[list(row.values()) for row in table]


def audit_rows(paths):
    rows=[]
    def collect(path,section,entry):
        if isinstance(entry,dict):
            for key,value in entry.items():
                collect(path,f"{section}.{key}" if section else key,value)
        elif isinstance(entry,(str,bool,int,float)) and not section.endswith("seconds"):
            rows.append((path.as_posix(),section,entry))
    for path,section in paths:
        data=read_json(path)
        collect(path,section,data[section] if section else data)
    return rows


def emit(out):
    tables_dir=out/"tables"
    tables_dir.mkdir(parents=True,exist_ok=True)
    main={head[0]:(head,rows) for head,rows in draft_tables(MAIN)}
    supp={}
    for head,rows in draft_tables(SUPP):
        key=("Primary EEG" if head[1]=="Included participants" else "Matched EEG") if head[0]=="Condition" else head[0]
        supp[key]=(head,rows)
    assert len(main)==4 and len(supp)==7
    verify_manuscript_tables(main,supp)
    checks=[
        (R1/"results/theory_summary.json","matrix_tests"),
        (R1/"results/theory_summary.json","networks"),
        (R1/"reviews/math_review_exact_outputs.json","matrices"),
        (R1/"reviews/math_review_v2_outputs.json","serialization"),
        (R2/"results/theory_summary.json","exact_example"),
        (R2/"results/latency_cost_lp_summary.json",""),
        (R2/"results/power_coordinate_summary.json",""),
        (R2/"results/independent_formula_audit.json",""),
        (R2/"results/multichannel_audit.json","summary"),
        (R2/"results/package_validation.json",""),
    ]
    inclusion=inclusion_rows()
    items=[
        ("T01_observation_regimes","Identification under different observation architectures.",
         main["Observation regime"],[MAIN]),
        ("T02_one_sample_construction","Checks of the three-channel one-sample population construction.",
         main["Quantity"],[MAIN,R2/"results/theory_summary.json",R2/"results/exact_short_memory_equivalence.npz"]),
        ("T03_rate_certificates","Positive continuous-rate certificates and median rate bounds in nats/sample.",
         main["Maximum delay"],[MAIN,R2/"results/continuous_rate_summary.csv",R2/"results/continuous_rate_replicates.csv"]),
        ("T04_matched_eeg","Mean scores by reference for the same complete-window EEG recordings.",
         main["Condition"],[MAIN,R2/"results/eeg_reference_summary.csv",R2/"results/eeg_reference_paired.csv"]),
        ("TS_population_checks","First-round population and algebraic validation summarized in the supplement.",
         supp["Validation"],[SUPP,R1/"results/theory_summary.json",R1/"reviews/math_review_exact_outputs.json",
                              R1/"results/variational_certificates.csv"]),
        ("TS_eeg_primary","Primary held-out EEG results under the original reference and first-round eligibility rule.",
         supp["Primary EEG"],[SUPP,R1/"results/eeg_primary_original_summary.csv"]),
        ("TS_eeg_window_sensitivity","Four-second window sensitivity for held-out EEG.",
         supp["Sensitivity"],[SUPP,R1/"results/eeg_four_seconds_original_summary.csv"]),
        ("TS_eeg_fixed_mask_filter","Causal-filter perturbation with participants and accepted-window masks fixed.",
         supp["Same-mask perturbation"],[SUPP,R1/"results/matched_filter_summary.json",R1/"results/matched_filter_robustness.csv"]),
        ("TS1_gaussian_models","Gaussian model settings and analysis units for the finite-record construction and Round 2 population and certificate studies.",
         (["experiment","model","observed_dimension","delay_samples","record_length_samples","support_or_cutoff",
           "frequency_design","seed","independent_units","analyses_or_cases","source_script"],gaussian_rows()),
         [R1/"reviews/math_review_v2_outputs.json",R1/"src/math_review_v2_calculations.py",
          R2/"protocols/round2_protocol.md",R2/"src/theory_round2.py",R2/"src/finite_certificate.py",
          R2/"src/continuous_rate_certificate.py",R2/"results/certificate_run.json",R2/"results/continuous_rate_run.json"]),
        ("TS2_eeg_inclusion","Record-level EEG selection and complete-window decisions under both references.",
         inclusion,[P/"generated_data/FigS8/redraw/A.csv",R1/"protocols/protocol_v1.md",R1/"protocols/freeze_v1.json",
                    R1/"results/eeg_primary_original_subjects.csv",R1/"results/eeg_primary_average_subjects.csv",
                    R2/"results/eeg_complete_window_records.csv",REDRAW/"Fig7/data/Fig7b_windows.csv"]),
        ("TS3_audit_metrics","Archived numerical-audit metrics and check flags. Per-case records retain optimizer outcomes.",
         (["source","metric","value"],audit_rows(checks)),
         [p for p,_ in checks]+[R2/"results/latency_power_optimization.csv",R2/"results/latency_cost_lp_intervals.csv"]),
    ]
    index=[]
    md=["# Manuscript tables and table captions",
        "Identifiers below are package labels. Final numbering follows manuscript integration. "
        "The eight display tables retain the working drafts' precision. The source index also links the full-precision archives."]
    for key,title,(header,rows),sources in items:
        assert rows and all(p.is_file() for p in sources)
        with (tables_dir/f"{key}.csv").open("w",encoding="utf-8-sig",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        index.append(dict(id=key,caption=title,rows=len(rows),csv=f"{key}.csv",
                          sources=" | ".join(p.as_posix() for p in sources)))
        md.extend([f"## {key}",title,f"[Editable CSV]({key}.csv)"])
        if not key.startswith(("TS1_","TS2_","TS3_")):
            md.append("\n".join(["| "+" | ".join(header)+" |","| "+" | ".join(["---"]*len(header))+" |",
                                 *("| "+" | ".join(row)+" |" for row in rows)]))
        else:
            md.append(f"{len(rows)} rows. The complete table is in the CSV.")
    with (tables_dir/"TABLE_SOURCE_INDEX.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(index[0]))
        writer.writeheader()
        writer.writerows(index)
    (tables_dir/"TABLES_EN.md").write_text("\n\n".join(md)+"\n",encoding="utf-8")

    captions=["# Figure captions","Main figures 1–7 and supplementary figures S1–S8."]
    for name in FIGURES:
        path=REDRAW/name/"caption.md"
        lines=path.read_text(encoding="utf-8-sig").strip().splitlines()
        if lines[0].startswith("# "):
            lines=lines[1:]
        captions.extend([f"## {name}","[Individual caption]("+path.as_posix()+")","\n".join(lines).strip()])
    (out/"FIGURE_CAPTIONS_EN.md").write_text("\n\n".join(captions)+"\n",encoding="utf-8")
    print(f"Wrote {len(FIGURES)} figure captions and {len(index)} tables.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("editorial_rebuilt"))
    args=parser.parse_args()
    if args.output.anchor:
        parser.error("Use a path relative to the handoff root.")
    emit(args.output)
