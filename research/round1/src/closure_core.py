"""Spectral cycle observables for the 2026-11-07 research challenge.

Convention: S_ij(f) = E[X_i(f) conj(X_j(f))].
All scientific assumptions and limitations are documented in the report.
"""
from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.optimize import minimize


def read_edf(path):
    """Read ordinary 16-bit EDF/EDF+ signals, preserving native units.

    Supports unequal samples per record. Annotations are omitted. EDF+D is
    rejected because treating discontinuities as continuous would be invalid.
    Returns signal arrays, sampling rates, clean labels, and header metadata.
    """
    raw = Path(path).read_bytes()
    if raw[:8].strip() != b"0":
        raise ValueError("Only standard EDF 16-bit files are supported")
    nch = int(raw[252:256])
    nrec = int(raw[236:244])
    duration = float(raw[244:252])
    header_n = int(raw[184:192])
    reserved = raw[192:236].decode("ascii").strip()
    if "EDF+D" in reserved:
        raise ValueError("Discontinuous EDF requires explicit segment handling")
    widths = [("label", 16), ("transducer", 80), ("unit", 8),
              ("pmin", 8), ("pmax", 8), ("dmin", 8), ("dmax", 8),
              ("prefilter", 80), ("samples", 8), ("reserved", 32)]
    fields, pos = {}, 256
    for key, width in widths:
        fields[key] = [raw[pos + j*width:pos + (j+1)*width].decode("ascii").strip()
                       for j in range(nch)]
        pos += nch * width
    ns = np.array([int(x) for x in fields["samples"]])
    per_record = int(ns.sum())
    data = np.frombuffer(raw, dtype="<i2", offset=header_n)
    if nrec < 0:
        nrec = len(data) // per_record
    if data.size != nrec * per_record:
        raise ValueError(f"EDF data size mismatch: {data.size}, {nrec*per_record}")
    records = data.reshape(nrec, per_record)
    offsets = np.r_[0, np.cumsum(ns)]
    arrays, rates, labels, units = [], [], [], []
    for j in range(nch):
        if "annotation" in fields["label"][j].lower():
            continue
        dmin, dmax = float(fields["dmin"][j]), float(fields["dmax"][j])
        pmin, pmax = float(fields["pmin"][j]), float(fields["pmax"][j])
        if dmax == dmin:
            raise ValueError("Zero digital scaling range")
        a = records[:, offsets[j]:offsets[j+1]].reshape(-1).astype(float)
        a = (a-dmin)*(pmax-pmin)/(dmax-dmin)+pmin
        arrays.append(a)
        rates.append(ns[j]/duration)
        labels.append(fields["label"][j].strip(".").upper())
        units.append(fields["unit"][j])
    return arrays, np.array(rates), labels, {
        "units": units, "prefilter": fields["prefilter"],
        "n_records": nrec, "record_duration": duration,
        "header_bytes": header_n, "reserved": reserved,
        "duration": nrec*duration, "file_bytes": len(raw),
    }


def coherency(s):
    s = np.asarray(s)
    diagonal = np.diagonal(s, axis1=-2, axis2=-1).real
    if np.any(diagonal <= 0):
        raise ValueError("Nonpositive spectral power")
    scale = np.sqrt(diagonal)
    return s / scale[..., :, None] / scale[..., None, :]


def triangles(n):
    return np.asarray(list(itertools.combinations(range(n), 3)), dtype=int)


def cycle_product(c, tri=None):
    if tri is None:
        tri = triangles(c.shape[-1])
    i, j, k = tri.T
    return c[..., i, j] * c[..., j, k] * c[..., k, i]


def spectral_reversal_density(s):
    """Gaussian spectral reversal density, following Seara et al. (2021).

    Transpose, not Hermitian transpose, is the reversed spectral matrix.
    The integral over angular frequency divided by 2pi is a Gaussian
    time-reversal KL rate. This alone is not a thermodynamic measurement.
    """
    n = s.shape[-1]
    return 0.5 * (np.trace(np.linalg.solve(np.swapaxes(s, -1, -2), s),
                          axis1=-2, axis2=-1).real - n)


def diagonal_congruence(s, h):
    return s * h[..., :, None] * h[..., None, :].conj()


def triangle_lower_bound(c):
    """Analytic lower bound for a 3x3 coherency matrix (batch supported)."""
    a, b, d = c[..., 0, 1], c[..., 1, 2], c[..., 2, 0]
    p = a*b*d
    den = abs(a*b)**2 + abs(b*d)**2 + abs(d*a)**2
    lam = np.linalg.eigvalsh(c)[..., -1]
    return np.divide(2*p.imag**2, lam**2*den,
                     out=np.zeros_like(den), where=den > 0)


def triangle_lower_bound_with_error(c_hat, epsilon):
    """Conditional lower bound given a simultaneous entrywise error radius.

    c_hat must be a valid 3x3 coherency matrix. The supplied epsilon must
    include both sampling error and finite-window/observation bias; this
    function does not infer or calibrate that radius from the same data.
    Batch matrices and broadcastable nonnegative radii are supported.
    """
    c_hat = np.asarray(c_hat)
    epsilon = np.asarray(epsilon)
    if c_hat.shape[-2:] != (3, 3) or np.any(epsilon < 0):
        raise ValueError('Expected 3x3 coherency and nonnegative error radius')
    a, b, c = c_hat[...,0,1], c_hat[...,1,2], c_hat[...,2,0]
    r = [np.minimum(1.,abs(x)+epsilon) for x in (a,b,c)]
    den = (r[0]*r[1])**2+(r[1]*r[2])**2+(r[2]*r[0])**2
    lam = np.minimum(3.,np.linalg.eigvalsh(c_hat)[...,-1]+2*epsilon)
    w = np.maximum(0.,abs((a*b*c).imag)-3*epsilon)
    return np.divide(2*w*w,lam*lam*den,out=np.zeros_like(w),where=den>0)


def minimize_reversal_density(s, rng=None, starts=8):
    """Multistart local optimization, not a certified global lower bound.

    Returns a numerically attained upper bound on the true phase minimum.
    The separate analytic triangle bound is a certified lower bound.
    """
    rng = np.random.default_rng(0) if rng is None else rng
    c = coherency(s)
    n = c.shape[-1]
    def objective(phi):
        h = np.exp(1j * np.r_[0., phi])
        return float(spectral_reversal_density(diagonal_congruence(c, h)))
    initial = [np.zeros(n-1)]
    initial += [rng.uniform(-np.pi, np.pi, n-1) for _ in range(starts-1)]
    fits = [minimize(objective, p, method="BFGS", options={"gtol": 1e-9})
            for p in initial]
    best = min(fits, key=lambda x: x.fun)
    return float(best.fun), best.x


def phase_reversal_certificate(s, rng=None, starts=12):
    """Primal/dual interval for the filter-relaxed Gaussian reversal density.

    Converts the phase optimization to a unit-modulus quadratic form. Every
    returned lower bound has an explicit feasible semidefinite dual matrix;
    no assumption that the local optimizer found a global minimum is needed.
    Inverse residuals are propagated into both ends of the interval, in
    addition to a numerical eigenvalue buffer. Ordinary floating-point
    arithmetic is used; this is not an interval-arithmetic proof.
    """
    rng = np.random.default_rng(0) if rng is None else rng
    c = coherency(s)
    n = c.shape[-1]
    inverse = np.linalg.inv(c.T)
    inverse = .5*(inverse+inverse.conj().T)
    inverse_norm = np.linalg.norm(inverse, 2)
    residual = np.linalg.norm(np.eye(n)-c.T@inverse, 2)
    unit_roundoff = np.finfo(float).eps
    gamma = 10*n*unit_roundoff/(1-10*n*unit_roundoff)
    residual_upper = residual + gamma*np.linalg.norm(abs(c.T), 2)*np.linalg.norm(abs(inverse), 2) + 10*unit_roundoff
    if residual_upper >= .1:
        raise ValueError('Inverse residual is too large for a useful floating-point certificate')
    # Schur multiplication by a correlation matrix contracts the operator
    # norm of a Hermitian error. This propagates the inverse residual to A.
    matrix_error = inverse_norm*residual_upper/(1-residual_upper)
    matrix_error += 8*unit_roundoff*np.linalg.norm(abs(inverse)*abs(c.T), 2)
    a = inverse * c.T
    a = .5*(a+a.conj().T)
    def objective(theta):
        v = np.exp(1j*np.r_[0., theta])
        av = a@v
        value = .5*(np.vdot(v,av).real-n)
        gradient = (v.conj()*av).imag[1:]
        return value, gradient
    inits = [np.zeros(n-1)]
    inits += [rng.uniform(-np.pi,np.pi,n-1) for _ in range(starts-1)]
    fits = [minimize(objective, t, jac=True, method='BFGS',
                     options={'gtol': 1e-10, 'maxiter': 1000}) for t in inits]
    fit = min(fits,key=lambda x:x.fun)
    v = np.exp(1j*np.r_[0.,fit.x])
    d = (v.conj()*(a@v)).real
    m = a-np.diag(d)
    eigenmin = np.linalg.eigvalsh(m)[0]
    buffer = 1e-12*max(1.,np.linalg.norm(a,2))
    delta = max(0.,-eigenmin)+buffer+matrix_error
    d_feasible = d-delta
    lower = max(0.,.5*(d_feasible.sum()-n))
    upper = max(0.,float(fit.fun)+.5*n*matrix_error)
    return dict(lower_bound=float(lower),upper_bound=upper,
                gap=float(upper-lower),dual_shift=float(delta),
                dual_min_eigenvalue=float(np.linalg.eigvalsh(a-np.diag(d_feasible))[0]),
                gradient_norm=float(np.linalg.norm(objective(fit.x)[1])),
                matrix_dimension=n,matrix_condition=float(np.linalg.cond(c)),
                inverse_residual=float(residual),
                inverse_residual_upper=float(residual_upper),
                propagated_matrix_error=float(matrix_error))


def periodogram_replicates(epochs, fs, detrend="linear", taper="hann"):
    """Independent epochs x time x channels -> epoch x frequency x channel."""
    epochs = signal.detrend(epochs, axis=1, type=detrend)
    window = signal.get_window(taper, epochs.shape[1], fftbins=True)
    f = np.fft.rfftfreq(epochs.shape[1], 1/fs)
    z = np.fft.rfft(epochs * window[None, :, None], axis=1)
    z /= np.sqrt(fs * np.sum(window**2))
    return f, z


def spectrum_from_replicates(z):
    return np.einsum("kfi,kfj->fij", z, z.conj(), optimize=True)/z.shape[0]


def split_cycle_statistic(z_a, z_b, tri=None):
    """Independent-half product removes the positive squaring noise floor.

    Exact null symmetry requires independence between halves and joint
    conjugation symmetry of the whole phase-adjusted spectral replicate law
    within each half (independent frequency bins are one sufficient case).
    Frequencywise real-gauge covariances alone do not ensure this finite-window
    property. Reproducible taper leakage remains in the cross-half product.
    """
    ca = coherency(spectrum_from_replicates(z_a))
    cb = coherency(spectrum_from_replicates(z_b))
    va = cycle_product(ca, tri).imag
    vb = cycle_product(cb, tri).imag
    return va*vb, va, vb


def complex_gaussian_replicates(s, k, rng):
    """Proper complex Gaussian observations with E[z_i conj(z_j)]=S_ij."""
    l = np.linalg.cholesky(s)
    z = (rng.normal(size=(k, s.shape[-1]))+
         1j*rng.normal(size=(k, s.shape[-1])))/np.sqrt(2)
    return z @ l.T


def sign_flip_test(values, rng, n_perm=49999, alternative="greater"):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    observed = values.mean()
    if values.size == 0:
        raise ValueError("No finite values")
    count = 0
    for start in range(0, n_perm, 2000):
        b = min(2000, n_perm-start)
        means = (rng.choice([-1., 1.], size=(b, len(values))) @ values)/len(values)
        if alternative == "greater":
            count += int(np.count_nonzero(means >= observed))
        else:
            count += int(np.count_nonzero(abs(means) >= abs(observed)))
    return (count+1)/(n_perm+1)


def bootstrap_mean_ci(values, rng, n_boot=20000, level=.95):
    values = np.asarray(values, dtype=float)
    boot = values[rng.integers(0, len(values), size=(n_boot, len(values)))].mean(axis=1)
    return np.quantile(boot, [(1-level)/2, (1+level)/2])
