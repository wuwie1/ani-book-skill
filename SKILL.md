---
name: produce-long-form-novel
description: 中文长篇小说创作与拆书。用于看大纲、评判网文大纲的追读吸引力、先审稿给建议、试写一段、续写当前试读、正式写章、修稿、开书与分卷规划、拆书和原创机制迁移、同人、榜单分析及定稿导出。适用于对话预览和本地 Markdown/YAML 小说工作区。
---

# 长篇小说创作

Codex is the only engine for creative understanding, writing and judgment. Python 负责状态、校验、索引、冲突检查和导出。以作者这次想读到或完成的东西决定工作量。

## 先认清这次交付什么

| 作者的说法 | 交付与停止位置 |
| --- | --- |
| “看看大纲”“先审核，给建议” | 直接展示所问的内容，或用具体段落说明问题与可选改法。审阅在答复中完成；作者指定修订后才改稿。 |
| “试写一版我看看” | 直接给可读的候选正文，停在约定的位置。默认在对话中交付。“单独存一份”只新增候选文件，同名已有稿时另取名。 |
| 试读之后说“继续” | 接刚才那一版的实际末句，沿用人物处境、篇幅和交付方式。前次指定的停笔事件已经完成，本段从其后承接。 |
| “把这版定下来”“继续正式写第几章” | 按本次采用的版本、作品和已授权范围进入正式流程。从工作区恢复，检查计划、正文与批准状态。 |

“继续”也可能接上一轮的审阅、卷纲或拆书。先用最近的明确对象和作者指定的文件消歧。新会话里若确有多个候选且选错会续到不同的故事，只问要接哪一版。已明确的决定或有效委托直接沿用。

把 Skill 中的示例、分镜、篇幅分配和风格建议当作写作工具。作者锁定的事实、受保护的原稿、角色此刻能知道的事和本次停笔处优先。作者明确修改约定时，沿用其最新决定和适用范围。

**能指出具体冲突或读感代价时，可以先提异议。** 例如，提前揭晓会让读者失去哪一个期待？说明影响，给一个可行处理。已获委托且可逆时说明取舍并继续。必须由作者选择互相冲突的硬要求或授权替换原稿时，才停在该决定前。普通的措辞、对白、节奏和场景调度由写手判断。读感不理想时，先检验这场戏本身和写法规则是否值得保留。

## 使用本地工作区

Before the first production action in a task, compare the checked-out source with the installed mirror using `python scripts/sync_skill_mirror.py check <repository-root> <installed-skill-directory>`. Resolve the mirror as `skills/produce-long-form-novel` under `CODEX_HOME`, falling back to the user's `.codex` directory. Report `missing`, `changed` and `extra` before relying on the mirror.

- 查询、讨论和预览只读所需材料。已有工程从 `小说状态.yaml` / `novel-state.yaml`、`analysis-state.yaml` 或 `trend-state.yaml` 确认登记路径。使用 `小说状态.yaml` 的作品后续沿用中文目录和文件名，保留稳定 ID、章号与扩展名。
- 正式保存或续作时遵循[工件与保护约定](references/artifact-contracts.md)。新工作区若已获授权而未给位置，说明选用的 `novels/<书名>/`、`analyses/<书名>/` 或 `trends/<范围>/`。预览只有经作者选定的内容才进入正式工件。
- 保护用户编辑和已验收正文。上游改变时将受影响的未写计划标为 `stale`。Markdown / YAML 为权威材料；结构化连续性以 YAML 为准，视图和 SQLite 可重建。
- 正式生产使用 `scripts/novelctl.py` 和[生成步骤合同](references/generation-contracts.md)。书级方向、故事发动机、卷战略、结构性重规划和受保护覆盖遵循[里程碑、既有授权与恢复](references/auto-director-and-recovery.md)。`next` 指向正式生产，不改变当前试读或只读请求。

## 按任务取材料

- **新书与创意。** 明确没有想法时给恰好五条[开书种子](references/opening-seeds.md)。已有灵感、确需探索方向时给恰好两份不同的简报预览；已选方向或委托直接生产时沿用决定。没有明说“无想法”的模糊开书请求先谈频道、发布形态、题材或主要回报。其余选择按[简报与渐进确认](references/novel-brief.md)随里程碑展开。单独要书名或灵感时直接交付所求。
- **卷纲、人物与世界。** 按[故事与卷规划](references/story-and-volume-planning.md)确定当前卷职责，保留作者固定的卷数、时间线和章末结果。涉及具体世界限制或角色状态时再读[世界设定](references/world-bible.md)或[人物档案](references/character-asset-layout.md)。
- **大纲评判。** 作者要按维度评判网文架构、跑首版自动评判时，按[大纲评判 v1](references/outline-evaluation.md)取规划、逐项判断并校验报告。给出证据最充分的优点、最值得先修的位置和负责的规划环节。只问一个问题时直接回答该项。
- **试写与正式写章。** 取[章节生产](references/chapter-production.md)中对应部分。短试读只展开本场视角、能改变局面的选择、必留事实和停笔位置，细节由写手发挥。正式章节先核对本章计划、上一稳定章尾和有效写法，按章内需要安排场景。正式多章由同一写手串行完成，一章验收且已提交连续性后才计划下一章。暂停的章节预热和子代理候选流程不进入生产。
- **写法、审阅与修复。** 用[写法合同](references/style-engine.md)中的本书偏好指导表达，作者指定要某本已拆书的读感时按其中的文笔样例登记并对照，用[审校与最小修复](references/quality-and-repair.md)回看具体正文。完整章节及指定的对照修订按[中文表达修订](references/chinese-novel-humanization.md)保留有效原句和叙事余味。只有作者要求引入外部方法时才按[远端写法来源](references/remote-skill-sources.md)核验、锁定与确认。
- **连续性。** 正式生产按[上下文取舍](references/context-and-continuity.md)和[连续性账本](references/continuity-ledgers.md)核对事实。已迁移的工作区遵循[结构化连续性](references/structured-continuity-store.md)。同一版正文审校通过后才回灌。涉及跨书资产或共享正史再读[跨书资产、版本锁定与发布权限](references/cross-book-asset-graph.md)。
- **拆书与迁移。** 按[拆书分析](references/book-analysis.md)核对授权、覆盖范围和来源指纹。正式拆书先估算范围，确认透镜后分批做笔记，为结论保留证据与反例。长篇查证用[拆书检索](references/book-analysis-retrieval.md)。借机制写原创时依[原创改造](references/analysis-to-novel.md)核对证据、重建人物与因果。沿用原作人物写新故事或续写时按[同人交接](references/fanfic.md)锁定已读边界。“仿写”指向不明时先澄清是哪种创作。
- **榜单与导出。** [题材趋势](references/hot-genre-trends.md)只用公开榜单元数据或用户提供的榜单材料，两次可比快照才判断趋势。导出用 `novelctl.py export <workspace>`，默认只取与验收版本匹配、连续性已提交的正文，按章号排序。指定非默认范围或来源时先 `--dry-run`。
- **跨路线或历史工程。** 用[工作流路由](references/workflow-routing.md)定位所需里程碑。只有明确要求对照或交接其他写作系统才读[项目适配边界](references/ai-novel-writing-assistant-v2-adapter.md)。

## 交付与维护

作者要读正文就先给正文，要判断就先给判断。仅在与任务有关时说明候选文件、存疑之处或下一步。正式生产记录[实际生成用量](references/token-usage.md)、状态变更和未解决问题，供需要时查阅。确定性操作不记作创作调用。

After every functional edit to the Skill sources, run the required compile, tests and Skill quick validator, then automatically synchronize the source to the installed mirror and recheck. Never synchronize failed or unvalidated changes. Sync is additive and preserves mirror-only files. Use the relevant [behavioral regression cases](references/behavioral-regressions.md) to check the actual decision, text and files. An author's accepted workflow change belongs in the Skill and its affected reference. An individual book preference belongs in that book.
