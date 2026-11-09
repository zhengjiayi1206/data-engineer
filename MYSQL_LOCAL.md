# 本机 MySQL 启动说明

本次在当前 Windows 用户目录的 `.local\mysql-project\mysql-8.4.13-winx64` 安装 MySQL Community Server 8.4.13，数据文件位于同级 `data`，仅监听本机 127.0.0.1:3306。它不是 Windows 服务，重启电脑后需手动启动。随机 root 密码存储在同级 `password.txt`，文件权限已限制到当前用户；不要将其加入仓库或聊天。

```powershell
$base = Join-Path $env:USERPROFILE '.local\mysql-project\mysql-8.4.13-winx64'
$data = Join-Path $env:USERPROFILE '.local\mysql-project\data'
Start-Process -FilePath "$base\bin\mysqld.exe" -ArgumentList @('--no-defaults', "--basedir=$base", "--datadir=$data", '--bind-address=127.0.0.1', '--port=3306') -WindowStyle Hidden
```

项目数据库名为 `olist`。SQL 脚本不会覆盖已有同名表，数据库连接配置见 `q2_sql_analysis/README.md`。此说明只适用于本机的便携安装；其他机器需自行准备 MySQL 8。
