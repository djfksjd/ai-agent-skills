import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import pipeline as p
from financials import scenario

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = p.load(ROOT/'templates/deck.example.json')
    def test_valid_example(self):
        self.assertEqual(p.validate(self.data, True)['status'], 'passed')
    def test_duplicate_id(self):
        self.data['slides'][1]['id'] = 'S01'
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_unknown_claim(self):
        self.data['slides'][0]['claim_ids'] = ['missing']
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_unknown_source(self):
        self.data['claims'][0]['source_ids'] = ['missing']
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_metadata_cannot_verify(self):
        self.data['claims'][0]['status'] = 'verified'; self.data['sources'][0]['access'] = 'metadata_only'
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_unavailable_cannot_verify(self):
        self.data['claims'][0]['status'] = 'verified'; self.data['sources'][0]['access'] = 'unavailable'
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_verified_requires_evidence(self):
        self.data['claims'][0]['status'] = 'verified'; self.data['claims'][0]['source_ids'] = []
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_calculation_requires_formula(self):
        self.data['claims'][0]['status'] = 'calculation'
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_qa_main_slide_rejected(self):
        self.data['qa'][0]['appendix_id'] = 'S01'
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_main_after_appendix(self):
        self.data['slides'][0]['kind'] = 'appendix'
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_timing_budget(self):
        self.data['project']['duration_seconds'] = 1
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_nan_timing(self):
        self.data['project']['timing_rate'] = float('nan')
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_style_strict(self):
        self.data['slides'][0]['title'] = '내용을 정리했습니다'
        with self.assertRaises(ValueError): p.validate(self.data, True)
        self.assertTrue(p.validate(self.data)['warnings'])
    def test_deliberate_sentence_title(self):
        self.data['slides'][0]['title'] = '내용을 정리했습니다'
        self.data['slides'][0]['allow_sentence_title'] = True
        self.assertEqual(p.validate(self.data, True)['status'], 'passed')
    def test_bad_control_character(self):
        self.data['slides'][0]['speaker_text'] = '\x00'
        with self.assertRaises(ValueError): p.validate(self.data)
    def test_sync_title_and_order(self):
        other = {'slides': p.slide_map(self.data)}
        p.check_sync(self.data, other)
        other['slides'][0]['title'] = 'different'
        with self.assertRaises(ValueError): p.check_sync(self.data, other)
    def test_sync_count(self):
        with self.assertRaises(ValueError): p.check_sync(self.data, {'slides':p.slide_map(self.data)[:-1]})
    def test_dense_slide_rejected(self):
        self.data['slides'][0]['bullets'] *= 3
        with self.assertRaises(ValueError): p.validate(self.data)

class BuildTests(unittest.TestCase):
    def test_build_roundtrip_and_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'release'
            data = p.load(ROOT/'templates/deck.example.json')
            p.build(data, out, strict_style=True)
            self.assertEqual(p.verify(out)['slides'], 4)
            with self.assertRaises(ValueError): p.build(data, out)
            (out/'script.md').write_text('changed', encoding='utf-8')
            with self.assertRaises(ValueError): p.verify(out)
    def test_unsafe_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'release'; p.build(p.load(ROOT/'templates/deck.example.json'), out)
            manifest = p.load(out/'manifest.json'); manifest['files']['../secret'] = 'bad'
            p.dump(out/'manifest.json',manifest)
            with self.assertRaises(ValueError): p.verify(out)

class FinancialTests(unittest.TestCase):
    def setUp(self): self.data = p.load(ROOT/'templates/financial.example.json')
    def test_run_rate_is_not_cumulative(self):
        result = scenario(self.data)
        self.assertEqual(result['cumulative_net_revenue'], '300000.00')
        self.assertEqual(result['ending_annualized_revenue'], '2400000.00')
        self.assertEqual(result['single_plan_breakeven_active_customers']['Synthetic only'], 38)
    def test_negative_rejected(self):
        self.data['plans'][0]['active_by_month'][0] = -1
        with self.assertRaises(ValueError): scenario(self.data)
    def test_nonpositive_margin(self):
        self.data['plans'][0]['monthly_variable_cost'] = '10000'
        self.assertIsNone(scenario(self.data)['single_plan_breakeven_active_customers']['Synthetic only'])
    def test_annual_recognition(self):
        self.data['plans'][0]['tax_inclusive_price'] = '132000'
        self.data['plans'][0]['price_period_months'] = 12
        self.assertEqual(scenario(self.data)['cumulative_net_revenue'], '300000.00')

if __name__ == '__main__': unittest.main()
