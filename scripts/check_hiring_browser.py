"""Verify recruiter entry points, snapshot filters and the isolated DataFlow demo."""
from __future__ import annotations
import argparse,csv,io,json,os,tempfile
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def check(base,evidence):
    evidence.mkdir(parents=True,exist_ok=True);records=[]
    with sync_playwright() as pw:
        opts={'headless':True}
        if os.environ.get('BROWSER_EXECUTABLE'):opts['executable_path']=os.environ['BROWSER_EXECUTABLE']
        browser=pw.chromium.launch(**opts)
        try:
            for width,height in [(1440,1000),(390,844)]:
                context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce',locale='en-US',accept_downloads=True)
                page=context.new_page();page.set_default_timeout(20000);errors=[];mutations=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                def protect(route):
                    if route.request.method not in ('GET','HEAD','OPTIONS'):
                        mutations.append(route.request.method+' '+route.request.url);route.abort()
                    else:route.continue_()
                context.route('**/*',protect)
                try:
                    response=page.goto(base,wait_until='networkidle');assert response.status==200
                    expect(page.locator('.hero h1')).to_be_visible()
                    assert page.locator('a[href="mailto:mauricioryotoitataguchi@gmail.com"]').count()>=2
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
                    page.screenshot(path=str(evidence/f'{width}-home.png'))
                    for label, filename in [('Currículo em português', 'mauricio-taguchi-curriculo-pt.pdf'), ('Résumé in English', 'mauricio-taguchi-resume.pdf')]:
                        link = page.get_by_role('link', name=label, exact=True)
                        expect(link).to_be_in_viewport()
                        with page.expect_download() as d:
                            link.click()
                        with tempfile.TemporaryDirectory() as temp:
                            target = Path(temp) / filename
                            d.value.save_as(target)
                            assert d.value.suggested_filename == filename
                            assert target.read_bytes() == (ROOT / 'docs/resume' / filename).read_bytes()
                    if width<600:
                        page.get_by_role('button',name='Open menu',exact=True).click()
                        page.screenshot(path=str(evidence/f'{width}-menu.png'))
                        page.get_by_role('navigation',name='Mobile menu',exact=True).get_by_role('link',name='Case studies',exact=True).click()
                    else:page.get_by_role('navigation',name='Main navigation',exact=True).get_by_role('link',name='Case studies',exact=True).click()
                    expect(page.get_by_role('link',name='Read income case study',exact=True)).to_be_visible()
                    for path in ['case-studies/','case-studies/brazil-income.html','case-studies/dataflow.html','resume/']:
                        response=page.goto(base+path,wait_until='networkidle');assert response.status==200
                        expect(page.locator('html')).to_have_attribute('lang','en');assert page.locator('h1').count()==1
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
                    page.goto(base+'case-studies/brazil-income.html');page.get_by_role('link',name='Open interactive dashboard',exact=True).click()
                    expect(page.locator('#income')).to_have_text('3,437.41')
                    expect(page.locator('#coverage')).to_have_text('27')
                    page.locator('#state').select_option('53');expect(page.locator('#income')).to_have_text('6,720.00');expect(page.locator('#coverage')).to_have_text('1')
                    with page.expect_download() as d:page.get_by_role('button',name='Export displayed rows').click()
                    with tempfile.TemporaryDirectory() as temp:
                        target=Path(temp)/'view.csv';d.value.save_as(target);rows=list(csv.DictReader(io.StringIO(target.read_text())));assert len(rows)==1 and rows[0]['state_code']=='53'
                    page.locator('#quarter').select_option('202102');expect(page.locator('#change')).to_have_text('Unavailable')
                    page.get_by_role('button',name='Reset filters').click();expect(page.locator('#coverage')).to_have_text('27')
                    page.locator('#region').select_option('North');expect(page.locator('#coverage')).to_have_text('7')
                    page.get_by_role('button',name='Reset filters').click()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1');page.screenshot(path=str(evidence/f'{width}-income.png'),full_page=True)
                    page.goto(base+'case-studies/brazil-income.html')
                    with page.expect_download() as d:page.get_by_role('link',name='Download SQL lab',exact=True).click()
                    with tempfile.TemporaryDirectory() as temp:
                        target=Path(temp)/'lab.zip';d.value.save_as(target);assert target.read_bytes()==(ROOT/'docs/case-studies/downloads/income-analysis-lab.zip').read_bytes()
                    page.goto(base+'demos/dataflow/',wait_until='networkidle');frame=page.frame_locator('iframe')
                    frame.get_by_role('button',name='Skip tour',exact=True).click()
                    expect(frame.get_by_label('Upload dataset file',exact=True)).to_be_disabled()
                    menu=frame.get_by_role('button',name='Open menu',exact=True)
                    if menu.is_visible():menu.click()
                    frame.get_by_role('navigation',name='Workspace',exact=True).get_by_role('button',name='Transformations',exact=True).click()
                    frame.get_by_role('button',name='Preview impact').click();expect(frame.locator('.comparison')).to_contain_text('5 rows')
                    frame.get_by_role('button',name='Apply transformation').click();expect(frame.get_by_role('status')).to_contain_text('The transformation was applied to the local demo.');expect(frame.locator('.footer-summary strong')).to_contain_text('5 preview rows')
                    frame.get_by_role('button',name='Undo latest transformation').click();expect(frame.get_by_role('status')).to_contain_text('The latest completed transformation was reversed.');expect(frame.locator('.footer-summary strong')).to_contain_text('6 preview rows')
                    page.screenshot(path=str(evidence/f'{width}-dataflow.png'))
                    assert not errors,errors;assert not mutations,mutations
                    records.append({'viewport':f'{width}x{height}','passed':['resume download bytes','email target','case study navigation','English pages','income scope and reset','exact prior-year absence','filtered CSV export','SQL archive bytes','DataFlow preview, apply and undo','disabled real-file input'],'runtime_errors':errors,'outbound_mutations':mutations})
                except Exception as error:
                    (evidence/f'{width}-failure.json').write_text(json.dumps({'error':str(error),'runtime_errors':errors,'outbound_mutations':mutations},indent=2))
                    page.screenshot(path=str(evidence/f'{width}-failure.png'),full_page=True);raise
                finally:context.close()
        finally:browser.close()
    return {'status':'passed','base_url':base,'checks':records,'limits':'Chromium smoke coverage; no Power BI native runtime or DataFlow backend integration.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base-url');parser.add_argument('--evidence-dir',type=Path,required=True);args=parser.parse_args();server=None
    if args.base_url:
        p=urlsplit(args.base_url)
        if p.scheme!='https' or p.netloc!='mauriciotaguchi.com.br' or p.path not in ('','/') or p.query or p.fragment:raise ValueError('Unexpected deployed URL')
        base=args.base_url.rstrip('/')+'/'
    else:
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
    try:
        result=check(base,args.evidence_dir);(args.evidence_dir/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    finally:
        if server:server.shutdown();server.server_close()
if __name__=='__main__':main()
