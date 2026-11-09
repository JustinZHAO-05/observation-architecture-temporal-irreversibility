# Supplement · S1–S8 重绘

八幅图共 31 个面板。S1–S4 核对定理范围、构造和优化，S5–S7 核对有限窗偏差、置信保证和数据量，S8 展开真实 EEG 的参考敏感性。图宽 178 mm。S1 和 S2 另有原生 PowerPoint 机制图，全部图提供可编辑 SVG、矢量 PDF、600 dpi PNG、英文图注及逐面板数据。

| 图稿 | 面板顺序与数据口径 |
| --- | --- |
| [S1 · Phase geometry](FigS1/FigS1.pdf) | a 五节点生成树与两条闭边，b 实谱相位规范条件，c 75 点归档扫描中的 15 个联合极限点，d 三组边权的数值相位份额和渐近份额。 |
| [S2 · Finite-record equivalence](FigS2/FigS2.pdf) | a 共享白噪声的三个不相交区间，b 48×48 协方差，c 闭环虚部及两个总体谱矩阵的差异。 |
| [S3 · General construction audit](FigS3/FigS3.pdf) | a–c 同一批 90 个网络各自的重构误差、潜在谱最小特征值、观测反演密度峰值。d 600 个正交变换的原始和相位松弛反演密度差。 |
| [S4 · Spectral-power optimization](FigS4/FigS4.pdf) | a 32 个 LP 区间对照解析最小值，b 区间相对宽度，c 等式残差与 PSD 审计，d 扩展参数网格的解析谱迹比。 |
| [S5 · Finite-window mechanism](FigS5/FigS5.pdf) | a 四种窗长的精确频谱平滑，b 三个延迟的偏差曲线，c 六种窗长的归一化系数，d 随机与结构化可逆零假设下的名义检验结果。 |
| [S6 · Confidence validity](FigS6/FigS6.pdf) | a 代表性谱误差包络，b 300 个未知均值仿真，c 2,500 次 Hermitian 扰动，d 7,680 次分析的误差与理论半径之比。 |
| [S7 · Sample complexity](FigS7/FigS7.pdf) | a 最弱信号的 12 个单元格，b 两种较强信号按延迟分组的检出比例，c 384 次连续率分析，d 同一长轨迹的嵌套前缀，使用各前缀组中位数为零参考。 |
| [S8 · EEG sensitivity](FigS8/FigS8.pdf) | a 218 条记录的筛选与 QC，b 两参考完整窗交叉计数，c 71 名参与者的配对重参考效应，d 226 个记录–参考组合的 alpha 频带贡献。 |

每图目录的 panel_data.json 对应 generated_data/FigSN/redraw 下的数据文件。[逐 panel 来源、抽样单位与核对口径](SUPPLEMENT_SOURCE_MAPPING.csv)

## 复现

从交接包根目录运行。S1 和 S2 的机制图由 Windows PowerPoint 生成，SVG 和 PDF 保留矢量。可以单独生成任一补图，或一次生成全部八幅。

~~~powershell
$src = '03_FIGURE_PRODUCTION/redraw/supplement_reproduce'
$out = '03_FIGURE_PRODUCTION/supplement_rebuilt'
py -3.12 -m pip install -r "$src/requirements.txt"
py -3.12 "$src/build.py" --output $out
& "$src/build_mechanisms.ps1" -Output $out
py -3.12 "$src/assemble_mechanisms.py" --output $out
py -3.12 "$src/validate.py" --output $out
~~~

单独复现时，在 build.py 后指定图名，例如 FigS2。若图含机制面板，给 PowerPoint 命令加 -Figure 2，并在 assemble_mechanisms.py 后加 2。全套验收命令检查八幅图。

S3d 用归档种子 341903 重放正交矩阵，并逐例核对原始谱反演密度。相位松弛计算的初始点种子为 261112，CSV 保留每个最小值区间及两者差的区间。S6b–c 沿用原审计种子 863902，S6a 沿用代表性轨迹种子 713420。可视化微移使用 261109 加图号。

S5d 每个点对应一次组检验，保留各自的抽样规模。S6、S7 的不同记录长度共享长轨迹。S8b 的完整窗交集使用每个参考的接受窗计数与固定时间表，因此可重建全部窗均合格的交集。部分合格记录的逐窗掩码细节未进入图中。S8d 使用全频率分母，避免把 alpha 频带内部的均值直接当成对全频带分数的贡献。
