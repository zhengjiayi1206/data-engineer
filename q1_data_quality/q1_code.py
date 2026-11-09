from pathlib import Path
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from q3_etl_pipeline.pipeline import load_data
HERE=Path(__file__).resolve().parent

def tab(frame):
    return frame.to_string(index=False)

def main():
    d=load_data(); n=len(d)
    types=pd.DataFrame({'字段':d.columns,'类型':[str(x) for x in d.dtypes], '缺失数':d.isna().sum().values, '缺失率':d.isna().mean().map(lambda x:f'{x:.2%}').values})
    num=d.select_dtypes(include='number').agg(['min','max','mean','std']).T.reset_index().rename(columns={'index':'字段'})
    high=[]
    for col in ['invoice_no','stock_code','description','customer_id','country']:
        high.append(f'### {col}（唯一值 {d[col].nunique():,}）\n\n```\n{d[col].value_counts().head(10).to_string()}\n```')
    findings=[f'客户 ID 缺失 {d.customer_id.isna().sum():,} 行（{d.customer_id.isna().mean():.2%}），不能直接视为无效交易。',f'数量负数 {d.quantity.lt(0).sum():,} 行，涉及退货和调整；数量零值 {d.quantity.eq(0).sum():,} 行。',f'单价负数 {d.unit_price.lt(0).sum():,} 行，单价为零 {d.unit_price.eq(0).sum():,} 行。',f'完整重复行 {d.duplicated().sum():,} 行；需要业务主键才能确认是否重复上报。',f'非商品格式编码 {((~d.stock_code.str.fullmatch(r"\d+[A-Za-z]*",na=False))).sum():,} 行，含费用或调整，不能一概视为商品。',f'数量极值 {d.quantity.min():,.0f} 至 {d.quantity.max():,.0f}，须结合交易上下文判断。']
    (HERE/'data_quality_report.md').write_text('# 数据质量报告\n\n数据来源：Online Retail II；行数 {:,}。金额为数量乘单价，未经业务调整。\n\n## 字段和缺失\n\n```\n{}\n```\n\n## 数值分布\n\n```\n{}\n```\n\n## 高频值\n\n{}\n\n## 可疑现象\n\n{}\n'.format(n,tab(types),tab(num),'\n\n'.join(high),'\n'.join('- '+x for x in findings)),encoding='utf-8')
    pref=d.loc[~d.invoice_no.str.fullmatch(r'\d+',na=False)].copy(); pref['prefix']=pref.invoice_no.str.extract(r'^([^\d]+)',expand=False).fillna('(其他)')
    special=d.loc[~d.stock_code.str.fullmatch(r'\d+[A-Za-z]*',na=False)].copy()
    codes=special.groupby('stock_code',dropna=False).agg(rows=('stock_code','size'),amount=('total_amount','sum'),sample=('description','first')).sort_values('rows',ascending=False)
    extreme=d.loc[d.quantity.isin([d.quantity.min(),d.quantity.max()])]
    neg=d.loc[d.unit_price.lt(0)].groupby(['invoice_no','stock_code','description'],dropna=False).agg(rows=('unit_price','size'),min_price=('unit_price','min')).reset_index()
    d['anonymous']=d.customer_id.isna(); group=d.groupby('anonymous').agg(rows=('invoice_no','size'),amount=('total_amount','sum'),invoices=('invoice_no','nunique'))
    inv=d.groupby(['anonymous','invoice_no'],dropna=False).total_amount.sum().groupby('anonymous').agg(['mean','median'])
    countries=d.groupby(['anonymous','country']).size().groupby(level=0,group_keys=False).nlargest(5)
    products=d.groupby(['anonymous','stock_code']).size().groupby(level=0,group_keys=False).nlargest(5)
    text=f'''# 数据探索发现\n\n本报告由 `python q1_data_quality/q1_code.py` 从原始数据生成。金额使用数量乘单价的原始净额，不等同于财务收入。\n\n## 1. 发票前缀\n\n```\n{pref.groupby('prefix').agg(rows=('invoice_no','size'),invoices=('invoice_no','nunique'),quantity=('quantity','sum'),amount=('total_amount','sum')).to_string()}\n```\nC 通常表示取消；其他代码须结合下列明细及业务方核实，不能按前缀机械认定。净销售需单独核算取消、折扣、运费和坏账调整。\n\n```\n{pref.groupby(['prefix','stock_code','description'],dropna=False).size().sort_values(ascending=False).head(20).to_string()}\n```\n\n## 2. 非普通商品编码\n\n行占比 {len(special)/n:.2%}；原始净金额占比 {special.total_amount.sum()/d.total_amount.sum():.2%}；绝对金额占比 {special.total_amount.abs().sum()/d.total_amount.abs().sum():.2%}。正则是识别候选的启发式，不等于完整商品主数据。POST 通常为邮费，D 为折扣，M 为手工调整，AMAZONFEE/BANK CHARGES 为费用；其余见描述并待核实。\n\n```\n{codes.to_string()}\n```\n\n## 3. 数量极值与负单价\n\n```\n{extreme.to_string(index=False)}\n```\n比较客户、商品、日期和相反数量可发现潜在冲销，但不能仅凭此断言业务真实性。保留原始行，并在统计层区分销售与取消。\n\n负价行按发票、编码、描述汇总：\n\n```\n{neg.to_string(index=False)}\n```\n这些记录需要按描述核实是否为坏账或调整，不应作为普通商品收入。\n\n## 4. 客户 ID 缺失\n\n```\n{group.to_string()}\n```\n匿名行占比 {d.anonymous.mean():.2%}；匿名原始净额占比 {d.loc[d.anonymous,'total_amount'].sum()/d.total_amount.sum():.2%}。\n\n发票金额而非客户客单价：\n```\n{inv.to_string()}\n```\n国家与编码前五：\n```\n{countries.to_string()}\n{products.to_string()}\n```\n匿名可能反映未登记客户或零售渠道，但数据本身不足以证明具体人群；不能把发票金额称作客户客单价。\n'''
    (HERE/'findings.md').write_text(text,encoding='utf-8')
    print('质量报告已生成')
if __name__=='__main__': main()
