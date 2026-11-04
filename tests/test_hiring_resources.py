"""Inspect the public kit without pretending to execute a native BI runtime."""
import base64,csv,io,json,re,sqlite3,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/'public/case-studies/downloads/income-analysis-lab.zip'
class HiringResourcesTests(unittest.TestCase):
    def test_resume_is_pdf(self):self.assertTrue((ROOT/'public/resume/mauricio-taguchi-resume.pdf').read_bytes().startswith(b'%PDF-'))
    def test_resume_facts_match(self):
        text=(ROOT/'public/resume/index.html').read_text();self.assertIn('June 2024 - December 2025',text);self.assertIn('Completed in 2026',text)
    def test_archive_contains_only_lab(self):
        with zipfile.ZipFile(LAB) as z:
            names=z.namelist();self.assertIn('queries.sql',names);self.assertIn('power-bi/BrazilIncome.pbip',names)
            self.assertFalse(any('..' in Path(n).parts or n.startswith('/') or '__pycache__' in n for n in names))
    def test_standalone_analysis(self):
        with tempfile.TemporaryDirectory() as temp,zipfile.ZipFile(LAB) as z:
            z.extractall(temp);p=subprocess.run([sys.executable,'-B','analyze.py'],cwd=temp,capture_output=True,text=True,check=True);self.assertEqual(json.loads(p.stdout)['snapshot']['rows'],540)
    def test_source_snapshot_exact(self):
        with zipfile.ZipFile(LAB) as z:self.assertEqual(z.read('income.csv'),(ROOT/'public/case-studies/data/income.csv').read_bytes())
    def test_native_validation_not_claimed(self):
        with zipfile.ZipFile(LAB) as z:self.assertIn('have NOT been executed',z.read('power-bi/README.md').decode())
    def test_powerbi_relationships(self):
        with zipfile.ZipFile(LAB) as z:m=json.loads(z.read('power-bi/BrazilIncome.SemanticModel/model.bim'))['model']
        self.assertEqual(len(m['relationships']),2);self.assertEqual({t['name'] for t in m['tables']},{'Income','States','Quarters'})
    def test_embedded_model_row_counts(self):
        with zipfile.ZipFile(LAB) as z:m=json.loads(z.read('power-bi/BrazilIncome.SemanticModel/model.bim'))['model']
        counts={}
        for t in m['tables']:
            expr='\n'.join(t['partitions'][0]['source']['expression']);encoded=re.search(r'Binary.FromText\("([A-Za-z0-9+/=]+)"',expr).group(1);counts[t['name']]=len(json.loads(base64.b64decode(encoded)))
        self.assertEqual(counts,{'Income':540,'States':27,'Quarters':20})
    def test_visuals_reference_existing_fields(self):
        with zipfile.ZipFile(LAB) as z:
            m=json.loads(z.read('power-bi/BrazilIncome.SemanticModel/model.bim'))['model'];tables={t['name']:t for t in m['tables']}
            for name in z.namelist():
                if name.endswith('/visual.json'):
                    visual=json.loads(z.read(name))
                    for role in visual['visual']['query']['queryState'].values():
                        for p in role['projections']:
                            kind,field=next(iter(p['field'].items()));table=tables[field['Expression']['SourceRef']['Entity']];self.assertIn(field['Property'],{x['name'] for x in table['measures' if kind=='Measure' else 'columns']})
    def test_hiring_links_in_source(self):
        s=(ROOT/'src/portfolio.tsx').read_text();self.assertIn('Download résumé',s);self.assertIn('mailto:mauricioryotoitataguchi@gmail.com',s);self.assertIn('case-studies/',s)
if __name__=='__main__':unittest.main()
