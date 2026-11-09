# Figure 1 · 观测到的时间箭头与观测架构

正文 Section II 的 178 × 112 mm 图稿。

- [PowerPoint 源](Fig1.pptx) 的 panel c 由原生 PowerPoint 对象和可编辑公式组成。选择窗格按变量、协方差线、信号路由、观测变换、波形和标签分组。Panel a、b 作为 Python 生成的矢量图嵌入；其可单独编辑的 SVG 和矢量 PDF 位于 [panels](panels/)。
- 整图提供 [SVG](Fig1.svg)、[PDF](Fig1.pdf)、[600 dpi PNG](Fig1.png)、[英文图注](caption.md) 和[校验记录](validation.json)。
- [data](data/) 包含 a 的 25 个样本和三张总体滞后矩阵、b 的复谱矩阵，以及 c 的滤波前后轨迹、源延迟索引和零滞后协方差。合并 NPZ 保留 MA(1) 系数、归档观测矩阵及随机种子。

## 科学口径

Panel a 和 b 共用原研究三通道 $b=0.9$ 模型与 $\Gamma(\ell)=E[y_{t+\ell}y_t^T]$ 约定。三条轨迹来自同一次固定种子的高斯 MA(1) 模拟，纵轴统一使用总体标准差（SD），$t$ 为采样索引。滞后矩阵和实部、虚部谱矩阵的行列都依次对应 $y_1,y_2,y_3$。滞后协方差色条单位为 $\mathrm{SD}^2$。滞后矩阵是精确总体值，$\Delta\Gamma=bK$。在 $\omega=\pi/2$ rad/sample，$\operatorname{Im}S=-\Delta\Gamma$。色条按两位小数排版，CSV 保留完整精度。

Panel c 的 Model A 使用示例两抽头响应 $h_i(z)=(1-\alpha_i)+\alpha_i z^{-1}$，$\alpha=(0.12,0.30,0.46)$。输入截自 a 的轨迹，逐通道计算输出。Model B 使用原研究归档的六维潜在协方差与观察矩阵，另取固定种子的实现。与 Fig. 2 一致，蓝色上层表示直通源组 $u$，紫色下层表示延迟源组 $v$。$3\times6$ 混合矩阵 $M=[I_3\ I_3]$ 相加两条支路对应分量，按 $u_i(t)+v_i(t-1)$ 画出三条输出轨迹。两层之间的六条无向线对应归档零滞后交叉块的六个非零值。两组示例帮助阅读算子顺序。

## 复现

从交接包根目录运行。Windows PowerPoint 提供原生机制图的编辑与导出。下面命令建立独立的重建目录。Python 版本为 3.12，依赖版本见 [requirements.txt](reproduce/requirements.txt)。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/Fig1/reproduce'
$out = '03_FIGURE_PRODUCTION/redraw/Fig1_rebuilt'
py -3.12 -m pip install -r "$src/requirements.txt"
py -3.12 "$src/draw_data.py" --output $out
& "$src/build_mechanism.ps1" -Output $out -DeckName 'Fig1.pptx'
py -3.12 "$src/assemble.py" --output $out
~~~

科学输入来自 01_RESEARCH/ROUND2/PRE_round2 的 src/theory_round2.py、results/theory_summary.json 和 results/exact_short_memory_equivalence.npz。随机种子为 26110801（a 和 Model A）与 26110802（Model B）。

## 视觉来源

版式参考两幅论文图的视觉组织方式。所有图元均为本项目自绘，图稿中的曲线与矩阵来自上述科学输入。 [Higher-order connectomics, Fig. 1](https://doi.org/10.1038/s41467-024-54472-y) · [Seara et al., Fig. 1](https://doi.org/10.1038/s41467-020-20281-2)

白底、按内容分配面板、可编辑矢量和配色取向参照 Nature 图指南。纸面尺寸、字号和线宽采用本图的 PRE 目标版式。 [Nature Figure Guide](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/) · [APS Style Basics](https://journals.aps.org/authors/style-basics)
