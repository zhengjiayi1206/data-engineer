# Q2 - MySQL 8 SQL 与业务分析

先运行根目录 `python download_data.py`，启动 MySQL 8 并准备数据库；本机的安装和重启方式见根目录 `MYSQL_LOCAL.md`。设置连接，例如 PowerShell：

```powershell
$env:MYSQL_URL='mysql+pymysql://用户名:密码@127.0.0.1:3306/olist'
python q2_sql_analysis/setup_mysql.py
```

空数据库会导入九张表；九张表齐全时跳过导入并重新执行查询；只存在部分表时停止，避免覆盖。导入中途失败可能留下部分表，须检查后处理或使用新库。连接信息不要提交。查询结果输出到 `results/`，实际运行和对账详见 `validation_report.md`。

Q2.1 翻译缺失可保留葡语并标记待翻译（不丢信息但英文体验不一致）、统一显示 Unknown（简单但类别合并）、维护人工审核映射（可读但需维护）；应同时保留原文与翻译来源。
