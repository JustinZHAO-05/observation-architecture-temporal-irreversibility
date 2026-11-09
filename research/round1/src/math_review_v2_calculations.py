"""Frozen independent follow-up: leakage scaling, sharpness, conditioning."""
from pathlib import Path
import itertools
import json
import time
import numpy as np
from scipy.linalg import cholesky, solve_triangular
from scipy.optimize import minimize
import math_review_independent as audit

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'reviews'

def stable_E(c):
    r=c.real; y=c.imag
    ll=cholesky(r,lower=True)
    t=solve_triangular(ll,y,lower=True)
    b=solve_triangular(ll,t.T,lower=True).T
    b=.5*(b-b.T)
    eigen=np.linalg.eigvalsh(1j*b)
    return float(np.sum(eigen*eigen/(1-eigen*eigen)))

def triangle_matrix(r,angles):
    c=np.eye(3,dtype=complex)
    for j,(a,b) in enumerate([(0,1),(1,2),(2,0)]):
        c[a,b]=r[j]*np.exp(1j*angles[j]);c[b,a]=c[a,b].conjugate()
    return c

def sharpness():
    results=[]
    for loading in [[1,1,1],[1,.7,.25],[1,.7,.05]]:
        aa=np.array(loading,float)
        for eps in [.1,.03,.01,.003,.001]:
            for psi in [.1,.03,.01,.003,.001]:
                rr=eps*aa
                fraction=(1/rr**2)/np.sum(1/rr**2)
                predicted=2*psi**2/np.sum(1/rr**2)
                def angles(q):return psi*np.r_[q,1-np.sum(q)]
                def objective(q):return stable_E(triangle_matrix(rr,angles(q)))/predicted
                fit=minimize(objective,fraction[:2],method='BFGS',options={'gtol':1e-8,'maxiter':300})
                c=triangle_matrix(rr,angles(fit.x))
                est=stable_E(c)
                lam=np.linalg.eigvalsh(c)[-1]
                lb=2*np.sin(psi)**2/(lam*lam*np.sum(1/rr**2))
                # Same matrix used by the root certificate, to quantify cancellation.
                a=np.linalg.inv(c.T)*c.T
                computed=.5*((np.ones(3)@a@np.ones(3)).real-3)
                buffer=1e-12*max(1.,np.linalg.norm(a,2))
                results.append(dict(amplitudes=loading,epsilon=eps,psi=psi,
                                    Estar_numerical=est,L=lb,leading=predicted,
                                    Estar_over_leading=est/predicted,L_over_leading=lb/predicted,
                                    Estar_over_L=est/lb,
                                    residual_phase_fractions=list(np.r_[fit.x,1-np.sum(fit.x)]),
                                    leading_phase_fractions=list(fraction),
                                    quadratic_objective=computed,
                                    quadratic_absolute_error=abs(computed-est),
                                    minimum_dual_buffer_gap=1.5*buffer))
    return results

def psd_and_derivative(f,f0,linewidth=.15,fs=160):
    r=np.exp(-2*np.pi*linewidth/fs)
    theta=2*np.pi*(f+np.array([-f0,f0]))/fs
    denominator=1-2*r*np.cos(theta)+r*r
    p=.5*(1-r*r)*np.sum(1/denominator)
    dp=-.5*(1-r*r)*np.sum(2*r*np.sin(theta)*(2*np.pi/fs)/denominator**2)
    return p,dp

def coefficient(delay_s):
    p1,dp1=psd_and_derivative(10.,9.75)
    p2,dp2=psd_and_derivative(10.,10.25)
    r=np.array([p1+.4*p2,p1-.4*p2,p1-.4*p2])
    dr=np.array([dp1+.4*dp2,dp1-.4*dp2,dp1-.4*dp2])
    dd=np.array([2*np.pi*delay_s,-2*np.pi*delay_s,0])
    b=sum(np.prod(np.delete(r,j))*dr[j]*dd[j] for j in range(3))
    power=p1+.4*p2+.2
    return float(b/(3*power**3))

def leakage_curves():
    fs=160
    previous=OUT/'math_review_v2_leakage_partial.json'
    output=json.loads(previous.read_text()) if previous.exists() else []
    completed={row['T_s'] for row in output}
    for duration in [1,2,4,8,16,32]:
        if duration in completed:
            continue
        before=time.perf_counter()
        f,weights,lags=audit.window_weights(fs,duration,True)
        for delay_s in [.025,.125,.5]:
            delay=np.array([0,round(delay_s*fs),0])
            covariance=np.zeros((len(lags),3,3))
            lag=lags[:,None,None]-delay[None,:,None]+delay[None,None,:]
            for center,variance,loading in [(9.75,1.,np.ones(3)),(10.25,.4,np.array([1,1,-1]))]:
                covariance+=variance*np.exp(-2*np.pi*.15*abs(lag)/fs)*np.cos(2*np.pi*center*lag/fs)*loading[None,:,None]*loading[None,None,:]
            covariance[lags==0]+=.2*np.eye(3)
            spectrum=np.einsum('fl,lij->fij',weights,covariance)
            d=np.sqrt(np.diagonal(spectrum,axis1=1,axis2=2).real)
            c=spectrum/d[:,:,None]/d[:,None,:]
            v=(c[:,0,1]*c[:,1,2]*c[:,2,0]).imag
            v10=float(v[np.argmin(abs(f-10))])
            target=coefficient(delay_s)
            output.append(dict(T_s=duration,delay_s=delay_s,closure_at10Hz=v10,
                               T2_closure_at10Hz=duration**2*v10,
                               asymptotic_T2_coefficient=target,
                               observed_over_asymptotic=duration**2*v10/target,
                               mean_v2_3channels=float(np.mean(v*v)),
                               mean_v2_12channels=float(np.mean(v*v)*64/220),
                               T4_mean_v2_3channels=float(duration**4*np.mean(v*v)),
                               max_abs_v=float(abs(v).max()),peak_frequency=float(f[np.argmax(abs(v))])))
        print('window',duration,'elapsed_s',time.perf_counter()-before,flush=True)
        (OUT/'math_review_v2_leakage_partial.json').write_text(json.dumps(output,indent=2))
    return output

def finite_record_serialization():
    rng=np.random.default_rng(801242)
    n=16;p=3;q=3;L=4
    b=rng.normal(scale=.25,size=(p,q,L+1))
    b[:,:,0]+=np.eye(p)
    delays=np.arange(q)*(n+L+1)
    memory=int(delays[-1]+L)
    h=np.zeros((p,memory+1))
    for a in range(q):
        h[:,delays[a]:delays[a]+L+1]+=b[:,a,:]
    # Explicit innovation-to-observation maps, separately constructed.
    target_map=np.zeros((n*p,q*(n+L)))
    scalar_map=np.zeros((n*p,n+memory))
    for t in range(n):
        for i in range(p):
            for a in range(q):
                for k in range(L+1):
                    target_map[t*p+i,a*(n+L)+t-k+L]+=b[i,a,k]
            for k in range(memory+1):
                scalar_map[t*p+i,t-k+memory]+=h[i,k]
    target=target_map@target_map.T+.2*np.eye(n*p)
    serialized=scalar_map@scalar_map.T+.2*np.eye(n*p)
    frequencies=np.linspace(.001,.499,501)
    target_max=0.;null_max=0.
    for f in frequencies:
        transfer=np.einsum('iak,k->ia',b,np.exp(-2j*np.pi*f*np.arange(L+1)))
        target_s=transfer@transfer.conj().T+.2*np.eye(p)
        scalar_transfer=h@np.exp(-2j*np.pi*f*np.arange(memory+1))
        null_s=scalar_transfer[:,None]*scalar_transfer.conj()[None,:]+.2*np.eye(p)
        target_max=max(target_max,abs(audit.cycle(target_s).imag))
        null_max=max(null_max,abs(audit.cycle(null_s).imag))
    np.savez(OUT/'serialization_covariance_example.npz',target_covariance=target,
             serialized_covariance=serialized,target_coefficients=b,serialized_filters=h,delays=delays)
    return dict(record_length=n,channels=p,input_streams=q,target_MA_order=L,
                shifts=list(map(int,delays)),serialized_filter_memory=memory,
                max_block_covariance_difference=float(abs(target-serialized).max()),
                Frobenius_block_covariance_difference=float(np.linalg.norm(target-serialized)),
                minimum_block_covariance_eigenvalue=float(np.linalg.eigvalsh(target)[0]),
                target_max_population_abs_imag_cycle=float(target_max),
                serialized_max_population_abs_imag_cycle=float(null_max),
                independent_output_noise_variance=.2)

def conditional_bound_checks():
    rng=np.random.default_rng(720182)
    largest_excess=-np.inf;largest_ratio=0.;largest_cycle_error_ratio=0.
    for _ in range(1000):
        z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        c=audit.normalize(z@z.conj().T+.1*np.eye(3))
        z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        other=audit.normalize(z@z.conj().T+.1*np.eye(3))
        fraction=10**rng.uniform(-5,-2)
        chat=(1-fraction)*c+fraction*other
        error=float(abs(chat-c).max())
        phat=audit.cycle(chat).imag
        rplus=np.minimum(1,np.abs([chat[0,1],chat[1,2],chat[2,0]])+error)
        dplus=sum(rplus[i]**2*rplus[j]**2 for i,j in [(0,1),(1,2),(2,0)])
        lplus=min(3.,np.linalg.eigvalsh(chat)[-1]+2*error)
        lower=2*max(0,abs(phat)-3*error)**2/(lplus*lplus*dplus)
        exact=audit.lower_bound(c)
        largest_excess=max(largest_excess,lower-exact)
        largest_ratio=max(largest_ratio,lower/exact)
        largest_cycle_error_ratio=max(largest_cycle_error_ratio,abs(phat-audit.cycle(c).imag)/(3*error))
    return dict(n_cases=1000,max_conditional_minus_true_L=float(largest_excess),
                max_conditional_over_true_L=float(largest_ratio),
                max_cycle_imaginary_error_over_3epsilon=float(largest_cycle_error_ratio))

def projection_checks():
    rng=np.random.default_rng(95382); output=[]
    for n in [3,5,8]:
        z=rng.normal(size=(n,n));r=z@z.T+np.eye(n)
        r=audit.normalize(r)
        y=rng.normal(size=(n,n));y=y-y.T
        ll=cholesky(r,lower=True)
        def white(y):
            t=solve_triangular(ll,y,lower=True)
            return solve_triangular(ll,t.T,lower=True).T
        y=y/np.linalg.norm(1j*white(y),2)
        wy=white(y)
        directions=[]
        for j in range(1,n):
            e=np.zeros((n,n));e[j,j]=1
            directions.append(white(e@r-r@e))
        directions=np.array(directions)
        gram=np.einsum('aij,bij->ab',directions,directions)
        linear=np.einsum('aij,ij->a',directions,wy)
        phase=-np.linalg.solve(gram,linear)
        residual=wy+np.einsum('a,aij->ij',phase,directions)
        leading=float(np.sum(residual*residual))
        for eps in [.1,.03,.01,.003,.001]:
            c=r+1j*eps*y
            def objective(q):
                u=np.exp(1j*eps*np.r_[0,q])
                return stable_E(c*u[:,None]*u.conj()[None,:])/(eps*eps*leading)
            fit=minimize(objective,phase,method='BFGS',options={'gtol':1e-8,'maxiter':400})
            output.append(dict(dimension=n,epsilon=eps,projection_coefficient=leading,
                               optimized_over_projected=float(fit.fun),
                               projection_normal_equation_residual=float(np.linalg.norm(gram@phase+linear))))
    return output

def conditioning_checks():
    rng=np.random.default_rng(29478); output=[]
    for requested in [1e1,1e3,1e5,1e7,1e9,1e11,1e13]:
        z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        q,_=np.linalg.qr(z)
        c=audit.normalize(q@np.diag([1,requested**-.5,1/requested])@q.conj().T)
        inverse=np.linalg.inv(c.T)
        a=inverse*c.T
        hermitian_defect=np.linalg.norm(a-a.conj().T,2)
        aa=.5*(a+a.conj().T)
        candidate=np.ones(3)
        value=.5*(np.vdot(candidate,aa@candidate).real-3)
        direct=audit.reversal(c)
        residual=np.linalg.norm(np.eye(3)-c.T@inverse,2)
        buffer=1e-12*max(1.,np.linalg.norm(aa,2))
        output.append(dict(requested_condition=requested,actual_condition=float(np.linalg.cond(c)),
                           inverse_residual=float(residual),schur_hermitian_defect=float(hermitian_defect),
                           quadratic_value=float(value),independent_Cholesky_value=float(direct),
                           objective_disagreement=float(abs(value-direct)),
                           relative_disagreement=float(abs(value-direct)/direct),
                           eigenvalue_buffer=float(buffer)))
    return output

if __name__=='__main__':
    results={}
    for name,function in [('serialization',finite_record_serialization),('conditional_bound',conditional_bound_checks),('leakage',leakage_curves),('sharpness',sharpness),('projection',projection_checks),('conditioning',conditioning_checks)]:
        start=time.perf_counter(); results[name]=function()
        (OUT/'math_review_v2_outputs.json').write_text(json.dumps(results,indent=2))
        print(name,'done_s',time.perf_counter()-start,flush=True)
