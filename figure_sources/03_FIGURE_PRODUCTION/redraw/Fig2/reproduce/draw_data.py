"""Verify the archived Gaussian lift and draw the quantitative panels of Figure 2."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Polygon, Rectangle
import numpy as np

BLUE = "#0072B2"
ORANGE = "#D55E00"
GRAY = "#555D69"
INK = "#181B20"
FAINT = "#CCD1D6"
GRID = "#D8DDE2"
CMAP = LinearSegmentedColormap.from_list("signed_covariance",[BLUE,"#FFFFFF",ORANGE],N=257)
SEED = 26110802
LAYOUT = {"a": (0,0,178,52), "b": (2,53.4,86,57),
          "c": (90,53.4,86,57), "d": (2,112.2,174,37.8)}

matplotlib.rcParams.update({
    "font.family":"Arial","font.size":8.6,"mathtext.fontset":"custom",
    "mathtext.rm":"Cambria","mathtext.it":"Cambria:italic",
    "svg.fonttype":"none","svg.hashsalt":"pre-fig2-gaussian-lift","pdf.fonttype":42,
})


def axes(letter,title):
    _,_,w,h=LAYOUT[letter]
    f=plt.figure(figsize=(w/25.4,h/25.4),facecolor="white")
    a=f.add_axes((0,0,1,1))
    a.set(xlim=(0,w),ylim=(h,0))
    a.axis("off")
    label(a,1.3,3.8,letter,size=12,weight="bold")
    label(a,7.3,3.8,title,size=10.4,weight="bold")
    return f,a


def label(a,x,y,text,*,ha="left",color=INK,size=8.6,weight="normal"):
    a.text(x,y,text,ha=ha,va="center",color=color,fontsize=size,fontweight=weight)


def matrix(a, mat, x, y, side, norm, *, signs=False):
    n=len(mat)
    cell=side/n
    a.add_patch(Rectangle((x,y),side,side,fc=CMAP(norm(0)),ec="none"))
    for i,j in np.argwhere(mat!=0):
        z=mat[i,j]
        a.add_patch(Rectangle((x+j*cell,y+i*cell),cell,cell,fc=CMAP(norm(z)),ec="none"))
        if signs:
            label(a,x+(j+.5)*cell,y+(i+.5)*cell,r"$+$" if z>0 else r"$-$",
                  ha="center",color="white" if abs(z)>.8*norm.vmax else INK)
    for k in range(1,n):
        v=k*cell
        a.plot([x,x+side],[y+v,y+v],color=GRID,lw=.5,zorder=4)
        a.plot([x+v,x+v],[y,y+side],color=GRID,lw=.5,zorder=4)
    a.add_patch(Rectangle((x,y),side,side,fill=False,ec=GRAY,lw=.55,zorder=5))


def indices(a,x,y,side,labels,*,row=True,col=True):
    cell=side/len(labels)
    for i,text in enumerate(labels):
        if row:
            label(a,x-1.05,y+(i+.5)*cell,text,ha="right",size=8.1)
        if col:
            label(a,x+(i+.5)*cell,y+side+1.6,text,ha="center",size=8.1)


def colorbar(a,x,y,length,ticks,*,vertical=False):
    n=120
    for i in range(n):
        pos=i*length/n
        if vertical:
            box=(x,y+pos,1.75,length/n+.035)
            val=1-(i+.5)/n
        else:
            box=(x+pos,y,length/n+.035,1.75)
            val=(i+.5)/n
        a.add_patch(Rectangle(box[:2],box[2],box[3],fc=CMAP(val),ec="none"))
    a.add_patch(Rectangle((x,y),1.75 if vertical else length,
                          length if vertical else 1.75,fill=False,ec=GRAY,lw=.55))
    for u,text in zip((0.,.5,1.),ticks):
        if vertical:
            yt=y+(1-u)*length
            a.plot([x+1.75,x+2.25],[yt,yt],color=GRAY,lw=.55)
            label(a,x+2.65,yt,text,size=8.15)
        else:
            xt=x+u*length
            a.plot([xt,xt],[y+1.75,y+2.35],color=GRAY,lw=.55)
            label(a,xt,y+3.85,text,ha="center",size=8.15)


def save(f,out,letter):
    f.savefig(out/f"panels/Fig2{letter}.svg",metadata={"Date":None})
    f.savefig(out/f"panels/Fig2{letter}.pdf",metadata={"CreationDate":None,"ModDate":None})
    plt.close(f)


def draw_b(x_lag,y_lag,out):
    f,a=axes("b","Lag-one asymmetry")
    limit=abs(y_lag-y_lag.T).max()
    norm=Normalize(-limit,limit)
    centers=(15.5,38.0,60.5)
    latent_channels=[rf"${v}_{i}$" for v in "uv" for i in (1,2,3)]
    observed_channels=[rf"$y_{i}$" for i in (1,2,3)]
    rows=(
        (x_lag,"Latent","x",BLUE,13.4,18.0,latent_channels,r"$\mathbf{0}_{6\times6}$"),
        (y_lag,"Observed","y",ORANGE,42.1,12.2,observed_channels,r"$\Delta\Gamma_y(1)$"),
    )
    for lag,name,key,color,y,side,channels,result in rows:
        label(a,6.5,y-5.9,name,color=color,weight="bold")
        headings=(rf"$\Gamma_{key}(1)$",rf"$\Gamma_{key}(1)^{{\mathsf{{T}}}}$",result)
        for center,mat,title in zip(centers,(lag,lag.T,lag-lag.T),headings,strict=True):
            label(a,center,y-2.25,title,ha="center")
            matrix(a,mat,center-side/2,y,side,norm,signs=key=="y")
        indices(a,centers[0]-side/2,y,side,channels)
        for x,symbol in zip((26.75,49.25),(r"$-$",r"$=$"),strict=True):
            label(a,x,y+side/2,symbol,ha="center",size=10)
    colorbar(a,74.1,19.1,25.5,[rf"$-{limit:.2f}$",r"$0$",rf"${limit:.2f}$"],vertical=True)
    label(a,75.0,16.25,r"$\mathrm{SD}^{2}$",ha="center",size=8.3)
    save(f,out,"b")


def lag_blocks(cov, samples=32, channels=3):
    """Lossless reduction from the complete block-Toeplitz covariance."""
    timed=cov.reshape(samples,channels,samples,channels)
    lags=np.arange(1-samples,samples)
    blocks=np.array([timed[max(ell,0),:,max(-ell,0),:] for ell in lags])
    times=np.arange(samples)
    full=blocks[times[:,None]-times[None,:]+samples-1].transpose(0,2,1,3)
    assert np.array_equal(full,timed)
    return lags,blocks


def draw_c(lags,target,mapped,out):
    f,a=axes("c","Exact covariance equality")
    assert np.all(target[abs(lags)>1]==0) and np.all(mapped[abs(lags)>1]==0)
    shared=Normalize(-1,1)
    side=19.0
    y=13.1
    cells=side/3
    for i,(x,ell) in enumerate(zip([5.6,26.0,46.4],[-1,0,1])):
        block=np.flatnonzero(lags==ell)[0]
        label(a,x+side/2,10.0,rf"$\ell={ell:+d}$" if ell else r"$\ell=0$",ha="center")
        for row,col in np.ndindex(3,3):
            x0=x+col*cells; y0=y+row*cells
            tl=(x0,y0); tr=(x0+cells,y0)
            bl=(x0,y0+cells); br=(x0+cells,y0+cells)
            for value,vertices in [(target[block,row,col],(tl,tr,bl)),
                                   (mapped[block,row,col],(tr,br,bl))]:
                a.add_patch(Polygon(vertices,fc=CMAP(shared(value)),ec="none"))
            a.plot([tr[0],bl[0]],[tr[1],bl[1]],color="#B6C1C9",lw=.50)
        for j in (1,2):
            offset=j*cells
            a.plot([x+offset,x+offset],[y,y+side],color=GRID,lw=.5)
            a.plot([x,x+side],[y+offset,y+offset],color=GRID,lw=.5)
        a.add_patch(Rectangle((x,y),side,side,fill=False,ec=GRAY,lw=.55))
        indices(a,x,y,side,[rf"$y_{j}$" for j in (1,2,3)],row=i==0)

    colorbar(a,68.4,25.7,15.4,[r"$-1$",r"$0$",r"$1$"])
    label(a,76.1,19.0,"Covariance",ha="center",size=8.1)
    label(a,76.1,22.35,r"$\mathrm{SD}^{2}$",ha="center",size=8.1)

    error=np.max(abs(mapped-target),axis=(1,2))
    label(a,5.6,38.7,r"Max. residual ($\mathrm{SD}^{2}$)",size=8.4)
    ax=f.add_axes((9.0/86,7.8/57,56.4/86,8.1/57))
    ax.plot(lags,error,color=GRAY,lw=1.02)
    ax.scatter([lags[0],lags[-1]],[error[0],error[-1]],s=8,color=GRAY,zorder=3)
    eps=np.finfo(float).eps
    ticks=(-31,-24,-16,-8,0,8,16,24,31)
    ax.set(xlim=(-32,32),ylim=(-eps,eps),xticks=ticks,
           xticklabels=[rf"${value}$" for value in ticks],yticks=[0],yticklabels=[r"$0$"])
    ax.set_xticks(lags,minor=True)
    ax.tick_params(axis="x",which="minor",length=1.0,width=.5)
    ax.set_xlabel(r"$\ell$ (samples)",labelpad=1)
    ax.tick_params(length=2.1,width=.55,pad=1.05,labelsize=8.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for k in ("left","bottom"):
        ax.spines[k].set_linewidth(.55)
    save(f,out,"c")


def draw_d(w,target,mapped,reversal,rate,out):
    f,a=axes("d","Observed cycle and reversal rates")
    freq=w/np.pi
    a.plot([95,95],[18.9,20.7],color="#A7AFB7",lw=.65,ls=(0,(3,2)))
    top=f.add_axes((21/174,18.9/37.8,148/174,11.1/37.8))
    bottom=f.add_axes((21/174,6.95/37.8,148/174,10.15/37.8),sharex=top)
    for ax in (top,bottom):
        ax.axvline(.5,color="#A7AFB7",lw=.65,ls=(0,(3,2)),zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for k in ("left","bottom"):
            ax.spines[k].set_linewidth(.55)
        ax.tick_params(length=2.1,width=.55,pad=1.2,labelsize=8.25)
    top.axhline(0,color=FAINT,lw=.55)
    line,=top.plot(freq,target,color=ORANGE,lw=1.45,label="Analytic target")
    every=np.arange(0,len(w),32)
    marks,=top.plot(freq[every],mapped[every],ls="none",marker="o",mfc="white",mec=GRAY,
                    mew=.75,ms=72/25.4,label="Mapped latent")
    top.set(ylim=(-.157,.019),yticks=[-.15,0],yticklabels=[r"$-0.15$",r"$0$"],
            ylabel=r"$\mathrm{Im}\,P$")
    top.yaxis.labelpad=1.3
    top.tick_params(axis="x",bottom=False,labelbottom=False)
    top.text(.045,.14,r"$P=C_{12}C_{23}C_{31}$",transform=top.transAxes,fontsize=8.4,color=GRAY)
    f.legend(handles=[line,marks],loc="upper right",bbox_to_anchor=(.972,.965),ncol=2,
             frameon=False,borderaxespad=0,handlelength=1.45,columnspacing=1.2,fontsize=8.3)

    bottom.fill_between(freq,0,reversal,facecolor="#F9E7D9",lw=0,zorder=.8)
    bottom.plot(freq,reversal,color=ORANGE,lw=1.35)
    bottom.plot(freq,np.zeros_like(freq),color=BLUE,lw=.95)
    bottom.set(xlim=(-.012,1.012),ylim=(-.9,9.65),xticks=[0,.25,.5,.75,1],
               xticklabels=[r"$0$",r"$0.25$",r"$0.5$",r"$0.75$",r"$1$"],
               yticks=[0,8],yticklabels=[r"$0$",r"$8$"],xlabel=r"$\omega/\pi$",
               ylabel=r"$e(\omega)$")
    bottom.xaxis.labelpad=1
    bottom.yaxis.labelpad=2.9
    bottom.text(.035,.49,r"Latent  $\mathrm{ℛ}_x=0$",transform=bottom.transAxes,
                color=BLUE,fontsize=8.6)
    bottom.text(.705,.65,rf"Observed  $\mathrm{{ℛ}}_y={rate:.6f}$",transform=bottom.transAxes,
                color=ORANGE,fontsize=8.6)
    save(f,out,"d")


def cycle(spec):
    power=spec.diagonal(axis1=-2,axis2=-1).real
    c=spec/np.sqrt(power[:,:,None]*power[:,None,:])
    return (c[:,0,1]*c[:,1,2]*c[:,2,0]).imag


def write_csv(path,fields,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(fields)
        writer.writerows(rows)


def build(root,out):
    (out/"panels").mkdir(parents=True,exist_ok=True)
    (out/"data").mkdir(exist_ok=True)
    r2=root/"01_RESEARCH/ROUND2/PRE_round2"
    source=r2/"results/exact_short_memory_equivalence.npz"
    summary=json.loads((r2/"results/theory_summary.json").read_text())["exact_example"]
    module=importlib.util.spec_from_file_location("r2_lift",r2/"src/theory_round2.py")
    theory=importlib.util.module_from_spec(module)
    module.loader.exec_module(theory)
    with np.load(source) as z:
        lags=z["latent_lags"]
        block=z["latent_covariance"]
        o=z["observation_matrix"]
        target=z["target_covariance"]
        archived=z["observed_covariance"]
        w=z["w"]
        reversal=z["reversal"]
    b=summary["b"]
    assert b==.9 and summary["observation_delay"]==1
    assert w.shape==(513,) and block.shape==(198,198) and o.shape==(96,198)
    assert target.shape==archived.shape==(96,96)
    expected=np.zeros_like(o)
    for t in range(32):
        expected[3*t:3*t+3,6*(t+1):6*(t+1)+3]=np.eye(3)
        expected[3*t:3*t+3,6*t+3:6*t+6]=np.eye(3)
    assert np.array_equal(expected,o)
    mapped=o@block@o.T
    assert np.array_equal(mapped,archived)
    assert np.array_equal(mapped,target)
    assert np.array_equal(lags,lags.transpose(0,2,1))
    x_lag=block[6:12,:6]
    y_lag=mapped[3:6,:3]
    assert np.array_equal(x_lag,lags[1]) and np.allclose(y_lag,b*theory.K3()/2)
    x_delta=x_lag-x_lag.T
    y_delta=y_lag-y_lag.T
    assert np.count_nonzero(x_delta)==0 and np.count_nonzero(y_delta)==6

    spectrum=np.array([theory.ma_spectrum(b,wi) for wi in w])
    g=lags[0]+2*np.cos(w)[:,None,None]*lags[1]+2*np.cos(2*w)[:,None,None]*lags[2]
    eye=np.broadcast_to(np.eye(3),(len(w),3,3))
    h=np.concatenate([eye,np.exp(-1j*w)[:,None,None]*eye],axis=-1)
    reconstruction=h@g@h.conj().transpose(0,2,1)
    spectrum_error=float(abs(reconstruction-spectrum).max())
    assert spectrum_error<5e-16 and np.linalg.eigvalsh(g).min()>0
    t_cycle,m_cycle=cycle(spectrum),cycle(reconstruction)
    assert abs(t_cycle.min()+summary["max_abs_imaginary_cycle"])<1e-14
    assert abs(t_cycle-m_cycle).max()<5e-16
    observed_rate=2*(1/np.sqrt(1-b*b)-1)
    assert np.isclose(observed_rate,np.trapezoid(reversal,w)/np.pi,rtol=1e-12)
    assert round(observed_rate,6)==2.588315

    series=np.linalg.cholesky(block)@np.random.default_rng(SEED).standard_normal(block.shape[0])
    series=series.reshape(33,6)
    wave=(o@series.ravel()).reshape(32,3)
    assert np.array_equal(wave,series[1:,:3]+series[:-1,3:])
    links=[(i+1,j+1,float(lags[0,i,j+3])) for i,j in np.ndindex(3,3) if lags[0,i,j+3]!=0]
    assert len(links)==6
    write_csv(out/"data/Fig2a_routes.csv",["t","u1","u2","u3","v1_t_minus_1","v2_t_minus_1","v3_t_minus_1","y1","y2","y3"],
              ((t+1,*series[t+1,:3],*series[t,3:],*wave[t]) for t in range(32)))
    write_csv(out/"data/Fig2a_source_links.csv",["u_index","v_index","zero_lag_covariance"],links)
    (out/"data/Fig2a_geometry_inputs.json").write_text(
        json.dumps(dict(seed=SEED,trace_samples=25,output=wave[:25].tolist(),links=links),indent=2)+"\n",
        encoding="utf-8")
    np.savez_compressed(out/"data/Fig2b_lag_one.npz",lag=1,latent=x_lag,observed=y_lag,
                       latent_antisymmetric=x_delta,observed_antisymmetric=y_delta)
    order=np.arange(96).reshape(32,3).T.ravel()
    tg=target[np.ix_(order,order)]
    mg=mapped[np.ix_(order,order)]
    diff=mg-tg
    np.savez_compressed(out/"data/Fig2c_full_covariances.npz",target=tg,constructed=mg,difference=diff,
                       archive_order=order,channel=np.repeat(np.arange(1,4),32),
                       sample=np.tile(np.arange(32),3),residual_display_epsilon=np.finfo(float).eps)
    write_csv(out/"data/Fig2d_cycle.csv",["omega_rad_sample","omega_over_pi","target_im_cycle","mapped_im_cycle","observed_reversal_density"],
              zip(w,w/np.pi,t_cycle,m_cycle,reversal))
    np.savez_compressed(out/"data/Fig2d_spectra.npz",omega=w,target=spectrum,constructed=reconstruction,latent=g,
                       observation_transfer=h,latent_rate=0.,observed_rate=observed_rate)
    (out/"data/Fig2_scientific_checks.json").write_text(json.dumps({
        "b":b,"draw_seed":SEED,"samples_per_channel":32,"frequencies":len(w),
        "max_covariance_difference":float(abs(diff).max()),"max_spectral_difference":spectrum_error,
        "max_cycle_difference":float(abs(t_cycle-m_cycle).max()),"peak_imaginary_cycle_magnitude":float(abs(t_cycle).max()),
        "latent_reversal_rate":0.,"observed_reversal_rate":observed_rate,
    },indent=2)+"\n",encoding="utf-8")
    draw_b(x_lag,y_lag,out)
    ell,lag_target=lag_blocks(target)
    _,lag_mapped=lag_blocks(mapped)
    lag_residual=np.max(abs(lag_mapped-lag_target),axis=(1,2))
    assert np.max(lag_residual)==np.max(abs(diff))==0
    np.savez_compressed(out/"data/Fig2c_lag_blocks.npz",lag_samples=ell,target=lag_target,
                       constructed=lag_mapped,max_abs_residual=lag_residual)
    draw_c(ell,lag_target,lag_mapped,out)
    draw_d(w,t_cycle,m_cycle,reversal,observed_rate,out)
    print(f"96 x 96 exact covariance equality; spectral error {spectrum_error:.3g}; observed reversal rate {observed_rate:.6f}")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,default=Path("03_FIGURE_PRODUCTION/redraw/Fig2"))
    args=p.parse_args()
    if args.root.is_absolute() or args.output.is_absolute():
        p.error("Use relative paths.")
    build(args.root,args.output)
