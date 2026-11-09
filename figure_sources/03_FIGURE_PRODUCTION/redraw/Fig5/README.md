# Figure 5 · 有限带宽制造可重复的表观闭环

178 × 133 mm。按本轮 Fig. 5 的四 panel 顺序组织。稿件节号对齐为 **PENDING**。当前英文工作稿把频谱平均偏差机制放在 Section V，结构化反例详见扩展补充材料 §6.4。

- [可编辑 PowerPoint](Fig5.pptx) · [可编辑 SVG](Fig5.svg) · [矢量 PDF](Fig5.pdf) · [600 dpi PNG](Fig5.png) · [图注](caption.md) · [校验记录](validation.json)
- [a 的谱与两条路径](../../generated_data/Fig5/redraw/Fig5a_window_order.npz) · [b 的源峰、谱核与延迟相位](../../generated_data/Fig5/redraw/Fig5b_peaks_and_kernel.npz) · [c 的六个窗长](data/Fig5c_exact_windows.csv) · [d 的 500 条记录](data/Fig5d_records.csv) · [冻结检验汇总](data/Fig5d_frozen_test.json)

## 科学口径

**a–b** 使用归档结构化可逆模型。两个独立振荡源以实载荷混合到已定义通道，再施加逐通道纯延迟与独立传感器噪声。a 两条计算路径共用逐频点归一化的功率加权窗核 \(w_f(\nu)\)。由于三个通道的自谱相同，\(\langle C_e\rangle_w\) 严格等于先平均谱矩阵再归一化的结果。连续曲线用 16,384 点周期频率求积，逐个对照档案的精确协方差和。b 的两个源谱按第一源峰值缩放，窗核按自身峰值缩放。相位曲线使用各边在 10 Hz 的中心相位为零点。

**c** 直接沿用归档的 125 ms 条件与六个窗长。上图采用已归档的解析 \(T^{-2}\) 系数。下图的 \(T^{-4}\) 参考线过 32 s 的数值点。窗长从 16 增至 32 s 时，平方闭环量的比值为 15.4755。

**d** 直方图使用全部 500 条归档记录，点带按排序等距选取 42 条，CSV 记录选中标志。图中的菱形是冻结前 99 条记录的均值。原审计脚本以种子 732419 重放，逐记录最大误差为约 \(7.1\times10^{-20}\)，并重现 49,999 次单侧符号翻转的 \(p=0.00008\)。科学采样单位是一条独立的 60 s 模拟记录。

## 复现

从交接包根目录运行。机制图需要 Windows PowerPoint，定量图使用 Python 3.12。a 的路径、箭头与公式为原生 PowerPoint 对象。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/Fig5/reproduce'
$out = '03_FIGURE_PRODUCTION/redraw/Fig5_rebuilt'
$grid = '03_FIGURE_PRODUCTION/generated_data/Fig5/redraw_rebuilt'
py -3.12 -m pip install -r "$src/requirements.txt"
py -3.12 "$src/draw_data.py" --output $out --grid-output $grid --replay
& "$src/build_mechanism.ps1" -Output $out
py -3.12 "$src/assemble.py" --output $out
~~~

输入为 Round 1 的 math_review_independent.py 与归档的 math_review_v2_leakage_partial.json、math_review_exact_outputs.json 和 adversarial_M0_60s_scores.npy。绘图元素均按本项目计算和绘制。流程表达参考 Huang 等将数据结构嵌入分析步骤的做法。 [Huang et al., Fig. 2](https://www.nature.com/articles/s41467-024-51582-5)
