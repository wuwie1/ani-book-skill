"""Pin outline inputs and verify Codex's evidence-backed planning review."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


RUBRIC = "outline-v1"
DIMENSIONS = (
    "卖点与读者承诺",
    "开篇牵引与首次兑现",
    "故事发动机与冲突升级",
    "人物选择与关系变化",
    "世界规则与代价",
    "期待管理与阶段回报",
    "分卷递进与终局",
)
BOOK_SOURCES = ("novel_brief", "story_bible", "world_bible", "character_roster", "volume_strategy")
VOLUME_SOURCE = re.compile(r"volume_(\d+)_(skeleton|beat_sheet|opening_outline|chapter_outline)")


def planning_keys(artifacts: dict, volume: int) -> list[str]:
    keys = list(BOOK_SOURCES)
    volume_slots = set()
    beat_volumes = {int(m[1]) for key in artifacts if (m := re.fullmatch(r"volume_(\d+)_beat_sheet", key))}
    for key, item in artifacts.items():
        match = VOLUME_SOURCE.fullmatch(key)
        if match and int(match[1]) == volume:
            keys.append(key)
            volume_slots.add(match[2])
        elif key == "opening_window" and volume == 1:
            keys.append(key)
        elif key == "character_profiles" or (
            key.startswith("character_") and isinstance(item, dict)
            and Path(str(item.get("path", ""))).parent.name in {"profiles", "档案"}
        ):
            keys.append(key)
        elif re.fullmatch(r"chapter_\d+_plan", key) and isinstance(item, dict):
            # Formal plans can record the volume directly or through its beat sheet.
            dependencies = item.get("depends_on") or []
            owners = {int(m[1]) for dep in dependencies
                      if (m := re.fullmatch(r"volume_(\d+)_beat_sheet", dep))}
            owner = item.get("volume")
            if owner is None:
                # Match novelctl's legacy inference only when there is a single possible volume.
                belongs = (owners or beat_volumes or {1}) == {volume}
            else:
                belongs = str(owner).isdecimal() and int(owner) == volume
            if belongs:
                keys.append(key)
    for slot in ("skeleton", "beat_sheet", "chapter_outline"):
        if slot not in volume_slots:
            keys.append(f"volume_{volume:02d}_{slot}")
    return list(dict.fromkeys(keys))


def read_source(workspace: Path, item: dict) -> tuple[dict, list[str]]:
    raw = item.get("path")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("规划材料缺少登记路径")
    relative = Path(raw)
    path = (workspace / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(workspace):
        raise ValueError(f"规划材料超出作品目录：{raw}")
    source = {"path": raw, "status": item.get("status", "missing")}
    if source["status"] != "ready":
        return source, []
    if not path.is_file():
        return {**source, "status": "missing"}, []
    data = path.read_bytes()
    source["sha256"] = hashlib.sha256(data).hexdigest()
    registered = item.get("sha256")
    if registered and registered != source["sha256"]:
        source.update(status="working_copy", registered_sha256=registered)
    return source, data.decode("utf-8-sig").splitlines()


def prepare(workspace: Path, state: dict, volume: int) -> tuple[dict, dict[str, list[str]]]:
    if type(volume) is not int or volume < 1:
        raise ValueError("卷号必须为正整数")
    workspace = workspace.resolve()
    artifacts = state.get("artifacts", {})
    if not isinstance(artifacts, dict):
        raise ValueError("artifacts 必须是映射")
    sources, lines = {}, {}
    for key in planning_keys(artifacts, volume):
        if key not in artifacts:
            sources[key] = {"status": "unregistered"}
            continue
        if not isinstance(artifacts[key], dict):
            raise ValueError(f"{key} 登记格式有误")
        sources[key], lines[key] = read_source(workspace, artifacts[key])
    choices = state.get("opening_choices") or {}
    packet = {
        "rubric": RUBRIC,
        "book": state.get("novel", {}).get("title") or workspace.name,
        "volume": volume,
        "opening_choices": {key: choices[key] for key in
                            ("status", "channel", "publication_format", "primary_reader_reward") if key in choices},
        "sources": sources,
    }
    return packet, lines


def review_form(packet: dict) -> dict:
    return {
        **packet,
        "judge": {"host": "Codex", "model": None, "context": "unknown"},
        "ratings": {
            name: {"score": None, "evidence": [], "reason": "", "next_step": ""}
            for name in DIMENSIONS
        },
    }


def verify_evidence(evidence: Any, lines: dict[str, list[str]], name: str) -> None:
    if not isinstance(evidence, dict):
        raise ValueError(f"{name} 的证据应含 source、line 和 quote")
    source, line, quote = (evidence.get(field) for field in ("source", "line", "quote"))
    content = lines.get(source, []) if isinstance(source, str) else []
    if (type(line) is not int or not 1 <= line <= len(content)
            or not isinstance(quote, str) or not quote.strip() or quote not in content[line - 1]):
        raise ValueError(f"{name} 引文与规划原文不符：{source} 行 {line}")


def verify_review(packet: dict, lines: dict[str, list[str]], review: Any) -> dict:
    if not isinstance(review, dict) or any(review.get(k) != v for k, v in packet.items()):
        raise ValueError("量表、作品、卷号、读者定位或材料版本已变动，请重新取材评判")
    judge = review.get("judge")
    if (not isinstance(judge, dict) or judge.get("host") != "Codex" or "model" not in judge
            or judge.get("context") not in ("shared", "separate", "unknown")):
        raise ValueError("请记录本次 Codex 裁判及其与规划者的上下文关系")
    if judge["model"] is not None and (not isinstance(judge["model"], str) or not judge["model"].strip()):
        raise ValueError("裁判模型应填实际型号，宿主未提供时填 null")
    ratings = review.get("ratings")
    if not isinstance(ratings, dict) or set(ratings) != set(DIMENSIONS):
        raise ValueError("评判记录需要包含 v1 全部七个维度")
    scores, missing = {}, []
    for name in DIMENSIONS:
        item = ratings[name]
        if not isinstance(item, dict) or not {"score", "evidence", "reason", "next_step"} <= item.keys():
            raise ValueError(f"{name} 缺少评判字段")
        score, evidence = item["score"], item["evidence"]
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            raise ValueError(f"{name} 需要判断理由或缺少的材料")
        if score is not None and (type(score) is not int or not 1 <= score <= 5):
            raise ValueError(f"{name} 的分数应为 1–5 的整数或 null")
        if not isinstance(evidence, list) or (score is not None and not evidence):
            raise ValueError(f"{name} 的分数需要规划原文证据")
        for entry in evidence:
            verify_evidence(entry, lines, name)
        action = item["next_step"]
        if not isinstance(action, str) or ((score is None or score <= 3) and not action.strip()):
            raise ValueError(f"{name} 需要可定位的修订或补证建议")
        if score is None:
            missing.append(name)
        else:
            scores[name] = score
    summary = {
        "scored": len(scores),
        "total": len(DIMENSIONS),
        "mean": None if missing else round(sum(scores.values()) / len(DIMENSIONS), 2),
        "needs_evidence": missing,
        "revise_first": sorted((name for name in scores if scores[name] <= 3), key=scores.get),
    }
    return {**packet, "judge": judge, "ratings": ratings, "summary": summary}
