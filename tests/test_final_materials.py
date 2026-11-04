"""Keep the résumé facts, companion language and current branding consistent."""
import json, unittest, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class FinalMaterialsTests(unittest.TestCase):
    def setUp(self):
        self.en=json.loads((ROOT/'content/hiring/resume.json').read_text())
        self.pt=json.loads((ROOT/'content/hiring/resume-pt.json').read_text())
    def test_contact_and_identity_match(self):
        for k in ('name','email','phone'):self.assertEqual(self.en[k],self.pt[k])
    def test_fipe_scope_and_dates(self):
        self.assertEqual(len(self.en['experience']['bullets']),5)
        self.assertEqual(len(self.pt['experience']['bullets']),5)
        self.assertIn('June 2024 - December 2025',self.en['experience']['dates'])
        for term in ('collective bargaining','researchers and managers','traceability'):
            self.assertIn(term,' '.join(self.en['experience']['bullets']))
    def test_selected_training_not_certifications(self):
        self.assertEqual(len(self.en['training']),3)
        self.assertTrue(any('97 hours' in x for x in self.en['training']))
        self.assertTrue(any('8 completed' in x for x in self.en['training']))
        self.assertIn('not as a Microsoft professional certification',(ROOT/'public/resume/index.html').read_text())
    def test_two_projects_and_supporting_writing(self):
        self.assertEqual(len(self.en['projects']),2)
        self.assertIn('/blog/',self.en['communication']['url'])
        for p in self.en['projects']:self.assertIn('/case-studies/',p['url'])
    def test_both_pdfs_published(self):
        for name in ('mauricio-taguchi-resume.pdf','mauricio-taguchi-curriculo-pt.pdf'):
            self.assertTrue((ROOT/'public/resume'/name).read_bytes().startswith(b'%PDF-'))
            self.assertIn(name,(ROOT/'public/resume/index.html').read_text())
    def test_site_remains_english(self):
        self.assertIn('<html lang="en">',(ROOT/'public/resume/index.html').read_text())
    def test_every_slide_uses_tm(self):
        with zipfile.ZipFile(ROOT/'public/blog/downloads/csv-validation-slides.pptx') as z:
            slides=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            self.assertEqual(len(slides),10)
            for n in slides:
                texts=[e.text for e in ET.fromstring(z.read(n)).iter() if e.tag.endswith('}t')]
                self.assertIn('TM.',texts);self.assertNotIn('MT.',texts)
    def test_no_fabricated_recording(self):
        s=(ROOT/'content/hiring/demonstration-script.md').read_text()
        self.assertIn('not a record of a completed talk',s)
        self.assertIn('does not establish a measured percentage',s)
    def test_message_panel_focus_contrast(self):
        self.assertIn('.prepared-message :focus-visible{outline:3px solid #233de5',(ROOT/'src/globals.css').read_text())
if __name__=='__main__':unittest.main()


class LoadingAndContrastTests(unittest.TestCase):
    def test_empty_root_reserves_first_screen(self):
        self.assertIn("#root:empty{min-height:100svh}",(ROOT/"index.html").read_text())
    def test_portrait_preload_keeps_relative_base(self):
        self.assertIn('as="image" href="%BASE_URL%images/portrait.webp" fetchpriority="high"',(ROOT/"index.html").read_text())
    def test_secondary_text_uses_accessible_color(self):
        self.assertIn(".section-heading>p,.skill-index,.service-number{color:#62636b}",(ROOT/"src/globals.css").read_text())
