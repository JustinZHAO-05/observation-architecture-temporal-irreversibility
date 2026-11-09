"""Reproducible multi-triangle consistency check, with a distinct random seed."""
from pathlib import Path
import json
import numpy as np
from finite_certificate import multichannel_certificate
from theory_round2 import E

def main():
    rng=np.random.default_rng(20261107)
    rows=[]
    for d in (3,6,12):
        for rep in range(40):
            z=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d))
            S=z@z.conj().T+.5*np.eye(d)
            eps=1e-5*float(np.max(S.diagonal().real))
            delta=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d))
            delta=(delta+delta.conj().T)/2
            delta*=eps/np.max(abs(delta))
            bound,tri=multichannel_certificate((S+delta)[None],eps)
            rows.append(dict(d=d,rep=rep,lower=float(bound[0]),raw_reversal=E(S),triangle=tri[0].tolist()))
    summary=dict(cases=len(rows),all_below_raw_reversal=all(r['lower']<=r['raw_reversal']+1e-12 for r in rows),positive=sum(r['lower']>0 for r in rows),seed=20261107)
    path=Path(__file__).resolve().parents[1]/'results'/'multichannel_audit.json'
    path.write_text(json.dumps(dict(summary=summary,cases=rows),indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
