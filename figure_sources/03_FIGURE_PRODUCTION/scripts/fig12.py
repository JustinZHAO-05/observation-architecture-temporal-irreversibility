"""Population equivalence and the sensor-diagonal closure bound."""
import json

import numpy as np
from matplotlib.patches import Arc, Rectangle

from common import (A, B, GRAY, GREEN, INK, LATENT, TARGET, TWO, WIDE_TOP,
                    Build, arrow, block, import_file, math_sci, tag, vector_matrix)


def fig2(root, out):
    f = Build(root, out, "Fig2", 11.8,
              [(0,.52,.48,.48),(.52,.52,.48,.48),(0,0,.54,.47),(.57,0,.43,.47)],
              ["One delayed branch", "Full-record covariance",
               "Identical observed spectral cycles", "Across VAR(1) networks"])
    source = f.r2 / "results"
    summary = json.loads((source / "theory_summary.json").read_text())["exact_example"]
    theory = import_file(f.r2 / "src/theory_round2.py", "theory_round2")
    with np.load(source / "exact_short_memory_equivalence.npz") as z:
        latent = z["latent_covariance"]
        observation = z["observation_matrix"]
        target, mapped = z["target_covariance"], z["observed_covariance"]
        lags, w, archived_density = z["latent_lags"], z["w"], z["reversal"]
    assert latent.shape == (198, 198) and observation.shape == (96, 198)
    assert target.shape == mapped.shape == (96, 96)
    assert w.size == 513 and np.allclose(observation @ latent @ observation.T, mapped)
    expected = np.zeros_like(observation)
    for t in range(32):
        expected[3*t:3*t+3,6*(t+1):6*(t+1)+3] = np.eye(3)
        expected[3*t:3*t+3,6*t+3:6*t+6] = np.eye(3)
    assert np.array_equal(expected, observation)
    f.npz("A", latent_covariance=latent, observation_matrix=observation, latent_lags=lags,
          latent_times=np.arange(-1,32), observed_times=np.arange(32))

    p, q, r, s = f.panels
    ax = p.ax(.025,.07,.95,.77,diagram=True)
    tag(ax,.19,.98,"Reversible latent",color=LATENT,weight="semibold")
    tag(ax,.51,.98,"Filters",color=LATENT)
    tag(ax,.83,.98,"Observed",color=TARGET,weight="semibold")
    # Off-diagonal entries from G0; only the visible u-v covariances are drawn.
    u_y = np.array([.83,.74,.65])
    v_y = np.array([.48,.39,.30])
    for i in range(3):
        for j in range(3):
            if lags[0,i,j+3] != 0:
                arrow(ax,(.19,u_y[i]),(.19,v_y[j]),GRAY,curve=.25+.08*(i+j),
                      style="-",lw=.55)
    for i in range(3):
        y_u,y_v = u_y[i],v_y[i]
        y = .56 + (.18-i*.18)
        for group, y_in, op, color in (("u",y_u,r"$I$",LATENT),
                                        ("v",y_v,r"$z^{-1}$",B)):
            ax.scatter(.19,y_in,s=13,color=LATENT,zorder=5)
            ax.text(.145,y_in,rf"${group}_{i+1}$",ha="right",va="center")
            arrow(ax,(.22,y_in),(.45,y_in),color)
            block(ax,.50,y_in,.10,.068,op,color)
            arrow(ax,(.55,y_in),(.79,y),color,lw=.8)
        ax.scatter(.81,y,s=55,facecolor="white",edgecolor=TARGET,zorder=5)
        tag(ax,.81,y,"+",color=TARGET,zorder=6,size=7)
        arrow(ax,(.84,y),(.91,y),TARGET)
        tag(ax,.955,y,rf"$y_{i+1}$",color=TARGET)
    ax.text(.03,.21,r"Gray links: nonzero $G_0^{uv}$",size=7,color=LATENT)
    for y,label,color,current in ((.125,r"$u_i$",LATENT,1),(.04,r"$v_i$",B,0)):
        tag(ax,.40,y,label,color=color)
        ax.plot([.47,.66],[y,y],lw=.8,color=GRAY)
        ax.scatter([.49,.62],[y,y],s=9,facecolors="white",edgecolors=GRAY,zorder=4)
        ax.scatter([(.49,.62)[current]],[y],s=14,color=color,zorder=5)
    tag(ax,.49,.174,r"$t-1$",size=7)
    tag(ax,.62,.174,r"$t$",size=7)
    tag(ax,.85,.095,r"$y_i(t)=u_i(t)+v_i(t-1)$",color=TARGET,size=7.8)
    tag(ax,.88,.220,r"$\mathrm{Im}\,P_y\ne0$",color=TARGET,size=7)

    # The archive is time-major. Reorder to channel-major for the 32-sample blocks.
    order = np.arange(96).reshape(32,3).T.ravel()
    target, mapped = target[np.ix_(order,order)], mapped[np.ix_(order,order)]
    residual = mapped-target
    assert np.max(abs(residual)) == summary["max_full_record_covariance_difference"]
    f.npz("B", target_covariance=target, observed_covariance=mapped, residual=residual,
          archive_indices=order, channel=np.repeat(np.arange(1,4),32),
          sample=np.tile(np.arange(32),3))
    lim = max(abs(target).max(),abs(mapped).max())
    for x, matrix, title in ((.035,target,"Target"),(.375,mapped,"Constructed"),
                              (.795,residual,"Residual")):
        is_residual = title == "Residual"
        box=(x,.3525,.135,.425) if is_residual else (x,.31,.275,.51)
        ax = q.ax(*box,tag=title)
        image = vector_matrix(ax,matrix,np.finfo(float).eps if is_residual else lim)
        if is_residual:
            ax.set_aspect("auto")
        for i in (32,64):
            ax.axvline(i,color=GRAY,lw=.45)
            ax.axhline(i,color=GRAY,lw=.45)
        ax.set_title(title,pad=3)
        if not is_residual:
            ax.set_xticks([16,48,80],["1","2","3"],size=6.5)
            ax.tick_params(length=0,pad=1)
        if x == .03:
            cax = q.ax(.11,.19,.46,.037,tag="covariance-scale")
            f.figure.colorbar(image,cax=cax,orientation="horizontal",ticks=[-lim,0,lim]).solids.set_label("colorbar-solids")
        if is_residual:
            cax = q.ax(.78,.19,.167,.037,tag="residual-scale")
            f.figure.colorbar(image,cax=cax,orientation="horizontal",
                              ticks=[-np.finfo(float).eps,0,np.finfo(float).eps]).solids.set_label("colorbar-solids")
            cax.set_xticklabels([r"$-\epsilon$","0",r"$+\epsilon$"],size=6.5)
    note = q.ax(.04,.025,.92,.075,diagram=True)
    tag(note,.35,.43,"32 samples per channel | covariance",size=7)
    tag(note,.86,.43,r"$\max|\Delta|=0$",size=7)

    spectra = np.array([theory.ma_spectrum(summary["b"],x) for x in w])
    g = lags[0] + 2*np.cos(w)[:,None,None]*lags[1] + 2*np.cos(2*w)[:,None,None]*lags[2]
    eye = np.broadcast_to(np.eye(3),(w.size,3,3))
    h = np.concatenate((eye, np.exp(-1j*w[:,None,None])*eye),axis=2)
    recovered = h @ g @ h.conj().transpose(0,2,1)
    assert np.max(abs(recovered-spectra)) < 5e-16
    assert np.linalg.eigvalsh(g).min() > 0 and not np.iscomplexobj(g)
    cycle = lambda spec: (spec[:,0,1]*spec[:,1,2]*spec[:,2,0]).imag
    y, yhat = cycle(spectra),cycle(recovered)
    rate = 2*(1/np.sqrt(1-summary["b"]**2)-1)
    assert np.isclose(max(abs(y)),summary["max_abs_imaginary_cycle"])
    assert np.isclose(np.trapezoid(archived_density,w)/np.pi,rate)
    f.npz("C", omega_rad_sample=w, target_spectrum=spectra, mapped_spectrum=recovered,
          latent_spectrum=g, target_im_cycle=y, mapped_im_cycle=yhat,
          latent_im_cycle=np.zeros_like(w), observed_density=archived_density,
          observed_rate=rate, latent_rate=0.)
    ax = r.ax(.16,.38,.80,.44)
    ax.plot(w/np.pi,y,color=TARGET,label="Target")
    ax.plot(w/np.pi,yhat,linestyle="none",marker="o",mfc="white",mec=B,
            markevery=24,ms=3.2,label="Mapped latent")
    ax.set(xlim=(0,1),ylim=(-.151,.015),ylabel=r"$\mathrm{Im}(C_{12} C_{23} C_{31})$")
    ax.tick_params(labelbottom=False)
    ax.legend(frameon=False,loc="upper center",ncol=2,borderaxespad=.3)
    ax.annotate(r"$|\mathrm{Im}\,P|_{\max}=0.1403$",(.5,y.min()),(.72,-.132),
                arrowprops={"arrowstyle":"-","lw":.65},size=7)
    low = r.ax(.16,.19,.80,.14)
    low.axhline(0,color=LATENT,lw=1.2)
    low.set(xlim=(0,1),ylim=(-1,1),yticks=[0],xticks=[0,.25,.5,.75,1],
            xlabel=r"Normalized angular frequency $\omega/\pi$")
    low.text(.98,.74,"Reversible latent",transform=low.transAxes,ha="right",size=7,color=LATENT)

    table = f.archive_csv(2,"general_lift_validation.csv")
    assert table.groupby("dimension")["network"].nunique().to_dict() == {3:30,6:30,12:30}
    assert len(table)==90 and table.min_latent_eigenvalue.min()>0
    table["x_jitter"] = f.rng.uniform(-.17,.17,len(table))
    f.csv("D",table)
    ax=s.ax(.25,.19,.70,.64)
    network_strip(ax,table,"max_relative_error","Max. relative spectral error",log=True)
    ax.text(.085,.92,"Maximum "+math_sci(table.max_relative_error.max()),
            transform=ax.transAxes,size=7,color=LATENT)
    f.finish(r"""
**Figure 2. A single-sample differential delay gives population equivalence in Model B.**
(a) For the archived three-output example, the six-component reversible Gaussian latent
process has nonzero cross-covariances. Gray links show the nonzero entries of the
zero-lag \(u\)-\(v\) block, and the observation adds \(u_i(t)\) to \(v_i(t-1)\).
(b) The target and constructed covariances match on the full 32-sample record. Both
96×96 matrices are displayed channel-major, with time varying within each block.
The separate residual scale is \(\epsilon=2.22\times10^{-16}\) (double-precision machine
epsilon), and every displayed residual is zero.
(c) For \(b=0.9\), the oriented imaginary coherency cycle of the target and mapped
observations matches on 513 frequencies. Its peak magnitude is 0.140296. Every latent
cycle is real. The observed and latent Gaussian reversal rates are 2.588315 and 0
nats/sample, respectively. The horizontal coordinate is angular frequency in rad/sample
divided by \(\pi\).
(d) One point per independently generated VAR(1) network (30 per dimension, 83 frequencies
per network). The horizontal marks give group medians. Errors are maximum relative
Frobenius reconstruction errors. The exact population statement is Theorem 1.
""")


def network_strip(ax, table, field, ylabel, log=False):
    for i,(d,g) in enumerate(table.groupby("dimension")):
        ax.scatter(i+g.x_jitter,g[field],s=13,marker=["o","s","^"][i],
                   facecolor="white",edgecolor=TARGET,linewidth=.65)
        ax.hlines(g[field].median(),i-.23,i+.23,color=INK,lw=1.5,zorder=5)
    ax.set(xticks=[0,1,2],xticklabels=["3","6","12"],xlim=(-.45,2.45),
           xlabel="Observed dimension",ylabel=ylabel)
    if log:
        ax.set(yscale="log",ylim=(1e-16,1e-12))


def phase_scan(f):
    core = import_file(f.r1/"src/closure_core.py","closure_core")
    def row(rho, psi):
        c = np.eye(3,dtype=complex)
        for i,j in ((0,1),(1,2),(2,0)):
            c[i,j] = rho*np.exp(1j*psi/3)
            c[j,i] = c[i,j].conjugate()
        minimum = np.linalg.eigvalsh(c)[0]
        assert minimum>0
        cert = core.phase_reversal_certificate(c,rng=f.rng,starts=5)
        bound = float(core.triangle_lower_bound(c))
        assert bound <= cert["upper_bound"]+1e-12
        return dict(rho=rho,psi_rad=psi,min_eigenvalue=minimum,triangle_bound=bound,**cert)
    main = [row(.30,p) for p in np.linspace(0,np.pi,181)]
    weak = [row(r,r) for r in np.geomspace(.006,.22,32)]
    return main,weak


def fig1(root,out):
    import pandas as pd
    f = Build(root,out,"Fig1",12.0,WIDE_TOP,
              ["Where the temporal filter acts","Phase cancellation on a triangle",
               "Triangle bound on reversal"])
    p,q,r=f.panels
    ax=p.ax(.02,.04,.96,.79,diagram=True)
    colors=[A,GREEN,B]
    t=np.linspace(0,1,161)
    wave=np.array([np.sin(2*np.pi*(1.55+i*.36)*t+i*.65)
                   +.26*np.sin(2*np.pi*3.5*t-i*.4) for i in range(3)])
    f.npz("A",schematic_sample_index=np.arange(len(t)), schematic_time=t,
          schematic_waveforms=wave, model_b_example_delay_samples=np.array([0,1]))
    ax.axhline(.48,color=GRAY,lw=.6)
    ax.text(.01,.91,"Model A",color=A,weight="bold")
    ax.text(.01,.81,"Sensor-diagonal",color=A)
    ax.text(.01,.39,"Model B",color=B,weight="bold")
    ax.text(.01,.29,"Source-mix",color=B)
    ax.text(.955,.98,"Schematic",ha="right",size=7,color=LATENT)
    tag(ax,.27,.92,"Defined sensor channels")
    tag(ax,.55,.92,"Channel filters")
    tag(ax,.82,.92,"Observed channels")
    tag(ax,.27,.39,r"Correlated $2d$ latent components")
    tag(ax,.48,.39,"Source filters")
    tag(ax,.65,.39,"Spatial mix")
    ys=[.77,.66,.55]
    for i,(y,c) in enumerate(zip(ys,colors),1):
        block(ax,.27,y,.063,.081,rf"$x_{i}$",c)
        arrow(ax,(.303,y),(.514,y),c)
        block(ax,.55,y,.069,.081,rf"$h_{i}$",A)
        arrow(ax,(.585,y),(.735,y),c)
        ax.plot(.745+.117*t,y+.030*wave[i-1],color=c,lw=1.1)
        tag(ax,.90,y,rf"$y_{i}$",color=c)
    levels=[.283,.233,.183,.133,.083,.033]
    for j,y in enumerate(levels):
        i=j%3
        ax.scatter(.27,y,s=13,color=LATENT,zorder=5)
        tag(ax,.227,y,rf"${'u' if j<3 else 'v'}_{i+1}$",size=7)
        arrow(ax,(.279,y),(.446,y),LATENT if j<3 else B,lw=.8)
        ax.plot([.45,.513],[y,y],color=B,alpha=.22,lw=.6)
        arrow(ax,(.514,y),(.597,y),B,lw=.8)
        for yy in (.265,.165,.065):
            ax.plot([.598,.698],[y,yy],color=B,alpha=.24,lw=.6)
    block(ax,.48,.233,.065,.137,r"$1$",B,fill="#f9eee9")
    block(ax,.48,.083,.065,.137,r"$z^{-1}$",B,fill="#f9eee9")
    ax.add_patch(Rectangle((.597,.018),.102,.282,
                                                            fill=False,ec=B,lw=1))
    tag(ax,.65,.16,r"$M$",color=B,bbox=dict(fc="white",ec="none",pad=1))
    for i,(y,c) in enumerate(zip([.265,.165,.065],colors),1):
        arrow(ax,(.7,y),(.735,y),c)
        ax.plot(.745+.117*t,y+.028*wave[i-1],color=c,lw=1.1)
        tag(ax,.90,y,rf"$y_{i}$",color=c)
    arrow(ax,(.93,.048),(.985,.048),LATENT)
    tag(ax,.955,.11,r"$t$",size=7)

    ax=q.ax(.04,.02,.92,.83,diagram=True)
    xy=np.array([[.48,.88],[.77,.29],[.19,.29]])
    phase_labels=[r"$\phi_1-\phi_2$",r"$\phi_2-\phi_3$",r"$\phi_3-\phi_1$"]
    centers=[(.79,.64),(.49,.18),(.18,.64)]
    for i,point in enumerate(xy):
        next_point=xy[(i+1)%3]
        arrow(ax,point+.11*(next_point-point),next_point-.11*(next_point-point),A)
        ax.scatter(*point,s=153,facecolor="white",edgecolor=A,lw=1.2,zorder=5)
        tag(ax,*point,str(i+1),color=A,zorder=6)
        tag(ax,*centers[i],phase_labels[i],color=LATENT)
        ax.add_patch(Arc((centers[i][0],centers[i][1]-.039),.077,.061,
                         theta1=197,theta2=345,color=GRAY,lw=.85))
    tag(ax,.48,.46,r"$\arg(C_{12}C_{23}C_{31})$",color=TARGET)
    tag(ax,.49,.060,r"$\sum_{\mathrm{cycle}}(\phi_i-\phi_j)=0$",color=A)
    f.csv("B",dict(from_sensor=[1,2,3],to_sensor=[2,3,1],phase_offset=phase_labels,
                   x=xy[:,0],y=xy[:,1],role="oriented spectral product"))

    main,weak=map(pd.DataFrame,phase_scan(f))
    weak["bound_over_upper"]=weak.triangle_bound/weak.upper_bound
    f.csv("C",main)
    f.csv("C",weak,"_weak")
    ax=r.ax(.19,.19,.77,.63)
    x=main.psi_rad
    ax.fill_between(x,0,main.triangle_bound,color=GREEN,alpha=.14)
    ax.plot(x,main.triangle_bound,color=GREEN,label="Triangle bound")
    ax.plot(x,main.upper_bound,color=TARGET,label="Phase minimum")
    ax.fill_between(x,main.lower_bound,main.upper_bound,color=TARGET,alpha=.24)
    ax.legend(loc="upper right",frameon=False)
    ax.set(xlim=(0,np.pi),ylim=(0,None),xticks=[0,np.pi/2,np.pi],
           xticklabels=["0",r"$\pi/2$",r"$\pi$"],xlabel=r"Closure phase $\psi$ (rad)",
           ylabel="Reversal density (nats)")
    inset=r.ax(.675,.445,.235,.173)
    inset.semilogx(weak.rho,weak.bound_over_upper,color=GREEN,lw=1.15)
    inset.axhline(1,color=GRAY,ls="--",lw=.9)
    inset.set(ylim=(.44,1.04),xticks=[.01,.1],xticklabels=[".01",".1"],yticks=[.5,1])
    inset.tick_params(labelsize=6.5,length=2,pad=1)
    inset.set_xlabel(r"$\rho=\psi$",size=7,labelpad=0)
    inset.set_title(r"Bound / minimum",size=7,pad=2)
    gap=main.gap.max()
    assert gap < 1e-7, gap
    f.finish(r"""
**Figure 1. Sensor-diagonal filtering preserves closure phase.**
(a) In Model A, temporal filters \(h_i\) act separately on already defined sensor
channels. In Model B, source responses act before real spatial mixing \(M\).
The two response classes illustrate the one-sample construction developed in Fig. 2.
Waveforms are deterministic schematics.
(b) Diagonal phase shifts add \(\phi_i-\phi_j\) to edge phases. Their sum around
\(1\to2\to3\to1\) vanishes, preserving \(\arg(C_{12}C_{23}C_{31})\).
(c) The phase minimum and the triangle lower bound for a positive-definite
three-channel coherency family with equal edge magnitude \(\rho=0.30\), over 181
values of \(\psi\) from 0 to \(\pi\). The narrow numerical primal–dual interval
is retained in the data. The inset approaches unity along the joint
weak-coherence and small-closure path \(\psi=\rho\) (radians). Reversal densities
are pointwise Gaussian spectral contributions in nats.
""")
