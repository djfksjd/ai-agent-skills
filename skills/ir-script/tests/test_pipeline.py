from __future__ import annotations
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pipeline
import financials
import install


class PipelineTests(unittest.TestCase):
    def setUp(self): self.deck = pipeline.read_json(ROOT / "templates/deck.example.json")
    def test_example_valid(self): self.assertEqual(pipeline.lint(self.deck, True)["errors"], [])
    def test_repeated_title_style(self):
        self.deck["slides"][0]["title"] = "문서를 연결합니다"
        self.assertTrue(pipeline.lint(self.deck, True)["errors"])
    def test_explicit_sentence_override(self):
        self.deck["slides"][0].update(title="문서를 연결합니다", allow_sentence_title=True)
        self.assertFalse(pipeline.lint(self.deck, True)["errors"])
    def test_duplicate_id(self):
        self.deck["slides"][1]["id"] = "S01"; self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_unknown_claim(self):
        self.deck["slides"][0]["claim_ids"] = ["C99"]; self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_false_verification(self):
        self.deck["claims"][0]["status"] = "verified"; self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_metadata_not_evidence(self):
        self.deck["sources"] = [{"id":"R1","title":"Video title","publisher":"Publisher","url":"https://example.com","retrieved_at":"2026-09-28","access":"metadata_only","observed_scope":"title only"}]
        self.deck["claims"][0].update(status="verified", source_ids=["R1"], locator="title")
        self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_calculation_requires_assumptions(self):
        self.deck["claims"][0]["status"] = "calculation"; self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_duration(self):
        self.deck["talk_seconds"] = 30; self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_appendix_boundary(self):
        self.deck["slides"][0]["kind"] = "appendix"; self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_q_and_a_mapping(self):
        self.deck["qa"][0]["appendix_ids"] = ["S01"]; self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_sync(self):
        mapping = {"slides": pipeline.slide_manifest(self.deck)}
        self.assertFalse(pipeline.check_sync(self.deck, mapping)["errors"])
        mapping["slides"][0]["title"] = "Another version"
        self.assertTrue(pipeline.check_sync(self.deck, mapping)["errors"])
    def test_bad_types(self):
        self.deck["slides"][0]["seconds"] = float("nan"); self.assertTrue(pipeline.lint(self.deck)["errors"])
    def test_json_nan(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/"bad.json"; p.write_text('{"x":NaN}')
            with self.assertRaises(ValueError): pipeline.read_json(p)
    def test_build_verify_and_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)/"release"
            pipeline.build(self.deck, out, strict_style=True)
            self.assertFalse(pipeline.verify(out)["errors"])
            (out/"script.md").write_text("modified", encoding="utf-8")
            self.assertTrue(pipeline.verify(out)["errors"])
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t); sentinel = out/"keep.txt"; sentinel.write_text("keep")
            with self.assertRaises(FileExistsError): pipeline.build(self.deck, out)
            self.assertEqual(sentinel.read_text(), "keep")
    def test_unsafe_manifest(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)/"release"; pipeline.build(self.deck, out)
            m = pipeline.read_json(out/"manifest.json"); m["files"]["../outside"] = "fake"; pipeline.dump(out/"manifest.json", m)
            self.assertTrue(pipeline.verify(out)["errors"])
    def test_financials(self):
        d = pipeline.read_json(ROOT/"templates/financial.example.json")
        r = financials.calculate(d)
        self.assertEqual(r["cumulative_revenue_ex_tax"], "4950000.00")
        self.assertEqual(r["ending_month_revenue_annualized"], "10800000.00")
        self.assertEqual(r["single_plan_break_even_customers"]["가상 월 요금제"], 67)
    def test_nonpositive_margin(self):
        self.assertIsNone(financials.break_even(100, 10, 0, 10))
    def test_financial_input_validation(self):
        for bad in (-1, "NaN", True):
            with self.assertRaises(ValueError): financials.amount(bad)
    def test_install_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            target = install.install(ROOT, Path(t)/"skills")
            self.assertTrue((target/"SKILL.md").exists())
            with self.assertRaises(FileExistsError): install.install(ROOT, Path(t)/"skills")
    def test_install_reject_inside_source(self):
        with self.assertRaises(ValueError): install.install(ROOT, ROOT/"bad-location")


if __name__ == "__main__": unittest.main()
