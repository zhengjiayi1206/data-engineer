from pathlib import Path
import shutil
import kagglehub

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'

def download():
    DATA.mkdir(exist_ok=True)
    retail = DATA / 'online_retail_ii.csv'
    if not retail.exists():
        root = Path(kagglehub.dataset_download('mashlyn/online-retail-ii-uci'))
        matches = [p for p in root.rglob('*.csv') if p.name.lower() == 'online_retail_ii.csv']
        if not matches:
            raise FileNotFoundError(f'零售 CSV 不存在: {root}')
        shutil.copy2(matches[0], retail)
    olist = DATA / 'olist'
    required = ['olist_customers_dataset.csv', 'olist_geolocation_dataset.csv', 'olist_order_items_dataset.csv', 'olist_order_payments_dataset.csv', 'olist_order_reviews_dataset.csv', 'olist_orders_dataset.csv', 'olist_products_dataset.csv', 'olist_sellers_dataset.csv', 'product_category_name_translation.csv']
    if not all((olist / n).exists() for n in required):
        root = Path(kagglehub.dataset_download('olistbr/brazilian-ecommerce'))
        olist.mkdir(exist_ok=True)
        for name in required:
            matches = list(root.rglob(name))
            if not matches:
                raise FileNotFoundError(f'缺少 {name}: {root}')
            shutil.copy2(matches[0], olist / name)
    print('数据准备完成')

if __name__ == '__main__':
    download()

