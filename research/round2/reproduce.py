"""Execute the complete round-two CPU pipeline using bundled inputs."""
from pathlib import Path
import json, os, platform, subprocess, sys, time
ROOT=Path(__file__).resolve().parent
SCRIPTS=['theory_round2.py','finite_certificate.py','power_cost_and_coordinates.py',
         'latency_cost_lp_audit.py','audit_round2.py','multichannel_audit.py',
         'continuous_rate_certificate.py','eeg_matched_reference.py',
         'make_figures_round2.py','validate_package.py']
def main():
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    log=[]
    for name in SCRIPTS:
        start=time.perf_counter();print(f'Running {name}',flush=True)
        result=subprocess.run([sys.executable,str(ROOT/'src'/name)],cwd=ROOT,env=env,
                              capture_output=True,text=True,check=False)
        item=dict(script=name,returncode=result.returncode,seconds=time.perf_counter()-start,
                  stdout=result.stdout,stderr=result.stderr)
        log.append(item)
        (ROOT/'results'/'reproduction_log.json').write_text(json.dumps(log,indent=2))
        print(result.stdout,flush=True)
        if result.returncode:
            print(result.stderr,file=sys.stderr)
            raise SystemExit(f'{name} failed; inspect results/reproduction_log.json')
    print('All pipeline stages completed. See results/reproduction_log.json.')
if __name__=='__main__': main()
