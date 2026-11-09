# Q4 评价文本抽取

运行 `python q4_llm_extraction/extract_reviews.py --key-file 本地密钥文件`，或设置 `DASHSCOPE_API_KEY` 后运行总入口。默认调用北京百炼 `qwen3.8-flash`，非思考模式、批量抽取并校验原文证据；处理结果写入 `extracted_issues.json`。`llm_results.jsonl` 和 `llm_usage.json` 用于断点续跑和费用记录。短文本标记为信息不足，模型失败的记录保留待复核状态。

读取数据、成本控制、评估和已知限制分别见 `pipeline_design.md`、`cost_report.md` 和 `accuracy_evaluation.md`。密钥不可放入仓库。可用 `python q4_llm_extraction/evaluate.py` 对照独立编写的 30 条参考标签重新计算初步指标。
