# 数据质量报告

数据来源：Online Retail II；行数 1,067,371。金额为数量乘单价，未经业务调整。

## 字段和缺失

```
              字段             类型    缺失数    缺失率
      invoice_no         string      0  0.00%
      stock_code         string      0  0.00%
     description         object   4382  0.41%
        quantity          int64      0  0.00%
invoice_datetime datetime64[ns]      0  0.00%
      unit_price        float64      0  0.00%
     customer_id         string 243007 22.77%
         country         object      0  0.00%
    total_amount        float64      0  0.00%
```

## 数值分布

```
          字段        min      max      mean        std
    quantity  -80995.00  80995.0  9.938898 172.705794
  unit_price  -53594.36  38970.0  4.649388 123.553059
total_amount -168469.60 168469.6 18.069866 292.420223
```

## 高频值

### invoice_no（唯一值 53,628）

```
invoice_no
537434    1350
538071    1304
537638    1202
537237    1194
536876    1186
536592    1184
537823    1182
537240    1136
573585    1114
537666    1072
```

### stock_code（唯一值 5,305）

```
stock_code
85123A    5829
22423     4424
85099B    4216
21212     3318
20725     3259
84879     2960
47566     2768
21232     2747
22197     2549
22383     2540
```

### description（唯一值 5,698）

```
description
WHITE HANGING HEART T-LIGHT HOLDER    5918
REGENCY CAKESTAND 3 TIER              4412
JUMBO BAG RED RETROSPOT               3469
ASSORTED COLOUR BIRD ORNAMENT         2958
PARTY BUNTING                         2765
STRAWBERRY CERAMIC TRINKET BOX        2613
LUNCH BAG  BLACK SKULL.               2529
JUMBO STORAGE BAG SUKI                2434
HEART OF WICKER SMALL                 2319
JUMBO SHOPPER VINTAGE RED PAISLEY     2297
```

### customer_id（唯一值 5,942）

```
customer_id
17841    13097
14911    11613
12748     7307
14606     6709
14096     5128
15311     4717
14156     4130
14646     3890
13089     3438
16549     3255
```

### country（唯一值 43）

```
country
United Kingdom    981330
EIRE               17866
Germany            17624
France             14330
Netherlands         5140
Spain               3811
Switzerland         3189
Belgium             3123
Portugal            2620
Australia           1913
```

## 可疑现象

- 客户 ID 缺失 243,007 行（22.77%），不能直接视为无效交易。
- 数量负数 22,950 行，涉及退货和调整；数量零值 0 行。
- 单价负数 5 行，单价为零 6,202 行。
- 完整重复行 34,335 行；需要业务主键才能确认是否重复上报。
- 非商品格式编码 6,094 行，含费用或调整，不能一概视为商品。
- 数量极值 -80,995 至 80,995，须结合交易上下文判断。
