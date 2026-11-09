# 将本目录上传到 GitHub

目标：https://github.com/JustinZHAO-05/observation-architecture-temporal-irreversibility

**步骤**：
1. 下载并解压 `PRE_GitHub_Public_Repository_Upload.zip`，确认本目录文件完整。
2. 在电脑上 `git clone https://github.com/JustinZHAO-05/observation-architecture-temporal-irreversibility.git`，把解压后的内容复制到克隆目录，保留现有 Git 历史和已有 README 的更新；不要上传 zip 本身作为唯一数据文件。
3. 使用 `git add . && git commit -m "Release reproducibility sources for PRE and arXiv" && git push origin main` 上传。
4. 进入 GitHub 仓库网页检查 `research/`、`results/`、`figure_sources/`、`paper/` 和 `provenance/` 是否均已出现；运行本目录 `python verify_release.py`。
5. 如需稳定版本引用，在 GitHub 创建 Release；可选将仓库关联 Zenodo 生成 DOI，并将真实 DOI 更新到论文及数据可用性声明。

EDF 原始文件有独立公开来源，未放入本目录；本目录不应包含个人密钥、API Token 或私人服务器登录信息。
