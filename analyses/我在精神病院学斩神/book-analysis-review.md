# 《我在精神病院学斩神》跨阶段写法拆书审核

状态：批准的抽样任务已完成，等待统一审核；**不是全文拆完**。用户确认主轴为具体关照与并肩行动如何产生情绪回报，并保留悬疑、动作、信息释放与节奏。人物独立卡关闭，新书设计尚未开始。

## 实际范围与预算

固定用户授权快照；SHA-256：7657e4a174a1a8e6382e739ce3b4c4464cd486d9e9419371bce10d46cc10a9bc。偏移是UTF-8-SIG解码后的Unicode字符、右端不含。

正式12窗、56个章级来源单元，共**125812非空来源字符**，约为本地4240232字符的2.97%；累计唯一阅读也是125812，所有初次预读均已纳入正式笔记，无额外未登记游离定位窗。本次继B01新增唯一阅读63313；B01结束时62499，已含三窗预读。四批正式量分别B01 37306、B02 33457、B03 24850、B04 30199。总目标10–20万已满足，上限余量74188，不自动扩围。

量按来源单元计，含少量作者留言/维护提示及末章附带感言/站点声明；副文本不充当小说表达、市场成绩或当前改编信息的证据。局部事件未闭环的窗口均在note说明，完整章末不等于完整事件链。

| 样本/笔记 | 原章号 / catalog ordinal | 字符区间 | 非空来源字符 | 观察类型 |
| --- | --- | --- | ---: | --- |
| [B01-W01 / segment-001](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-001.md) | 1–4 / 1–4 | [173,12370) | 10248 | 街头问诊家庭校园 |
| [B01-W02 / segment-002](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-002.md) | 5–11 / 5–11 | [12370,31793) | 15938 | 关照失效/初战救援归家 |
| [B01-W03 / segment-003](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-003.md) | 100–104 / 100–104 | [262378,276073) | 11120 | 训练退出与生活照顾 |
| [B02-W01 / segment-004](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-004.md) | 500–507 / 500–507 | [1252365,1272764) | 16921 | 多人战斗/卧底揭示/危机扩展与救治 |
| [B02-W02 / segment-005](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-005.md) | 300–303 / 300–303 | [764050,773773) | 8299 | 受困筹划/病院监控/梦境取证/传闻与敌线 |
| [B02-W03 / segment-006](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-006.md) | 700–703 / 699–702 | [1750275,1759792) | 8237 | 掷币/预言/双线潜海/侦察悬疑 |
| [B03-W01 / segment-007](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-007.md) | 1200–1203 / 1199–1202 | [2977476,2987490) | 8524 | 代理人私密身份/海岛试错/疯王看护 |
| [B03-W02 / segment-008](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-008.md) | 1400–1403 / 1399–1402 | [3463307,3472756) | 8109 | 海岛防御/强者救场/他人完成私仇 |
| [B03-W03 / segment-009](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-009.md) | 1600–1603 / 1605–1608 | [3954600,3964127) | 8217 | 档案悬疑/会议喜剧/资源让渡/亲人求同行 |
| [B04-W01 / segment-010](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-010.md) | 2000–2003 / 2008–2011 | [4924928,4934577) | 8171 | 牺牲交接/记忆重获/伙伴响应与神战 |
| [B04-W02 / segment-011](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-011.md) | 1800–1803 / 1807–1810 | [4443803,4453384) | 8193 | 凤凰护民/压倒性入场/人质反转/共同破笼 |
| [B04-W03 / segment-012](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/notes/segment-012.md) | 2018–2021 / 2026–2029 | [4968921,4985208) | 13835 | 升维援助/队友重聚/共同制敌/归家与门前期待 |


source/segment-map.json仅为整文件候选分区，与notes同名编号不对应；正式范围以本表和[sample-plan.md](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/sample-plan.md)为准。未读补集见[coverage-map.md](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/coverage-map.md)。

## 值得保留的跨阶段结论

| 维度 | 有证据的判断 | 独立支持与反例 |
| --- | --- | --- |
| 视角 | 换线改变读者对行为的解释，可领先、同步或落后 | 1–3章公共误读；300–303章机构/敌线；2001–2003章公开回应。1600章可同步探索，无需多视角；CLAIM-036 |
| 对白 | 立场/目标差异推动拒绝、协商、边界与交接 | 10章拒招募、101章朋友/交易、1602–1603任务/亲人、2020协作窗口。共享吐槽和说明很多，不声称句法全独有；CLAIM-037 |
| 细节/语言 | 付出先成为具体劳动、资源、留下或身体成本，才能承载被在乎 | 2/4章生活成本、1202看护、1800/1803护民、2019/2021重聚。7章善意破裂，302章恭维非温情；CLAIM-038 |
| 信息释放 | 后置原因、局部验证、先知等待各不同，不应混成一种悬疑 | 4章鸡蛋原因、302门禁验证、6–8两只怪物、2021回家误判。课堂/终局也集中解释；CLAIM-040 |
| 动作清晰度 | 条件与后果持续，后期更多用分工和法则机制维持可懂 | 7–10章身体/工具、500–507空间/媒介、1801–1803定水破笼、2020内外分工。702拆警报概括，1403有强者兜底；CLAIM-039 |
| 情绪/场景节奏 | 场景责任交接与尺度变换，比固定悲喜配方更稳定 | 危机归家、1202静场、1603私下复盘、2021宇宙缩回厨房/车边/门店。喜剧/复活可能减弱创伤重量；CLAIM-041 |
| 章节牵引 | 可等待危险、身份、回应、行动后果，也可完成关系判断后收束 | 9–10章惯性、1202静态、2001–2003援手、2019–2021解释/出刀/留白。核心未完成不能靠含糊停笔冒充留白；CLAIM-042 |

主轴检验：支持不等于任何有利安排。300–303章监控、302章力量后的服务、1603章亲人同行的争议条件需要与真切照顾分开；700–703探索与1600档案主要是认知/行动回报，关系轴移动弱。A仍能解释跨阶段关系满足，但不是排他的全书发动机。

阶段变化：早期以日常生活和身体窄空间为主；中段进入机构观察、跨空间行动与看护；后期扩大为资源/群体救援和宇宙机制，最终回到熟悉生活。不是后期只剩史诗腔：仍有口语、玩笑、伸手、拒绝、同意和家常愿望。第1601–1603与1800–1803的夏思萌可比喜剧/护民两种呈现，但中间弧未覆盖，不补完成长故事。

## 产物导航

- [总览](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/sections/overview.md)、[跨阶段写法比较](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/sections/style-technique.md)：七维结论、适用条件与反例；B01原小节有独立历史文件保留。
- [证据账本](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/evidence-ledger.md)：42条稳定CLAIM，fact/inference明确；效果结论主要为中等置信度推断，不冒称作者意图。
- [未知清单](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/uncertainty-ledger.md)：未读前情、证言层级与样本偏差。
- [七张方法候选](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/pattern-cards.md)：原因后置、支持成本/边界、局部行动条件、知情位置、保留行动权、付出可见、责任后缩小尺度；不是新书writing-style合同。
- [样本注册](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/sampling-register.yaml)、[覆盖地图](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/coverage-map.md)：精确映射和预算；[图节点](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/graph/nodes.jsonl)/[边](/Users/likai/go/src/write/ani-book-skill/analyses/我在精神病院学斩神/graph/edges.jsonl)与本地分析索引仅用于检索。

## 不能据此断言的内容

没有读取第12–99章、绝大多数中间章节与2004–2017章，不能评价所有伏笔是否公平、完整关系弧、全部角色结局或全书节奏比例。第103章“他”仍未指认；终页门内人物未直写，不补画面。第1803章夏思萌完整后果不在本窗；第2021复活解释的准备过程未读，不能断言铺垫足够。

开篇/终局的“帅”、敲门/开门可以核对表达职责的回响（CLAIM-035），不能据两端证明作者从一开始就预谋全部。结尾重聚/复活有情绪回报，也有损失不可逆性变弱的权衡。所有阅读效果推断均无读者实验/市场验证。

## 审核重点与边界

请统一审核：这些结论是否足够具体可定位、适用条件/失败方式是否明确、反例是否保留、哪些方法值得以后另行授权迁移。当前只交原作研究，不输出新书设定、剧情、都市映射、写法合同或仿写。下一步状态为review_completed_analysis，等待父Agent汇总后的审核。

验证结果另见文末最终校验记录。

## 最终校验记录

- 来源快照SHA-256复核一致；12窗的原章号、catalog ordinal、字符边界及非空计数逐项吻合。去重正式/唯一阅读均125812，56个章级单元；未读4114420非空字符，state中的补集区间一致。
- 42个CLAIM ID唯一，笔记/小节/方法卡/审核入口引用均存在；7张方法候选；19个图节点、15条边，端点与证据引用有效，图的note来源均存在。
- YAML实际解析通过：analysis.complete只指抽样任务；coverage.sampled；透镜ready；人物同步字符串off；唯一下一步review_completed_analysis。
- SQLite integrity_check=ok；88个分析chunk；全部索引路径检查无source原文，检索可返回有效分析片段。6份历史派生索引保留且重建前尺寸已核对；无遗留tmp。
- token账本validate通过，共3次获准创作执行的覆盖记录（透镜、B01、本次B02–B04及综合）；模型gpt-6.1-sol，均unavailable/runtime_usage_not_exposed。宿主没有usage，不据字符折算；汇总精确token显示0表示无数据，非零消耗声明。
- 无独立人物卡、无新书设定/剧情/写法合同/正文；未运行应用测试、浏览器、Web生产API。当前等待父Agent统一汇总给用户审核。
