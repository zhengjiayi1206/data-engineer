from pathlib import Path
import logging, time
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
COLS = ['invoice_no','stock_code','description','quantity','unit_price','total_amount','invoice_datetime','customer_id','country']
logging.basicConfig(filename=HERE/'pipeline_log.txt', filemode='w', level=logging.INFO, encoding='utf-8', format='%(asctime)s %(levelname)s %(message)s')

def load_data(path=ROOT/'data/online_retail_ii.csv'):
    df = pd.read_csv(path, dtype={'Invoice':'string','StockCode':'string','Customer ID':'string'}, encoding='utf-8')
    df = df.rename(columns={'Invoice':'invoice_no','StockCode':'stock_code','Description':'description','Quantity':'quantity','Price':'unit_price','InvoiceDate':'invoice_datetime','Customer ID':'customer_id','Country':'country'})
    df['customer_id'] = df.customer_id.str.replace(r'\.0$', '', regex=True)
    df['invoice_datetime'] = pd.to_datetime(df.invoice_datetime, errors='coerce')
    df['quantity'] = pd.to_numeric(df.quantity, errors='coerce')
    df['unit_price'] = pd.to_numeric(df.unit_price, errors='coerce')
    df['total_amount'] = df.quantity * df.unit_price
    logging.info('读取 %d 行，日期无效 %d 行', len(df), df.invoice_datetime.isna().sum())
    return df

def filter_real_sales(df):
    # 商品格式含数据中可识别的 DCGS/SP 商品编码；仍需商品主数据核实。
    product = df.stock_code.str.fullmatch(r'(?:\d+[A-Za-z]*|DCGS\d+[A-Za-z]*|SP\d+)', na=False)
    mask = product & df.invoice_no.str.fullmatch(r'\d+', na=False) & df.quantity.gt(0) & df.unit_price.gt(0) & df.invoice_datetime.notna()
    out = df.loc[mask, COLS].copy()
    logging.info('正向商品销售 %d 行', len(out))
    return out

def compute_rfm(sales, reference_date):
    d = sales.dropna(subset=['customer_id']).copy()
    g = d.groupby('customer_id', sort=True)
    result = g.agg(frequency=('invoice_no','nunique'), monetary=('total_amount','sum'), first_purchase_date=('invoice_datetime','min'), last_purchase_date=('invoice_datetime','max'), unique_products=('stock_code','nunique')).reset_index()
    countries = d.groupby(['customer_id','country'], dropna=False).size().reset_index(name='n').sort_values(['customer_id','n','country'], ascending=[True,False,True], na_position='last').drop_duplicates('customer_id')
    result = result.merge(countries[['customer_id','country']], on='customer_id', how='left', validate='one_to_one')
    result['recency_days'] = (reference_date.normalize() - result.last_purchase_date.dt.normalize()).dt.days
    result['is_one_time_buyer'] = result.frequency.eq(1)
    return result[['customer_id','recency_days','frequency','monetary','first_purchase_date','last_purchase_date','unique_products','country','is_one_time_buyer']]

def match_returns(df, sales):
    # 按客户和商品维护原单可退余额，仅对涉及退货的组循环，不遍历全表。
    import json
    ret = df.loc[df.invoice_no.str.startswith('C', na=False), COLS].copy().reset_index(drop=True)
    ret['matched_original_invoice'] = pd.Series(pd.NA, index=ret.index, dtype='string')
    ret['matched_allocations'] = '[]'
    ret['matched_quantity'] = 0.0
    ret['match_status'] = 'unmatched'
    ret['row_id'] = np.arange(len(ret))
    eligible = ret.loc[ret.customer_id.notna() & ret.stock_code.notna() & ret.invoice_datetime.notna() & ret.quantity.lt(0)]
    keys = eligible[['customer_id','stock_code']].drop_duplicates()
    candidates = sales.merge(keys, on=['customer_id','stock_code'], how='inner')
    groups = {key: part.sort_values(['invoice_datetime','invoice_no'], kind='stable') for key,part in candidates.groupby(['customer_id','stock_code'],sort=False)}
    for key, part in eligible.groupby(['customer_id','stock_code'],sort=False):
        source=groups.get(key)
        if source is None: continue
        ordered=source[['invoice_datetime','invoice_no','quantity']].itertuples(index=False,name=None)
        purchases=list(ordered); pos=0; available=[]
        for row in part.sort_values(['invoice_datetime','invoice_no','row_id'],kind='stable').itertuples(index=False):
            # 严格早于退货时间；同时间销售不作匹配。
            while pos<len(purchases) and purchases[pos][0]<row.invoice_datetime:
                when,invoice,quantity=purchases[pos]; available.append([invoice,float(quantity)]); pos+=1
            need=float(-row.quantity); remaining=need; allocations=[]
            # 优先使用余额恰好相等且时间最近的原单；其余按最近优先拆分。
            exact=next((j for j in range(len(available)-1,-1,-1) if available[j][1]==remaining),None)
            indices=([exact] if exact is not None else [])+[j for j in range(len(available)-1,-1,-1) if j!=exact]
            for j in indices:
                if remaining<=0: break
                invoice,balance=available[j]
                if balance<=0: continue
                take=min(balance,remaining); available[j][1]-=take; remaining-=take
                allocations.append({'invoice_no':invoice,'quantity':take})
            idx=row.row_id
            # itertuples 会重命名前导下划线列，改由排序后的索引定位。
            if idx is None: raise RuntimeError('内部退货编号不可用')
            if allocations:
                ret.at[idx,'matched_original_invoice']=allocations[0]['invoice_no']
                ret.at[idx,'matched_allocations']=json.dumps(allocations,ensure_ascii=False)
                ret.at[idx,'matched_quantity']=need-remaining
                ret.at[idx,'match_status']='matched' if remaining==0 else 'partial'
    logging.info('退货 %d 行；完全匹配 %d，部分匹配 %d，未匹配 %d',len(ret),ret.match_status.eq('matched').sum(),ret.match_status.eq('partial').sum(),ret.match_status.eq('unmatched').sum())
    return ret.drop(columns='row_id')

def validate_output(sales, features, returns):
    assert sales.total_amount.ge(0).all() and sales.invoice_datetime.notna().all()
    assert features.customer_id.notna().all() and features.customer_id.is_unique and features.recency_days.ge(0).all()
    assert returns.invoice_no.str.startswith('C').all()
    assert (returns.matched_quantity <= returns.quantity.abs()).all()
    logging.info('断言通过')

def main():
    start=time.monotonic()
    try:
        df=load_data(); sales=filter_real_sales(df)
        features=compute_rfm(sales, df.invoice_datetime.max())
        returns=match_returns(df,sales); validate_output(sales,features,returns)
        out=HERE/'outputs'; out.mkdir(exist_ok=True)
        for name, frame in [('sales_facts',sales),('customer_features',features),('returns_log',returns)]:
            frame.to_parquet(out/f'{name}.parquet', index=False)
        elapsed=time.monotonic()-start
        report=f'''# 数据校验报告\n\n- 原始记录：{len(df):,}；销售事实：{len(sales):,}；客户特征：{len(features):,}；取消记录：{len(returns):,}。\n- 销售金额：{sales.total_amount.sum():,.2f}；匿名销售行占比：{sales.customer_id.isna().mean():.2%}。\n- RFM recency 范围：{features.recency_days.min()}–{features.recency_days.max()} 天；一次购买客户：{features.is_one_time_buyer.sum():,}。\n- 退货完全匹配：{returns.match_status.eq('matched').sum():,}；部分匹配：{returns.match_status.eq('partial').sum():,}；未匹配：{returns.match_status.eq('unmatched').sum():,}。\n- 运行耗时：{elapsed:.2f} 秒；断言通过。\n- 匹配先找同数量原单，再按最近销售拆分，维护每笔销售的可退余额；只依据客户、商品、时间和数量推断，仍需人工或业务系统核验。\n'''
        (HERE/'validation_report.md').write_text(report, encoding='utf-8')
        logging.info('完成，耗时 %.2f 秒',elapsed); print(report)
    except Exception:
        logging.exception('管道失败'); raise
if __name__=='__main__': main()

