from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "style_exemplars.py"

FIRST = "".join(f"    陆青抬头看了看第{index}面旗，又把手里的账册往怀里收了收。\n" for index in range(1, 7))
SECOND = "    “你来晚了。”\n    “路上有人拦车。”陆青说。\n    “谁？”\n    “不认识……他只问了我一句话。”\n" * 3
SOURCE = "前言\n" + FIRST + "\n" + SECOND + "尾声\n"


class StyleExemplarsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "source").mkdir()
        raw = ("\ufeff" + SOURCE).encode("utf-8")
        (self.root / "source/book.txt").write_bytes(raw)
        self.first = (SOURCE.index(FIRST), SOURCE.index(FIRST) + len(FIRST))
        self.second = (SOURCE.index(SECOND), SOURCE.index(SECOND) + len(SECOND))
        self.register = {
            "schema_version": 1,
            "source": {"title": "样书", "snapshot": "source/book.txt",
                       "fingerprint": f"sha256:{hashlib.sha256(raw).hexdigest()}", "decoding": "utf-8-sig",
                       "offset_unit": "unicode_character", "end_exclusive": True},
            "policy": {"text_storage": "coordinates_only", "max_chars": 600},
            "source_entities": [{"name": "陆青", "aliases": ["青哥"]}],
            "exemplars": [
                self.entry("EX-001", "selected", self.first),
                self.entry("EX-002", "candidate", self.second),
            ],
        }
        self.save()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def entry(identifier: str, status: str, span: tuple[int, int]) -> dict:
        return {"id": identifier, "status": status, "scene_function": "旁人起笔", "locator": "第1章",
                "span": list(span), "learn": ["短段先落地"], "do_not_carry": ["旗和账册"]}

    def save(self) -> None:
        (self.root / "style-exemplars.yaml").write_text(
            yaml.safe_dump(self.register, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def call(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), *args], check=False, capture_output=True,
                              text=True, encoding="utf-8")

    def assert_rejected(self, fragment: str) -> None:
        self.save()
        result = self.call("validate", str(self.root))
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn(fragment, result.stderr)

    def test_validate_reports_sizes_without_source_text(self) -> None:
        result = self.call("validate", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual([item["id"] for item in data["exemplars"]], ["EX-001", "EX-002"])
        self.assertEqual(data["exemplars"][0]["chars"], len(FIRST))
        self.assertNotIn("账册", result.stdout)

    def test_register_must_stay_coordinates_only(self) -> None:
        self.register["exemplars"][0]["text"] = "陆青抬头看了看"
        self.assert_rejected("coordinates only")

    def test_changed_snapshot_is_rejected(self) -> None:
        (self.root / "source/book.txt").write_text(SOURCE + "改动", encoding="utf-8")
        self.assert_rejected("source snapshot changed")

    def test_state_fingerprint_must_match(self) -> None:
        (self.root / "analysis-state.yaml").write_text("source:\n  fingerprint: sha256:other\n", encoding="utf-8")
        self.assert_rejected("analysis-state.yaml")

    def test_span_must_follow_paragraphs_and_limits(self) -> None:
        start, end = self.first
        self.register["exemplars"][0]["span"] = [start + 3, end]
        self.assert_rejected("paragraph start")
        self.register["exemplars"][0]["span"] = [start, end - 3]
        self.assert_rejected("paragraph end")
        self.register["exemplars"][0]["span"] = [start, end]
        self.register["policy"]["max_chars"] = 100
        self.assert_rejected("exceeds 100")
        self.register["policy"]["max_chars"] = 5000
        self.assert_rejected("up to 1200")

    def test_windows_line_endings_keep_paragraph_boundaries(self) -> None:
        source = SOURCE.replace("\n", "\r\n")
        raw = source.encode("utf-8")
        (self.root / "source/book.txt").write_bytes(raw)
        self.register["source"]["fingerprint"] = f"sha256:{hashlib.sha256(raw).hexdigest()}"
        first = FIRST.replace("\n", "\r\n")
        start = source.index(first)
        # A span may stop before the line ending or after it; both are whole paragraphs.
        for end in (start + len(first) - 2, start + len(first)):
            self.register["exemplars"] = [self.entry("EX-001", "selected", (start, end))]
            self.save()
            self.assertEqual(self.call("validate", str(self.root)).returncode, 0)
        shown = self.call("show", str(self.root)).stdout
        self.assertIn("第6面旗", shown)
        self.assertNotIn("\r", shown)

    def test_overlapping_spans_and_duplicate_ids_are_rejected(self) -> None:
        self.register["exemplars"][1]["span"] = [self.first[0], self.second[1]]
        self.assert_rejected("overlap")
        self.register["exemplars"][1] = self.entry("EX-001", "candidate", self.second)
        self.assert_rejected("unique EX-XXX")

    def test_export_masks_source_names_and_keeps_only_selected(self) -> None:
        data = json.loads(self.call("export", str(self.root)).stdout)
        self.assertEqual([item["id"] for item in data["exemplars"]], ["EX-001"])
        exemplar = data["exemplars"][0]
        self.assertNotIn("陆青", exemplar["text"])
        self.assertIn("〔甲〕抬头看了看第1面旗", exemplar["text"])
        self.assertEqual(exemplar["doNotCarry"], ["旗和账册"])
        self.assertIn(f"[{self.first[0]},{self.first[1]})", exemplar["sourceRef"])
        self.assertEqual(data["sourceEntities"], ["陆青", "青哥"])
        both = json.loads(self.call("export", str(self.root), "--include-candidates").stdout)
        self.assertEqual(len(both["exemplars"]), 2)

    def test_naming_an_entry_does_not_override_the_authors_choice(self) -> None:
        self.register["exemplars"][0]["status"] = "rejected"
        self.save()
        for identifier, status in (("EX-001", "rejected"), ("EX-002", "candidate")):
            refused = self.call("export", str(self.root), "--id", identifier)
            self.assertEqual(refused.returncode, 2, refused.stdout)
            self.assertIn(f"{identifier} ({status})", refused.stderr)
        trial = json.loads(self.call("export", str(self.root), "--id", "EX-002", "--include-candidates").stdout)
        self.assertEqual([item["id"] for item in trial["exemplars"]], ["EX-002"])
        self.assertEqual(self.call("export", str(self.root), "--id", "EX-001", "--include-candidates").returncode, 2)
        # Reading a rejected entry locally stays possible, so the author can reconsider it.
        self.assertIn("第1面旗", self.call("show", str(self.root), "--id", "EX-001").stdout)

    def test_sampled_analysis_only_registers_what_it_read(self) -> None:
        state = self.root / "analysis-state.yaml"
        sampling = self.root / "sampling-register.yaml"
        state.write_text("source:\n  coverage: sampled\n", encoding="utf-8")
        self.assert_rejected("needs sampling-register.yaml")

        def read(*ranges: tuple[int, int], excerpts: tuple[tuple[int, int], ...] = ()) -> None:
            sampling.write_text(yaml.safe_dump({
                "windows": [{"id": f"W{index}", "start": start, "end": end} for index, (start, end) in enumerate(ranges)],
                "review_excerpts": {"excerpts": [{"start": start, "end": end} for start, end in excerpts]},
            }), encoding="utf-8")

        read(self.first)
        self.assert_rejected("EX-002: span lies outside the ranges this analysis has read")
        middle = self.first[0] + 40
        for ranges, excerpts in (((self.first, self.second), ()), ((self.first,), (self.second,)),
                                 (((0, middle), (middle, len(SOURCE))), ())):
            read(*ranges, excerpts=excerpts)
            self.assertEqual(self.call("validate", str(self.root)).returncode, 0, (ranges, excerpts))
        read((0, middle), (middle + 1, len(SOURCE)))
        self.assert_rejected("EX-001: span lies outside")
        sampling.write_text("windows: [{id: W1}]\n", encoding="utf-8")
        self.assert_rejected("without valid start and end")
        # A finished full read no longer depends on the earlier sampling record.
        state.write_text("source:\n  coverage: full\n", encoding="utf-8")
        self.assertEqual(self.call("validate", str(self.root)).returncode, 0)

    def test_notes_stay_short(self) -> None:
        self.register["exemplars"][0]["learn"] = ["短"] * 5
        self.assert_rejected("EX-001.learn must list 1 to 4")
        self.register["exemplars"][0]["learn"] = ["长" * 81]
        self.assert_rejected("EX-001.learn must stay within 80")
        self.register["exemplars"][0]["learn"] = ["短段先落地"]
        self.register["exemplars"][0]["scene_function"] = "长" * 81
        self.assert_rejected("EX-001.scene_function must stay within 80")

    def test_export_requires_a_selection(self) -> None:
        self.register["exemplars"][0]["status"] = "candidate"
        self.save()
        result = self.call("export", str(self.root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("no selected exemplars", result.stderr)

    def test_show_reads_text_from_the_snapshot(self) -> None:
        masked = self.call("show", str(self.root), "--id", "EX-002").stdout
        self.assertIn("“路上有人拦车。”〔甲〕说。", masked)
        raw = self.call("show", str(self.root), "--id", "EX-002", "--raw").stdout
        self.assertIn("陆青说", raw)
        self.assertEqual(self.call("show", str(self.root), "--id", "EX-009").returncode, 2)

    def test_metrics_compare_exemplars_with_a_draft(self) -> None:
        draft = self.root / "draft.md"
        draft.write_text("他站了很久，没有说话，也没有动，只是看着那扇门，想起很多年前的一个下午。\n", encoding="utf-8")
        result = self.call("metrics", "--analysis", str(self.root), "--id", "EX-002", "--text-file", str(draft))
        data = json.loads(result.stdout)
        self.assertEqual(data["exemplar_ids"], ["EX-002"])
        self.assertEqual(data["exemplars"]["measurement"], "observation_only")
        self.assertEqual(data["exemplars"]["dialogue_paragraph_ratio"], 1.0)
        self.assertGreater(data["exemplars"]["dialogue_char_ratio"], 0.6)
        self.assertGreater(data["exemplars"]["ellipsis_per_mille"], 0)
        self.assertEqual(data["text"]["dialogue_char_ratio"], 0)
        self.assertEqual(data["text"]["paragraphs"], 1)
        alone = json.loads(self.call("metrics", "--text-file", str(draft)).stdout)
        self.assertEqual(set(alone), {"text"})
        self.assertEqual(self.call("metrics").returncode, 2)

    def test_overlap_flags_reused_passages_only(self) -> None:
        draft = self.root / "draft.md"
        draft.write_text("她抬头看了看天色，把伞往怀里收了收。\n“你来晚了。”\n", encoding="utf-8")
        clean = self.call("overlap", str(self.root), "--text-file", str(draft), "--include-candidates")
        self.assertEqual(clean.returncode, 0, clean.stdout)
        self.assertTrue(json.loads(clean.stdout)["clean"])
        draft.write_text("开头。\n陆青抬头看了看第3面旗，又把手里的账册，往怀里收了收。\n", encoding="utf-8")
        reused = self.call("overlap", str(self.root), "--text-file", str(draft))
        self.assertEqual(reused.returncode, 1)
        finding = json.loads(reused.stdout)["overlaps"][0]
        self.assertEqual(finding["exemplar"], "EX-001")
        self.assertGreaterEqual(finding["shared_chars"], 14)
        self.assertEqual(self.call("overlap", str(self.root), "--text-file", str(draft), "--min-chars", "4").returncode, 2)

    def test_overlap_sees_through_changed_names(self) -> None:
        lines = "".join(f"    陆青抬头看了第{index}面旗，青哥把账册收进怀里，陆青转身往回走。\n" for index in range(1, 6))
        source = "前言\n" + lines + "尾声\n"
        raw = source.encode("utf-8")
        (self.root / "source/book.txt").write_bytes(raw)
        self.register["source"]["fingerprint"] = f"sha256:{hashlib.sha256(raw).hexdigest()}"
        self.register["exemplars"] = [self.entry("EX-001", "selected", (source.index(lines), source.index("尾声")))]
        self.save()
        shown = json.loads(self.call("export", str(self.root)).stdout)["exemplars"][0]["text"]
        self.assertIn("〔甲〕抬头看了第1面旗，〔甲〕把账册收进怀里，〔甲〕转身往回走。", shown)
        draft = self.root / "draft.md"
        # The passage as the writer saw it, with the writer's own names, and with the original names.
        for copied in (shown, shown.replace("〔甲〕", "沈舟"), shown.replace("〔甲〕", ""), lines):
            draft.write_text(copied, encoding="utf-8")
            result = self.call("overlap", str(self.root), "--text-file", str(draft))
            self.assertEqual(result.returncode, 1, copied)
            finding = json.loads(result.stdout)["overlaps"][0]
            self.assertEqual(finding["exemplar"], "EX-001")
            self.assertGreaterEqual(finding["shared_chars"], 20)
        # The same ordinary actions, two in a row or all three in another order, are not a copied passage.
        for original in ("沈舟把账册收进怀里，沈舟转身往回走。\n",
                         "沈舟转身往回走，接着沈舟把账册收进怀里，最后才抬头看了第9面旗。\n"):
            draft.write_text(original, encoding="utf-8")
            self.assertEqual(self.call("overlap", str(self.root), "--text-file", str(draft)).returncode, 0, original)

    def test_nested_quotes_count_once(self) -> None:
        draft = self.root / "draft.md"
        draft.write_text("「他只留了一句『别等我』就走了」\n“他说：‘你先走。’”她顿了顿。\n“话没说完，\n", encoding="utf-8")
        data = json.loads(self.call("metrics", "--text-file", str(draft)).stdout)["text"]
        inside = len("他只留了一句『别等我』就走了") + len("他说：‘你先走。’") + len("话没说完，")
        self.assertEqual(data["dialogue_char_ratio"], round(inside / data["non_whitespace_chars"], 2))
        self.assertLess(data["dialogue_char_ratio"], 1)


if __name__ == "__main__":
    unittest.main()
