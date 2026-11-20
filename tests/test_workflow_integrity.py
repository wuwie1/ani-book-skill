from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import novelctl as ctl


class WorkflowIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "novel"
        ctl.ensure_workspace_directories(self.workspace)
        state = ctl.initial_state("验证小说", "auto")
        state["opening_choices"] = {"status": "confirmed", "channel": "泛读者", "publication_format": "免费", "primary_reader_reward": "解谜"}
        for key, item in state["artifacts"].items():
            self.ready_file(item, f"# {key}\n已确认。")
        state["next_action"] = ctl.decide_next(state)
        ctl.atomic_write_state(self.workspace, state)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def ready_file(self, item: dict, text: str = "已确认。") -> None:
        path = self.workspace / item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        item.update(status="ready", approval="not_required", sha256=ctl.file_sha256(path))

    def command(self, name: str, *args: str) -> str:
        parsed = ctl.build_parser().parse_args([name, str(self.workspace), *args])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(0, parsed.handler(parsed))
        return out.getvalue()

    def step(self, step: str, filename: str, decision: str | None = None) -> None:
        relative = "chapters/chapter-001/" + filename
        self.command("start-step", "--step", step, "--target", "chapter_001", "--artifact", relative)
        path = self.workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {filename}\n场景原版本。", encoding="utf-8")
        args = ["--step", step, "--target", "chapter_001", "--artifact", relative,
                "--measurement", "unavailable", "--reason", "runtime_usage_not_exposed"]
        if decision:
            args += ["--review-decision", decision]
        self.command("finish-step", *args)

    def prepare_prose(self, review: str | None = "accepted") -> None:
        for step, name in (("chapter_plan", "plan.md"), ("context_package", "context.md"),
                           ("chapter_draft", "draft.md"), ("humanization_revision", "draft-humanized.md")):
            self.step(step, name)
        if review:
            self.step("chapter_review", "review.md", review)

    def test_accepted_prose_is_protected_and_approved_revision_invalidates_review(self) -> None:
        self.prepare_prose()
        state = ctl.read_state(self.workspace)
        self.assertTrue(state["artifacts"]["chapter_001_humanized"]["protected"])
        args = ("--step", "humanization_revision", "--target", "chapter_001", "--artifact", "chapters/chapter-001/draft-humanized.md")
        with self.assertRaisesRegex(ValueError, "protected"):
            self.command("start-step", *args)
        old = (self.workspace / args[-1]).read_bytes()
        self.command("approve", "--target", "chapter_001_humanized", "--overwrite")
        self.command("start-step", *args)
        backups = list((self.workspace / "production/revisions/chapter_001_humanized").iterdir())
        self.assertEqual(old, backups[0].read_bytes())
        (self.workspace / args[-1]).write_text("未经复审的新结局。", encoding="utf-8")
        self.command("finish-step", *args, "--measurement", "unavailable", "--reason", "runtime_usage_not_exposed")
        review = ctl.read_state(self.workspace)["artifacts"]["chapter_001_review"]
        self.assertEqual("stale", review["status"])
        self.assertNotIn("review_decision", review)
        with self.assertRaisesRegex(ValueError, "accepted chapter review"):
            self.command("start-step", "--step", "continuity_update", "--target", "chapter_001", "--artifact", "chapters/chapter-001/delta.md")

    def test_content_tampering_and_contract_changes_cannot_reuse_acceptance(self) -> None:
        self.prepare_prose()
        for filename in ("plan.md", "context.md", "draft-humanized.md"):
            path = self.workspace / "chapters/chapter-001" / filename
            original = path.read_bytes()
            path.write_text("用户修改内容。", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "review input changed"):
                self.command("start-step", "--step", "continuity_update", "--target", "chapter_001", "--artifact", "chapters/chapter-001/delta.md")
            path.write_bytes(original)

    def test_review_rejects_inputs_changed_during_generation(self) -> None:
        self.prepare_prose(review=None)
        self.command("start-step", "--step", "chapter_review", "--target", "chapter_001", "--artifact", "chapters/chapter-001/review.md")
        (self.workspace / "chapters/chapter-001/review.md").write_text("已检查。", encoding="utf-8")
        (self.workspace / "chapters/chapter-001/draft-humanized.md").write_text("新的正文。", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed"):
            self.command("finish-step", "--step", "chapter_review", "--target", "chapter_001", "--artifact", "chapters/chapter-001/review.md",
                         "--review-decision", "accepted", "--measurement", "unavailable", "--reason", "runtime_usage_not_exposed")

    def test_missing_inputs_and_skipped_chapters_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "required chapter plan"):
            self.command("context", "--chapter", "1")
        with self.assertRaisesRegex(ValueError, "dependency is not ready"):
            self.command("start-step", "--step", "chapter_draft", "--target", "chapter_001", "--artifact", "chapters/chapter-001/draft.md")
        with self.assertRaisesRegex(ValueError, "chapter sequence"):
            self.command("start-step", "--step", "chapter_plan", "--target", "chapter_008", "--artifact", "chapters/chapter-008/plan.md")

    def test_volume_selection_is_explicit_and_persists(self) -> None:
        state = ctl.read_state(self.workspace)
        state["artifacts"]["volume_02_beat_sheet"] = {"path": "volumes/volume-02-beat-sheet.md", "depends_on": []}
        self.ready_file(state["artifacts"]["volume_02_beat_sheet"])
        ctl.atomic_write_state(self.workspace, state)
        args = ("--step", "chapter_plan", "--target", "chapter_001", "--artifact", "chapters/chapter-001/plan.md")
        with self.assertRaisesRegex(ValueError, "volume is ambiguous"):
            self.command("start-step", *args)
        self.command("start-step", *args, "--volume", "2")
        plan = ctl.read_state(self.workspace)["artifacts"]["chapter_001_plan"]
        self.assertEqual(2, plan["volume"])
        self.assertEqual(["volume_02_beat_sheet"], plan["depends_on"])

    def test_next_finds_trial_plan_and_adopts_only_the_selected_bytes(self) -> None:
        state = ctl.read_state(self.workspace)
        trial = {"path": "chapters/chapter-001/plan.md", "source": "user_edited", "protected": True,
                 "depends_on": ["volume_01_beat_sheet"]}
        self.ready_file(trial, "留住这个动作。\r\n")
        state["artifacts"]["opening_plan_001"] = trial
        context = {"path": "chapters/chapter-001/context.md", "depends_on": ["opening_plan_001"]}
        self.ready_file(context, "早期试写使用的上下文。")
        state["artifacts"]["opening_context_001"] = context
        # Previous releases persisted a normal produce_artifact projection.
        ctl.atomic_write_state(self.workspace, state)
        original_state = ctl.state_path(self.workspace).read_bytes()
        action = json.loads(self.command("next"))
        self.assertEqual(("select_trial_plan", "opening_plan_001", trial["path"]),
                         (action["type"], action["candidate"], action["path"]))
        self.assertTrue(json.loads(self.command("validate"))["valid"])
        with self.assertRaisesRegex(ValueError, "试写文件"):
            self.command("start-step", "--step", "chapter_plan", "--target", "chapter_001", "--artifact", trial["path"])
        source = self.workspace / trial["path"]
        original = source.read_bytes()
        source.write_text("另一次编辑。", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed"):
            self.command("adopt-plan", "--chapter", "1")
        source.write_bytes(original)
        occupied = self.workspace / "other.md"
        occupied.write_text("保留这份。", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "已有不同内容"):
            self.command("adopt-plan", "--chapter", "1", "--output", "other.md")
        self.assertEqual(original_state, ctl.state_path(self.workspace).read_bytes())
        accepted = json.loads(self.command("adopt-plan", "--chapter", "1"))
        formal = self.workspace / accepted["path"]
        self.assertEqual(original, formal.read_bytes())
        self.assertFalse(formal.samefile(source))
        self.assertEqual(original, source.read_bytes())
        self.assertEqual("chapter_001_context", accepted["next_action"]["target"])
        adopted_state = ctl.state_path(self.workspace).read_bytes()
        self.assertTrue(json.loads(self.command("adopt-plan", "--chapter", "1"))["already_adopted"])
        self.assertEqual(adopted_state, ctl.state_path(self.workspace).read_bytes())
        self.assertTrue(ctl.read_state(self.workspace)["artifacts"]["chapter_001_plan"]["protected"])
        with self.assertRaisesRegex(ValueError, "试写文件"):
            self.command("context", "--chapter", "1", "--output", context["path"])
        self.assertIn("留住这个动作", self.command("context", "--chapter", "1"))
        self.assertEqual("早期试写使用的上下文。", (self.workspace / context["path"]).read_text(encoding="utf-8"))
        self.assertFalse(ctl.token_usage.usage_path(self.workspace).exists())
        self.assertFalse(json.loads(self.command("validate"))["warnings"])

    def test_warning_binds_debt_to_reviewed_prose_and_allows_stable_export(self) -> None:
        self.prepare_prose(review=None)
        args = ("--step", "chapter_review", "--target", "chapter_001", "--artifact", "chapters/chapter-001/review.md")
        self.command("start-step", *args)
        (self.workspace / "chapters/chapter-001/review.md").write_text("结尾多解释了一次，不影响后章。", encoding="utf-8")
        finish = (*args, "--measurement", "unavailable", "--reason", "test")
        warning = (*finish, "--review-decision", "continue_with_warning")
        before = ctl.state_path(self.workspace).read_bytes()
        with self.assertRaisesRegex(ValueError, "quality-debt-id"):
            self.command("finish-step", *warning)
        ledger = self.workspace / "production/quality-debt.md"
        ledger.write_text("| QD-10 | 第1章的另一项问题 |", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing"):
            self.command("finish-step", *warning, "--quality-debt-id", "QD-1")
        self.assertEqual(before, ctl.state_path(self.workspace).read_bytes())
        state = ctl.read_state(self.workspace)
        prose = state["artifacts"]["chapter_001_humanized"]
        ledger.write_text(f"| QD-1 | 第1章 | {prose['sha256']} | 末段有一句重复说明，精修时收回 |", encoding="utf-8")
        self.command("finish-step", *warning, "--quality-debt-id", "QD-1")
        state = ctl.read_state(self.workspace)
        review = state["artifacts"]["chapter_001_review"]
        self.assertEqual("accepted", review["review_decision"])
        self.assertEqual(["QD-1"], review["quality_debt_ids"])
        self.assertEqual(prose["sha256"], review["review_inputs"]["chapter_001_humanized"]["sha256"])
        self.assertTrue(state["artifacts"]["chapter_001_humanized"]["protected"])
        self.assertEqual("chapter_001_delta", json.loads(self.command("next"))["target"])
        self.step("continuity_update", "delta.md")
        output = self.root / "book.txt"
        self.command("export", "--output", str(output))
        self.assertIn("场景原版本", output.read_text(encoding="utf-8-sig"))
        self.assertTrue(json.loads(self.command("validate"))["valid"])

    def test_trial_adoption_inherits_its_registered_volume(self) -> None:
        state = ctl.read_state(self.workspace)
        artifacts = state["artifacts"]
        artifacts["volume_02_beat_sheet"] = {"path": "volumes/volume-02-beat-sheet.md", "depends_on": []}
        trial = {"path": "test-plan.md", "depends_on": ["volume_02_beat_sheet"]}
        artifacts["opening_plan_001"] = trial
        self.ready_file(artifacts["volume_02_beat_sheet"])
        self.ready_file(trial)
        state["next_action"] = ctl.decide_next(state)
        ctl.atomic_write_state(self.workspace, state)
        with self.assertRaisesRegex(ValueError, "volume conflicts"):
            self.command("adopt-plan", "--chapter", "1", "--volume", "1")
        self.command("adopt-plan", "--chapter", "1")
        plan = ctl.read_state(self.workspace)["artifacts"]["chapter_001_plan"]
        self.assertEqual(2, plan["volume"])
        self.assertEqual(["volume_02_beat_sheet"], plan["depends_on"])

    def test_repair_requires_new_review_and_then_commits(self) -> None:
        self.prepare_prose(review="repair_required")
        self.step("chapter_repair", "repair.md")
        self.step("chapter_review", "review.md", "accepted")
        self.step("continuity_update", "delta.md")
        state = ctl.read_state(self.workspace)
        self.assertEqual("chapter_001", state["continuity"]["last_committed_chapter"])
        self.assertTrue(state["artifacts"]["chapter_001_repair"]["protected"])

    def test_analysis_conclusion_change_invalidates_handoff_without_source_change(self) -> None:
        root = self.root / "analysis"
        root.mkdir()
        data = {"source": {"fingerprint": "sha256:source", "scope": "第1-3章", "coverage": "sampled"}, "analysis_lens": {"status": "ready"}}
        (root / "analysis-state.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
        lens = root / "analysis-lens.md"
        lens.write_text("最初结论。", encoding="utf-8")
        state = {"novel": {"mode": "fanfic"}, "source_analysis": {"path": str(root)}}
        ctl.validate_fanfic_source(state, refresh=True)
        ctl.validate_fanfic_source(state)
        lens.write_text("作者纠正并确认后的结论。", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "analysis source changed"):
            ctl.validate_fanfic_source(state)


if __name__ == "__main__":
    unittest.main()
