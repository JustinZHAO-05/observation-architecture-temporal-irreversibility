"""Reproduce the numerical primal/dual certificate study (seed 92817)."""
from pathlib import Path
import time
import numpy as np
import pandas as pd
from closure_core import (coherency, phase_reversal_certificate,
                          spectral_reversal_density, triangle_lower_bound)

ROOT = Path(__file__).resolve().parents[1]

def main():
    rng = np.random.default_rng(92817)
    start = time.perf_counter()
    rows = []
    for n, count in [(2, 50), (3, 300), (8, 100), (24, 30)]:
        for case in range(count):
            z = rng.normal(size=(n, n+2)) + 1j*rng.normal(size=(n, n+2))
            s = z @ z.conj().T + .5*np.eye(n)
            result = phase_reversal_certificate(s, rng=rng, starts=8)
            result.update(case=case,
                          unfiltered_density=float(spectral_reversal_density(s)),
                          triangle_bound=float(triangle_lower_bound(coherency(s)))
                          if n == 3 else np.nan)
            rows.append(result)
            # Preserve the nuisance-filter draw schedule of the original
            # interactive experiment, so all archived matrices regenerate.
            # These filters are not used in the certificate table itself.
            rng.uniform(-1., 1., n)
            rng.uniform(-np.pi, np.pi, n)
    frame = pd.DataFrame(rows)
    frame.to_csv(ROOT/'results'/'variational_certificates.csv', index=False)
    print(frame.groupby('matrix_dimension')['gap'].agg(['count','median','max']))
    print('wall_seconds', time.perf_counter()-start)

if __name__ == '__main__':
    main()
