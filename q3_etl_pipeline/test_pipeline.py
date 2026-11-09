import unittest
import pandas as pd
from q3_etl_pipeline.pipeline import filter_real_sales, compute_rfm, match_returns

class PipelineTests(unittest.TestCase):
    def test_match_with_balance_and_rfm(self):
        df=pd.DataFrame([
            ['1','123','item',5,2,'2020-01-01','10','UK'],
            ['2','123','item',10,2,'2020-01-02','10','UK'],
            ['3','POST','post',1,5,'2020-01-02','10','UK'],
            ['C4','123','item',-5,2,'2020-01-03','10','UK'],
            ['C5','123','item',-7,2,'2020-01-04','10','UK'],
            ['C6','123','item',-5,2,'2020-01-05','10','UK'],
        ],columns=['invoice_no','stock_code','description','quantity','unit_price','invoice_datetime','customer_id','country'])
        df['invoice_datetime']=pd.to_datetime(df.invoice_datetime); df['total_amount']=df.quantity*df.unit_price
        sales=filter_real_sales(df); self.assertEqual(sales.invoice_no.tolist(),['1','2'])
        features=compute_rfm(sales,pd.Timestamp('2020-01-03'))
        self.assertEqual((features.frequency.iloc[0],features.monetary.iloc[0],features.recency_days.iloc[0]),(2,30,1))
        returns=match_returns(df,sales).set_index('invoice_no')
        self.assertEqual(returns.loc['C4','matched_original_invoice'],'1')
        self.assertEqual(returns.loc['C5','matched_original_invoice'],'2')
        self.assertEqual(returns.loc['C6','matched_quantity'],3)
        self.assertEqual(returns.loc['C6','match_status'],'partial')
if __name__=='__main__': unittest.main()
