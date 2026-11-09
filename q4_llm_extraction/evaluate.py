"""对人工编写的 30 条参考标签进行粗粒度多标签评估。"""
from pathlib import Path
import json
import pandas as pd
HERE=Path(__file__).resolve().parent

def main():
    ref=pd.read_csv(HERE/'evaluation_sample.csv').fillna({'reference_categories':''})
    results={json.loads(line)['row_id']:json.loads(line) for line in (HERE/'llm_results.jsonl').read_text(encoding='utf8').splitlines() if line.strip()}
    tp=fp=fn=evidence=issues=covered=0; details=[]
    for row in ref.itertuples(index=False):
        result=results.get(str(row.row_id))
        if not result: continue
        covered+=1; expected=set(row.reference_categories.split('|'))-{''}; predicted={x['category'] for x in result['issues']}
        tp+=len(expected&predicted); fp+=len(predicted-expected); fn+=len(expected-predicted)
        for x in result['issues']:
            issues+=1; evidence+=bool(x['evidence_quote'] in row.review_comment_message)
        details.append({'row_id':row.row_id,'reference':'|'.join(sorted(expected)),'prediction':'|'.join(sorted(predicted))})
    precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0
    pd.DataFrame(details).to_csv(HERE/'evaluation_comparison.csv',index=False,encoding='utf-8-sig')
    text=f'''# 准确率评估\n\n随机种子 42，从评分≤3 且文本超过 15 字的评价抽样 30 条；参考类别由本次 Codex 在查看模型输出前逐条阅读葡萄牙语编写，不是独立人工标注的 ground truth。无具体问题可标为空；未收到整单归为 other，明确超过预计期限才归为 delivery_late，商品短缺归为 missing_item。定义存在主观性，争议案例需要葡语业务标注员复核。\n\n已获得有效模型输出 {covered}/30 条；类别微平均 TP={tp}、FP={fp}、FN={fn}，精确率 {precision:.1%}，召回率 {recall:.1%}。输出证据原文存在率 {evidence}/{issues}；这只检查字符串是否存在，不能证明语义分类与翻译正确。逐条参考和预测见 `evaluation_sample.csv` 与 `evaluation_comparison.csv`。30 条样本小且仅覆盖有内容的评价，不能推广到全部评价，也不能替代人工独立双人复核。\n'''
    (HERE/'accuracy_evaluation.md').write_text(text,encoding='utf8'); print(text)
if __name__=='__main__': main()
