"""Targeted cross-browser accessibility, download and lab-performance checks.

Not a WCAG certification or a field Core Web Vitals assessment.
"""
from __future__ import annotations
import argparse, hashlib, json, os, time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def require(value,message):
    if not value:raise AssertionError(message)

def check(base: str, evidence: Path, axe: Path):
    evidence.mkdir(parents=True,exist_ok=True)
    result={'environment':'CI browser checks','scope':'Targeted checks, not full WCAG conformance. CSS 200% zoom and 320px reflow are tested separately.','browsers':[],'lab_performance':[]}
    with sync_playwright() as p:
        for name in ('chromium','firefox'):
            browser=getattr(p,name).launch()
            entry={'browser':name,'version':browser.version,'checks':[],'accessibility':[]}
            result['browsers'].append(entry)
            try:
                for width,height in [(1440,1000),(390,844),(320,844)]:
                    ctx=browser.new_context(viewport={'width':width,'height':height},locale='en-US',reduced_motion='reduce')
                    page=ctx.new_page();errors=[]
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    ctx.route('**/*',lambda route:route.continue_() if route.request.method in ('GET','HEAD','OPTIONS') else route.abort())
                    for route in ('','resume/','blog/','case-studies/','case-studies/brazil-income.html','demos/income/'):
                        response=page.goto(base+route,wait_until='networkidle');require(response and response.status==200,'HTTP failure '+route)
                        require('Taguchi' in page.title(),'Incorrect page identity')
                        expect(page.locator('h1').first).to_be_visible()
                        require(page.locator('vite-error-overlay').count()==0,'Framework overlay')
                        require(page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),'Overflow: '+name+'/'+str(width)+'/'+route)
                        if width==1440:
                            page.add_script_tag(path=str(axe))
                            scan=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
                            entry['accessibility'].append({'route':route,'violations':[{'id':v['id'],'impact':v['impact'],'help':v['help'],'nodes':[n['target'] for n in v['nodes']]} for v in scan['violations']],'incomplete_rule_ids':[x['id'] for x in scan['incomplete']]})
                        (evidence/'quality-results.json').write_text(json.dumps(result,indent=2))
                        if route in ('','resume/','demos/income/'):
                            page.screenshot(path=str(evidence/f'{name}-{width}-{route.split("/")[0] or "home"}.png'))
                    page.goto(base,wait_until='networkidle')
                    if width<600:
                        require(page.locator('.portrait-stage').bounding_box()['y'] >= page.locator('.availability').bounding_box()['y'] + page.locator('.availability').bounding_box()['height'] + 4,'Portrait overlaps hiring copy')
                    page.keyboard.press('Tab')
                    require(page.locator('.skip-link').evaluate('(e)=>e===document.activeElement'),'Skip link is not first')
                    page.keyboard.press('Enter');require(page.evaluate('document.activeElement.id')=='projetos','Skip link did not move focus')
                    if width<600:
                        trigger=page.get_by_role('button',name='Open menu',exact=True)
                        trigger.focus();page.keyboard.press('Enter');expect(page.get_by_role('dialog')).to_be_visible()
                        page.keyboard.press('Tab');require(page.get_by_role('dialog').evaluate('(e)=>e.contains(document.activeElement)'),'Dialog focus escaped')
                        page.keyboard.press('Escape');expect(page.get_by_role('dialog')).to_have_count(0)
                        expect(trigger).to_be_focused()
                    page.goto(base+'resume/',wait_until='networkidle')
                    for label,filename in [('Download résumé (PDF)','mauricio-taguchi-resume.pdf'),('Portuguese résumé (PDF)','mauricio-taguchi-curriculo-pt.pdf')]:
                        anchor=page.get_by_role('link',name=label,exact=True);anchor.focus()
                        with page.expect_download() as d:page.keyboard.press('Enter')
                        got=Path(d.value.path()).read_bytes();expected=(ROOT/'docs/resume'/filename).read_bytes()
                        require(got==expected,'Downloaded résumé differs')
                    if width==1440:
                        page.evaluate('document.documentElement.style.zoom="2"')
                        require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'200% CSS zoom overflow')
                        expect(page.get_by_role('link',name='Portuguese résumé (PDF)',exact=True)).to_be_visible()
                        page.screenshot(path=str(evidence/f'{name}-resume-zoom-200.png'))
                    require(not errors,'Runtime errors: '+';'.join(errors))
                    entry['checks'].append({'viewport':f'{width}x{height}','status':'passed','keyboard':'skip link; menu Enter/Escape/focus return; PDF Enter/download','runtime_errors':errors})
                    ctx.close()
                # Inspect focus on the light panel separately from the dark contact section.
                ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
                page=ctx.new_page();page.goto(base,wait_until='networkidle')
                page.locator('input[name=name]').fill('Example Reader');page.locator('input[name=email]').fill('reader@example.invalid')
                page.locator('textarea[name=message]').fill('A synthetic local message; nothing is submitted.')
                page.get_by_role('button',name='Prepare message',exact=True).click()
                page.get_by_role('textbox',name='Prepared message').focus();page.keyboard.press('Tab')
                button=page.get_by_role('button',name='Copy message',exact=True);expect(button).to_be_focused()
                require(button.evaluate('(e)=>getComputedStyle(e).outlineColor')=='rgb(35, 61, 229)','Light panel focus is not dark blue')
                page.screenshot(path=str(evidence/f'{name}-message-focus.png'));ctx.close()
                (evidence/'quality-results.json').write_text(json.dumps(result,indent=2))
            finally:browser.close()
        browser=p.chromium.launch()
        try:
            for run in range(1,4):
                ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=1)
                page=ctx.new_page();cdp=ctx.new_cdp_session(page)
                cdp.send('Network.enable');cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':150,'downloadThroughput':200000,'uploadThroughput':93750})
                cdp.send('Emulation.setCPUThrottlingRate',{'rate':4})
                page.add_init_script("""window.observed={lcp:0,shifts:[],events:[]};
new PerformanceObserver(l=>{for(const e of l.getEntries())observed.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)observed.shifts.push({t:e.startTime,v:e.value})}).observe({type:'layout-shift',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries())if(e.interactionId)observed.events.push(e.duration)}).observe({type:'event',durationThreshold:16,buffered:true});""")
                page.goto(base,wait_until='load');page.wait_for_timeout(6000)
                data=page.evaluate("({lcp:observed.lcp,shifts:observed.shifts,fcp:performance.getEntriesByName('first-contentful-paint')[0]?.startTime||null,transfer:performance.getEntriesByType('resource').reduce((s,e)=>s+e.transferSize,0)})")
                peak=total=0;start=last=0
                for shift in data['shifts']:
                    if shift['t']-last>1000 or shift['t']-start>5000:total=0;start=shift['t']
                    total+=shift['v'];peak=max(peak,total);last=shift['t']
                page.get_by_role('button',name='Open menu',exact=True).click();expect(page.get_by_role('dialog')).to_be_visible();page.keyboard.press('Escape');page.wait_for_timeout(200)
                events=page.evaluate('observed.events')
                result['lab_performance'].append({'run':run,'LCP_ms':round(data['lcp'],1),'CLS':round(peak,5),'FCP_ms':data['fcp'],'resource_transfer_bytes':data['transfer'],'max_recorded_interaction_event_ms':max(events) if events else None})
                ctx.close()
        finally:browser.close()
    result['performance_conditions']={'network':'150ms added latency; 1.6Mbps download; 0.75Mbps upload','cpu':'4x slowdown','viewport':'390x844','measurement_window':'load plus 6 seconds, then menu open/close','field_INP':'not measured; event duration is a limited lab observation, not field INP','coverage':'Homepage only; three cold contexts, not real-user percentile data.'}
    (evidence/'quality-results.json').write_text(json.dumps(result,indent=2))
    violations=[(b['browser'],r) for b in result['browsers'] for r in b['accessibility'] if r['violations']]
    if violations:raise AssertionError('Accessibility findings retained in quality-results.json')
    print(json.dumps(result,indent=2));return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-dir',type=Path,required=True);parser.add_argument('--axe',type=Path,required=True);parser.add_argument('--base-url');args=parser.parse_args()
    server=None
    try:
        if args.base_url:base=args.base_url.rstrip('/')+'/'
        else:
            server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
        check(base,args.evidence_dir,args.axe)
    finally:
        if server:server.shutdown();server.server_close()
if __name__=='__main__':main()
