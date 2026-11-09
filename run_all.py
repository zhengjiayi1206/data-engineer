from pathlib import Path
import os, subprocess, sys
from download_data import download
ROOT=Path(__file__).resolve().parent

def main():
    failed=[]
    try: download()
    except Exception as e:
        print(f'数据下载失败，仍尝试其他模块: {e}',flush=True); failed.append('download')
    modules=['q1_data_quality/q1_code.py','q3_etl_pipeline/pipeline.py']
    if os.getenv('MYSQL_URL'): modules.append('q2_sql_analysis/setup_mysql.py')
    else:
        print('未配置 MYSQL_URL：跳过 MySQL 导入及 SQL，详见说明。',flush=True); failed.append('MYSQL_URL 未配置')
    if os.getenv('DASHSCOPE_API_KEY'): modules.append('q4_llm_extraction/extract_reviews.py')
    else:
        print('未配置 DASHSCOPE_API_KEY：保留已有评价结果，跳过百炼调用。',flush=True); failed.append('DASHSCOPE_API_KEY 未配置')
    for module in modules:
        print(f'执行 {module}',flush=True)
        if subprocess.run([sys.executable,str(ROOT/module)],cwd=ROOT).returncode: failed.append(module)
    print('MySQL 导入与 SQL 执行见 q2_sql_analysis/README.md；避免覆盖已有数据，需使用空数据库。',flush=True)
    if failed: print('失败模块：'+', '.join(failed)); return 1
    return 0
if __name__=='__main__': sys.exit(main())
