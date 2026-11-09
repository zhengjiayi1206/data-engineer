# 实际使用的工具

- Python 3.12、pandas、NumPy：质量探索、ETL 和业务对账；可换其他数据处理引擎，但需验证口径。
- PyArrow：生成 Parquet；可换兼容 Parquet 的实现。
- kagglehub：下载两个公开数据集；可手动下载到题目指定路径。
- MySQL Community Server 8.4.13：导入 Olist 并实际执行 SQL，题目强制要求。PyMySQL 和 SQLAlchemy 用于连接、导入和执行；可换官方驱动或 MySQL 客户端。
- 阿里云百炼 qwen3.8-flash：批量抽取葡语评价；通过 OpenAI 兼容 HTTP API 调用。可替换为支持相同 JSON 约束的模型，但需重新评测与核算费用。密钥从环境变量或本机指定文件读取，不写入仓库。
- PowerShell：安装、运行与检查；可换其他终端。
- Codex（OpenAI）：协助实现、测试和撰写；所写内容需由提交人复核、理解后使用。对话原文快照见 AI_LOG，正在进行的消息仍需追加。
