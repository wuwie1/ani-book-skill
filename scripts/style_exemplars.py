#!/usr/bin/env python3
"""Coordinates-only style exemplar register: validate, read spans from the local source snapshot,
measure prose rhythm and check reuse. Deterministic, read-only, no model calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

import yaml

REGISTER_NAME = "style-exemplars.yaml"
SAMPLING_REGISTER_NAME = "sampling-register.yaml"
STATUSES = {"candidate", "selected", "rejected"}
DECODINGS = {"utf-8", "utf-8-sig"}
HARD_MAX_CHARS = 1200
MIN_NON_WHITESPACE = 80
MAX_EXEMPLARS = 12
MAX_NOTES = 4
MAX_NOTE_CHARS = 80
DEFAULT_OVERLAP_CHARS = 14
# A copied passage usually has its names swapped, which breaks one long run into several short ones.
# Runs this long are chained across the places where the exemplar had a name.
OVERLAP_SEED_CHARS = 4
MAX_NAME_CHARS = 12
TEXT_KEYS = {"text", "excerpt", "content", "quote", "原文"}
PLACEHOLDERS = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥"
QUOTE_PAIRS = (("“", "”"), ("「", "」"), ("『", "』"))
QUOTE_OPENERS = {opening: closing for opening, closing in QUOTE_PAIRS}
NON_CONTENT = re.compile(r"[\s\W_]+", re.UNICODE)
PLACEHOLDER_PATTERN = r"〔[^〔〕]{1,6}〕"


def fail(message: str) -> ValueError:
    return ValueError(message)


def text_value(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise fail(f"missing non-empty {label}")
    return value.strip()


def note(value: Any, label: str) -> str:
    result = text_value(value, label)
    if len(result) > MAX_NOTE_CHARS:
        raise fail(f"{label} must stay within {MAX_NOTE_CHARS} characters")
    return result


def note_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_NOTES:
        raise fail(f"{label} must list 1 to {MAX_NOTES} short notes")
    return [note(item, label) for item in value]


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise fail(f"invalid YAML: {path.name}") from exc
    if not isinstance(value, dict):
        raise fail(f"expected YAML mapping: {path.name}")
    return value


def local_file(root: Path, relative: Any, label: str) -> Path:
    relative = text_value(relative, label)
    candidate = Path(relative)
    if "\\" in relative or candidate.is_absolute() or ".." in candidate.parts:
        raise fail(f"{label} must be a workspace-relative path")
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise fail(f"{label} is missing or escapes the analysis workspace")
    return resolved


class Register:
    """A validated register plus the decoded source snapshot it points into."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.data = load_yaml(local_file(self.root, REGISTER_NAME, "register"))
        if self.data.get("schema_version") != 1:
            raise fail("unsupported style exemplar register schema")
        source = self.data.get("source")
        if not isinstance(source, dict):
            raise fail("register source metadata is missing")
        self.title = text_value(source.get("title"), "source.title")
        self.fingerprint = text_value(source.get("fingerprint"), "source.fingerprint")
        decoding = source.get("decoding")
        if decoding not in DECODINGS:
            raise fail("source.decoding must be utf-8 or utf-8-sig")
        if source.get("offset_unit") != "unicode_character" or source.get("end_exclusive") is not True:
            raise fail("spans must be half-open Unicode character offsets")
        snapshot = local_file(self.root, source.get("snapshot"), "source.snapshot")
        raw = snapshot.read_bytes()
        if f"sha256:{hashlib.sha256(raw).hexdigest()}" != self.fingerprint:
            raise fail("source snapshot changed; re-read the spans before using this register")
        state_path = self.root / "analysis-state.yaml"
        state_source = load_yaml(state_path).get("source") if state_path.is_file() else None
        if not isinstance(state_source, dict):
            state_source = {}
        if state_source.get("fingerprint") not in (None, self.fingerprint):
            raise fail("register fingerprint differs from analysis-state.yaml")
        self.text = raw.decode(decoding)
        self.read_ranges = self._read_ranges(state_source.get("coverage"))

        policy = self.data.get("policy")
        if not isinstance(policy, dict) or policy.get("text_storage") != "coordinates_only":
            raise fail("policy.text_storage must be coordinates_only")
        self.max_chars = policy.get("max_chars", HARD_MAX_CHARS)
        if type(self.max_chars) is not int or not 1 <= self.max_chars <= HARD_MAX_CHARS:
            raise fail(f"policy.max_chars must be an integer up to {HARD_MAX_CHARS}")

        self.entities = self._entities(self.data.get("source_entities", []))
        self.exemplars = self._exemplars(self.data.get("exemplars"))

    def _read_ranges(self, coverage: Any) -> list[tuple[int, int]] | None:
        """Ranges a sampled analysis has actually read, merged; None when the whole snapshot counts as read."""
        path = self.root / SAMPLING_REGISTER_NAME
        if coverage == "full" or (coverage != "sampled" and not path.is_file()):
            return None
        if not path.is_file():
            raise fail(f"a sampled analysis needs {SAMPLING_REGISTER_NAME} to show which ranges were read")
        data = load_yaml(path)
        excerpts = data.get("review_excerpts")
        items = [*(data.get("windows") or []), *((excerpts.get("excerpts") or []) if isinstance(excerpts, dict) else [])]
        ranges: list[tuple[int, int]] = []
        for item in items:
            start, end = (item.get("start"), item.get("end")) if isinstance(item, dict) else (None, None)
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(self.text):
                raise fail(f"{SAMPLING_REGISTER_NAME} has a read range without valid start and end offsets")
            ranges.append((start, end))
        if not ranges:
            raise fail(f"{SAMPLING_REGISTER_NAME} lists no read ranges")
        merged: list[tuple[int, int]] = []
        for start, end in sorted(ranges):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        return merged

    @staticmethod
    def _entities(value: Any) -> list[list[str]]:
        if not isinstance(value, list):
            raise fail("source_entities must be a list")
        groups: list[list[str]] = []
        seen: set[str] = set()
        for item in value:
            if not isinstance(item, dict):
                raise fail("each source entity needs a name")
            names = [text_value(item.get("name"), "source_entities.name")]
            aliases = item.get("aliases", [])
            if not isinstance(aliases, list):
                raise fail("source_entities.aliases must be a list")
            names += [text_value(alias, "source_entities.aliases") for alias in aliases]
            for name in names:
                if not 2 <= len(name) <= 12 or name in seen:
                    raise fail(f"source entity must be unique and 2-12 characters: {name}")
                seen.add(name)
            groups.append(names)
        return groups

    def _exemplars(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list) or not value:
            raise fail("exemplars must be a non-empty list")
        if len(value) > MAX_EXEMPLARS:
            raise fail(f"keep at most {MAX_EXEMPLARS} exemplars; a register is a short reading list")
        result: list[dict[str, Any]] = []
        ids: set[str] = set()
        for item in value:
            if not isinstance(item, dict):
                raise fail("invalid exemplar entry")
            identifier = item.get("id")
            if not isinstance(identifier, str) or not re.fullmatch(r"EX-\d{3}", identifier) or identifier in ids:
                raise fail("exemplar IDs must be unique EX-XXX identifiers")
            ids.add(identifier)
            if TEXT_KEYS & set(item):
                raise fail(f"{identifier}: store coordinates only; remove copied source text")
            if item.get("status") not in STATUSES:
                raise fail(f"{identifier}: status must be candidate, selected or rejected")
            span = item.get("span")
            if not isinstance(span, list) or len(span) != 2 or any(type(edge) is not int for edge in span):
                raise fail(f"{identifier}: span must be [start, end]")
            start, end = span
            if not 0 <= start < end <= len(self.text):
                raise fail(f"{identifier}: span is outside the source snapshot")
            if end - start > self.max_chars:
                raise fail(f"{identifier}: span has {end - start} characters, exceeds {self.max_chars}")
            if start and self.text[start - 1] != "\n":
                raise fail(f"{identifier}: span must start at a paragraph start")
            if end < len(self.text) and self.text[end - 1] != "\n" and self.text[end] not in "\r\n":
                raise fail(f"{identifier}: span must end at a paragraph end")
            if self.read_ranges is not None and not any(low <= start and end <= high for low, high in self.read_ranges):
                raise fail(f"{identifier}: span lies outside the ranges this analysis has read")
            body = self.text[start:end]
            if len("".join(body.split())) < MIN_NON_WHITESPACE:
                raise fail(f"{identifier}: span is too short to show rhythm")
            result.append({
                "id": identifier,
                "status": item["status"],
                "scene_function": note(item.get("scene_function"), f"{identifier}.scene_function"),
                "locator": text_value(item.get("locator"), f"{identifier}.locator"),
                "span": (start, end),
                "learn": note_list(item.get("learn"), f"{identifier}.learn"),
                "do_not_carry": note_list(item.get("do_not_carry"), f"{identifier}.do_not_carry"),
                "evidence": [text_value(entry, f"{identifier}.evidence") for entry in item.get("evidence") or []],
                "text": body,
            })
        ordered = sorted(result, key=lambda entry: entry["span"])
        for previous, current in zip(ordered, ordered[1:]):
            if current["span"][0] < previous["span"][1]:
                raise fail(f"{previous['id']} and {current['id']} overlap")
        return result

    def pick(self, ids: list[str] | None, include_candidates: bool, any_status: bool) -> list[dict[str, Any]]:
        """Entries for a command. Naming an entry never overrides the author's choice unless the
        command only reads locally (any_status)."""
        allowed = {"selected", "candidate"} if include_candidates else {"selected"}
        if not ids:
            return [entry for entry in self.exemplars if entry["status"] in allowed]
        known = {entry["id"]: entry for entry in self.exemplars}
        missing = [identifier for identifier in ids if identifier not in known]
        if missing:
            raise fail(f"unknown exemplar: {', '.join(missing)}")
        chosen = [known[identifier] for identifier in ids]
        refused = [f"{entry['id']} ({entry['status']})" for entry in chosen if entry["status"] not in allowed]
        if refused and not any_status:
            raise fail(f"not selected by the author: {', '.join(refused)}")
        return chosen

    def mask(self, value: str) -> str:
        """Replace registered source names with neutral placeholders, lettered in order of
        appearance; aliases share one placeholder."""
        present = [(min(value.find(name) for name in names if name in value), names)
                   for names in self.entities if any(name in value for name in names)]
        pairs: list[tuple[str, str]] = []
        for index, (_, names) in enumerate(sorted(present, key=lambda item: item[0])):
            label = PLACEHOLDERS[index] if index < len(PLACEHOLDERS) else f"人物{index + 1}"
            pairs += [(name, f"〔{label}〕") for name in names]
        for name, placeholder in sorted(pairs, key=lambda pair: -len(pair[0])):
            value = value.replace(name, placeholder)
        return value

    def flat_entities(self) -> list[str]:
        return [name for names in self.entities for name in names]


def clean_body(value: str) -> str:
    return "\n".join(line.strip() for line in value.replace("\r", "").split("\n") if line.strip())


def per_mille(count: int, total: int) -> float:
    return round(count * 1000 / total, 1) if total else 0.0


def quoted_chars(paragraph: str) -> int:
    """Characters inside the outermost quotation marks. A quote nested in speech is part of that
    speech and counts once; speech left open at the end of a paragraph runs to its end."""
    total = 0
    closers: list[str] = []
    for char in "".join(paragraph.split()):
        if closers and char == closers[-1]:
            closers.pop()
            if closers:
                total += 1
        elif char in QUOTE_OPENERS:
            if closers:
                total += 1
            closers.append(QUOTE_OPENERS[char])
        elif closers:
            total += 1
    return total


def measure(value: str) -> dict[str, Any]:
    """Observed rhythm figures. They describe a text; they are not thresholds to write towards."""
    paragraphs = [line.strip() for line in value.replace("\r", "").split("\n") if line.strip()]
    visible = "".join("".join(paragraph.split()) for paragraph in paragraphs)
    total = len(visible)
    lengths = [len("".join(paragraph.split())) for paragraph in paragraphs]
    quoted = sum(quoted_chars(paragraph) for paragraph in paragraphs)
    sentences = [len(part) for part in re.split(r"[。！？!?…]+", visible) if part]
    openers = tuple(opening for opening, _ in QUOTE_PAIRS)
    return {
        "measurement": "observation_only",
        "non_whitespace_chars": total,
        "paragraphs": len(paragraphs),
        "paragraph_chars_median": statistics.median(lengths) if lengths else 0,
        "short_paragraph_ratio": round(sum(length <= 15 for length in lengths) / len(lengths), 2) if lengths else 0,
        "long_paragraph_ratio": round(sum(length > 120 for length in lengths) / len(lengths), 2) if lengths else 0,
        "sentence_chars_median": statistics.median(sentences) if sentences else 0,
        "dialogue_char_ratio": round(quoted / total, 2) if total else 0,
        "dialogue_paragraph_ratio": round(sum(p.startswith(openers) for p in paragraphs) / len(paragraphs), 2) if paragraphs else 0,
        "exclamation_per_mille": per_mille(len(re.findall(r"[！!]", visible)), total),
        "question_per_mille": per_mille(len(re.findall(r"[？?]", visible)), total),
        "ellipsis_per_mille": per_mille(len(re.findall(r"…+", visible)), total),
        "dash_per_mille": per_mille(len(re.findall(r"—+", visible)), total),
    }


def normalize(value: str) -> str:
    return NON_CONTENT.sub("", value)


def without_names(value: str, names: list[str]) -> tuple[str, set[int]]:
    """Content characters with source names and their placeholders taken out, and the offsets
    where one stood. A writer sees placeholders and writes other names there."""
    pattern = "|".join([PLACEHOLDER_PATTERN, *(re.escape(name) for name in sorted(names, key=len, reverse=True))])
    content, joints = "", set()
    for index, part in enumerate(re.split(pattern, value)):
        if index:
            joints.add(len(content))
        content += normalize(part)
    return content, joints


def continues_across_name(source: str, joints: set[int], head: str, tail: str) -> bool:
    position = source.find(head + tail)
    while position != -1:
        if position + len(head) in joints:
            return True
        position = source.find(head + tail, position + 1)
    return False


def find_overlaps(candidate: str, exemplars: list[dict[str, Any]], min_chars: int,
                  names: list[str] | None = None) -> list[dict[str, Any]]:
    """Report passages the candidate shares with an exemplar: at least min_chars content characters
    in a row, or in pieces that are only interrupted where the exemplar had a name."""
    if min_chars < 8:
        raise fail("overlap threshold below 8 characters only reports ordinary phrases")
    content = normalize(candidate)
    findings: list[dict[str, Any]] = []
    for entry in exemplars:
        source, joints = without_names(entry["text"], names or [])
        grams = {source[index:index + OVERLAP_SEED_CHARS] for index in range(len(source) - OVERLAP_SEED_CHARS + 1)}
        pieces: list[str] = []
        last_end = 0

        def close() -> None:
            shared = sum(len(piece) for piece in pieces)
            if shared >= min_chars:
                findings.append({"exemplar": entry["id"], "shared_chars": shared, "shared": "…".join(pieces)[:60]})

        index = 0
        while index <= len(content) - OVERLAP_SEED_CHARS:
            if content[index:index + OVERLAP_SEED_CHARS] not in grams:
                index += 1
                continue
            end = index + OVERLAP_SEED_CHARS
            while end < len(content) and content[index:end + 1] in source:
                end += 1
            piece = content[index:end]
            if not (pieces and index - last_end <= MAX_NAME_CHARS
                    and continues_across_name(source, joints, "".join(pieces), piece)):
                close()
                pieces = []
            pieces.append(piece)
            index = last_end = end
        close()
    return findings


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def describe(register: Register, entry: dict[str, Any]) -> dict[str, Any]:
    start, end = entry["span"]
    return {
        "id": entry["id"], "status": entry["status"], "scene_function": entry["scene_function"],
        "locator": entry["locator"], "span": [start, end], "chars": end - start,
        "non_whitespace_chars": len("".join(entry["text"].split())),
    }


def export_entry(register: Register, entry: dict[str, Any]) -> dict[str, Any]:
    start, end = entry["span"]
    return {
        "id": entry["id"],
        "sceneFunction": entry["scene_function"],
        "text": register.mask(clean_body(entry["text"])),
        "learn": entry["learn"],
        "doNotCarry": entry["do_not_carry"],
        "sourceRef": f"《{register.title}》{entry['locator']} [{start},{end}) {register.fingerprint}",
        "enabled": True,
    }


def run(args: argparse.Namespace) -> tuple[Any, int]:
    if args.command == "metrics" and not args.analysis:
        return {"text": measure(read_text_file(args.text_file))}, 0
    register = Register(args.analysis)
    if args.command == "validate":
        return {"valid": True, "source": register.fingerprint, "policy": "coordinates_only",
                "exemplars": [describe(register, entry) for entry in register.exemplars]}, 0
    chosen = register.pick(getattr(args, "id", None), getattr(args, "include_candidates", False),
                           any_status=args.command in {"show", "metrics", "overlap"})
    if not chosen:
        raise fail("no selected exemplars; mark entries selected or pass --include-candidates")
    if args.command == "show":
        blocks = [f"## {entry['id']} · {entry['scene_function']}（{entry['locator']}）\n\n"
                  + (clean_body(entry["text"]) if args.raw else register.mask(clean_body(entry["text"])))
                  for entry in chosen]
        return "\n\n".join(blocks), 0
    if args.command == "metrics":
        result: dict[str, Any] = {"exemplars": measure("\n".join(entry["text"] for entry in chosen)),
                                  "exemplar_ids": [entry["id"] for entry in chosen]}
        if args.text_file:
            result["text"] = measure(read_text_file(args.text_file))
        return result, 0
    if args.command == "export":
        return {"schemaVersion": 1, "source": {"title": register.title, "fingerprint": register.fingerprint},
                "sourceEntities": register.flat_entities(),
                "exemplars": [export_entry(register, entry) for entry in chosen]}, 0
    findings = find_overlaps(read_text_file(args.text_file), chosen, args.min_chars, register.flat_entities())
    return {"clean": not findings, "min_chars": args.min_chars, "overlaps": findings}, 1 if findings else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="check the register against the source snapshot").add_argument("analysis", type=Path)
    for name, summary in (("show", "print exemplar text read from the local snapshot"),
                          ("export", "print exemplars as JSON for a writing system")):
        sub = commands.add_parser(name, help=summary)
        sub.add_argument("analysis", type=Path)
        sub.add_argument("--id", action="append")
        sub.add_argument("--include-candidates", action="store_true")
        if name == "show":
            sub.add_argument("--raw", action="store_true", help="keep source names instead of placeholders")
    metrics = commands.add_parser("metrics", help="observe rhythm of exemplars and/or a text file")
    metrics.add_argument("--analysis", type=Path)
    metrics.add_argument("--id", action="append")
    metrics.add_argument("--include-candidates", action="store_true")
    metrics.add_argument("--text-file", type=Path)
    overlap = commands.add_parser("overlap", help="find passages a text shares with the exemplars")
    overlap.add_argument("analysis", type=Path)
    overlap.add_argument("--text-file", type=Path, required=True)
    overlap.add_argument("--id", action="append")
    overlap.add_argument("--include-candidates", action="store_true")
    overlap.add_argument("--min-chars", type=int, default=DEFAULT_OVERLAP_CHARS)
    args = parser.parse_args()
    try:
        if args.command == "metrics" and not args.analysis and not args.text_file:
            raise fail("metrics needs --analysis, --text-file or both")
        result, code = run(args)
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        print(f"style exemplar error: {exc}", file=sys.stderr)
        return 2
    print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
