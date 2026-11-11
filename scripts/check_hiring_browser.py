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
                page=context.new_page();page.set_default_timeout(20000);errors=[];mutations=[];api_requests=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                def protect(route):
                    if urlsplit(route.request.url).path.startswith('/api/'):
                        api_requests.append(route.request.url)
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
                    for label, filename in [('Resume in Portuguese', 'mauricio-taguchi-curriculo-pt.pdf'), ('Resume in English', 'mauricio-taguchi-resume.pdf')]:
                        link = page.get_by_role('link', name=label, exact=True)
                        expect(link).to_be_in_viewport()
                        with page.expect_download() as d:
                            link.click()
                        with tempfile.TemporaryDirectory() as temp:
                            target = Path(temp) / filename
                            d.value.save_as(target)
                            assert d.value.suggested_filename == filename
                            assert target.read_bytes() == (ROOT / 'docs/resume' / filename).read_bytes()
                    power_bi = page.get_by_role('link', name='Power BI report and 15 DAX checks', exact=True)
                    expect(power_bi).to_be_in_viewport()
                    power_bi.click()
                    expect(page.locator('#power-bi-validation')).to_be_in_viewport()
                    expect(page.get_by_role('link', name='Download the verified Power BI report')).to_be_visible()
                    expect(page.get_by_role('link', name='View the 15 DAX results')).to_be_visible()
                    page.go_back()
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
                    frame.get_by_role('button',name='About this demo',exact=True).click()
                    expect(frame.get_by_role('status')).to_contain_text('Accounts and API connections are unavailable here.')
                    expect(frame.get_by_role('dialog',name='Sign in to DataFlow',exact=True)).to_have_count(0)
                    if menu.is_visible():menu.click()
                    frame.get_by_role('navigation',name='Workspace',exact=True).get_by_role('button',name='Transformations',exact=True).click()
                    frame.get_by_role('button',name='Preview impact').click();expect(frame.locator('.comparison')).to_contain_text('5 rows')
                    frame.get_by_role('button',name='Apply transformation').click();expect(frame.get_by_role('status')).to_contain_text('The transformation was applied to the local demo.');expect(frame.locator('.footer-summary strong')).to_contain_text('5 preview rows')
                    frame.get_by_role('button',name='Undo latest transformation').click();expect(frame.get_by_role('status')).to_contain_text('The latest completed transformation was reversed.');expect(frame.locator('.footer-summary strong')).to_contain_text('6 preview rows')
                    with page.expect_download() as download:
                        frame.get_by_role('button',name='Export preview CSV (up to 100 rows)',exact=True).click()
                    with tempfile.TemporaryDirectory() as temp:
                        target=Path(temp)/'dataflow-preview.csv';download.value.save_as(target)
                        with target.open(encoding='utf-8',newline='') as exported:
                            sample=list(csv.DictReader(exported,strict=True))
                        assert len(sample)==6 and sample[0]['customer']=='Ana Silva'
                        assert sample[3]['total']=='' and sample[4]==sample[5]
                    if menu.is_visible():menu.click()
                    frame.get_by_role('navigation',name='Workspace',exact=True).get_by_role('button',name='Dashboards',exact=True).click()
                    frame.get_by_label('Chart type',exact=True).select_option('scatter')
                    frame.get_by_label('X value',exact=True).select_option('order_id')
                    frame.get_by_label('Y value',exact=True).select_option('total')
                    expect(frame.get_by_label('Aggregation',exact=True)).to_be_disabled()
                    frame.get_by_role('button',name='Build chart',exact=True).click()
                    expect(frame.get_by_role('img',name='Generated scatter chart',exact=True)).to_be_visible()
                    expect(frame.locator('.line-chart circle')).to_have_count(5)
                    positions=frame.locator('.line-chart circle').evaluate_all('(points) => points.map(point => Number(point.getAttribute("cx")))')
                    assert positions==[30,165,300,570,570],positions
                    expect(frame.locator('.chart-notice').filter(has_text='without a finite numeric X/Y pair')).to_contain_text('1 rows without a finite numeric X/Y pair were excluded.')
                    expect(frame.locator('[aria-label="Metric definition"]')).to_contain_text('5 usable X/Y pairs')
                    expect(frame.locator('.chart-canvas .panel-header p')).to_contain_text('from the local preview')
                    frame.get_by_label('Chart type',exact=True).select_option('bar')
                    frame.get_by_label('Aggregation',exact=True).select_option('mean')
                    frame.get_by_label('Chart type',exact=True).select_option('pie')
                    expect(frame.get_by_role('button',name='Build chart',exact=True)).to_be_disabled()
                    expect(frame.get_by_label('Aggregation',exact=True).get_by_role('option',name='mean',exact=True)).to_be_disabled()
                    frame.get_by_label('Aggregation',exact=True).select_option('sum')
                    frame.get_by_label('Dimension',exact=True).select_option('category')
                    frame.get_by_role('button',name='Build chart',exact=True).click()
                    expect(frame.locator('.pie-chart span')).to_have_text('9,495.9')
                    expect(frame.locator('[aria-label="Metric definition"]')).to_contain_text('share of the sum')
                    page.screenshot(path=str(evidence/f'{width}-dataflow.png'))
                    page.goto(base+'demos/dataflow/app/#reset_token=synthetic-demo-boundary-check',wait_until='networkidle')
                    assert 'reset_token' not in page.url
                    expect(page.get_by_role('button',name='Skip tour',exact=True)).to_be_visible()
                    expect(page.get_by_role('dialog',name='Choose a new password',exact=True)).to_have_count(0)
                    expect(page.locator('input[type="password"]')).to_have_count(0)
                    assert not errors,errors;assert not mutations,mutations;assert not api_requests,api_requests
                    records.append({'viewport':f'{width}x{height}','passed':['resume download bytes','email target','case study navigation','English pages','income scope and reset','exact prior-year absence','filtered CSV export','SQL archive bytes','DataFlow preview, apply and undo','sample CSV export','numeric scatter pairs and omitted row notice','additive pie restriction and complete total','visible metric definition','disabled real-file input','account actions unavailable','reset fragment removed without account form'],'runtime_errors':errors,'outbound_mutations':mutations,'api_requests':api_requests})
                except Exception as error:
                    (evidence/f'{width}-failure.json').write_text(json.dumps({'error':str(error),'runtime_errors':errors,'outbound_mutations':mutations,'api_requests':api_requests},indent=2))
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
