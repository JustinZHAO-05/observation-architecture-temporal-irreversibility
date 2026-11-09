"""Independent adversarial audit; does not import closure_core or peer outputs."""
import json
import itertools
from pathlib import Path
import numpy as np
from scipy.linalg import cholesky, solve_triangular
from scipy.optimize import differential_evolution
from scipy.signal import correlate, lfilter

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reviews'
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(732419)

def normalize(s):
    d = np.sqrt(np.diag(s).real)
    return s / d[:, None] / d[None, :]

def transform(s, phases):
    u = np.exp(1j*np.asarray(phases))
    return s*u[:, None]*u.conj()[None, :]

def reversal(s):
    # Cholesky whitening, independent of root's trace-inverse code.
    a = cholesky(s, lower=True)
    m = solve_triangular(a.conj(), a, lower=True)
    return float((np.sum(abs(m)**2)-len(s))/2)

def lower_bound(s):
    c = normalize(s)
    e = [c[0,1], c[1,2], c[2,0]]
    denominator = sum(abs(e[i]*e[j])**2 for i,j in [(0,1),(1,2),(2,0)])
    return 2*np.imag(np.prod(e))**2 / (np.linalg.eigvalsh(c)[-1]**2*denominator)

def cycle(s):
    c = normalize(s)
    return c[0,1]*c[1,2]*c[2,0]

def random_spd(n):
    a = RNG.normal(size=(n,n)) + 1j*RNG.normal(size=(n,n))
    return a@a.conj().T + np.eye(n)*10**RNG.uniform(-3,1)

def matrix_checks():
    worst_bound_margin = np.inf
    largest_noise_increase = -np.inf
    invariance_error = 0.
    det_formula_error = 0.
    samples = []
    for k in range(300):
        s = normalize(random_spd(3))
        lb = lower_bound(s)
        # Global search is numerical corroboration, not a bound certificate.
        opt = differential_evolution(lambda p: reversal(transform(s,[0,*p])),
                                     [(-np.pi,np.pi)]*2, seed=k, popsize=9,
                                     tol=1e-9, maxiter=150, polish=True)
        margin = opt.fun-lb
        worst_bound_margin = min(worst_bound_margin,margin)
        z = transform(s, RNG.uniform(-np.pi,np.pi,3))
        det_identity = 2*(np.linalg.det(z.real).real/np.linalg.det(z).real-1)
        det_formula_error = max(det_formula_error,abs(det_identity-reversal(z)))
        h = np.exp(RNG.normal(size=3)+1j*RNG.uniform(-np.pi,np.pi,3))
        hs = s*h[:,None]*h.conj()[None,:]
        invariance_error = max(invariance_error,abs(cycle(s)-cycle(hs)))
        noise = np.diag(np.exp(RNG.normal(size=3)))
        largest_noise_increase = max(largest_noise_increase,reversal(z+noise)-reversal(z))
        if k<5:
            samples.append({'lower_bound':lb,'numerical_min':float(opt.fun),'raw_E':reversal(s)})
    # Higher-dimensional pointwise Gaussian data processing check.
    for n in [2,4,8,16]:
        for _ in range(80):
            s = random_spd(n)
            noise = np.diag(np.exp(RNG.normal(size=n)))
            largest_noise_increase = max(largest_noise_increase,reversal(s+noise)-reversal(s))
    return dict(n_optimized_3x3=300,min_numerical_Estar_minus_L=worst_bound_margin,
                max_noise_E_increase=largest_noise_increase,
                max_cycle_invariance_error=invariance_error,
                max_3x3_determinant_identity_error=det_formula_error,first_five=samples)

def wishart_checks():
    s = np.array([[1,.4+.2j,.1-.2j],[.4-.2j,1,.3+.15j],[.1+.2j,.3-.15j,1]],complex)
    p = s[0,1]*s[1,2]*s[2,0]
    l = np.linalg.cholesky(s)
    rows=[0,1,2]; cols=[1,2,0]
    results=[]
    for k in [1,2,3,8,24]:
        # Wick sum by independently enumerating pairings and replica partitions.
        exact = 0j
        for perm in itertools.permutations(range(3)):
            seen=set(); cycles=0
            for i in range(3):
                if i not in seen:
                    cycles+=1; j=i
                    while j not in seen:
                        seen.add(j); j=perm[j]
            exact += k**(cycles-3)*np.prod([s[rows[j],cols[perm[j]]] for j in range(3)])
        claimed = p + p.conjugate()/k**2 + (s[0,0]*abs(s[1,2])**2+s[1,1]*abs(s[2,0])**2+s[2,2]*abs(s[0,1])**2)/k + np.prod(np.diag(s))/k**2
        values=[]
        for _ in range(30):
            z=(RNG.normal(size=(2000,k,3))+1j*RNG.normal(size=(2000,k,3)))/np.sqrt(2)
            z=z@l.T
            c=np.einsum('nki,nkj->nij',z,z.conj())/k
            values.append(c[:,0,1]*c[:,1,2]*c[:,2,0])
        values=np.concatenate(values)
        results.append(dict(K=k,wick_error=abs(exact-claimed),exact_real=exact.real,
                            exact_imag=exact.imag,MC_real=values.real.mean(),
                            MC_imag=values.imag.mean(),MC_imag_SE=values.imag.std(ddof=1)/np.sqrt(len(values)),
                            max_abs_imag=float(abs(values.imag).max())))
    return results

def window_weights(fs,T,detrend):
    n=int(round(fs*T)); t=np.arange(n)
    f=np.fft.rfftfreq(n,1/fs)
    chosen=(f>=2)&(f<=30)
    f=f[chosen]
    window=np.sin(np.pi*t/n)**2
    a=window[None,:]*np.exp(-2j*np.pi*f[:,None]*t[None,:]/fs)
    if detrend:
        design=np.column_stack([np.ones(n),t-t.mean()])
        a=a-(a@design)@np.linalg.inv(design.T@design)@design.T
    coeff=np.array([correlate(row,row,mode='full',method='fft') for row in a])
    return f,coeff/np.dot(window,window),np.arange(-n+1,n)

def expected_spectrum(T,delay_seconds=.125,linewidth=.15,fs=160,detrend=True,nchannels=3):
    f,w,lags=window_weights(fs,T,detrend)
    delays=np.tile([0,round(delay_seconds*fs),0],nchannels//3)
    u=np.ones(nchannels); v=np.tile([1,1,-1],nchannels//3)
    cov=np.zeros((len(lags),nchannels,nchannels))
    for freq,variance,loading in [(9.75,1.,u),(10.25,.4,v)]:
        lag=lags[:,None,None]-delays[None,:,None]+delays[None,None,:]
        cov+=variance*np.exp(-2*np.pi*linewidth*abs(lag)/fs)*np.cos(2*np.pi*freq*lag/fs)*loading[None,:,None]*loading[None,None,:]
    # Independent additive sensor noise, per-sample variance .2.
    cov[lags==0]+= .2*np.eye(nchannels)
    s=np.einsum('fl,lij->fij',w,cov)
    d=np.sqrt(np.diagonal(s,axis1=1,axis2=2).real)
    c=s/d[:,:,None]/d[:,None,:]
    tri=np.array(list(itertools.combinations(range(nchannels),3)))
    vv=np.imag(c[:,tri[:,0],tri[:,1]]*c[:,tri[:,1],tri[:,2]]*c[:,tri[:,2],tri[:,0]])
    return f,s,vv

def leakage_checks():
    out=[]
    for delay in [0,.025,.125,.5]:
        for T in [1,2,4,8,16]:
            f,s,v=expected_spectrum(T,delay_seconds=delay)
            out.append(dict(delay_s=delay,T_s=T,max_abs_expected_closure=float(abs(v).max()),
                            mean_squared_expected_closure=float(np.mean(v*v)),
                            peak_frequency=float(f[np.argmax(abs(v[:,0]))])))
    # Multichannel counterexample matching the primary 12-channel count.
    f,s,v=expected_spectrum(2,delay_seconds=.125,nchannels=12)
    return dict(three_channel_results=out,
                twelve_channel_2s_delay125ms_mean_v2=float(np.mean(v*v)),
                twelve_channel_2s_delay125ms_peak_abs_v=float(abs(v).max()),
                interpretation='Exact expected finite tapered spectral matrices; infinite independent replica score. This is a stationary Gaussian reversible latent model with post-mixture diagonal pure-delay channel filters and independent sensor noise.')

def finite_record_counterexample(n_records=500):
    rng=np.random.default_rng(732419)
    fs=160; n=60*fs; burn=12*fs; delay=20
    r=np.exp(-2*np.pi*.15/fs)
    starts=np.r_[np.arange(2,26,2),np.arange(34,58,2)]*fs
    indices=starts[:,None]+np.arange(320)[None,:]
    times=np.arange(320)
    design=np.column_stack([np.ones(320),times-times.mean()])
    d_inv=np.linalg.inv(design.T@design)
    window=np.sin(np.pi*times/320)**2
    frequencies=np.fft.rfftfreq(320,1/fs)
    keep=(frequencies>=2)&(frequencies<=30)
    tr=np.array(list(itertools.combinations(range(12),3)))
    delays=np.tile([0,delay,0],4)
    v=np.tile([1,1,-1],4)
    scores=[]
    for record in range(n_records):
        modes=[]
        for freq in [9.75,10.25]:
            eps=(rng.normal(size=n+burn+delay)+1j*rng.normal(size=n+burn+delay))/np.sqrt(2)
            mode=np.sqrt(2)*lfilter([np.sqrt(1-r*r)],[1,-r*np.exp(2j*np.pi*freq/fs)],eps).real
            modes.append(mode)
        y=np.empty((n,12))
        for i in range(12):
            sl=slice(burn+delay-delays[i],burn+delay-delays[i]+n)
            y[:,i]=modes[0][sl]+np.sqrt(.4)*v[i]*modes[1][sl]
        y+=rng.normal(scale=np.sqrt(.2),size=y.shape)
        epochs=y[indices]
        beta=np.einsum('tc,ktn->kcn',design,epochs)
        fit=np.einsum('tc,cd,kdn->ktn',design,d_inv,beta)
        z=np.fft.rfft((epochs-fit)*window[None,:,None],axis=1)[:,keep,:]
        values=[]
        for block in [z[:12],z[12:]]:
            s=np.einsum('kfi,kfj->fij',block,block.conj())/12
            diag=np.sqrt(np.diagonal(s,axis1=1,axis2=2).real)
            c=s/diag[:,:,None]/diag[:,None,:]
            values.append(np.imag(c[:,tr[:,0],tr[:,1]]*c[:,tr[:,1],tr[:,2]]*c[:,tr[:,2],tr[:,0]]))
        scores.append(np.mean(values[0]*values[1]))
    scores=np.array(scores)
    np.save(OUT/'adversarial_M0_60s_scores.npy',scores)
    # A single frozen first-99 group matches the confirmatory EEG subject count.
    group=scores[:99]
    simulated_means=(rng.choice([-1.,1.],size=(49999,len(group)))@group)/len(group)
    p=(1+np.sum(simulated_means>=group.mean()))/50000
    return dict(n_records=n_records,mean=float(scores.mean()),SE=float(scores.std(ddof=1)/np.sqrt(n_records)),
                mean_95_normal_CI=[float(scores.mean()+q*1.96*scores.std(ddof=1)/np.sqrt(n_records)) for q in [-1,1]],
                proportion_positive=float(np.mean(scores>0)),first99_mean=float(group.mean()),
                first99_signflip_p=float(p),score_file='adversarial_M0_60s_scores.npy')

def quadratic_certificate_checks():
    rng=np.random.default_rng(84792)
    identity_error=0.;gradient_error=0.;min_dual_eigenvalue=np.inf
    max_lower_over_candidate=-np.inf
    for n in [2,3,8,24]:
        for _ in range(50):
            b=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
            c=normalize(b@b.conj().T+np.eye(n))
            a=np.linalg.solve(c.T,np.eye(n))*c.T
            theta=rng.uniform(-np.pi,np.pi,n)
            v=np.exp(1j*theta)
            value=.5*(np.vdot(v,a@v).real-n)
            direct=reversal(transform(c,theta/2))
            identity_error=max(identity_error,abs(value-direct))
            gradient=(v.conj()*(a@v)).imag
            for j in [0,n-1]:
                step=np.zeros(n);step[j]=1e-6
                vp=np.exp(1j*(theta+step));vm=np.exp(1j*(theta-step))
                fd=.25*(np.vdot(vp,a@vp).real-np.vdot(vm,a@vm).real)/1e-6
                gradient_error=max(gradient_error,abs(fd-gradient[j]))
            d=(v.conj()*(a@v)).real
            m=a-np.diag(d)
            shift=max(0.,-np.linalg.eigvalsh(m)[0])+1e-12*max(1.,np.linalg.norm(a,2))
            dd=d-shift
            lower=.5*(dd.sum()-n)
            min_dual_eigenvalue=min(min_dual_eigenvalue,np.linalg.eigvalsh(a-np.diag(dd))[0])
            max_lower_over_candidate=max(max_lower_over_candidate,lower-value)
    return dict(n_cases=200,max_quadratic_identity_error=identity_error,
                max_finite_difference_gradient_error=gradient_error,
                min_shifted_dual_eigenvalue=min_dual_eigenvalue,
                max_dual_lower_minus_candidate_upper=max_lower_over_candidate)

if __name__=='__main__':
    results={}
    for name,fun in [('matrices',matrix_checks),('wishart',wishart_checks),('leakage',leakage_checks),('finite_record_counterexample',finite_record_counterexample),('quadratic_certificate',quadratic_certificate_checks)]:
        results[name]=fun()
        (OUT/'math_review_exact_outputs.json').write_text(json.dumps(results,indent=2))
        print(name,json.dumps(results[name],indent=2),flush=True)
