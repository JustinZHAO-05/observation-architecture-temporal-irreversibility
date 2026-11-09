"""Draw Fig. 1a,b from the archived three-channel model and prepare Fig. 1c inputs."""
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
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.textpath import TextPath
import numpy as np

BLUE = "#0072B2"
ORANGE = "#D55E00"
GRAPHITE = "#555D69"
PURPLE = "#8E5385"
INK = "#181B20"
BORDER = "#D8DDE2"
FAINT = "#CCD1D6"
WAVE_COLORS = (ORANGE, GRAPHITE, PURPLE)
DIVERGE = LinearSegmentedColormap.from_list("signed", [BLUE, "#FFFFFF", ORANGE])
NEUTRAL = LinearSegmentedColormap.from_list("real", ["#FAFBFC", "#567083"])
W, H = 86, 52
MIN_FONT = 8.6
SEED = 26110801

matplotlib.rcParams.update({
    "font.family": "Arial",
    "mathtext.fontset": "custom", "mathtext.rm": "Cambria", "mathtext.it": "Cambria:italic",
    "font.size": MIN_FONT,
    "svg.fonttype": "none",
    "svg.hashsalt": "pre-fig1-architecture",
    "pdf.fonttype": 42,
    "pdf.compression": 9,
})


def axes():
    f = plt.figure(figsize=(W/25.4, H/25.4), facecolor="white")
    a = f.add_axes((0, 0, 1, 1))
    a.set(xlim=(0, W), ylim=(H, 0))
    a.axis("off")
    return f, a


def label(a, x, y, s, *, ha="left", color=INK, size=MIN_FONT,
          weight="normal", italic=False):
    a.text(x, y, s, va="center", ha=ha, color=color, fontsize=size,
           fontweight=weight, fontstyle="italic" if italic else "normal")


def header(a, letter, title):
    label(a, 1.3, 3.8, letter, size=12, weight="bold")
    label(a, 7.3, 3.8, title, size=10.4, weight="bold")


def arrow(a, start, end, color=GRAPHITE, width=.65, size=6):
    a.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=size,
                                linewidth=width, color=color, shrinkA=0, shrinkB=0))


def matrix(a, mat, x, y, d, scale, cmap, *, symbols=None, accents=False):
    cell = d/3
    for i, j in np.ndindex(3, 3):
        value = mat[i, j]
        a.add_patch(Rectangle((x+j*cell, y+i*cell), cell, cell,
                              facecolor=cmap(scale(value)), edgecolor=BORDER, lw=.5))
        if symbols is not None:
            sym = symbols(value)
            if sym:
                label(a, x+(j+.5)*cell, y+(i+.5)*cell, sym,
                      ha="center", color="white" if abs(value)>.8*scale.vmax else INK)
    a.add_patch(Rectangle((x,y),d,d, fill=False, ec=ORANGE if accents else GRAPHITE,
                          lw=.82 if accents else .60))


def colorbar(a, x, y, d, scale, cmap, ticks):
    n = 100
    for j in range(n):
        a.add_patch(Rectangle((x,y+d*j/n),1.85,d/n+.045,
                              fc=cmap(1-(j+.5)/n),ec="none"))
    a.add_patch(Rectangle((x,y),1.85,d,fill=False,ec=GRAPHITE,lw=.55))
    for val, text in ticks:
        yt = y+(1-scale(val))*d
        a.plot([x+1.85,x+2.45],[yt,yt],color=GRAPHITE,lw=.55)
        label(a,x+3.05,yt,text)


def save(f, path):
    f.savefig(path.with_suffix(".svg"), metadata={"Date": None})
    f.savefig(path.with_suffix(".pdf"), metadata={"CreationDate":None,"ModDate":None})
    plt.close(f)


def draw_temporal(y, plus, minus, diff, output):
    f, a = axes()
    header(a, "a", "Temporal structure")
    x = np.linspace(16.1, 73.8, len(y))
    scale = .79
    baselines = [11.5, 17.0, 22.5]
    a.plot([x[0],x[-1]],[baselines[0]]*2,lw=.5,color=FAINT)
    for i, baseline in enumerate(baselines):
        a.plot([x[0],x[0]],[baseline-2.43,baseline+2.43],lw=.55,color=GRAPHITE)
        a.plot(x,baseline-scale*y[:,i], color=WAVE_COLORS[i], lw=.66, marker="o",
               ms=72/25.4, markeredgewidth=0, zorder=4)
        label(a,77.1,baseline,rf"$y_{{{i+1}}}$")

    # One amplitude scale serves all three lanes. Align the actual math glyph
    # centers to the tick coordinates, independent of ascent and descent.
    tick_size = 7.7
    for tick in (2,-2):
        ty = baselines[0]-scale*tick
        value = "$"+str(tick)+"$"
        glyph = TextPath((0,0),value,size=tick_size).get_extents()
        mid = (glyph.ymin+glyph.ymax)*.5*25.4/72
        a.plot([x[0]-.8,x[0]],[ty,ty],lw=.55,color=GRAPHITE)
        a.text(x[0]-1.35,ty+mid,value,ha="right",va="baseline",fontsize=tick_size,color=INK)
    a.text(8.0,17.0,"Amplitude (SD)",ha="center",va="center",rotation=90,color=INK)

    time_axis_y = 25.8
    a.plot([x[0],x[-1]],[time_axis_y]*2,color=GRAPHITE,lw=.55)
    for i in (0,8,16,24):
        a.plot([x[i],x[i]],[time_axis_y,time_axis_y+.8],color=GRAPHITE,lw=.55)
        label(a,x[i],28.0,"$"+str(i)+"$",ha="center")
    label(a,(x[0]+x[-1])/2,30.2,r"$t$ (samples)",ha="center")

    limit = float(np.abs(diff).max())
    norm = Normalize(-limit,limit)
    yy, dd = 35.2, 13.1
    for x0, m, title in zip([7.5,31.2,54.9],[plus,minus,diff],[r"$\Gamma(+1)$",r"$\Gamma(-1)$",r"$\Delta\Gamma$"]):
        label(a,x0+dd/2,33.2,title,ha="center")
        highlight = title == r"$\Delta\Gamma$"
        signs = (lambda z: r"$+$" if z > 1e-12 else (r"$-$" if z < -1e-12 else "")) if highlight else None
        matrix(a,m,x0,yy,dd,norm,DIVERGE,symbols=signs,accents=highlight)
    for i in range(3):
        channel=rf"$y_{{{i+1}}}$"
        label(a,6.1,yy+(i+.5)*dd/3,channel,ha="right")
        label(a,7.5+(i+.5)*dd/3,50.1,channel,ha="center")
    label(a,25.9,41.8,r"$-$",ha="center",size=10)
    label(a,49.6,41.8,r"$=$",ha="center",size=10)
    label(a,75.3,32.6,r"$\mathrm{SD}^{2}$",ha="center")
    colorbar(a,74.4,yy,dd,norm,DIVERGE,[(-limit,r"$-0.52$"),(0.,r"$0$"),(limit,r"$0.52$")])
    save(f,output/"panels/Fig1a")


def draw_spectral(spectrum, output):
    f,a = axes()
    header(a,"b","Spectral structure")
    label(a,42.0,9.15,r"$\omega=\pi/2\ \mathrm{rad}/\mathrm{sample}$",ha="center")
    y,d=16.2,18.1
    re=Normalize(0,1)
    mag=float(np.max(abs(spectrum.imag)))
    im=Normalize(-mag,mag)
    label(a,16.7,13.3,r"$\mathrm{Re}\,S_y$",ha="center")
    label(a,57.7,13.3,r"$\mathrm{Im}\,S_y$",ha="center")
    matrix(a,spectrum.real,7.65,y,d,re,NEUTRAL,
           symbols=lambda z:r"$1$" if z>.5 else "")
    colorbar(a,28.6,y,d,re,NEUTRAL,[(0.,r"$0$"),(1.,r"$1$")])
    matrix(a,spectrum.imag,48.65,y,d,im,DIVERGE,
           symbols=lambda z:(r"$+$" if z>0 else r"$-$") if abs(z)>1e-12 else "")
    colorbar(a,69.6,y,d,im,DIVERGE,[(-mag,r"$-0.52$"),(0.,r"$0$"),(mag,r"$0.52$")])
    for i in range(3):
        channel=rf"$y_{{{i+1}}}$"
        for x in (7.65,48.65):
            label(a,x-1.35,y+(i+.5)*d/3,channel,ha="right")
            label(a,x+(i+.5)*d/3,36.0,channel,ha="center")
    label(a,39.7,25.2,r"$+\,i$",ha="center",size=9.4)

    x0,y0=44.5,45.1
    unit=9.0
    s11,s12,s21=spectrum[0,0],spectrum[0,1],spectrum[1,0]
    label(a,35.0,y0,r"Entries of $S_y$",ha="right")
    arrow(a,(x0-5,y0),(x0+18,y0),width=.55,size=5)
    arrow(a,(x0,y0+6.35),(x0,y0-6.35),width=.55,size=5)
    arrow(a,(x0,y0),(x0+unit*s11.real,y0),width=1.0)
    arrow(a,(x0,y0),(x0,y0-unit*s12.imag),ORANGE,width=1.05)
    arrow(a,(x0,y0),(x0,y0-unit*s21.imag),BLUE,width=1.05)
    label(a,40.7,y0-unit*s12.imag,r"$S_{12}$",ha="right",italic=True)
    label(a,40.7,y0-unit*s21.imag,r"$S_{21}$",ha="right",italic=True)
    label(a,x0+unit+1,y0-2.6,r"$S_{11}$",ha="center",italic=True)
    label(a,x0+19.5,y0,r"$\mathrm{Re}$")
    label(a,x0+1.5,y0-6.3,r"$\mathrm{Im}$")
    save(f,output/"panels/Fig1b")


def write_rows(path, header, rows):
    with path.open("w", newline="",encoding="utf-8") as stream:
        writer=csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def run(root, output):
    r2=root/"01_RESEARCH/ROUND2/PRE_round2"
    spec=importlib.util.spec_from_file_location("archived_theory_round2",r2/"src/theory_round2.py")
    theory=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(theory)
    archived_summary=json.loads((r2/"results/theory_summary.json").read_text())
    b=archived_summary["exact_example"]["b"]
    assert b==.9
    a0,a1=theory.ma_coeff(b)
    plus=a1@a0.T
    minus=plus.T
    diff=plus-minus
    g0=a0@a0.T+a1@a1.T
    omega=np.pi/2
    s=theory.ma_spectrum(b,omega)
    tol=2e-14
    assert np.max(abs(plus-b*theory.K3()/2))<tol
    assert np.max(abs(g0-np.eye(3)))<tol
    assert np.max(abs(s-(g0+np.exp(-1j*omega)*plus+np.exp(1j*omega)*minus)))<tol
    assert np.max(abs(s.imag+diff))<tol
    assert np.max(abs(s-s.conj().T))<tol
    assert np.min(np.linalg.eigvalsh(s))>0

    with np.load(r2/"results/exact_short_memory_equivalence.npz") as archive:
        target=archive["target_covariance"]
        latent_cov=archive["latent_covariance"]
        transform=archive["observation_matrix"]
        source_lags=archive["latent_lags"]
    assert target.shape==(96,96) and latent_cov.shape==(198,198) and transform.shape==(96,198)
    assert np.max(abs(plus-target[3:6,:3]))<tol
    assert np.max(abs(transform@latent_cov@transform.T-target))<tol
    innovations=np.random.default_rng(SEED).standard_normal((26,3))
    y=innovations[1:]@a0.T+innovations[:-1]@a1.T
    assert y.shape==(25,3)
    assert np.max(abs(y))<3.48  # Separate 5.5-mm lanes at the fixed display scale.
    n=18
    alpha=np.array([.12,.30,.46])
    # The incoming sample in each Model A lane is x(t)=y(t) from panel a.
    a_input=y[1:n+1]
    a_output=(1-alpha)*a_input+alpha*y[:n]
    latent=np.linalg.cholesky(latent_cov)@np.random.default_rng(SEED+1).standard_normal(198)
    latent=latent.reshape(-1,6)
    mapped=(transform@latent.ravel()).reshape(32,3)
    assert np.array_equal(mapped,latent[1:,:3]+latent[:-1,3:])
    uv=source_lags[0,:3,3:]
    edges=[[int(i+1),int(j+1),float(uv[i,j])] for i,j in np.argwhere(abs(uv)>1e-14)]
    assert len(edges)==6 and all(i!=j for i,j,_ in edges)
    mechanism=dict(b=b,samples=n,seed_panel_a=SEED,seed_model_b=SEED+1,
                   sensor_filter_delayed_weights=alpha.tolist(),
                   model_a_input=a_input.tolist(),model_a_output=a_output.tolist(),
                   model_b_output=mapped[:n].tolist(),model_b_uv_edges=edges)
    (output/"data").mkdir(parents=True,exist_ok=True)
    (output/"panels").mkdir(parents=True,exist_ok=True)
    write_rows(output/"data/Fig1a_trace.csv",["sample","y1","y2","y3"],
               ([i,*row] for i,row in enumerate(y)))
    write_rows(output/"data/Fig1a_lag_matrices.csv",["row","column","gamma_plus1","gamma_minus1","delta"],
               ([i+1,j+1,plus[i,j],minus[i,j],diff[i,j]] for i,j in np.ndindex(3,3)))
    write_rows(output/"data/Fig1b_spectrum.csv",["row","column","omega_rad_per_sample","real","imag"],
               ([i+1,j+1,omega,s.real[i,j],s.imag[i,j]] for i,j in np.ndindex(3,3)))
    write_rows(output/"data/Fig1c_routes.csv",
               ["t","x1","x2","x3","yA1","yA2","yA3","u1","u2","u3","v1_t_minus_1","v2_t_minus_1","v3_t_minus_1","yB1","yB2","yB3"],
               ([i+1,*a_input[i],*a_output[i],*latent[i+1,:3],*latent[i,3:],*mapped[i]]
                for i in range(n)))
    (output/"data/Fig1c_mechanism.json").write_text(json.dumps(mechanism,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(output/"data/Fig1_model.npz",b=b,omega=omega,K=theory.K3(),a0=a0,a1=a1,
                       innovations=innovations,seed=SEED,latent_seed=SEED+1,gamma0=g0,gamma_plus1=plus,
                       gamma_minus1=minus,gamma_difference=diff,spectrum=s,latent_lags=source_lags,
                       latent_sample=latent,observed_latent_sample=mapped,observation_matrix=transform)
    draw_temporal(y,plus,minus,diff,output)
    draw_spectral(s,output)
    print(f"b={b}; max |delta|={np.abs(diff).max():.12g}; spectrum min eigenvalue={np.linalg.eigvalsh(s)[0]:.3g}; trace samples={len(y)}")


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,default=Path("03_FIGURE_PRODUCTION/redraw/Fig1"))
    args=p.parse_args()
    if args.root.is_absolute() or args.output.is_absolute():
        p.error("Provide relative paths.")
    run(args.root,args.output)
