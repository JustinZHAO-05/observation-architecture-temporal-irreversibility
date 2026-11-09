# Figure 3 · 观测等价的谱功率代价

正文 Section IV，178 × 112 mm。左侧 a 比较两套达到同一观测谱的最优潜在构造，右侧 b、c 分别展示解析标度和参数相图。

- [PowerPoint](Fig3.pptx) 中 a 的信号路径、相量、矩阵、条带和公式均为原生可编辑对象。b、c 为嵌入的 Python 矢量图。 [逐 panel 矢量图](panels/)
- [矢量 PDF](Fig3.pdf) · [可编辑 SVG](Fig3.svg) · [600 dpi PNG](Fig3.png) · [英文图注](caption.md) · [校验记录](validation.json)
- [a 的最优解](data/Fig3a_optima.npz) · [b 的解析曲线和渐近线](data/Fig3b_curves.csv) · [c 的解析网格](../../generated_data/Fig3/redraw/Fig3c_grid.npz)

## 科学口径

固定观测增益为 1。图中的无量纲量 \(t_{\min}\) 是固定频点、二维旋转块的最小潜在／观测谱迹比。a 的两个条件固定 \(b=0.8\)，相位为 0.80 和 0.05 rad。圆与菱形在三块 panel 中分别标出这两个条件。谱迹条带用同一对数尺度，从 0.5 起画。相量为单位传递因子 \(e^{-i\theta}\) 的几何表示。

在这两个相位下，取 \(P=V=(t_{\min}/2)I_2\)，\(Q=qI_2+jJ\)，\(q=(1-t_{\min})/(2\cos\theta)\)，\(j=b/(2\sin\theta)\)。NPZ 保存完整实潜在谱、两个复观测算子和重构谱。脚本检查谱半正定性、\(HGH^*=S\) 和谱迹比，两个例子的最大观测谱误差约为 \(1.6\times10^{-14}\)。

b 直接读取归档 \(b=0.2,0.5,0.8\) 曲线，并在相同相位网格上按定理 2 计算 \(b=0.9\)。黑虚线为 \(0.4/|\theta|^2\)。c 用 \(\theta\in[0.01,1.5]\) rad、\(b\in[0,0.99]\) 的 201 × 303 点确定性解析网格。连续参数与优化设定是科学单位，绘图全程确定性。归档中的 32 个全矩阵优化区间由 [Fig. S4](../FigS4/FigS4.pdf) 展示。

## 复现

从交接包根目录运行。Python 3.12 的固定版本依赖与 Fig. 1 共用。机制图导出使用 Windows PowerPoint。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/Fig3/reproduce'
$out = '03_FIGURE_PRODUCTION/redraw/Fig3_rebuilt'
$grid = '03_FIGURE_PRODUCTION/generated_data/Fig3/redraw_rebuilt'
py -3.12 -m pip install -r 03_FIGURE_PRODUCTION/redraw/Fig1/reproduce/requirements.txt
py -3.12 "$src/draw_data.py" --output $out --grid-output $grid
& "$src/build_mechanism.ps1" -Output $out
py -3.12 "$src/assemble.py" --output $out
~~~

科学输入为 Round 2 的 `results/latency_power_curves.csv`、`results/latency_cost_lp_intervals.csv` 和英文正文 Section IV 定理 2。视觉参考为 Seara 等关于标度的图形组织。图面几何与数据图均为本项目绘制。 [Seara et al., Fig. 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC7810704/#Fig3)
