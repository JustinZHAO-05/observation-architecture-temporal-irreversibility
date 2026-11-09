# Figure 4 · 逐通道滤波不变量与反演下界

178 × 116 mm。重绘按本轮 Fig. 4 的三 panel 顺序组织。稿件节号对齐为 **PENDING**。当前英文工作稿的相位松弛与三角界位于 Section II，弱相干首阶式位于扩展补充材料 §3.3。

- [PowerPoint](Fig4.pptx) 的三角形、相量、相位份额条带和数学标签为原生可编辑对象。 [可编辑 SVG](Fig4.svg) · [矢量 PDF](Fig4.pdf) · [600 dpi PNG](Fig4.png) · [图注](caption.md) · [校验记录](validation.json)
- [a 的频谱和滤波器](../../generated_data/Fig4/redraw/Fig4a_frequency_grid.npz) · [b 的 181 点扫描](data/Fig4b_phase_scan.csv) · [b 的 32 点渐近路径](data/Fig4b_weak_limit.csv) · [c 的理论网格](../../generated_data/Fig4/redraw/Fig4c_weak_edge_grid.npz) · [c 的最优相位分配](data/Fig4c_examples.json)

## 科学口径

**a** 的母谱单位对角、边模长 0.30。三条边的相位由 \(\sin\omega\) 和 \(\sin 2\omega\) 组合生成，具体系数在 NPZ 中。每个通道施加真实系数的因果两抽头 FIR 与整数采样延迟，按 \(DSD^*\) 变换后再归一化为相干谱。257 个频率点均验证正定性、滤波器非零、边模长不变，以及复数闭环乘积不变。相量对应 \(\omega=\pi/2\) rad/sample。箭头用于闭环乘积的遍历。

**b** 直接复用初版 Fig. 1C 的两份归档 CSV。主图以数值原始–对偶区间中点表示 \(\mathcal E_*\)，区间保存在 CSV。两端的理论精确零值按零绘制。绿线为解析三角下界 \(L(C)\)。Inset 横轴是共同边模长 \(\rho\)，沿 \(\psi=\rho\) rad 的路径变化。最小归档 \(\rho=0.006\) 下，比值的数值区间为 0.9647–0.9664。

**c** 固定 \(r_{12}=r_{23}=0.12\) 与 \(\psi=0.20\) rad。三幅三角形采用实际边模长，并以共同的 0–100% 尺度展示优化所得的弱边相位份额。三个点以固定种子 26110904 运行归档优化程序，并用独立的原始–对偶区间核验。解析曲线使用联合弱相干、小相位的二次近似。每个点的科学单位为参数设定，频率网格和理论网格均为确定性计算。

## 复现

从交接包根目录运行，使用 Python 3.12 与 Windows PowerPoint。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/Fig4/reproduce'
$out = '03_FIGURE_PRODUCTION/redraw/Fig4_rebuilt'
$grid = '03_FIGURE_PRODUCTION/generated_data/Fig4/redraw_rebuilt'
py -3.12 -m pip install -r "$src/requirements.txt"
py -3.12 "$src/draw_data.py" --output $out --grid-output $grid
& "$src/build_mechanism.ps1" -Output $out
py -3.12 "$src/assemble.py" --output $out
~~~

图面几何为原创绘制。三角结构和相邻处理阶段的组织参考 Santoro 等的研究图。 [Higher-order connectomics, Fig. 1](https://www.nature.com/articles/s41467-024-54472-y)
