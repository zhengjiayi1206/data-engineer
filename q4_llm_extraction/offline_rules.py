import json, re, random
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent
# 只对文字完全包含的短语赋予有限标签，不能覆盖葡语的所有表达。
RULES=[(r'produto chegou quebrado','quality_defect','Product arrived broken'),(r'embalagem rasgada','packaging','Torn packaging'),(r'produto errado','wrong_product','Wrong product'),(r'produto quebrado','quality_defect','Broken product')]

def main():
    df=pd.read_csv(ROOT/'data/olist/olist_order_reviews_dataset.csv')
    df=df.loc[df.review_score.le(3)].copy()
    output=[]
    for row in df.itertuples(index=False):
        raw=row.review_comment_message
        txt=raw if isinstance(raw,str) else ''
        issues=[]
        for pattern,category,translation in RULES:
            m=re.search(pattern,txt,re.I)
            if m:
                issues.append({'category':category,'severity':'medium','evidence_quote':m.group(0),'evidence_quote_en':translation})
        # 分数是评分映射而非模型情感推断，置信度为规则置信度；空问题不等于没有问题。
        output.append({'review_id':str(row.review_id),'issues':issues,'sentiment_score':round((float(row.review_score)-3)/2,2),'actionable_for_seller':bool(issues),'confidence':0.55 if issues else 0.0,'processing_status':'rule_match' if issues else 'needs_review_or_model'})
    (HERE/'offline_rules_results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    random.seed(42)
    sample=df.sample(n=min(30,len(df)),random_state=42)[['review_id','review_score','review_comment_message']].copy()
    sample['manual_categories']=''; sample['manual_evidence']=''; sample.to_csv(HERE/'offline_evaluation_sample.csv',index=False,encoding='utf-8-sig')
    matched=sum(bool(x['issues']) for x in output)
    print(f'差评 {len(output)} 条；规则匹配 {matched} 条；待审核或模型处理 {len(output)-matched} 条')
if __name__=='__main__': main()

