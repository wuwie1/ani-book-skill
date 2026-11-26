# Repository Guidance

## 对话约定

- “web 系统”指本地项目 `/Users/likai/go/src/write/assistant`。
- “服务器服务”指该项目通过 `make ssh_server` 连接的远端 Web 和 API 服务。SSH 地址为 `root@152.136.155.200`，服务部署目录为 `/data/write/AI-Novel-Writing-Assistant`。
- 部署及重启参考该项目的 `make server_update`。排查问题时，可在远端部署目录查看 `logs/server.log` 和 `logs/nginx-error.log`。

## Product Boundary

- Keep this repository a Codex-native Skill project. Codex is the only creative generation and judgment engine; do not add model-provider SDKs, a web API, a database authority, or a custom agent runtime.
- Exception: `apps/workspace-reader` is an optional, isolated React/Fumadocs reader authorized to read explicitly configured local novel and analysis workspaces. Its loopback Node service may provide read-only pages, assets and local search; it must never invoke a model provider, call `novelctl`, write authoritative artifacts or become a required Skill runtime dependency.
- This repository is driven by Codex itself, not by `AI-Novel-Writing-Assistant`; that project may be read only for ideas and is never a runtime, submodule, or production dependency.
- Treat Skills as process contracts. Keep Python limited to deterministic state, validation, indexes, conflict detection, and export; provider/model metadata is diagnostics only when the Codex host exposes it.
- Treat `SKILL.md`, `references/`, deterministic scripts, and local Markdown/YAML workspaces as the product surface.
- Use `D:\code\AI-Novel-Writing-Assistant-v2` only as a read-only source of production ideas. Never create a runtime dependency on it.

## 跨项目协作中的大纲评判

| 职责 | 输入与交付 |
| --- | --- |
| 拆书分析 | 从已覆盖的参考文本提炼机制、反例和适用条件，保留证据位置。原创评判可用机制帮助提问，得分须由目标书自己的规划支持。 |
| 原创规划 | 维护简报、故事主线、人物与世界、分卷和章纲。收到评判后，按作者选定或委托的范围修订对应材料，复核受影响的卷章。 |
| 大纲评判 | Codex 依[大纲评判 v1](references/outline-evaluation.md)判断目标读者会期待什么、规划怎样兑现。Python 固定输入版本、核对引文、汇总分项。交付评判记录和优先修订位置，采纳决定归规划端和作者。 |
| 跨仓交接 | `autocommand` 记录已选的本地规划、评判范围和 Web 采用的修订。`assistant` 在对应小说生成、保存和审校正文。查到规划已有约定而正文遗漏时，由 Web 核对绑定与章节任务。 |

## Data Safety

- Use Chinese directory and file names for all future work in `novels/我在异界打天下/`. Follow the examples in its `作品导览.md` and the paths in `小说状态.yaml`. Keep chapter numbers, stable IDs and standard file extensions.
- Treat user-edited artifacts and accepted prose as protected. Mark dependent unwritten artifacts `stale`; never rewrite protected content to repair state.
- Keep YAML and accepted Markdown authoritative. SQLite, summaries, rendered ledgers, and exports are rebuildable derivatives.
- Back up `novel-state.yaml` before schema migration and use atomic replacement for state writes.

## Development

- Use Python 3.10 or newer and UTF-8 explicitly.
- Add or update tests for every deterministic workflow change.
- Run `python -m compileall -q scripts`, `python -m unittest discover -s tests -v`, and the Skill quick validator (`python -X utf8 <skill-creator>/scripts/quick_validate.py .` on Windows) before completion.
- For this checked-out project, treat the repository root as the editable Skill source. Resolve the local installed mirror from `$env:CODEX_HOME\skills\produce-long-form-novel`; when `CODEX_HOME` is unset, use `<UserProfile>\.codex\skills\produce-long-form-novel`. Do not hardcode a user-specific absolute path.
- On the first Skill run in a task, compare the repository root with the resolved installed mirror using `python scripts/sync_skill_mirror.py check <repository-root> <installed-skill-directory>`. Report `missing` or `changed` results as an explicit maintenance finding before creative or stateful production.
- After every functional edit to `SKILL.md`, `references/`, `scripts/`, `assets/`, `requirements.txt`, or `agents/`, run compile, tests, and the Skill quick validator; when all pass, automatically run `python scripts/sync_skill_mirror.py sync <repository-root> <installed-skill-directory>` and rerun `check`. This standing authorization applies without asking again.
- Never sync failed or unvalidated functional changes. Synchronization is additive and must preserve mirror-only files.
