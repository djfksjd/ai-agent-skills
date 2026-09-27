import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pipeline
import financials
import install

class PipelineTests(unittest.TestCase):
    def setUp(self): self.data = pipeline.load(ROOT / 'templates/deck.example.json')
    def bad(self, fragment):
        self.assertTrue(any(fragment in e for e in pipeline.lint(self.data, True)['errors']))
    def test_valid(self): self.assertEqual(pipeline.lint(self.data, True)['errors'], [])
    def test_duplicate_slide(self):
        self.data['slides'][1]['id']='S01'; self.bad('duplicate')
    def test_main_after_appendix(self):
        self.data['slides'][1]['kind']='appendix'; self.bad('follows appendix')
    def test_metadata_not_evidence(self):
        self.data['sources'][0]['access']='metadata_only'
        self.data['claims'][0].update(status='verified',locator='title'); self.bad('unread source')
    def test_video_metadata_not_evidence(self):
        self.data['sources'][0]['video_access']='metadata_only'
        self.data['claims'][0].update(status='verified',locator='00:01'); self.bad('unread source')
    def test_unknown_source(self):
        self.data['claims'][0]['source_ids']=['missing']; self.bad('unknown source')
    def test_unknown_claim(self):
        self.data['slides'][0]['claim_ids']=['missing']; self.bad('unknown claim')
    def test_calculation_method_required(self):
        self.data['claims'][0]['status']='calculation'; self.bad('calculation requires')
    def test_style(self):
        self.data['slides'][0]['title']='문서를 작성합니다'; self.bad('explanatory title')
        self.data['slides'][0]['title_style_exception']='Intentional specific headline'
        self.assertFalse(pipeline.lint(self.data, True)['errors'])
    def test_duration(self):
        self.data['duration_seconds']=20; self.bad('exceeds requested')
    def test_appendix_excluded(self):
        self.data['slides'][-1]['seconds']=10000
        self.assertEqual(pipeline.lint(self.data)['planned_main_seconds'],110)
    def test_qa_target(self):
        self.data['qa'][0]['appendix_id']='S01'; self.bad('existing appendix')
    def test_counts_and_order(self):
        obj={'slides':pipeline.signature(self.data)}
        pipeline.check_sync(self.data,obj)
        obj['slides'][1],obj['slides'][0]=obj['slides'][0],obj['slides'][1]
        self.assertRaises(ValueError,pipeline.check_sync,self.data,obj)
    def test_title_and_kind(self):
        for key in ('title','kind'):
            obj={'slides':pipeline.signature(self.data)}; obj['slides'][0][key]='wrong'
            self.assertRaises(ValueError,pipeline.check_sync,self.data,obj)
    def test_pdf_dependency_failure(self):
        with patch('pipeline.shutil.which',return_value=None):
            self.assertRaises(RuntimeError,pipeline.convert_pdf,Path('x.docx'),Path('.'))
    def test_generate_and_detect_edit(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'build'; pipeline.build(self.data,out,strict_style=True); pipeline.verify(out)
            self.assertRaises(FileExistsError,pipeline.build,self.data,out)
            with (out/'script.md').open('a') as handle: handle.write('changed')
            self.assertRaises(ValueError,pipeline.verify,out)
    def test_install_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            result=install.install(ROOT,Path(td))
            self.assertTrue((result/'SKILL.md').exists())
            self.assertRaises(FileExistsError,install.install,ROOT,Path(td))

class FinancialTests(unittest.TestCase):
    def setUp(self): self.data=json.loads((ROOT/'templates/financial.example.json').read_text())
    def test_monthly_and_cumulative(self):
        result=financials.model(self.data)
        self.assertEqual(result['cumulative_net_revenue'],150000)
        self.assertEqual(result['last_month_annualized_revenue'],1200000)
        self.assertEqual(result['products'][0]['single_product_break_even_customers'],12)
    def test_zero_margin(self):
        self.data['products'][0]['monthly_variable_cost']=10000
        self.assertIsNone(financials.model(self.data)['products'][0]['single_product_break_even_customers'])
    def test_negative_customers(self):
        self.data['products'][0]['active_customers'][0]=-1
        self.assertRaises(ValueError,financials.model,self.data)
    def test_mismatched_months(self):
        p=copy.deepcopy(self.data['products'][0]); p['active_customers']=[1]; self.data['products'].append(p)
        self.assertRaises(ValueError,financials.model,self.data)
    def test_zero_period(self):
        self.data['products'][0]['price_period_months']=0
        self.assertRaises(ValueError,financials.model,self.data)

if __name__=='__main__': unittest.main()
