# 用量边界与一次纯操作误记校正

首轮追加式账本有508条记录，宿主均未暴露usage，token与费用不可统计。首轮有效创作执行记录为507条，不是精确服务端请求计费。

事件07f1ec07-6c38-4616-b579-6fd9ac805f31对应history/pattern-cards-before-final.md纯文件复制，被通用保存器误记一次。旧行不改，以token-usage-corrections.json标明排除。production/token-summary.json为原始账本工具汇总，故原始事件数比有效执行记录数多1；不能把纯文件操作计作创作调用。无exact/estimated token，不根据字符数估算。

2026-11-24 复核另记 4 项可定位的内容修订。当前账本共 512 条，排除上述纯复制后为 511 条。宿主未提供每项生成的请求边界和用量。[机器汇总](token-summary.json)
