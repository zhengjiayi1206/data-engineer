"""向 MYSQL_URL 指定的空 MySQL 8 数据库导入 Olist 并执行分析。"""
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.types import String, Text, DateTime
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/olist'
FILES=['olist_customers_dataset','olist_geolocation_dataset','olist_order_items_dataset','olist_order_payments_dataset','olist_order_reviews_dataset','olist_orders_dataset','olist_products_dataset','olist_sellers_dataset','product_category_name_translation']

def main():
    url=os.environ.get('MYSQL_URL')
    if not url: raise RuntimeError('请设置 MYSQL_URL=mysql+pymysql://用户名:密码@主机:3306/数据库名；数据库需事先创建。')
    engine=create_engine(url)
    with engine.connect() as connection:
        version=connection.execute(text('SELECT VERSION()')).scalar_one()
        print('数据库版本:',version)
        if 'MariaDB' in version or int(version.split('.')[0]) < 8: raise RuntimeError('需要 MySQL 8.0 或更高版本')
    existing=set(inspect(engine).get_table_names())
    conflict=existing.intersection(FILES)
    if conflict and conflict != set(FILES): raise RuntimeError('目标库存在部分数据表，为避免覆盖请检查或使用空数据库: '+', '.join(sorted(conflict)))
    if conflict: print('发现完整的 Olist 表，跳过导入并重新执行查询。')
    for name in ([] if conflict else FILES):
        path=DATA/(name+'.csv')
        frame=pd.read_csv(path, low_memory=False)
        types={}
        for c in frame.columns:
            if c.endswith('_timestamp') or c.endswith('_date'):
                frame[c]=pd.to_datetime(frame[c],errors='coerce'); types[c]=DateTime()
            elif frame[c].dtype == 'object' or str(frame[c].dtype)=='str':
                types[c]=Text() if c in ('review_comment_title','review_comment_message') else String(255)
        frame.to_sql(name,engine,if_exists='fail',index=False,chunksize=1000,dtype=types)
        print(name, len(frame), flush=True)
    with engine.begin() as con:
        for table,col in ([] if conflict else [('olist_orders_dataset','order_id'),('olist_order_items_dataset','order_id'),('olist_order_reviews_dataset','order_id'),('olist_customers_dataset','customer_id'),('olist_sellers_dataset','seller_id')]):
            con.execute(text(f'CREATE INDEX idx_{table[:18]}_{col[:8]} ON {table} ({col})'))
    out=ROOT/'q2_sql_analysis'/'results'; out.mkdir(exist_ok=True)
    for filename in ['q2_1_translation_gap.sql','q2_2_monthly_metrics.sql','q2_3_top_sellers.sql']:
        sql=(ROOT/'q2_sql_analysis'/filename).read_text(encoding='utf-8-sig')
        with engine.connect() as con:
            result=pd.read_sql_query(text(sql),con)
        result.to_csv(out/(Path(filename).stem+'.csv'),index=False,encoding='utf-8-sig')
        print(filename,len(result),'行')
    engine.dispose()
if __name__=='__main__': main()

