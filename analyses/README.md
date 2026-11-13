# 拆书分析成果

这里保存两本参考书的分析成果和证据记录，用于阅读、核对与后续原创设计。原书 TXT 快照和可重建的 SQLite 检索缓存留在本地，不随仓库分发；`source/` 中提交的是章节目录、分段范围和分批元数据。

| 参考书 | 完成范围 | 主要用途 | 审核入口 |
| --- | --- | --- | --- |
| 《张三丰异界游》 | 本地文件全文，40 批、390 段、3,682,989 非空字符 | 结构、设定、重要伏笔；重点观察跨体系知识、资源经营和势力积累 | [全文分析报告](张三丰异界游/book-analysis-review.md) |
| 《我在精神病院学斩神》 | 跨阶段抽样，4 批、12 窗、125,812 非空字符 | 写法、叙事、节奏；重点观察具体关照与并肩行动的情绪回报，同时保留悬疑和行动机制 | [抽样分析报告](我在精神病院学斩神/book-analysis-review.md) |

全文覆盖指所提供的本地文件，不等于经过外部版本校勘。抽样结论只适用于登记的已读范围。两项拆书任务完成，综合结论仍等待作者审核；新书设计、系统建书和正文生成均未开始。

## 建议阅读顺序

1. 先读上表两份分析报告，了解结论、覆盖范围和待核对事项。
2. 读《张三丰异界游》的[总览](张三丰异界游/sections/overview.md)与[故事结构](张三丰异界游/sections/plot-structure.md)，理解长篇如何推进。
3. 读[世界设定](张三丰异界游/sections/worldbuilding.md)与[人物功能和关系](张三丰异界游/sections/character-system.md)，理解优势、约束和选择怎样产生冲突。
4. 读[重要伏笔终局审计](张三丰异界游/promise-final-audit.md)；涉及事件先后时查[时间线](张三丰异界游/sections/timeline.md)，涉及原文异常时查[来源质量复核](张三丰异界游/source-quality-review.md)。
5. 读《斩神》的[总览](我在精神病院学斩神/sections/overview.md)与[跨阶段写法比较](我在精神病院学斩神/sections/style-technique.md)，理解对白、动作、信息释放和情绪回报的具体方法。
6. 最后读两本书的机制卡：[结构与设定机制](张三丰异界游/pattern-cards.md)、[写法方法](我在精神病院学斩神/pattern-cards.md)，标记“想保留 / 想排除 / 需要解释”。机制卡是候选方法，不是已确认的新书设定或写法合同。

有疑问时按 `CLAIM → evidence-ledger.md → notes/segment-NNN.md → 来源范围` 查证。分批报告与阶段综合用于深入阅读；`history/` 是保留的历史版本。旧记录可能仍写“待后续核对”，最终状态以根目录 `analysis-state.yaml` 和综合报告为准。

《斩神》的正式 12 窗映射见 [sample-plan.md](我在精神病院学斩神/sample-plan.md) 和 [sampling-register.yaml](我在精神病院学斩神/sampling-register.yaml)。其 `source/segment-map.json` 是全文件候选分区，编号不对应 12 份正式笔记。

## 在新会话中接续原创设计

以下提示词适用于能够访问本地仓库文件的会话。路径以本机位置为例；换机器后将其替换为实际仓库路径。先读综合成果，只在需要查证时读取相关笔记，不必把全部文件一次塞入上下文。

```text
使用 $produce-long-form-novel，基于已完成的两份拆书分析，开始原创小说的设计预览。请用当前会话选定的模型完成设计，不使用子 Agent。

Skill 仓库：/Users/likai/go/src/write/ani-book-skill
分析根目录：/Users/likai/go/src/write/ani-book-skill/analyses

先读取 analyses/README.md，以及两个书目录内的 analysis-state.yaml、execution-brief.md、book-analysis-review.md、coverage-map.md、pattern-cards.md 和 uncertainty-ledger.md。
然后读取《张三丰异界游》的 sections/overview.md、sections/plot-structure.md、sections/worldbuilding.md、sections/character-system.md 和 promise-final-audit.md；读取《我在精神病院学斩神》的 sections/overview.md 和 sections/style-technique.md。有具体疑问再沿 CLAIM 查 evidence-ledger.md 与相关分段笔记。

材料分工：
- 《张三丰异界游》已完成本地全文分析，用于学习故事架构、设定运作和伏笔组织，重点是跨体系知识怎样转成资源、组织能力和势力积累。
- 《我在精神病院学斩神》只完成跨阶段抽样，用于学习对白、行动、信息释放和节奏，重点是具体关照与并肩行动怎样带来情绪回报。不要把样本结论扩写成全书定论。
- 采用原创机制迁移：说明保留什么阅读回报、重建什么人物与因果、适用前提和代价。重建本书的人物、世界、事件及表达，不以改名换皮代替原创，也不直接模仿作者的独特文风。

已确认需求，沿用即可：
- 男频；现代架空都市＋超凡力量，日常与隐藏世界并存。
- 主角较早拥有优势，核心满足感是强者反差与主动破局。
- 暂不限定发布平台，以完整成书和后续试写效果为目标。
- ani-book-skill 负责拆书、设计与规划；章节正文在 Web 系统生成。
- 不默认继承参考书的总字数、人物数量、具体桥段或终局规模。

本轮只交付：需求复述、可采用与需舍弃的机制、两份有实质差异的原创方向预览，以及你的推荐理由。每份预览包含暂定书名、一句话卖点、主角处境与主动目标、优势及边界、核心冲突、长期推进方式、开篇回报和结局方向，并解释这些机制为何适合都市生活与制度。

新设定标注为候选；已有分析完成不代表我接受所有机制。需要我决定时，只集中提出 2–3 个影响最大的未定问题，并给出推荐，不重复询问已确认定位。

等我选定方向后，再保存新书简报，并分阶段建立故事发动机、世界与人物、原创写法合同、全书卷战略、首卷细纲、伏笔表和近期章节计划。后续向 Web 交接前，另行检查当前系统支持的字段与导入方式，准备可审核的交接包，不假定分析文件能直接导入。

本轮不要写章节正文，不创建 Web 小说，不调用生产接口或修改数据库，不覆盖现有拆书成果。
```

## 在其他路径读取或核验

原分析文件保留生成时的本机路径、历史状态与证据指纹，没有为发布而批量改写。网页阅读可从本页的相对链接及仓库目录进入；本地会话应以实际文件内容为准，遇到旧绝对链接时在对应书目录定位文件。

阅读已有报告不依赖原书快照。需要重新核验原文偏移或来源指纹时，应另行提供相同且有权使用的文本，按 `source-manifest.md` 与 `analysis-state.yaml` 核对文件 SHA-256。不要因仓库未分发原文而声称已重新核验来源。偏移按 UTF-8-SIG 解码后的 Unicode 字符计，右端不含；核验时须保留原始换行。

本地检索索引可由仓库脚本重建；在仓库根目录运行，例如：

```sh
python scripts/analysis_retrieval.py build analyses/张三丰异界游
python scripts/analysis_retrieval.py build analyses/我在精神病院学斩神
```

Markdown / YAML 及其证据仍是分析依据，SQLite 只是检索缓存。纯文件归档与索引重建不计为创作模型调用；历史用量中 `unavailable` 表示运行时未提供数据，不能解释为零 Token 或零费用。
