from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import novelctl
import outline_evaluation as evaluation


class OutlineEvaluationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.book = Path(temp.name)
        self.plan = self.book / "首卷.md"
        self.plan.write_text("# 船期\n她把夜航留给了产妇。\n", encoding="utf-8-sig")
        self.source = {"path": self.plan.name, "status": "ready"}
        self.state = {"schema_version": 1, "novel": {"title": "渡口"}, "artifacts": {
            "volume_01_skeleton": self.source,
            "volume_02_skeleton": {"path": "下卷.md", "status": "missing"},
            "chapter_012_plan": {**self.source, "depends_on": ["volume_01_beat_sheet"]},
            "chapter_099_plan": {**self.source, "volume": 2},
            "chapter_012_draft": {"path": "../正文.md", "status": "ready"},
            "volume_01_outline_review": {"path": "../旧分数.md", "status": "ready"},
            "opening_window": self.source,
        }}
        self.state_file = self.book / "小说状态.yaml"
        self.state_file.write_text(yaml.safe_dump(self.state, allow_unicode=True), encoding="utf-8")
        self.packet, self.lines = evaluation.prepare(self.book, self.state, 1)
        form = evaluation.review_form(self.packet)
        self.evidence = {"source": "volume_01_skeleton", "line": 2, "quote": "夜航留给了产妇"}
        for item in form["ratings"].values():
            item.update(score=4, evidence=[self.evidence], reason="让出船期使下一次派船受限。")
        self.review = form

    def command(self, *args):
        parsed = novelctl.build_parser().parse_args(["outline-review", str(self.book), *args])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(parsed.handler(parsed), 0)
        return output.getvalue()

    def test_registered_scope_excludes_prose_and_reviews_in_both_naming_conventions(self):
        original = self.state_file.read_bytes()
        result = json.loads(self.command())
        self.assertIn("chapter_012_plan", result["sources"])
        for key in ("volume_02_skeleton", "chapter_099_plan", "chapter_012_draft", "volume_01_outline_review"):
            self.assertNotIn(key, result["sources"])
        self.assertEqual("unregistered", result["sources"]["novel_brief"]["status"])
        self.assertEqual("unregistered", result["sources"]["volume_01_beat_sheet"]["status"])
        self.assertEqual(original, self.state_file.read_bytes())
        self.state_file.rename(self.book / "novel-state.yaml")
        second = json.loads(self.command("--volume", "2"))
        self.assertIn("chapter_099_plan", second["sources"])
        self.assertNotIn("opening_window", second["sources"])
        self.assertNotIn("chapter_012_plan", second["sources"])

    def test_completed_report_unknown_coverage_and_protected_output(self):
        first = evaluation.DIMENSIONS[0]
        self.review["judge"].update(model="test-judge", context="separate")
        self.review["ratings"][first].update(score=2, next_step="在简报补上女船主想守住的船期。")
        path = self.book / "判读.json"
        path.write_text(json.dumps(self.review, ensure_ascii=False), encoding="utf-8")
        result = json.loads(self.command("--review", str(path)))
        self.assertEqual(result["judge"], self.review["judge"])
        self.assertEqual(result["summary"]["mean"], 3.71)
        self.assertEqual(result["summary"]["revise_first"], [first])
        self.review["ratings"][first].update(score=None, evidence=[], reason="缺少目标读者简报。")
        partial = evaluation.verify_review(self.packet, self.lines, self.review)["summary"]
        self.assertEqual(partial["scored"], 6)
        self.assertEqual(partial["needs_evidence"], [first])
        self.assertIsNone(partial["mean"])
        stored = path.read_bytes()
        with self.assertRaises(FileExistsError):
            self.command("--output", str(path))
        self.assertEqual(stored, path.read_bytes())

    def test_validates_scores_sources_and_exact_one_based_anchors(self):
        for patch in (
            {"score": 0}, {"score": True}, {"score": 6}, {"score": 3, "next_step": ""},
            {"reason": ""}, {"evidence": []},
            {"evidence": [{**self.evidence, "line": 1}]},
            {"evidence": [{**self.evidence, "line": 0}]},
            {"evidence": [{**self.evidence, "quote": "并未在稿中出现"}]},
            {"evidence": [{**self.evidence, "source": "chapter_012_draft"}]},
        ):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                review = copy.deepcopy(self.review)
                review["ratings"][evaluation.DIMENSIONS[0]].update(patch)
                evaluation.verify_review(self.packet, self.lines, review)
        del self.review["ratings"][evaluation.DIMENSIONS[-1]]
        with self.assertRaisesRegex(ValueError, "七个"):
            evaluation.verify_review(self.packet, self.lines, self.review)

    def test_rechecks_fingerprints_and_status_without_promoting_changed_plans(self):
        old = self.packet["sources"]["volume_01_skeleton"]["sha256"]
        self.source["sha256"] = old
        self.plan.write_text("她保留了头班船。", encoding="utf-8")
        packet, lines = evaluation.prepare(self.book, self.state, 1)
        self.assertEqual(packet["sources"]["volume_01_skeleton"]["status"], "working_copy")
        self.assertEqual(packet["sources"]["volume_01_skeleton"]["registered_sha256"], old)
        with self.assertRaisesRegex(ValueError, "版本"):
            evaluation.verify_review(packet, lines, self.review)
        self.source["status"] = "stale"
        packet, lines = evaluation.prepare(self.book, self.state, 1)
        self.assertEqual(lines["volume_01_skeleton"], [])
        self.assertEqual(packet["sources"]["volume_01_skeleton"]["status"], "stale")

    def test_rejects_invalid_scope_and_paths_outside_workspace(self):
        with self.assertRaisesRegex(ValueError, "正整数"):
            self.command("--volume", "0")
        self.source["path"] = "../越界.md"
        with self.assertRaisesRegex(ValueError, "超出"):
            evaluation.prepare(self.book, self.state, 1)
        outside = self.book / "linked"
        try:
            outside.symlink_to(self.book.parent, target_is_directory=True)
        except OSError:
            self.skipTest("symbolic links are unavailable on this filesystem")
        self.source["path"] = "linked/越界.md"
        with self.assertRaisesRegex(ValueError, "超出"):
            evaluation.prepare(self.book, self.state, 1)


if __name__ == "__main__":
    unittest.main()
