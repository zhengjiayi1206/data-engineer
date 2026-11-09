"""独立用 CSV 交叉核对 MySQL 的月度统计，不替代 MySQL 执行。"""
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]

def main():
    o=pd.read_csv(R/'data/olist/olist_orders_dataset.csv',parse_dates=['order_purchase_timestamp','order_delivered_customer_date'])
    items=pd.read_csv(R/'data/olist/olist_order_items_dataset.csv'); items['gmv']=items.price+items.freight_value
    o=o.merge(items.groupby('order_id',as_index=False).gmv.sum(),on='order_id',how='left')
    o['month']=o.order_purchase_timestamp.dt.strftime('%Y-%m'); o['delivered']=o.order_status.eq('delivered'); o['canceled']=o.order_status.eq('canceled')
    o['delivered_gmv']=o.gmv.fillna(0).where(o.delivered,0)
    o['days']=(o.order_delivered_customer_date-o.order_purchase_timestamp).dt.total_seconds().div(86400).where(o.delivered)
    g=o.groupby('month').agg(total_orders=('order_id','size'),delivered_orders=('delivered','sum'),canceled_orders=('canceled','sum'),delivered_gmv=('delivered_gmv','sum'),avg_delivery_days=('days','mean'))
    sql=pd.read_csv(R/'q2_sql_analysis/results/q2_2_monthly_metrics.csv').set_index('month').sort_index(); g=g.sort_index()
    assert g.index.equals(sql.index)
    for col in ['total_orders','delivered_orders','canceled_orders']:
        assert (g[col].astype(int)==sql[col].astype(int)).all(),col
    assert ((g.delivered_gmv-sql.delivered_gmv).abs()<0.011).all()
    assert ((g.avg_delivery_days-sql.avg_delivery_days).abs().fillna(0)<0.011).all()
    print(f'{len(g)} 个月的订单、送达、取消、GMV、时长与 MySQL 查询一致')
if __name__=='__main__': main()
