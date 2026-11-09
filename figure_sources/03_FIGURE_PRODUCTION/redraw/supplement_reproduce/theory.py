"""S1–S4: geometry, finite blocks, population lift and optimization audit."""
import json

import numpy as np
import pandas as pd

from style import (BLUE, ORANGE, TEAL, GRAY, LIGHT, INK, COLORS, MARKERS,
                   supplement, legend, key_ticks, import_file, vector_matrix)


def s1(root, out):
    f = supplement(root, out, 1, ["Spanning tree and fundamental cycles", "When the gauge is real",
                                  "Joint weak-coherence limit", "Optimal phase allocation"])
    _, _, c, d = f.panels
    nodes = np.array([[.10,.25],[.28,.71],[.50,.24],[.72,.71],[.90,.25]])
    tree = [(0,1,.34),(1,2,.21),(2,3,.40),(3,4,-.27)]
    chords = [(2,0,.28),(4,2,np.pi-.13)]
    phases = np.r_[0,np.cumsum([r[2] for r in tree])]
    edges = []
    for i,j,phi in tree+chords:
        chord = (i,j,phi) in chords
        q, r = nodes[[i,j]]
        gauge = phi+phases[i]-phases[j]
        edges.append(dict(i=i+1,j=j+1,edge="chord" if chord else "tree", phase_rad=phi,
                          theta_i_rad=phases[i],theta_j_rad=phases[j], gauged_phase_rad=gauge,
                          xi=q[0], yi=q[1], xj=r[0], yj=r[1]))
    assert np.allclose([x["gauged_phase_rad"] for x in edges], [0]*4+[.83,np.pi])
    f.csv("A", edges)

    labels = []
    for k,phi in enumerate((.83,np.pi),1):
        x,y=np.cos(phi),np.sin(phi)
        labels.append(dict(cycle=k,closure_rad=phi,normalized_cycle_re=x,normalized_cycle_im=y,
                           real_gauge_condition=np.isclose(y,0)))
    f.csv("B",labels)

    sharp = pd.DataFrame(json.loads((f.r1/"reviews/math_review_v2_outputs.json").read_text())["sharpness"])
    sharp["family"] = sharp.amplitudes.map(lambda xs: ":".join(map(str,xs)))
    joint = sharp[np.isclose(sharp.epsilon,sharp.psi)].copy()
    joint["bound_over_phase_minimum"] = joint.L/joint.Estar_numerical
    assert len(sharp)==75 and len(joint)==15 and joint.bound_over_phase_minimum.between(0,1).all()
    f.csv("C",joint)
    f.csv("C",sharp,"_full_scan")
    ax=c.ax()
    for k,(label,g) in enumerate(joint.groupby("family")):
        g=g.sort_values("epsilon")
        ax.semilogx(g.epsilon,g.bound_over_phase_minimum,marker=MARKERS[k],ms=3.7,
                    color=COLORS[k],lw=1.1,label=label)
    ax.axhline(1,color=GRAY,ls="--",lw=.72)
    ax.set(xlabel=r"Joint path $\epsilon=\psi$",ylabel=r"$L(C)/\mathcal{E}_*$",ylim=(.51,1.035))
    legend(ax,title="Relative edge strengths",loc="lower left")

    fixed = sharp[np.isclose(sharp.epsilon,.003)&np.isclose(sharp.psi,.003)]
    assert len(fixed)==3
    rows=[]
    ax=d.ax()
    for k,(label,g) in enumerate(fixed.groupby("family")):
        row=g.iloc[0]
        assert np.isclose(sum(row.residual_phase_fractions),1,atol=1e-7)
        for i,(opt,leading) in enumerate(zip(row.residual_phase_fractions,row.leading_phase_fractions,strict=True)):
            rows.append(dict(family=label,edge=["12","23","31"][i],edge_strength=.003*row.amplitudes[i],
                             epsilon=row.epsilon,psi_rad=row.psi,optimized_fraction=opt,leading_fraction=leading))
        xs=np.arange(3)+(k-1)*.23
        ax.bar(xs,row.residual_phase_fractions,width=.205,color=COLORS[k],alpha=.78,label=label)
        ax.scatter(xs,row.leading_phase_fractions,marker="_",s=54,lw=1.05,color=INK,zorder=4)
    ax.set(xticks=np.arange(3),xticklabels=["12","23","31"],xlabel="Edge",
           ylabel="Fraction of closure phase",ylim=(0,1.02))
    legend(ax,loc="upper left",ncol=2,title="Relative edge strengths")
    f.csv("D",rows)
    f.finish(r"""
**Figure S1. Phase geometry and allocation.**
(a) A five-vertex example has four spanning-tree edges and two closing edges. Channel phases make the tree edges real. The two closing edges carry the fundamental-cycle phases.
(b) After the tree gauge, the two example cycle phases are \(0.83\) and \(\pi\) rad. A real gauge requires every fundamental-cycle phase to be \(0\) modulo \(\pi\).
(c) Archived sharpness scans along the joint path \(\epsilon=\psi\), with \(r_e=\epsilon a_e\). The triangle lower bound and the numerical phase minimum agree to leading order as \(\epsilon\) decreases. The full 75-point scan is provided.
(d) Fractions of the closure phase borne by each edge at \(\epsilon=\psi=0.003\). Bars give the numerical phase optimum and black marks the leading weights \(a_e^{-2}/\sum_j a_j^{-2}\).
""")


def s2(root,out):
    boxes=[(0,.53,.48,.47),(.52,.53,.48,.47),(0,0,1,.47)]
    f=supplement(root,out,2,["Shared white-noise serialization","Exact finite-record covariance",
                             "Population spectra differ"],boxes=boxes)
    _,b,c=f.panels
    path=f.r1/"reviews"
    spec=json.loads((path/"math_review_v2_outputs.json").read_text())["serialization"]
    with np.load(path/"serialization_covariance_example.npz") as z:
        delay=z["delays"]
        target,serialized=z["target_covariance"],z["serialized_covariance"]
        coeff,filters=z["target_coefficients"],z["serialized_filters"]
    n,m=spec["record_length"],spec["target_MA_order"]
    noise=spec["independent_output_noise_variance"]
    first,last=-delay-m,n-1-delay
    assert (n,m)==(16,4) and np.all(last[1:]<first[:-1])
    f.csv("A",dict(stream=np.arange(1,4),delay_samples=delay,first_index=first,last_index=last,
                   filter_order=m,record_length=n))

    residual=serialized-target
    maxerr=float(abs(residual).max())
    assert target.shape==serialized.shape==(48,48) and np.isclose(maxerr,spec["max_block_covariance_difference"],rtol=1e-13,atol=0)
    f.npz("B",target_covariance=target,serialized_covariance=serialized,residual=residual)
    lim=max(abs(target).max(),abs(serialized).max())
    for i,(matrix,label) in enumerate(((target,"Target"),(serialized,"Serialized"))):
        ax=b.ax(.035+.48*i,.19,.455,.61)
        im=vector_matrix(ax,matrix,lim)
        ax.set_title(label,pad=3)
    ax=b.ax(.26,.16,.48,.031)
    f.figure.colorbar(im,cax=ax,orientation="horizontal",ticks=[-lim,0,lim],
                      format="%.1f").solids.set_label("colorbar-solids")
    note=b.ax(.05,.005,.90,.06,diagram=True)
    note.text(.5,.45,rf"$\max|\Delta|={maxerr/1e-16:.2f}\times10^{{-16}}$",ha="center",color=GRAY)

    w=np.linspace(.002*np.pi,.998*np.pi,501)
    h=np.einsum("iak,fk->fia",coeff,np.exp(-1j*w[:,None]*np.arange(m+1)))
    g=np.exp(-1j*w[:,None]*np.arange(filters.shape[1]))@filters.T
    st=h@h.conj().transpose(0,2,1)+noise*np.eye(3)
    ss=g[:,:,None]*g[:,None,:].conj()+noise*np.eye(3)
    core=import_file(f.r1/"src/closure_core.py","supp_core_s2")
    ct=core.cycle_product(core.coherency(st))[:,0].imag
    cs=core.cycle_product(core.coherency(ss))[:,0].imag
    norm=np.linalg.norm(st-ss,axis=(-2,-1))
    assert np.max(abs(cs))<5e-16 and np.isclose(abs(ct).max(),spec["target_max_population_abs_imag_cycle"])
    f.npz("C",omega_rad_sample=w,target_spectrum=st,serialized_spectrum=ss,
          target_im_cycle=ct,serialized_im_cycle=cs,spectrum_difference_frobenius=norm)
    ax=c.ax(.106,.19,.354,.64)
    ax.plot(w/np.pi,ct,color=ORANGE,lw=1.25,label="Target")
    ax.plot(w/np.pi,cs,color=GRAY,ls="--",lw=.87,label="Serialized")
    ax.set(xlabel=r"$\omega/\pi$",ylabel=r"$\mathrm{Im}\,P$",xlim=(0,1))
    legend(ax,loc="upper left",ncol=2)
    ax=c.ax(.604,.19,.376,.64)
    ax.plot(w/np.pi,norm,color=BLUE,lw=1.10)
    ax.set(xlabel=r"$\omega/\pi$",ylabel=r"$\|\Delta S\|_{\mathrm{F}}$",xlim=(0,1))

    f.finish(r"""
**Figure S2. Finite-record serialization and population spectral differences.**
(a) With \(N=16\) and MA order \(L=4\), shifts of 0, 21 and 42 samples select disjoint blocks of one white-noise stream. Pale segments are the four additional innovations before each record.
(b) Target and serialized \(48\times48\) covariance matrices in time-major order, with maximum absolute discrepancy \(4.44\times10^{-16}\). The common color scale gives covariance in the model's variance units.
(c) Imaginary cycle and spectral-matrix Frobenius discrepancy on a common angular-frequency grid, including independent output noise of variance 0.2 in each construction. The serialized cycle is real.
""")


def coordinate_minima(f, coord):
    spectrum=import_file(f.r2/"src/theory_round2.py","supp_round2_theory")
    core=import_file(f.r1/"src/closure_core.py","supp_core_s3")
    rng=np.random.default_rng(341903)
    opt=np.random.default_rng(261112)
    rows=[]
    for row in coord.itertuples(index=False):
        b,w=rng.uniform(.05,.95),rng.uniform(.01,np.pi-.01)
        np.testing.assert_allclose([b,w],[row.b,row.w],atol=2e-15,rtol=0)
        s=spectrum.ma_spectrum(b,w)
        rotation,_=np.linalg.qr(rng.normal(size=(3,3)))
        rotated=rotation@s@rotation.T
        raw=[spectrum.E(x) for x in (s,rotated)]
        np.testing.assert_allclose(raw,[row.raw_E_before,row.raw_E_after],atol=7e-14,rtol=0)
        bounds=[core.phase_reversal_certificate(x,rng=opt,starts=8) for x in (s,rotated)]
        pair=[(a["lower_bound"],a["upper_bound"]) for a in bounds]
        rows.append(dict(rep=row.rep,b=b,omega_rad_sample=w,raw_before=raw[0],raw_after=raw[1],
                         raw_change=raw[1]-raw[0],lower_before=pair[0][0],upper_before=pair[0][1],
                         lower_after=pair[1][0],upper_after=pair[1][1],
                         phase_change_lower=pair[1][0]-pair[0][1],phase_change_upper=pair[1][1]-pair[0][0]))
    result=pd.DataFrame(rows)
    result["phase_change"]=(result.phase_change_lower+result.phase_change_upper)/2
    result["change_interval_width"]=result.phase_change_upper-result.phase_change_lower
    assert len(result)==600 and result.raw_change.abs().max()<7e-14
    assert result.change_interval_width.max()<1e-7
    return result


def s3(root,out):
    f=supplement(root,out,3,["Reconstruction accuracy","Latent positive definiteness",
                             "Maximum observed reversal","Orthogonal basis changes"])
    net=f.archive_csv(2,"general_lift_validation.csv")
    assert len(net)==90 and net.groupby("dimension").size().to_dict()=={3:30,6:30,12:30}
    assert (net.min_latent_eigenvalue>0).all()
    net["plot_jitter"]=f.rng.uniform(-.18,.18,len(net))
    for p,col,label,scale in zip(f.panels[:3],("max_relative_error","min_latent_eigenvalue","max_observed_reversal"),
            ("Maximum relative error","Minimum latent eigenvalue","Maximum reversal density (nats)"),
            ("log","log","log"),strict=True):
        ax=p.ax(.18,.19,.78,.64)
        multiplier=1e16 if col=="max_relative_error" else 1
        for i,(dim,g) in enumerate(net.groupby("dimension")):
            values=g[col]*multiplier
            ax.scatter(i+g.plot_jitter,values,s=13,marker=MARKERS[i],facecolor="none",edgecolor=COLORS[i],lw=.67)
            ax.hlines(values.median(),i-.23,i+.23,color=INK,lw=1.05)
        ax.set(xticks=[0,1,2],xticklabels=[3,6,12],xlim=(-.5,2.5),yscale=scale,
               xlabel="Observed dimension",ylabel=label+(r" ($10^{-16}$)" if multiplier!=1 else ""))
        f.csv(p.key,net)

    coord=f.archive_csv(2,"coordinate_validation.csv")
    table=coordinate_minima(f,coord)
    p=f.panels[3]
    f.csv("D",table)
    ax=p.ax(.22,.60,.73,.22)
    ax.scatter(table.raw_before,table.raw_change*1e14,s=6,color=GRAY,alpha=.5,lw=0)
    ax.axhline(0,color=LIGHT,lw=.65)
    ax.set_ylabel(r"$\Delta\mathcal{E}$ ($10^{-14}$)")
    ax.tick_params(labelbottom=False)
    bx=p.ax(.22,.17,.73,.34)
    bx.scatter(table.raw_before,table.phase_change,s=6,color=ORANGE,alpha=.53,lw=0)
    bx.axhline(0,color=LIGHT,lw=.65)
    bx.set(xlabel="Raw reversal density (nats)",ylabel=r"$\Delta\mathcal{E}_*$ (nats)")
    for a in (ax,bx):
        a.set_xlim(-.03,table.raw_before.max()*1.03)
    f.finish(r"""
**Figure S3. General construction and coordinate audit.**
(a–c) Thirty independent VAR(1) networks at each observed dimension \(d=3,6,12\), evaluated at 83 frequencies per network. Each point is one network. The three panels show its maximum relative reconstruction error, minimum latent spectral eigenvalue and maximum observed Gaussian reversal density across the grid. Black marks give medians.
(d) Six hundred three-channel spectra and their paired real orthogonal rotations, replayed with seed 341903. Changes are rotated minus original. Raw reversal varies at floating-point scale. Phase-relaxed changes are midpoints of numerical primal–dual change intervals, computed with seed 261112. The CSV gives both endpoints. These are floating-point optimization bounds.
""")


def s4(root,out):
    f=supplement(root,out,4,["Analytic minimum and LP brackets","Width of the LP brackets",
                             "Equality and PSD diagnostics","Trace cost across parameters"])
    a,b,c,d=f.panels
    lp=f.archive_csv(2,"latency_cost_lp_intervals.csv")
    old=f.archive_csv(2,"latency_power_optimization.csv")
    assert len(lp)==len(old)==32 and lp.groupby("b").size().eq(8).all()
    assert (lp.lower_ratio<=lp.analytic_ratio+1e-14).all() and (lp.upper_ratio>=lp.analytic_ratio-1e-14).all()
    assert (lp.min_upper_eigenvalue>0).all()
    summary=json.loads((f.r2/"results/latency_cost_lp_summary.json").read_text())
    assert np.isclose(lp.relative_interval_width.max(),summary["max_relative_interval_width"],atol=1e-14)
    f.csv("A",lp)
    f.csv("B",lp)
    f.csv("C",lp)
    f.csv("C",old,"_slsqp")
    ax=a.ax()
    lo,hi=lp.analytic_ratio.min()*.89,lp.analytic_ratio.max()*1.12
    ax.plot([lo,hi],[lo,hi],color=LIGHT,ls="--",lw=.85)
    for i,(bval,g) in enumerate(lp.groupby("b")):
        mid=(g.upper_ratio+g.lower_ratio)/2
        ax.errorbar(g.analytic_ratio,mid,yerr=[mid-g.lower_ratio,g.upper_ratio-mid],ls="none",
                    marker=MARKERS[i],mfc="white",mec=COLORS[i],mew=.77,ms=3.8,color=COLORS[i],
                    lw=.75,label=f"{bval:g}")
    ax.set(xscale="log",yscale="log",xlim=(lo,hi),ylim=(lo,hi),xlabel="Analytic trace ratio",
           ylabel="LP trace ratio")
    legend(ax,loc="lower right",title=r"$b$",ncol=2)

    ax=b.ax()
    for i,(bval,g) in enumerate(lp.groupby("b")):
        ax.plot(g.theta,1e6*g.relative_interval_width,ls="none",marker=MARKERS[i],
                ms=3.8,color=COLORS[i],label=f"{bval:g}")
    ax.set(xscale="log",yscale="log",xlabel=r"Phase delay $\theta$ (rad)",ylabel="Relative width (ppm)")
    key_ticks(ax,[.1,.2,.4,.8,1.6,2.8])
    legend(ax,loc="lower left",title=r"$b$",ncol=2)

    ax=c.ax(.20,.19,.75,.64)
    ax.scatter(lp.constraint_error.clip(lower=1e-18),lp.min_upper_eigenvalue,s=17,facecolor="none",edgecolor=TEAL,
               lw=.7,label="LP upper endpoint")
    for ok,g in old.groupby("success"):
        ax.scatter(g.max_constraint_error.clip(lower=1e-18),g.minimum_eigenvalue,s=15,
                   marker="^" if ok else "x",color=GRAY if ok else ORANGE,lw=.7,
                   label="SLSQP success" if ok else "SLSQP stopped")
    ax.axhline(0,color=LIGHT,lw=.69)
    ax.set(xscale="log",xlabel="Equality residual",ylabel="Minimum latent eigenvalue")
    ax.set_yscale("symlog",linthresh=1e-10)
    ax.set_yticks([-1e-4,-1e-7,0,1e-7,1e-3,1e-1])
    ax.set_ylim(bottom=-.001,top=.4)
    legend(ax,loc="lower left",fontsize=7.35)

    theta=np.geomspace(.015,np.pi/2,151)
    strengths=np.linspace(.05,.99,131)
    t=(1-abs(np.cos(theta))*np.sqrt(1-strengths[:,None]**2))/np.sin(theta)**2
    f.npz("D",b=strengths,theta_rad=theta,minimum_trace_ratio=t)
    ax=d.ax(.145,.19,.65,.64)
    image=ax.contourf(theta,strengths,np.log10(t),levels=np.linspace(-.32,3.65,23),cmap="YlGnBu",extend="both")
    lines=ax.contour(theta,strengths,t,levels=[1,10,100,1000],colors=INK,linewidths=.61,alpha=.83)
    ax.clabel(lines,fmt="%d",inline=True,fontsize=7.15)
    ax.set(xscale="log",xlabel=r"Phase delay $\theta$ (rad)",ylabel=r"Antisymmetry strength $b$")
    key_ticks(ax,[.02,.1,.5,1.5])
    cb=d.ax(.84,.19,.024,.64)
    f.figure.colorbar(image,cax=cb,ticks=[0,1,2,3],label=r"$\log_{10}t_{\min}$")
    f.finish(r"""
**Figure S4. Spectral-power optimization and feasibility.**
(a) All 32 independent linear-programming checks of the closed form. Marks are the bracket midpoints, with lower and PSD-feasible upper endpoints. The widths are smaller than the markers at this scale.
(b) Relative bracket width \((t_{\mathrm{upper}}-t_{\mathrm{lower}})/t_{\min}\) in parts per million. The maximum is 2.30 ppm.
(c) Equality residual and smallest latent eigenvalue for each feasible LP upper endpoint and each earlier SLSQP output. A zero residual on the log axis would be plotted at \(10^{-18}\). Negative eigenvalues identify indefinite SLSQP outputs. The vertical axis is symmetric log with a linear interval near zero.
(d) Analytic \(t_{\min}(b,\theta)\) on an extended deterministic grid, with fixed unit gains. Lines denote contours of the untransformed ratio.
""")
