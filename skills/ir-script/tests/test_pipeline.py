import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pipeline,financials,install

class PipelineTests(unittest.TestCase):
    def setUp(self):self.data=pipeline.load(ROOT/'templates/deck.example.json')
    def test_valid(self):self.assertEqual(pipeline.lint(self.data,True)['errors'],[])
    def test_duplicate_id(self):
        self.data['slides'][1]['id']='S01';self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_unknown_source(self):
        self.data['claims'][0]['evidence'][0]['source_id']='missing';self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_verified_needs_evidence(self):
        self.data['claims'][1]['status']='verified';self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_metadata_does_not_verify(self):
        self.data['claims'][0]['status']='verified';self.data['sources'][0]['access']='metadata_only';self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_exact_locator_required(self):
        self.data['claims'][0]['evidence'][0]['locator']='';self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_title_style(self):
        self.data['slides'][0]['title']='작업을 연결합니다';self.assertTrue(pipeline.lint(self.data,True)['errors'])
        self.data['slides'][0]['allow_sentence_title']=True;self.assertEqual(pipeline.lint(self.data,True)['errors'],[])
    def test_long_text(self):
        self.data['slides'][0]['bullets']=['가'*111];self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_talk_limit(self):
        self.data['talk_seconds']=1;self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_negative_seconds(self):
        self.data['slides'][0]['seconds']=-1;self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_main_after_appendix(self):
        self.data['slides'].reverse();self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_qa_bad_appendix(self):
        self.data['qa'][0]['appendix_id']='S01';self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_unknown_claim(self):
        self.data['slides'][0]['claim_ids']=['bogus'];self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_count_mismatch(self):
        with self.assertRaises(ValueError):pipeline.check_sync(self.data,{'slides':pipeline.sequence(self.data)[:-1]})
    def test_order_mismatch(self):
        with self.assertRaises(ValueError):pipeline.check_sync(self.data,{'slides':list(reversed(pipeline.sequence(self.data)))})
    def test_title_mismatch(self):
        other={'slides':pipeline.sequence(self.data)};other['slides'][0]['title']='different'
        with self.assertRaises(ValueError):pipeline.check_sync(self.data,other)
    def test_malformed_collection(self):
        self.data['slides']=[2];self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_nonfinite(self):
        self.data['talk_seconds']=float('nan');self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_enum_wrong_type(self):
        self.data['sources'][0]['access']=[];self.data['claims'][0]['status']=[];self.assertTrue(pipeline.lint(self.data)['errors'])
    def test_build_verify_tamper_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run';pipeline.build(self.data,out,strict_style=True)
            self.assertEqual(pipeline.verify(out)['slides'],4)
            with self.assertRaises(FileExistsError):pipeline.build(self.data,out)
            (out/'script.md').write_text('tampered')
            with self.assertRaises(ValueError):pipeline.verify(out)
    def test_verify_unsafe_path(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run';pipeline.build(self.data,out)
            manifest=pipeline.load(out/'manifest.json');manifest['files']['../private.txt']='0'*64
            pipeline.dump(out/'manifest.json',manifest)
            with self.assertRaises(ValueError):pipeline.verify(out)
    def test_bad_json(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'input.json';f.write_text('{"x":NaN}')
            with self.assertRaises(ValueError):pipeline.load(f)

class FinancialTests(unittest.TestCase):
    def setUp(self):self.data=pipeline.load(ROOT/'templates/financial.example.json')
    def test_cumulative_not_runrate(self):
        r=financials.calculate(self.data);self.assertEqual(r['cumulative_revenue'],3000);self.assertEqual(r['last_month_annualized_revenue'],24000)
        self.assertEqual(r['single_product_break_even']['Synthetic plan'],2)
    def test_negative(self):
        self.data['monthly_payroll']=-1
        with self.assertRaises(ValueError):financials.calculate(self.data)
    def test_nonpositive_contribution(self):
        self.data['products'][0]['monthly_variable_cost']=1000
        self.assertIsNone(financials.calculate(self.data)['single_product_break_even']['Synthetic plan'])
    def test_customer_month_count(self):
        self.data['products'][0]['active_customers']=[1]
        with self.assertRaises(ValueError):financials.calculate(self.data)
    def test_fractional_customers(self):
        self.data['products'][0]['active_customers'][0]=1.5
        with self.assertRaises(ValueError):financials.calculate(self.data)
    def test_annual_allocation(self):
        self.data['products'][0]['tax_inclusive_price']=13200;self.data['products'][0]['price_period_months']=12
        self.assertEqual(financials.calculate(self.data)['cumulative_revenue'],3000)

class InstallTests(unittest.TestCase):
    def test_copy_and_collision(self):
        with tempfile.TemporaryDirectory() as d:
            out=install.install('codex',Path(d));self.assertTrue((out/'SKILL.md').is_file())
            self.assertFalse((out/'tests').exists())
            with self.assertRaises(FileExistsError):install.install('codex',Path(d))
    def test_dry_run(self):
        with tempfile.TemporaryDirectory() as d:
            out=install.install('claude',Path(d),True);self.assertFalse(out.exists())
    def test_invalid_host(self):
        with self.assertRaises(ValueError):install.install('cowork')

if __name__=='__main__':unittest.main()
