# Figure 7 · EEG 闭环结构对观测坐标的依赖

178 × 158 mm，英文标签。当前整合稿的 EEG 结果在 Section VI，重绘编号为 Fig. 7。稿件节号及图号对齐为 **PENDING**。

- [PDF](Fig7.pdf) · [600 dpi PNG](Fig7.png) · [可编辑 SVG](Fig7.svg) · [PowerPoint](Fig7.pptx)
- [英文图注](caption.md) · [稿件结果段](manuscript_insert.md) · [素材与许可证](ASSET_PROVENANCE.csv) · [校验记录](validation.json)

| Panel | 数据与科学任务 |
| --- | --- |
| a | [64 电极模板坐标](data/Fig7a_montage.csv)和 [Fz 真实片段及 64 通道均值](../../generated_data/Fig7/redraw/Fig7a_Fz_excerpt.npz)。以归档交集排序后的第一条记录 S011R01 为例，绘制 2–3 s，同一电压尺度。EDF 保存在 [inputs](inputs/S011R01.edf)，SHA256 与第一轮清单一致。 |
| b | [接受窗表](data/Fig7b_windows.csv)。两排来自同一 61 s EDF，分别使用 2–26 s 和 34–58 s 内的 12 个 2 s 窗。已用原始算法核验这条记录两种参考的窗数及闭环结果。 |
| c | [113 条同记录配对](data/Fig7c_pairs.csv)。两眼睛条件用形状区分，横纵同刻度并保留负值。5.16 和 2.63 为平均参考与原参考的组均值之比。 |
| d | [226 个记录—参考组合](data/Fig7d_factors.csv) · [分组均值](data/Fig7d_group_means.csv) · [几何坐标](data/Fig7d_geometry.csv) · [真实示例向量](../../generated_data/Fig7/redraw/Fig7d_example_vectors.npz) · [等值线网格](../../generated_data/Fig7/redraw/Fig7d_isoscore_grid.npz)。向量示意来自 S011R01 的平均参考，保留模长比和约 \(80.57^\circ\) 的夹角。每条连线是一条记录。 |
| e | [42 人的条件差值](data/Fig7e_participant_deltas.csv) · [组均值与置信区间](data/Fig7e_bootstrap.csv)。每人两点对应两种参考的闭眼减睁眼，区间复现了归档的参与者 bootstrap（种子 743109，20,000 次）。 |

## 复现

从交接包根目录运行。Windows PowerPoint 生成原生公式、窗口和几何示意。SVG 保留矢量数据与可编辑轮廓，PowerPoint 内的机制文字与公式可直接编辑。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/Fig7/reproduce'
$out = '03_FIGURE_PRODUCTION/redraw/Fig7_rebuilt'
$grid = '03_FIGURE_PRODUCTION/generated_data/Fig7/redraw_rebuilt'
py -3.12 -m pip install -r "$src/requirements.txt"
py -3.12 "$src/draw_data.py" --output $out --grid-output $grid
& "$src/build_mechanism.ps1" -Output $out
py -3.12 "$src/assemble.py" --output $out
~~~

可在完整交接目录给数据命令追加 **--verify-archive**，从两份第一轮闭环 NPZ 重算全部 226 组 \(Q\)、幅度和对齐。审阅包中的归档 CSV 足以复现全部点，唯一附带的 EDF 用于 a–b 的例图与 d 的向量示意。组统计继续采用第二轮归档的匹配设计。

外部资源的图内用途与署名见素材清单。版式参考把测量位置、时序与频谱量连在一起的构图。 [Brake et al., Fig. 1](https://www.nature.com/articles/s41467-024-45922-8/figures/1)
