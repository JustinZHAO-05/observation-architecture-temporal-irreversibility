# Figure 2 · 一采样差分延迟的总体等价

**Section III · 178 × 150 mm**

- [PowerPoint 源](Fig2.pptx) 的机制 panel a 使用按图层分组的原生矢量对象和可编辑公式。b、c、d 以 Python 生成的矢量图嵌入。各 panel 的独立可编辑 SVG 和矢量 PDF 位于 [panels](panels/)。
- 整图提供 [矢量 PDF](Fig2.pdf)、[SVG](Fig2.svg)、[600 dpi PNG](Fig2.png)、[英文图注](caption.md) 和[验收记录](validation.json)。
- [逐 panel 数据](data/)保存 32 点示例及机制波形、两组一阶滞后矩阵、完整协方差与残差，以及 513 个频率点的目标和重构谱。机制波形使用固定种子 26110802。

## 科学口径

归档来源为 01_RESEARCH/ROUND2/PRE_round2/results/exact_short_memory_equivalence.npz、同目录的 theory_summary.json，以及 src/theory_round2.py。

Panel a 用蓝色上层和紫色下层区分源组 $u$ 和 $v$。三处延迟框表示同一个 $z^{-1}$ 响应作用于三个 $v$ 分量。时间轴标出参与求和的源采样时刻。左侧虚线标出延迟器输出所取的 $v_i(t-1)$，右侧虚线标出直通支路的 $u_i(t)$。两项在观测时刻 $t$ 相加。源节点之间的六条细线对应归档零滞后交叉协方差的六个非零项。

Panel b 在每行依次画出一阶滞后协方差、转置及其差值。六维潜在矩阵对称，差值为零。三维观测矩阵的差值有六个非零元素。六张矩阵共用以零为中心的色标。

Panel c 将 $96\times96$ 联合协方差无损表示为 63 个不同滞后的 $3\times3$ 区块。上方仅绘制三个非零滞后块。每格左上和右下三角分别表示目标与构造，使用同一协方差色标。下方给出全部 63 个滞后的最大绝对残差，覆盖完整矩阵的 9,216 个元素。完整矩阵和滞后表示分别保存在 [Fig2c_full_covariances.npz](data/Fig2c_full_covariances.npz) 与 [Fig2c_lag_blocks.npz](data/Fig2c_lag_blocks.npz)。

Panel d 上图的空心点来自 $H(\omega)G(\omega)H(\omega)^*$，橙线为目标谱解析式，闭环使用相干谱、无量纲。下图显示两个过程的频率反演密度。沿共同的 $\omega/\pi$ 轴积分，橙色阴影面积是观测反演率，蓝色零基线对应潜在反演率。90 个网络的维数核验位于 [Supplement Fig. S3](../FigS3/FigS3.pdf)。

## 复现

从交接包根目录运行。Python 3.12 环境沿用 Figure 1 的固定依赖，机制制作与导出需要 Windows PowerPoint。两幅图共用公式和矢量处理代码。以下命令生成独立重建目录。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/Fig2/reproduce'
$out = '03_FIGURE_PRODUCTION/redraw/Fig2_rebuilt'
py -3.12 -m pip install -r 03_FIGURE_PRODUCTION/redraw/Fig1/reproduce/requirements.txt
py -3.12 "$src/draw_data.py" --output $out
& "$src/build_mechanism.ps1" -Output $out
py -3.12 "$src/assemble.py" --output $out
~~~

视觉组织参考 [Seara et al. (2021), Fig. 2](https://doi.org/10.1038/s41467-020-20281-2)。图中所有几何、波形、热图与曲线由本项目生成。
