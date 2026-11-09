# 数据探索发现

本报告由 `python q1_data_quality/q1_code.py` 从原始数据生成。金额使用数量乘单价的原始净额，不等同于财务收入。

## 1. 发票前缀

```
         rows  invoices  quantity      amount
prefix                                       
A           6         6         6  -147614.08
C       19494      8292   -490992 -1526667.86
```
C 通常表示取消；其他代码须结合下列明细及业务方核实，不能按前缀机械认定。净销售需单独核算取消、折扣、运费和坏账调整。

```
prefix  stock_code  description                       
C       M           Manual                                538
        22423       REGENCY CAKESTAND 3 TIER              347
        POST        POSTAGE                               229
        22138       BAKING SET 9 PIECE RETROSPOT          211
        21232       STRAWBERRY CERAMIC TRINKET BOX        184
        D           Discount                              172
        85123A      WHITE HANGING HEART T-LIGHT HOLDER    135
        79323W      WHITE CHERRY LIGHTS                   121
        21843       RED RETROSPOT CAKE STAND              111
        S           SAMPLES                               101
        22960       JAM MAKING SET WITH JARS               90
        82483       WOOD 2 DRAWER CABINET WHITE FINISH     89
        79323P      PINK CHERRY LIGHTS                     86
        22720       SET OF 3 CAKE TINS PANTRY DESIGN       74
        21527       RED RETROSPOT TRADITIONAL TEAPOT       74
        85099B      JUMBO BAG RED RETROSPOT                74
        21231       SWEETHEART CERAMIC TRINKET BOX         73
        37449       CERAMIC CAKE STAND + HANGING CAKES     72
        21314       SMALL GLASS HEART TRINKET POT          71
        84949       SILVER HANGING T-LIGHT HOLDER          68
```

## 2. 非普通商品编码

行占比 0.57%；原始净金额占比 -0.49%；绝对金额占比 8.05%。正则是识别候选的启发式，不等于完整商品主数据。POST 通常为邮费，D 为折扣，M 为手工调整，AMAZONFEE/BANK CHARGES 为费用；其余见描述并待核实。

```
              rows      amount                               sample
stock_code                                                         
POST          2122  112341.000                              POSTAGE
DOT           1446  322647.470                       DOTCOM POSTAGE
M             1421  -82796.320                               Manual
C2             282   13386.000                             CARRIAGE
D              177  -13484.540                             Discount
S              104   -6065.800                              SAMPLES
BANK CHARGES   102  -35562.629                         Bank Charges
ADJUST          67    6835.240  Adjustment by john on 26/01/2010 16
AMAZONFEE       43 -260763.580                           AMAZON FEE
DCGS0058        31      34.820                     MISO PRETTY  GUM
gift_0001_20    29     471.060   Dotcomgiftshop Gift Voucher £20.00
gift_0001_30    29     610.090   Dotcomgiftshop Gift Voucher £30.00
DCGSSGIRL       25     295.630                               update
DCGSSBOY        23     251.350                               update
PADS            19     -36.583           PADS TO MATCH ALL CUSHIONS
gift_0001_10    16     126.210   Dotcomgiftshop Gift Voucher £10.00
CRUK            16   -7933.430                      CRUK Commission
TEST001         15     202.500              This is a test product.
DCGS0076        15     292.090         SUNJAR LED NIGHT NIGHT LIGHT
DCGS0003        14      32.590                  BOXED GLASS ASHTRAY
gift_0001_50     8     253.590   Dotcomgiftshop Gift Voucher £50.00
gift_0001_40     7     166.090   Dotcomgiftshop Gift Voucher £40.00
DCGS0069         6      80.310                OOH LA LA DOGS COLLAR
B                6 -147614.080                      Adjust bad debt
DCGS0004         5      67.940           HAYNES CAMPER SHOULDER BAG
m                5      15.050                               Manual
gift_0001_80     4       0.000   Dotcomgiftshop Gift Voucher £80.00
DCGS0066N        4      17.300              NAVY CUDDLES DOG HOODIE
DCGS0072         4      20.680               CAT CAMOUFLAGUE COLLAR
SP1002           3      14.750               KID'S CHALKBOARD/EASEL
gift_0001_70     3      59.570   Dotcomgiftshop Gift Voucher £70.00
DCGS0070         3      25.440                CAMOUFLAGE DOG COLLAR
DCGS0068         3      17.120                    DOGS NIGHT COLLAR
ADJUST2          3     731.050  Adjustment by Peter on Jun 25 2010 
gift_0001_90     2       0.000                                 None
gift_0001_60     2       0.000                                 None
DCGS0062         2       2.510              ROAD-RAGE CAR FRESHENER
DCGS0037         2      12.720                   KEY-RING CORKSCREW
TEST002          2       1.000              This is a test product.
DCGS0067         1       0.000                                 ebay
DCGS0044         1       2.570              HANDZ-OFF CAR FRESHENER
C3               1       0.000                                 None
DCGS0006         1       0.000                                 None
DCGS0016         1       0.000                                 None
DCGS0027         1       0.000                                 None
DCGS0036         1       0.000                                 None
DCGS0039         1       0.000                                 None
DCGS0041         1       5.060     HAYNES MINI-COOPER PLAYING CARDS
DCGS0053         1       0.000                                 None
DCGS0071         1       0.000                                 None
DCGS0055         1       0.000                                 None
DCGS0056         1       0.000                                 None
GIFT             1       0.000                                 None
DCGS0057         1       0.000                                 None
DCGS0059         1       0.000                                 None
DCGS0060         1       0.000                                 None
DCGSLGIRL        1       0.000                                 None
DCGSLBOY         1       0.000                                 None
DCGS0075         1      12.720                 CAMOUFLAGUE DOG LEAD
DCGS0074         1       0.000                                 None
DCGS0073         1       0.000                                 ebay
DCGS0066P        1       0.000                                 None
47503J           1      16.130     SET/3 FLORAL GARDEN TOOLS IN BAG
```

## 3. 数量极值与负单价

```
invoice_no stock_code                 description  quantity    invoice_datetime  unit_price customer_id        country  total_amount
    581483      23843 PAPER CRAFT , LITTLE BIRDIE     80995 2011-12-09 09:15:00        2.08       16446 United Kingdom      168469.6
   C581484      23843 PAPER CRAFT , LITTLE BIRDIE    -80995 2011-12-09 09:27:00        2.08       16446 United Kingdom     -168469.6
```
比较客户、商品、日期和相反数量可发现潜在冲销，但不能仅凭此断言业务真实性。保留原始行，并在统计层区分销售与取消。

负价行按发票、编码、描述汇总：

```
invoice_no stock_code     description  rows  min_price
   A506401          B Adjust bad debt     1  -53594.36
   A516228          B Adjust bad debt     1  -44031.79
   A528059          B Adjust bad debt     1  -38925.87
   A563186          B Adjust bad debt     1  -11062.06
   A563187          B Adjust bad debt     1  -11062.06
```
这些记录需要按描述核实是否为坏账或调整，不应作为普通商品收入。

## 4. 客户 ID 缺失

```
             rows        amount  invoices
anonymous                                
False      824364  1.664829e+07     44876
True       243007  2.638958e+06      8752
```
匿名行占比 22.77%；匿名原始净额占比 13.68%。

发票金额而非客户客单价：
```
                 mean  median
anonymous                    
False      370.984321  240.57
True       301.526300    0.00
```
国家与编码前五：
```
anonymous  country       
False      United Kingdom    741301
           Germany            17624
           EIRE               16195
           France             14202
           Netherlands         5140
True       United Kingdom    240029
           EIRE                1671
           Hong Kong            364
           Unspecified          232
           France               128
anonymous  stock_code
False      85123A        5322
           22423         3777
           85099B        3446
           84879         2794
           20725         2755
True       DOT           1430
           85099B         770
           22423          647
           21212          639
           21931          635
```
匿名可能反映未登记客户或零售渠道，但数据本身不足以证明具体人群；不能把发票金额称作客户客单价。
