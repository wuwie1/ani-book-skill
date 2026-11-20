from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import analysis_reference
import asset_graph
import continuity_store
import novelctl as ctl
import skill_sources
import token_usage


class ChineseWorkspaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.book = Path(temporary.name) / "测试小说"
        self.command("init", "--title", "测试小说", "--mode", "auto", "--filename-language", "zh")

    def command(self, name, *arguments):
        parsed = ctl.build_parser().parse_args([name, str(self.book), *arguments])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(parsed.handler(parsed), 0)
        return output.getvalue()

    def test_chapter_context_approval_export_and_usage(self):
        self.assertTrue((self.book / "小说状态.yaml").is_file())
        self.assertFalse((self.book / "novel-state.yaml").exists())
        state = ctl.read_state(self.book)
        self.assertEqual(state["artifacts"]["volume_01_beat_sheet"]["path"], "分卷/第01卷-节奏表.md")
        state["opening_choices"]["status"] = "legacy_migrated"
        state["artifacts"]["novel_brief"]["path"] = "本书定位.md"
        for item in state["artifacts"].values():
            path = self.book / item["path"]
            path.write_text("已确认的资料。", encoding="utf-8")
            item.update(status="ready", sha256=ctl.file_sha256(path))
        ctl.atomic_write_state(self.book, state)
        (self.book / "写作风格.md").write_text("写清楚谁在说话。", encoding="utf-8")
        self.command("reconcile")

        for step, filename, expected in (
            ("chapter_plan", "plan.md", "章节计划.md"),
            ("context_package", "context-package.md", "上下文包.md"),
            ("chapter_draft", "draft.md", "正文初稿.md"),
            ("humanization_revision", "draft-humanized.md", "正文修订稿.md"),
            ("chapter_review", "review.md", "审校记录.md"),
            ("continuity_update", "delta.md", "连续性变更.md"),
        ):
            legacy = f"chapters/chapter-001/{filename}"
            args = ["--step", step, "--target", "chapter_001", "--artifact", legacy]
            relative = json.loads(self.command("start-step", *args))["artifact"]
            self.assertEqual(relative, f"章节/第001章/{expected}")
            path = self.book / relative
            path.parent.mkdir(exist_ok=True)
            if step == "context_package":
                report = json.loads(self.command("context", "--chapter", "1", "--output", legacy))
                self.assertEqual(report["written"], relative)
                self.assertIn("本书定位.md", report["sources"])
                self.assertIn("写作风格.md", report["sources"])
            else:
                path.write_text(f"# 第1章\n\n{expected}。", encoding="utf-8")
            if step == "chapter_review":
                args += ["--review-decision", "accepted"]
            self.command("finish-step", *args, "--measurement", "unavailable", "--reason", "test")
        self.assertEqual(json.loads(self.command("validate"))["warnings"], [])
        state = ctl.read_state(self.book)
        self.assertTrue(state["artifacts"]["chapter_001_humanized"]["protected"])
        self.assertEqual(state["usage"]["ledger_path"], "创作记录/用量明细.jsonl")
        self.assertTrue((self.book / "创作记录/用量汇总.json").is_file())
        records, errors = token_usage.read_records(self.book)
        self.assertEqual(errors, [])
        self.assertTrue(all((self.book / record["artifact"]).is_file() for record in records))
        subprocess.run([sys.executable, str(SCRIPTS / "novelctl.py"), "export", str(self.book)],
                       capture_output=True, check=True)
        exported = list((self.book / "导出").glob("*.txt"))
        self.assertEqual(len(exported), 1)
        self.assertIn("正文修订稿.md。", exported[0].read_text(encoding="utf-8-sig"))
        with self.assertRaisesRegex(ValueError, "中文名称"):
            self.command("context", "--chapter", "1", "--output", "english-only.md")
        self.assertFalse((self.book / "chapters").exists())
        self.assertFalse((self.book / "production").exists())

    def test_continuity_and_optional_sources_follow_the_same_layout(self):
        state = ctl.read_state(self.book)
        state["continuity"].update(baseline_chapter="chapter_001", last_committed_chapter="chapter_001")
        ctl.atomic_write_state(self.book, state)
        ledgers = self.book / "连续性"
        (ledgers / "基线.md").write_text("# 基线\n\n- 基线章节：`chapter-001`\n", encoding="utf-8")
        for name, field in (("事实账本", "稳定事实"), ("伏笔账本", "承诺/伏笔"), ("资源账本", "资源")):
            (ledgers / f"{name}.md").write_text(f"| ID | {field} |\n| --- | --- |\n", encoding="utf-8")
        continuity_store.migrate_workspace(self.book)
        store = ctl.read_state(self.book)["continuity"]["structured_store"]
        self.assertEqual(store["path"], "连续性/数据")
        self.assertEqual(store["index_path"], "连续性/索引.sqlite3")
        self.assertTrue((self.book / "连续性/数据/检查点/第001章-检查点.yaml").is_file())
        subprocess.run([sys.executable, str(SCRIPTS / "check_continuity_workspace.py"), str(self.book)],
                       capture_output=True, check=True)
        selection = asset_graph.default_selection_path(self.book, 1)
        self.assertEqual(selection, self.book / "上下文/第001章-素材选择.yaml")
        selection.write_text(yaml.safe_dump({"schema_version": 1, "chapter": "chapter-001", "assets": []}), encoding="utf-8")
        self.assertEqual(asset_graph.validate_asset_selection(self.book, selection)["assets"], [])
        self.assertEqual(analysis_reference.selection_path(self.book, 2), self.book / "上下文/第002章-拆书参考.yaml")
        self.assertEqual(skill_sources.config_path(self.book), self.book / "创作记录/技能来源.yaml")
