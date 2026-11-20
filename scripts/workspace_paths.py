"""Resolve the Skill's standard artifact paths in a novel's naming convention."""

from __future__ import annotations

import re
from pathlib import Path


CHINESE_STATE = "小说状态.yaml"
CHINESE_NAMES = {
    "novel-state.yaml": CHINESE_STATE,
    "README.md": "作品导览.md",
    "novel-brief.md": "新书简报.md",
    "story-bible.md": "故事主线.md",
    "world-bible.md": "世界设定.md",
    "writing-style.md": "写作风格.md",
    "fanfic-handoff.md": "同人创作交接.md",
    "characters": "人物",
    "character-roster.md": "人物总览.md",
    "profiles": "档案",
    "volumes": "分卷",
    "volume-strategy.md": "分卷规划.md",
    "chapters": "章节",
    "plan.md": "章节计划.md",
    "context-package.md": "上下文包.md",
    "context.md": "上下文包.md",
    "draft.md": "正文初稿.md",
    "draft-humanized.md": "正文修订稿.md",
    "repair.md": "正文返修稿.md",
    "delta.md": "连续性变更.md",
    "review.md": "审校记录.md",
    "context-packages": "上下文",
    "production": "创作记录",
    "revisions": "修订存档",
    "recovery.md": "恢复记录.md",
    "quality-debt.md": "待修问题.md",
    "token-usage.jsonl": "用量明细.jsonl",
    "token-summary.json": "用量汇总.json",
    "skill-sources.yaml": "技能来源.yaml",
    "remote-skill-candidates": "候选技能",
    "asset-candidates": "候选素材",
    "cross-book-assets": "跨书素材",
    "exports": "导出",
    "continuity": "连续性",
    "chapter-deltas": "分章变更",
    "legacy-markdown": "原账本备份",
    "baseline.md": "基线.md",
    "fact-ledger.md": "事实账本.md",
    "payoff-ledger.md": "伏笔账本.md",
    "resource-ledger.md": "资源账本.md",
    "data": "数据",
    "baseline.yaml": "基线.yaml",
    "manifest.yaml": "清单.yaml",
    "facts.yaml": "事实.yaml",
    "payoffs.yaml": "伏笔.yaml",
    "resources.yaml": "资源.yaml",
    "character-state.yaml": "人物状态.yaml",
    "relationships.yaml": "人物关系.yaml",
    "asset-links.yaml": "素材关联.yaml",
    "checkpoints": "检查点",
    "index.sqlite3": "索引.sqlite3",
    "graph": "关系图",
    "nodes.jsonl": "节点.jsonl",
    "edges.jsonl": "连线.jsonl",
    "asset-graph-index.sqlite3": "素材关系索引.sqlite3",
}
VOLUME_FILES = {
    "": "卷纲", "-beat-sheet": "节奏表", "-chapter-outline": "逐章细纲",
    "-opening-outline": "开篇细纲", "-outline-review": "细纲审查",
}
CHAPTER_FILES = {
    "": "", ".md": ".md", ".assets.yaml": "-素材选择.yaml",
    ".references.yaml": "-拆书参考.yaml",
}


def chinese_name(name: str) -> str:
    """Translate a standard path component, retaining numbers and custom names."""
    if name in CHINESE_NAMES:
        return CHINESE_NAMES[name]
    chapter = re.fullmatch(r"chapter-(\d+)(.*)", name)
    if chapter and chapter[2] in CHAPTER_FILES:
        return f"第{chapter[1]}章{CHAPTER_FILES[chapter[2]]}"
    volume = re.fullmatch(r"volume-(\d+)(.*?)\.md", name)
    if volume and volume[2] in VOLUME_FILES:
        return f"第{volume[1]}卷-{VOLUME_FILES[volume[2]]}.md"
    checkpoint = re.fullmatch(r"checkpoint-(\d+)\.yaml", name)
    if checkpoint:
        return f"第{checkpoint[1]}章-检查点.yaml"
    return name


def chinese_relative(relative: str | Path) -> Path:
    return Path(*(chinese_name(part) for part in Path(relative).parts))


def uses_chinese_names(workspace: Path) -> bool:
    return (workspace / CHINESE_STATE).is_file()


def book_path(workspace: Path, relative: str | Path) -> Path:
    return workspace / (chinese_relative(relative) if uses_chinese_names(workspace) else relative)
