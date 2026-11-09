"""Supplementary geometry, exact serialization, basis changes, and power audits."""
import json

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from common import A,B,EC,GRAY,GREEN,INK,LATENT,TARGET,TWO,Build,arrow,import_file,tag,vector_matrix
from fig12 import network_strip
from fig34 import draw_lp,power_data,power_min


def sup1(root,out):
    f=Build(root,out,"FigS1",11.4,TWO,["Real gauge on a tree and a cycle",
        "Joint weak-coherence limit","Numerical phase-minimum brackets","Weighted phase allocation"])
    a,b,c,d=f.panels
    ax=a.ax(.03,.09,.94,.74,diagram=True)
    edges=[]
    for j,x0 in enumerate([.235,.748]):
        xy=np.array([[x0,.84],[x0+.16,.36],[x0-.16,.36]])
        for i in range(2+j):
            q,r=xy[i],xy[(i+1)%3]
            arrow(ax,q+.14*(r-q),r-.14*(r-q),A if i<2 else B,style="-",
                  lw=1.35)
            tag(ax,*((q+r)/2+[.0,.09 if i==1 else .05]),["0","0",r"$\psi$"][i],
                color=A if i<2 else B,size=7)
            edges.append(dict(graph=["tree","triangle"][j],from_sensor=i+1,
                              to_sensor=(i+1)%3+1,edge_phase=["0","0","psi"][i]))
        for i,pt in enumerate(xy,1):
            ax.scatter(*pt,s=105,facecolor="white",edgecolor=A,lw=1,zorder=5)
            tag(ax,*pt,str(i),zorder=6,size=7)
        tag(ax,x0,.17,["Tree","Triangle"][j],weight="semibold")
        tag(ax,x0,.04,[r"$2$ phases fixed",r"Residual $\psi$ mod $\pi$"][j],color=LATENT,size=7)
    f.csv("A",edges)

    p=f.r1/"reviews/math_review_v2_outputs.json"
    sharp=pd.DataFrame(json.loads(p.read_text())["sharpness"])
    assert len(sharp)==75
    sharp["family"]=sharp.amplitudes.map(lambda xs:" / ".join(map(str,xs)))
    diagonal=sharp[np.isclose(sharp.epsilon,sharp.psi)].copy()
    assert len(diagonal)==15
    f.csv("B",sharp)
    ax=b.ax(.17,.19,.79,.64)
    for i,(family,g) in enumerate(diagonal.groupby("family")):
        g=g.sort_values("epsilon")
        ax.semilogx(g.epsilon,g.L/g.Estar_numerical,color=[GREEN,A,B][i],
                    marker=["o","s","^"][i],label=family)
    ax.axhline(1,color=GRAY,ls="--",lw=.85)
    ax.set(xlabel=r"Joint path $\epsilon=\psi$",ylabel="Triangle bound / optimum",ylim=(.50,1.02))
    ax.legend(frameon=False,title="Relative edge magnitudes",loc="lower left",ncol=1)

    cert=f.archive_csv(1,"variational_certificates.csv")
    assert len(cert)==480 and cert.groupby("matrix_dimension").size().to_dict()=={2:50,3:300,8:100,24:30}
    assert (cert.upper_bound>=cert.lower_bound).all()
    f.csv("C",cert)
    ax=c.ax(.19,.19,.77,.64)
    # The archived brackets are often visually coincident at the scale of their values.
    # Plot their actual widths against the attained upper endpoints.
    for i,(dim,g) in enumerate(cert.groupby("matrix_dimension")):
        ax.scatter(g.upper_bound,g.gap,s=11,facecolor="none",edgecolors=[LATENT,A,B,GREEN][i],
                   marker=["o","s","^","D"][i],linewidths=.55,label=f"{dim}")
    ax.set(xscale="log",yscale="log",xlabel="Numerical upper endpoint (nats)",
           ylabel="Upper − lower (nats)")
    ax.legend(title=r"$d$",ncol=2,loc="upper left",frameon=False)

    slope=sharp[sharp.epsilon==.003].copy()
    slope["slope_div_eps2"]=slope.Estar_numerical/(slope.psi*slope.epsilon)**2
    slope["theory_div_eps2"]=slope.leading/(slope.psi*slope.epsilon)**2
    f.csv("D",slope)
    ax=d.ax(.17,.19,.79,.64)
    for i,(family,g) in enumerate(slope.groupby("family")):
        g=g.sort_values("psi")
        color=[GREEN,A,B][i]
        ax.axhline(g.theory_div_eps2.iloc[0],ls="--",lw=.9,color=color)
        ax.loglog(g.psi,g.slope_div_eps2,ls="none",marker=["o","s","^"][i],
                  mfc="white",mec=color,label=family)
    ax.set(xlabel=r"Closure phase $\psi$ (rad)",ylabel=r"$\mathcal{E}_*/(\epsilon\psi)^2$")
    ax.legend(frameon=False,loc="lower right",bbox_to_anchor=(1,.16),title="Relative edge magnitudes")
    f.finish(r"""
**Figure S1. Real gauges and numerical sharpness.**
(a) Two channel phases make the edges of a three-node tree real. Closing the
triangle leaves the cycle phase modulo \(\pi\). (b) Archived three-channel
sharpness calculations along \(\epsilon=\psi\) for three fixed relative edge
magnitudes. The full \(5\times5\) scans are included in the data. (c) Numerical
primal–dual interval width versus upper endpoint for all 480 archived matrices.
Each point is one matrix. (d) The normalized phase minimum at \(\epsilon=0.003\)
compared with the small-phase coefficient \(2/\sum_i a_i^{-2}\) for edge
magnitudes \(r_i=\epsilon a_i\). The leading residual phase is apportioned in
proportion to \(a_i^{-2}\).
""")


def sup2(root,out):
    f=Build(root,out,"FigS2",11.8,[(0,.57,1,.43),(0,0,.335,.52),(.35,0,.345,.52),(.71,0,.29,.52)],
            ["One white-noise stream, three disjoint blocks","Finite-block equality",
             "Distinct population cycles","Equality regimes"])
    a,b,c,d=f.panels
    path=f.r1/"reviews"
    spec=json.loads((path/"math_review_v2_outputs.json").read_text())["serialization"]
    with np.load(path/"serialization_covariance_example.npz") as z:
        delay=z["delays"]
        target,serial=z["target_covariance"],z["serialized_covariance"]
        coeff,filters=z["target_coefficients"],z["serialized_filters"]
    n,l=spec["record_length"],spec["target_MA_order"]
    noise=spec["independent_output_noise_variance"]
    assert (n,l)==(16,4) and target.shape==serial.shape==(48,48)
    starts,ends=-delay-l,n-1-delay
    assert np.all(ends[1:]<starts[:-1])
    f.csv("A",dict(innovation=np.arange(1,4),delay_samples=delay,first_index=starts,
                   last_index=ends,past_padding_samples=l,record_length=n))
    ax=a.ax(.08,.20,.87,.50)
    for i,(left,right,col) in enumerate(zip(starts,ends,[TARGET,A,LATENT])):
        ax.add_patch(Rectangle((left-.5,.36),l,.27,fc=col,alpha=.28,ec="none"))
        ax.add_patch(Rectangle((left-.5+l,.36),n,.27,fc=col,alpha=.78,ec="none"))
        tag(ax,(left+right)/2,.79,rf"Stream {i+1} · shift {delay[i]}",color=col)
    for left,right,y,label in [(starts[0]-.5,starts[0]-.5+l,.22,r"$L=4$"),
                               (starts[0]-.5+l,ends[0]+.5,.22,r"$N=16$")]:
        ax.plot([left,left,right,right],[y+.05,y,y,y+.05],lw=.7,color=LATENT)
        tag(ax,(left+right)/2,y-.10,label,size=7)
    ax.set(xlim=(-50,19),ylim=(0,1),yticks=[],xlabel="Index of shared white-noise innovation (samples)")
    ax.spines["left"].set_visible(False)

    residual=serial-target
    assert np.max(abs(residual))<1e-15
    f.npz("B",target_covariance=target,serialized_covariance=serial,residual=residual)
    lim=max(abs(target).max(),abs(serial).max())
    for i,(matrix,title) in enumerate([(target,"Target"),(serial,"Serialized")]):
        ax=b.ax(.045+.495*i,.33,.445,.44)
        im=vector_matrix(ax,matrix,lim)
        ax.set_title(title,pad=3)
    cb=b.ax(.17,.21,.66,.033)
    f.figure.colorbar(im,cax=cb,orientation="horizontal",ticks=[-lim,0,lim],
                      format="%.1f").solids.set_label("colorbar-solids")
    note=b.ax(.02,.04,.96,.07,diagram=True)
    tag(note,.50,.60,r"$\max|\Delta|=4.44\times10^{-16}$",size=7,color=LATENT)

    w=2*np.pi*np.linspace(.001,.499,501)
    h=np.einsum("iak,fk->fia",coeff,np.exp(-1j*w[:,None]*np.arange(l+1)))
    g=np.exp(-1j*w[:,None]*np.arange(filters.shape[1]))@filters.T
    st=h@h.conj().transpose(0,2,1)+noise*np.eye(3)
    ss=g[:,:,None]*g[:,None,:].conj()+noise*np.eye(3)
    core=import_file(f.r1/"src/closure_core.py","closure_core_s2")
    ct=core.cycle_product(core.coherency(st))[:,0].imag
    cs=core.cycle_product(core.coherency(ss))[:,0].imag
    assert np.isclose(np.max(abs(ct)),spec["target_max_population_abs_imag_cycle"])
    assert np.max(abs(cs))<5e-16
    f.csv("C",dict(omega_rad_sample=w,target_im_cycle=ct,serialized_im_cycle=cs))
    ax=c.ax(.23,.19,.73,.62)
    ax.plot(w/np.pi,ct,color=TARGET,label="Target")
    ax.plot(w/np.pi,cs,color=B,ls="--",label="Serialized")
    ax.set(xlabel=r"$\omega/\pi$",ylabel=r"$\mathrm{Im}\,P$",xlim=(0,1))
    ax.legend(loc="upper left",frameon=False)

    ax=d.ax(.08,.16,.88,.66,diagram=True)
    for y,label,col,x1,x2,caption in [
            (.73,"Model A · long filters",A,.27,.74,"Fixed record"),
            (.28,"Model B · one delay",B,.05,.95,"Entire process")]:
        tag(ax,.50,y+.17,label,color=col,weight="semibold",size=7.5)
        ax.plot([.05,.95],[y,y],color=GRAY,lw=.85,ls=":" if col==A else "-")
        ax.plot([x1,x2],[y,y],color=col,lw=2.5)
        for x in [x1,x2]:
            ax.plot([x,x],[y-.06,y+.06],color=col,lw=1.1)
        tag(ax,.50,y-.15,caption,color=col,size=7)
    f.csv("D",[dict(model="A",scope="finite block",record_length=n,filter_memory=spec["serialized_filter_memory"]),
               dict(model="B",scope="entire stationary process",differential_delay_samples=1)])
    f.finish(r"""
**Figure S2. A finite-record serialization and a population lift have different scopes.**
(a) For the archived \(N=16\), order-4 MA example, shifts of 0, 21 and 42
samples allocate disjoint innovation indices to the three target streams.
Pale segments are the four pre-record innovations used in each block.
(b) The target and serialized covariance matrices are \(48\times48\) in
time-major order. Their maximum absolute difference is \(4.44\times10^{-16}\).
(c) The population cycles are computed from the archived MA coefficients and
serialized filters with independent observation noise of variance 0.2. The
target cycle reaches magnitude 0.07050, and the serialized population cycle
is real. (d) The illustrated Model A serialization uses memory 46 for this
fixed record. The Model B construction of Theorem 1 matches the entire
process using a differential delay of one sample.
""")


def sup3(root,out):
    f=Build(root,out,"FigS3",11.5,TWO,["Spectral reconstruction error","Positive latent spectrum",
        "Raw reversal under basis change","Triangle bound under basis change"])
    a,b,c,d=f.panels
    net=f.archive_csv(2,"general_lift_validation.csv")
    coord=f.archive_csv(2,"coordinate_validation.csv")
    assert len(net)==90 and net.groupby("dimension").size().eq(30).all() and len(coord)==600
    net["x_jitter"]=f.rng.uniform(-.17,.17,len(net))
    f.csv("A",net)
    f.csv("B",net)
    network_strip(a.ax(.21,.19,.75,.63),net,"max_relative_error","Maximum relative error",log=True)
    network_strip(b.ax(.21,.19,.75,.63),net,"min_latent_eigenvalue","Minimum latent eigenvalue")
    assert np.allclose(coord.raw_E_before,coord.raw_E_after,rtol=0,atol=1e-10)
    coord["raw_change"]=coord.raw_E_after-coord.raw_E_before
    f.csv("C",coord)
    f.csv("D",coord)
    ax=c.ax(.19,.19,.77,.64)
    ax.scatter(coord.raw_E_before,coord.raw_change*1e14,s=9,color=TARGET,alpha=.45,lw=0)
    ax.axhline(0,color=GRAY,ls="--",lw=.85)
    ax.set(xlabel="Raw reversal density (nats)",ylabel=r"After $-$ before ($10^{-14}$ nats)")
    ax=d.ax(.18,.19,.78,.64)
    ax.scatter(coord.raw_E_after,coord.triangle_bound_before,s=9,marker="o",
               facecolor="none",edgecolor=GRAY,alpha=.62,lw=.55,label="Before")
    ax.scatter(coord.raw_E_after,coord.triangle_bound_after,s=9,marker="^",
               color=GREEN,alpha=.58,lw=0,label="After")
    ax.set(xlabel="Raw reversal density (nats)",ylabel="Triangle bound (nats)")
    ax.legend(frameon=False,loc="upper left")
    f.finish(r"""
**Figure S3. Numerical lifting and the role of the coordinate basis.**
(a) Thirty independent VAR(1) networks at each of three dimensions,
evaluated at 83 frequencies each. Points give the per-network maximum
relative reconstruction error. (b) Minimum latent spectral eigenvalue per network.
Horizontal marks give medians. (c) Six hundred archived orthogonal
transformations preserve raw Gaussian reversal density to floating-point
accuracy. (d) The triangle bound can change under the same rotation. Each comparison uses the
same spectral matrix and its rotated representation.
""")


def sup4(root,out):
    f=Build(root,out,"FigS4",12.0,TWO,["PSD feasibility at fixed target","Independent LP brackets",
        "Numerical feasibility diagnostics","Small-angle coefficient"])
    a,b,c,d=f.panels
    curves,lp=power_data(f)
    strength,theta=.5,.8
    j=strength/(2*np.sin(theta))
    t=np.linspace(0,2.75,361)
    q=(1-t)/(2*np.cos(theta))
    limit=np.sqrt(np.maximum(0,t*t/4-j*j))
    mask=t>=2*abs(j)
    opt=power_min(strength,theta)
    f.csv("A",dict(trace_ratio=t,q_constraint=q,psd_abs_q_max=limit,
                   psd_slice_exists=mask,b=strength,theta_rad=theta))
    ax=a.ax(.17,.19,.79,.63)
    ax.fill_between(t,-limit,limit,where=mask,color=GREEN,alpha=.16,label="PSD-feasible")
    ax.plot(t[mask],limit[mask],color=GREEN,lw=.9)
    ax.plot(t[mask],-limit[mask],color=GREEN,lw=.9)
    ax.plot(t,q,color=B,label=r"$t+2q\cos\theta=1$")
    ax.scatter([opt],[(1-opt)/(2*np.cos(theta))],s=32,facecolor="white",edgecolor=INK,zorder=6)
    ax.set(xlim=(0,2.75),ylim=(-1.46,1.46),xlabel=r"Trace ratio $t=p+v$",ylabel=r"Real coupling $q$")
    ax.legend(frameon=False,loc="upper left")

    f.csv("B",lp)
    ax=b.ax(.18,.19,.78,.63)
    draw_lp(ax,lp,relative=True)
    ax.legend(title=r"$b$",ncol=2,frameon=False,loc="upper left")
    old=f.archive_csv(2,"latency_power_optimization.csv")
    assert len(old)==32
    f.csv("C",lp)
    f.csv("C",old,"_archived_slsqp")
    ax=c.ax(.20,.19,.76,.63)
    ax.scatter(lp.constraint_error.clip(lower=1e-18),lp.min_upper_eigenvalue,s=20,
               marker="o",facecolor="white",edgecolor=GREEN,label="LP feasible endpoint")
    for success,g in old.groupby("success"):
        ax.scatter(g.max_constraint_error.clip(lower=1e-18),g.minimum_eigenvalue,s=15,
                   marker="^" if success else "x",color=LATENT if success else B,
                   label="SLSQP success" if success else "SLSQP failed")
    ax.axhline(0,color=GRAY,lw=.7)
    ax.set(xscale="log",yscale="symlog",ylim=(-.08,.001),
           xlabel="Equality residual",ylabel="Smallest latent eigenvalue")
    ax.set_yscale("symlog",linthresh=1e-11)
    ax.set_yticks([-1e-3,-1e-6,-1e-9,0,1e-9,1e-6])
    ax.legend(frameon=False,loc="lower left",fontsize=6.5)
    curves["theta2_trace"]=curves.theta**2*curves.minimum_power_ratio
    early=curves[curves.theta<=.30]
    f.csv("D",early)
    ax=d.ax(.17,.19,.79,.63)
    for i,(strength,g) in enumerate(early.groupby("b")):
        col=[LATENT,A,B,INK][i]
        ax.semilogx(g.theta,g.theta2_trace,color=col,label=f"{strength:g}")
        ax.axhline(g.small_delay_coefficient.iloc[0],color=col,ls=":",lw=.8)
    ax.set(xlabel=r"Phase delay $|\theta|$ (rad)",ylabel=r"$\theta^2 t_{\min}$")
    ax.legend(title=r"$b$",ncol=2,frameon=False,loc="center left")
    f.finish(r"""
**Figure S4. Feasibility and numerical diagnostics of the trace optimization.**
(a) Rotationally averaged PSD slice at \(b=0.5,\theta=0.8\) rad with \(p=v=t/2\).
The line fixes the real observed spectrum. The circle is its leftmost feasible
point. (b) All 32 LP intervals in parts per million relative to the analytic
minimum. (c) Equality residuals and smallest latent eigenvalues of the LP
upper endpoints and the archived initial SLSQP solutions. The signed
vertical scale resolves both feasible and indefinite solutions. Values
at exactly zero on the log horizontal axis use a display floor of \(10^{-18}\).
(d) The scaled trace tends to \(1-\sqrt{1-b^2}\) (dotted) at each archived \(b\).
""")
