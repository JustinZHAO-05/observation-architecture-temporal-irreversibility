# Figure 6 · 有限记录的校准不可逆性推断

178 × 125 mm。按本轮 Fig. 6 的三 panel 顺序组织。稿件节号与编号对齐为 **PENDING**。当前英文工作稿把连续频率下界构造放在 Section V，把功效和连续频率实验放在 Section VI。

- [可编辑 PowerPoint](Fig6.pptx) · [可编辑 SVG](Fig6.svg) · [矢量 PDF](Fig6.pdf) · [600 dpi PNG](Fig6.png) · [图注](caption.md) · [校验记录](validation.json)
- [a 的完整频率数组与轨迹片段](../../generated_data/Fig6/redraw/Fig6a_representative_trajectory.npz) · [b 的逐次结果](data/Fig6b_replicates.csv) · [b 的单元格计数](data/Fig6b_cell_counts.csv) · [c 的逐次结果](data/Fig6c_replicates.csv) · [c 的分位数](data/Fig6c_quantiles.csv)

## 科学口径

**a** 用原连续频率模拟种子 713420 重放无延迟组的第一条长轨迹，完整分析 \(N=524{,}288\)、\(b=0.9\)。前 48 点只用于显示。估计谱使用 \(L=1\)，并以 0–5 样本滞后的最大绝对协方差元素展示截断。\(B=1.9\) 与 \(T_L=0\) 由模拟模型给定。统一半径 \(\epsilon_\infty=0.03351697\)，单元变化余量为 \(0.00079851\)。最后一格按实际 2,048 个区间填充常数下界，平均值为 0.00831742 nats/sample。NPZ 保存全部单元边界、中心频率、真谱、估计谱、误差包络、闭环及误差、单元下界和校准参数。重放的率、半径、单元变化余量、谱误差与总体积分均已和归档对照。

**b** 从 7,680 行原始逐次结果重新聚合 60 个单元格，并与原汇总逐格比对。图中展示 36 个备择单元格。五个模型族合计 1,920 条独立长轨迹，其中零假设下有 768 条。不同长度为同一长轨迹的前缀。零假设的 3,072 次分析得到零个正证书。各备择设置与零假设计数表见 [Fig. S7](../FigS7/FigS7.pdf) 和[补图数据索引](../FigS7/panel_data.json)。

**c** 128 条独立长轨迹产生 384 次分析，每个延迟与长度单元格有 64 次。画出每次取值与中位数及 10%–90% 经验分位。两组延迟分别用圆和方块。横向微移用种子 26110906，且同一轨迹的三个前缀共用微移。纵轴在距零 \(8\times10^{-5}\) nats/sample 内为线性，以上为对数。总体三角积分参考为 0.02976977 nats/sample。

## 复现

从交接包根目录运行。Python 3.12 用于定量绘图，Windows PowerPoint 用于 a 的原生标题、箭头和可编辑公式。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/Fig6/reproduce'
$out = '03_FIGURE_PRODUCTION/redraw/Fig6_rebuilt'
$grid = '03_FIGURE_PRODUCTION/generated_data/Fig6/redraw_rebuilt'
py -3.12 -m pip install -r "$src/requirements.txt"
py -3.12 "$src/draw_data.py" --output $out --grid-output $grid
& "$src/build_mechanism.ps1" -Output $out
py -3.12 "$src/assemble.py" --output $out
~~~

数据和算法来自 Round 2。版式参考真实数据贯穿分析流程、在估计图中并列总体参考和数值结果的表达。 [Seara et al., Fig. 1](https://www.nature.com/articles/s41467-020-20281-2) · [Huang et al., Fig. 2](https://www.nature.com/articles/s41467-024-51582-5)
