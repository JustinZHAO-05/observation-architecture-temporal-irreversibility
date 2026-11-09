"""Verify and draw the exact-frequency, phase-minimum and weak-edge examples."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter
import numpy as np

sys.dont_write_bytecode = True
CORE = Path("01_RESEARCH/ROUND1/neural_time_arrow_study/src/closure_core.py")
ARCHIVE = Path("03_FIGURE_PRODUCTION/generated_data/Fig1")
DEFAULT_OUTPUT = Path("03_FIGURE_PRODUCTION/redraw/Fig4")
DEFAULT_GRID = Path("03_FIGURE_PRODUCTION/generated_data/Fig4/redraw")
LAYOUT = {"a-top": (18,2,142,28.8), "a-data": (18,31.4,142,21.3),
          "b": (2,55,103,59), "c-top": (108,55,68,28.7), "c-data": (108,83.7,68,30.3)}
INK, GRAY, ORANGE, TEAL = "#181B20", "#555D69", "#D55E00", "#009E73"
EDGE_COLORS = ("#0072B2", "#8E5385", "#555D69")
I,J = np.array([(0,1),(1,2),(2,0)]).T
FIXED_R, FIXED_PSI = .12, .20
SEED = 26110904

plt.rcParams.update({
    "font.family": "Arial", "font.size": 8.4, "axes.labelsize": 8.9,
    "mathtext.fontset": "custom", "mathtext.rm": "Cambria", "mathtext.it": "Cambria:italic",
    "svg.fonttype": "none", "svg.hashsalt": "pre-fig4-cycles", "pdf.fonttype": 42,
    "axes.linewidth": .62,
})


def load_core():
    spec=importlib.util.spec_from_file_location("closure_core",CORE)
    core=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    return core


def coherency_family(phases,magnitudes):
    phases=np.asarray(phases)
    c=np.broadcast_to(np.eye(3,dtype=complex),(*phases.shape[:-1],3,3)).copy()
    c[...,I,J]=magnitudes*np.exp(1j*phases)
    c[...,J,I]=c[...,I,J].conj()
    return c


def panel(key):
    _,_,w,h=LAYOUT[key]
    return plt.figure(figsize=(w/25.4,h/25.4),facecolor="white")


def save(fig,out,name):
    path=out/"panels"/name
    fig.savefig(path.with_suffix(".svg"),metadata={"Date":None})
    fig.savefig(path.with_suffix(".pdf"),metadata={"CreationDate":None,"ModDate":None})
    plt.close(fig)


def polish(ax,*,box=False):
    if not box:
        for side in ("top","right"):
            ax.spines[side].set_visible(False)
    ax.tick_params(length=2.4,width=.58,pad=1.65)
    ax.set_axisbelow(True)


def number_ticks(ax):
    ax.set_major_formatter(FuncFormatter(lambda x,_:f"{x:g}"))


def draw_a(core,out,grid_output):
    w=np.linspace(0,np.pi,257)
    coefficients=np.array([[.62,.12],[.43,-.19],[.30,.42]])
    phases=np.stack((np.sin(w),np.sin(2*w)),axis=-1)@coefficients.T
    a=np.array([.12,.28,.42])
    delays=np.array([0,1,0])
    gains=np.array([.90,1.25,.75])
    z=np.exp(-1j*w[:,None])
    h=gains*(1-a+a*z)*z**delays
    before=coherency_family(phases,.30)
    filtered=core.diagonal_congruence(before,h)
    after=core.coherency(filtered)
    angles=np.unwrap(np.angle(after[:,I,J]),axis=0)
    p_before=core.cycle_product(before)[:,0]
    p_after=core.cycle_product(after)[:,0]
    phase_before=np.angle(p_before)
    phase_after=np.angle(p_after)
    psi_error=float(np.max(abs(phase_before-phase_after)))
    cycle_error=float(np.max(abs(p_before-p_after)))
    assert np.allclose(abs(before[:,I,J]),abs(after[:,I,J]),atol=1e-15)
    assert np.min(np.linalg.eigvalsh(filtered))>0 and np.min(abs(h))>0
    assert np.max(abs(angles-phases))>1 and psi_error<1e-14 and cycle_error<1e-15
    assert np.allclose(np.exp(1j*(angles-phases)),np.exp(1j*np.angle(h[:,I]*h[:,J].conj())),atol=1e-13)
    m=len(w)//2
    assert w[m]==np.pi/2
    np.savez_compressed(grid_output/"Fig4a_frequency_grid.npz",omega_rad_sample=w,transfer=h,
                       coherency_before=before,spectrum_after=filtered,coherency_after=after,
                       edge_phase_before=phases,edge_phase_after=angles,
                       cycle_before=p_before,cycle_after=p_after,phase_coefficients=coefficients,
                       fir_second_tap=a,delay_samples=delays,gains=gains)

    fig=panel("a-data")
    left=fig.add_axes((.088,.362,.508,.416))
    right=fig.add_axes((.692,.362,.285,.416))
    for ax in (left,right):
        polish(ax)
        ax.set_xlim(0,1)
        ax.set_xticks([0,.5,1])
        number_ticks(ax.xaxis)
        ax.set_xlabel(r"$\omega/\pi$",labelpad=.7)
        ax.axvline(.5,color="#9BA8AF",linewidth=.57,ls=(0,(2,2)),zorder=1)
        ax.axhline(0,color="#D8DFE3",linewidth=.5,zorder=0)
    for k,color in enumerate(EDGE_COLORS):
        left.plot(w/np.pi,phases[:,k],color=color,lw=1.14)
        left.plot(w/np.pi,angles[:,k],color=color,lw=1.10,ls=(0,(4,2)))
    left.set_ylim(-3.55,3.55)
    left.set_yticks([-3,0,3])
    left.set_ylabel(r"$\arg C_{ij}$ (rad)",labelpad=2)
    handles=[Line2D([],[],color=c,lw=1.12,label=n)
             for c,n in zip(EDGE_COLORS,("12","23","31"),strict=True)]
    handles.extend([Line2D([],[],color=INK,lw=1.0,label="Before"),
                    Line2D([],[],color=INK,lw=1.0,ls=(0,(4,2)),label="After")])
    left.legend(handles=handles,ncol=5,loc="lower center",bbox_to_anchor=(.5,.98),
                frameon=False,fontsize=8.1,handlelength=1.55,handletextpad=.35,columnspacing=.9,
                borderaxespad=.1)
    right.plot(w/np.pi,phase_before,color=ORANGE,lw=1.4,label="Before")
    right.plot((w/np.pi)[::32],phase_after[::32],ls="none",marker="o",ms=3.2,
               mfc="white",mec=ORANGE,mew=.74,label="After")
    right.set_ylim(-.12,1.76)
    right.set_yticks([0,1])
    right.set_ylabel(r"$\psi$ (rad)",labelpad=2)
    right.legend(ncol=2,loc="lower center",bbox_to_anchor=(.5,.98),frameon=False,fontsize=8.1,
                 handlelength=1.4,handletextpad=.35,columnspacing=.85,borderaxespad=.1)
    save(fig,out,"Fig4a_data")
    geometry=dict(before_rad=phases[m].tolist(),after_rad=angles[m].tolist(),psi_rad=float(phase_before[m]))
    return geometry,psi_error,cycle_error


def draw_b(core,out):
    names=("C.csv","C_weak.csv")
    scan,weak=(np.genfromtxt(ARCHIVE/name,delimiter=",",names=True) for name in names)
    assert len(scan)==181 and len(weak)==32 and np.all(scan["rho"]==.3)
    assert np.array_equal(weak["rho"],weak["psi_rad"]) and np.all(weak["lower_bound"]>0)
    for table in (scan,weak):
        c=coherency_family(np.repeat(table["psi_rad"][:,None]/3,3,axis=1),table["rho"][:,None])
        assert np.all(table["min_eigenvalue"]>0)
        assert np.allclose(np.linalg.eigvalsh(c)[:,0],table["min_eigenvalue"],atol=2e-14)
        assert np.allclose(core.triangle_lower_bound(c),table["triangle_bound"],rtol=1e-11,atol=1e-15)
        assert np.all(table["triangle_bound"] <= table["upper_bound"]+1e-12)
        assert np.max(table["upper_bound"]-table["lower_bound"])<3e-12
    for source,target in zip(names,("Fig4b_phase_scan.csv","Fig4b_weak_limit.csv"),strict=True):
        shutil.copyfile(ARCHIVE/source,out/"data"/target)

    fig=panel("b")
    fig.text(.013,.968,"b",fontsize=12,fontweight="bold",va="top",color=INK)
    fig.text(.075,.964,"Quantitative reversal bound",fontsize=10.4,fontweight="bold",va="top",color=INK)
    ax=fig.add_axes((.145,.195,.809,.632))
    polish(ax)
    psi=scan["psi_rad"]
    minimum=.5*(scan["lower_bound"]+scan["upper_bound"])
    minimum[[0,-1]]=0
    ax.set(xlim=(-.035,np.pi+.035),ylim=(-.004,.169),
           xticks=[0,np.pi/2,np.pi],xticklabels=[r"$\psi=0$",r"$\pi/2$",r"$\psi=\pi$"],
           yticks=[0,.05,.10,.15])
    number_ticks(ax.yaxis)
    ax.set_xlabel("Closure phase (rad)",labelpad=1.2)
    ax.set_ylabel("Reversal density (nats)",labelpad=3.0)
    ax.grid(axis="y",color="#DCE3E6",lw=.5)
    ax.plot(psi,minimum,color=ORANGE,lw=1.45,label=r"$\mathcal{E}_*$")
    ax.plot(psi[::15],minimum[::15],marker="o",ls="none",mfc="white",mec=ORANGE,mew=.78,ms=3.45)
    ax.plot(psi,scan["triangle_bound"],color=TEAL,lw=1.35,ls=(0,(5,2)),label=r"$L(C)$")
    ax.legend(loc="upper left",frameon=False,fontsize=8.7,ncol=2,columnspacing=.95,
              handlelength=1.7,handletextpad=.4,borderaxespad=.24)

    inset=fig.add_axes((.641,.565,.303,.252),facecolor="white")
    polish(inset,box=True)
    inset.set_xscale("log")
    inset.set_xlim(.0057,.24)
    inset.set_ylim(.22,1.07)
    inset.xaxis.set_major_locator(FixedLocator([.006,.02,.1]))
    number_ticks(inset.xaxis)
    inset.tick_params(which="minor",bottom=False,labelbottom=False)
    inset.tick_params(labelsize=7.8,length=2,pad=1.05)
    inset.set_yticks([.3,.6,1])
    number_ticks(inset.yaxis)
    inset.set_xlabel(r"$\rho$  ($\psi=\rho$ rad)",fontsize=8.2,labelpad=.5)
    inset.set_ylabel(r"$L/\mathcal{E}_*$",fontsize=8.2,labelpad=1.15)
    inset.axhline(1,color=GRAY,ls=(0,(2,2)),lw=.65)
    low=weak["triangle_bound"]/weak["upper_bound"]
    high=weak["triangle_bound"]/weak["lower_bound"]
    inset.fill_between(weak["rho"],low,high,color="#CFECE2",lw=0)
    inset.plot(weak["rho"],.5*(low+high),color=TEAL,lw=1.25)
    save(fig,out,"Fig4b")
    return float(np.max(scan["gap"])),float(low[0]),float(high[0])


def draw_c(core,out,grid_output):
    r=np.unique(np.r_[np.linspace(.012,.12,181),[.024,.06,.12]])
    e=2*FIXED_PSI**2/(2/FIXED_R**2+1/r**2)
    np.savez_compressed(grid_output/"Fig4c_weak_edge_grid.npz",r31=r,r12=FIXED_R,r23=FIXED_R,
                        psi_rad=FIXED_PSI,quadratic_density=e)
    rng=np.random.default_rng(SEED)
    cases=[]
    for i,(weak,marker) in enumerate(zip((.12,.06,.024),("o","s","D"),strict=True),1):
        strengths=np.array([FIXED_R,FIXED_R,weak])
        c=coherency_family(np.repeat(FIXED_PSI/3,3),strengths)
        value,phases=core.minimize_reversal_density(c,rng=rng,starts=10)
        cert=core.phase_reversal_certificate(c,rng=rng,starts=10)
        assert cert["lower_bound"]-1e-12<=value<=cert["upper_bound"]+1e-12
        assert cert["gap"]<3e-12
        transformed=core.diagonal_congruence(c,np.exp(1j*np.r_[0.,phases]))
        angle=(np.angle(transformed[I,J])+np.pi/2)%np.pi-np.pi/2
        assert np.isclose(angle.sum(),FIXED_PSI,atol=1e-12)
        share=angle[-1]/FIXED_PSI
        assert 0<share<1
        cases.append(dict(id=i,r31=weak,marker=marker,phase_rad=angle.tolist(),
                          phase_share=float(share),density=float(value),
                          lower=float(cert["lower_bound"]),upper=float(cert["upper_bound"])))
    assert np.all(np.diff([c["phase_share"] for c in cases])>0)
    (out/"data/Fig4c_examples.json").write_text(json.dumps(cases,indent=2)+"\n",encoding="utf-8")

    fig=panel("c-data")
    ax=fig.add_axes((.164,.274,.788,.576))
    polish(ax)
    ax.plot(r,1e4*e,color=ORANGE,lw=1.35,label=r"Quadratic limit, $\psi=0.20$ rad")
    for case in cases:
        ax.plot(case["r31"],1e4*case["density"],marker=case["marker"],ls="none",ms=3.7,
                mfc="white",mec=INK,mew=.78)
    ax.set(xlim=(.008,.126),ylim=(-.1,5.45),xticks=[.02,.05,.08,.11],yticks=[0,2,4])
    number_ticks(ax.xaxis)
    ax.set_xlabel(r"Weak edge $r_{31}$",labelpad=1.25)
    ax.set_ylabel(r"$\mathcal{E}_*$ ($10^{-4}$ nats)",labelpad=2.0)
    ax.grid(axis="y",color="#DFE6E8",lw=.5)
    ax.legend(loc="upper left",frameon=False,fontsize=8.2,handlelength=1.5,
              handletextpad=.4,borderaxespad=.28)
    save(fig,out,"Fig4c_data")
    return cases


def build(out,grid_output):
    (out/"panels").mkdir(parents=True,exist_ok=True)
    (out/"data").mkdir(exist_ok=True)
    grid_output.mkdir(parents=True,exist_ok=True)
    core=load_core()
    geometry,psi_err,cycle_err=draw_a(core,out,grid_output)
    gap,ratio_low,ratio_high=draw_b(core,out)
    cases=draw_c(core,out,grid_output)
    inputs=dict(a=geometry,c=cases,reference_r=FIXED_R,psi_rad=FIXED_PSI)
    (out/"data/Fig4_geometry.json").write_text(json.dumps(inputs,indent=2)+"\n",encoding="utf-8")
    checks=dict(frequencies=257,phasor_frequency_rad_sample=float(np.pi/2),
                maximum_closure_phase_difference_rad=psi_err,maximum_cycle_product_difference=cycle_err,
                phase_scan_count=181,maximum_numeric_interval_width=gap,weak_limit_count=32,
                weak_path_first_ratio_bracket=[ratio_low,ratio_high],optimization_seed=SEED,
                weak_edge_example_phase_shares=[c["phase_share"] for c in cases])
    (out/"data/Fig4_checks.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(checks,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument("--grid-output",type=Path,default=DEFAULT_GRID)
    args=parser.parse_args()
    if args.output.anchor or args.grid_output.anchor:
        parser.error("Use paths relative to the handoff root.")
    build(args.output,args.grid_output)
