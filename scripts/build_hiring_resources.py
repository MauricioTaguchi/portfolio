"""Build public hiring resources from reviewed content and a pinned data snapshot."""
from __future__ import annotations
import csv, hashlib, html, io, json, shutil, sqlite3, zipfile
from pathlib import Path
from reportlab import rl_config
rl_config.invariant = 1
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public'
SOURCE=PUBLIC/'case-studies/data/income.csv'
BASE='https://mauriciotaguchi.com.br'
INCOME_COMMIT='5810d34116d0e8da9ab10005c561359e73a8560a'
DATAFLOW_COMMIT='d61eaf9780238b1bacc741eec4f645e2f53c4360'

def write(path:Path,text:str):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

def load_income():
    with SOURCE.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    for r in rows:
        for k in ('year','quarter_number','state_code'):r[k]=int(r[k])
        r['income_real_brl']=float(r['income_real_brl'])
    if len(rows)!=540 or len({(r['quarter_code'],r['state_code']) for r in rows})!=540:
        raise ValueError('Unexpected snapshot grain or duplicates')
    if any(len({r['state_code'] for r in rows if r['quarter_code']==q})!=27 for q in {r['quarter_code'] for r in rows}):
        raise ValueError('Incomplete federal-unit coverage')
    return rows

def page(title,description,body,relative):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — Maurício Taguchi</title><meta name="description" content="{html.escape(description,quote=True)}"><link rel="canonical" href="{BASE}/{relative}"><link rel="stylesheet" href="/case-studies/styles.css"><link rel="icon" href="/favicon.svg"></head><body><a class="skip" href="#content">Skip to content</a><header class="top"><a class="brand" href="/">TM<span>.</span></a><nav aria-label="Main navigation"><a href="/">Portfolio</a><a href="/case-studies/">Case studies</a><a href="/blog/">Blog</a><a href="/resume/">Resume</a></nav></header><main id="content">{body}</main><footer><span>Maurício Taguchi · Data analysis and BI</span><a href="mailto:mauricioryotoitataguchi@gmail.com">Email me</a></footer></body></html>'''

def resume():
    from build_resumes import build_resumes
    build_resumes(ROOT, page)


def cases(rows):
    last=max(r['quarter_code'] for r in rows);latest=[r for r in rows if r['quarter_code']==last];mean=sum(r['income_real_brl'] for r in latest)/len(latest)
    high=max(latest,key=lambda r:r['income_real_brl']);low=min(latest,key=lambda r:r['income_real_brl'])
    source=f'https://github.com/MauricioTaguchi/analise-renda-brasil/tree/{INCOME_COMMIT}'
    dataflow=f'https://github.com/MauricioTaguchi/data-analytics-platform/tree/{DATAFLOW_COMMIT}'
    introduction='<div class="eyebrow">SELECTED WORK / EVIDENCE AND TRADE-OFFS</div><h1>From a question<br>to a working answer.</h1><p class="lead">Two projects that connect analytical reasoning, reliable data and explainable implementation.</p>'
    cards=f'''<div class="cards"><article><span class="eyebrow">01 / DATA ANALYSIS</span><h2>Income across Brazil</h2><p>A pinned public-data snapshot, SQL questions and an interactive view of federal-unit income.</p><a class="button" href="brazil-income.html">Read income case study</a></article><article><span class="eyebrow">02 / DATA QUALITY</span><h2>DataFlow</h2><p>Explore a dataset, preview a change and understand why recovery and version history matter.</p><a class="button" href="dataflow.html">Read DataFlow case study</a></article></div><section class="note"><h2>Evaluate the work directly.</h2><p>Open the income dashboard without installing anything, inspect the SQL lab, or read the source and its stated limits.</p><div class="actions"><a href="/demos/income/">Open income dashboard</a><a href="downloads/income-analysis-lab.zip" download>Download SQL lab</a><a href="/resume/">Resume and contact</a></div></section>'''
    write(PUBLIC/'case-studies/index.html',page('Case studies','Analytical and engineering case studies with reproducible sources and explicit limits.',introduction+cards,'case-studies/'))
    body=f'''<div class="eyebrow">CASE STUDY 01 / PYTHON · SQL · BI</div><h1>Income across Brazil.<br><span>Compare earnings across states and quarters.</span></h1><p class="lead">Explore Brazil’s 26 states and the Federal District: 27 federal units. The dashboard’s simple average is not the official national estimate.</p><div class="actions"><a class="button" href="/demos/income/">Open interactive dashboard</a><a class="button secondary" href="downloads/income-analysis-lab.zip" download>Download SQL lab</a></div><div class="facts"><div><strong>540</strong><span>state-quarter observations</span></div><div><strong>27</strong><span>federal units per quarter</span></div><div><strong>20</strong><span>quarters in this snapshot</span></div></div><h2>The question</h2><p>How do average real monthly earnings vary across Brazil’s federal units? How did earnings change compared with the same quarter a year earlier? The intended reader is an analyst comparing places and periods, not estimating an individual’s salary.</p><h2>My contribution</h2><p>This personal project combines extraction from IBGE SIDRA, a normalized dataset, coverage checks, a dashboard and an executive summary. This case study adds explicit SQL questions and a browser-based view so the analytical choices can be inspected before running the project.</p><h2>Data and analytical decisions</h2><p>The source is SIDRA table 6472, variable 5933. The grain is one federal unit per quarter. The committed extract is dated <strong>15 August 2026</strong> and spans Q2 2021–Q1 2026. This is a fixed historical snapshot, not a live feed or a claim to the latest available release.</p><p>State values must not be summed. The dashboard’s multi-state value is an <strong>unweighted mean of the selected federal units</strong>; it is not the official population-weighted national estimate. Year-over-year comparisons join the same quarter in the prior year rather than assuming four preceding rows always exist.</p><h2>What this snapshot shows</h2><p>For Q1 2026, the simple mean across all 27 federal units is <strong>BRL {mean:,.2f}</strong>. {html.escape(high['state'])} has the highest value (BRL {high['income_real_brl']:,.2f}) and {html.escape(low['state'])} the lowest (BRL {low['income_real_brl']:,.2f}). These are descriptive observations from this snapshot, not causal explanations.</p><h2>How to inspect the result</h2><ol><li>Open the dashboard and select a quarter, region or state.</li><li>Read the scope and comparison coverage alongside the metrics.</li><li>Inspect the ranking and time series, then export the displayed rows.</li><li>Run the SQL lab to reproduce coverage, ranking, regional means and exact year-over-year joins.</li></ol><h2 id="power-bi-validation">Power BI Desktop validation</h2><p>The report was refreshed in Power BI Desktop 2.159.1231.0 on 4 November 2026. All 15 DAX checks passed. In Q1 2026 the Southeast slicer returned four federal units and a mean of BRL 3,971.50. With all regions selected in Q2 2021, the year-over-year card was blank because the snapshot has no prior-year observation for that quarter.</p><p><a href="downloads/BrazilIncome_Validado.pbix" download>Download the verified Power BI report</a> · <a href="downloads/BrazilIncome_15_testes.png">View the 15 DAX results</a> · <a href="downloads/BrazilIncome_Q1_2026.png">View the report with Q1 2026 selected</a></p><p>The SQL lab ZIP includes the editable Power BI project, the DAX query and the same verified report and screenshots.</p><h2>Limitations</h2><p>No population weights, confidence intervals or causal model are supplied in this snapshot. Regional means describe their member states equally. Revisions to the underlying statistical series may change historical values. The data does not establish a company’s hiring outcomes or individual earnings.</p><h2>Source and reproducibility</h2><p><a href="{source}">Pinned source repository</a> · <a href="{source}/docs/EXECUTIVE_SUMMARY.md">Original executive summary</a> · <a href="data/income.csv" download>Exact CSV snapshot</a></p><p class="small">Source commit: {INCOME_COMMIT}. Snapshot SHA-256: {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}.</p>'''
    write(PUBLIC/'case-studies/brazil-income.html',page('Brazil income analysis','A reproducible case study of quarterly income data, its grain, SQL queries and interpretation.',body,'case-studies/brazil-income.html'))
    body=f'''<div class="eyebrow">CASE STUDY 02 / PYTHON · FASTAPI · REACT · POSTGRESQL</div><h1>Data preparation<br><span>with a traceable history.</span></h1><p class="lead">DataFlow makes the path from a raw file to a transformation explicit, including what happens when an operation must be retried or undone.</p><div class="actions"><a class="button" href="/demos/dataflow/">Explore the isolated demo</a><a class="button secondary" href="{dataflow}">Inspect the source</a></div><section class="note"><strong>Portfolio reference implementation.</strong><p>The hosted frontend uses synthetic sample data and temporary, in-memory edits. It does not run the backend, verify durable recovery, or accept an API connection.</p></section><h2>The problem</h2><p>Cleaning data is not only a sequence of successful operations. A request can be retried, a worker can disappear, and a dataset can change while an earlier job is still running. A useful interface must make current data, change history and failure boundaries understandable.</p><h2>My contribution</h2><p>This personal project connects a React workspace to a FastAPI backend, PostgreSQL metadata, Celery workers and Redis coordination. Its documented implementation covers imports, quality inspection, transformation previews, revision-aware changes and recovery. The project is separate from my professional work at FIPE.</p><h2>Decisions worth inspecting</h2><div class="table-wrap"><table><thead><tr><th>Problem</th><th>Design choice</th><th>Evidence in the repository</th></tr></thead><tbody><tr><td>A stale transformation finishes late</td><td>Expected revisions and conditional publication</td><td><a href="{dataflow}/backend/tests/test_dataset_concurrency.py">Concurrency tests</a></td></tr><tr><td>An undo response is lost</td><td>Idempotency keys and durable operation receipts</td><td><a href="{dataflow}/backend/tests/test_dataset_audit_receipts.py">Receipt tests</a></td></tr><tr><td>A broker or worker fails</td><td>Transactional outbox, leases and a recovery scheduler</td><td><a href="{dataflow}/backend/tests/test_outbox_recovery.py">Recovery tests</a></td></tr><tr><td>Historical bytes are damaged</td><td>Snapshot digests checked before restoration</td><td><a href="{dataflow}/backend/tests/test_snapshot_integrity.py">Integrity tests</a></td></tr></tbody></table></div><h2>A short evaluation journey</h2><ol><li>Open the isolated demo and dismiss or follow the guided tour.</li><li>Inspect the sample dataset and its missing or duplicated values.</li><li>Preview a transformation before applying it.</li><li>Inspect the resulting history and undo the demo change.</li><li>Reload to confirm that the frontend demo does not persist dataset edits.</li></ol><h2>What the result demonstrates</h2><p>The browser demo demonstrates the workspace and local user journey. The repository exposes the backend’s contracts and test procedures. Neither a frontend demo nor a list of test files establishes production reliability: live recovery requires the separate process-integration suite and disposable database/broker services.</p><h2>Trade-offs and next engineering work</h2><p>Local versioned files make development reproducible, but horizontally scaled production requires a shared runtime storage design. The project documents additional work for high availability, telemetry, formal operating objectives and independent security review. No customer adoption, measured business savings or production service guarantee is claimed here.</p><h2>Continue the investigation</h2><p><a href="{dataflow}/docs/ARCHITECTURE.md">Architecture</a> · <a href="{dataflow}/docs/LIMITATIONS.md">Known limitations</a> · <a href="{dataflow}/docs/PROCESSING_RECOVERY.md">Recovery procedure</a> · <a href="/blog/data-revisions.html">The small revision tutorial</a></p><p class="small">Demo source: {DATAFLOW_COMMIT}. Hosting adds an isolated demonstration boundary; it does not change the main project repository.</p>'''
    write(PUBLIC/'case-studies/dataflow.html',page('DataFlow case study','Data quality and traceable transformations, with an isolated demo and documented engineering boundaries.',body,'case-studies/dataflow.html'))


def package_income_lab():
    lab=ROOT/'content/hiring/income-lab'
    shutil.copyfile(SOURCE,lab/'income.csv')
    target=PUBLIC/'case-studies/downloads/income-analysis-lab.zip';target.parent.mkdir(parents=True,exist_ok=True)
    for name in ('BrazilIncome_Validado.pbix', 'BrazilIncome_15_testes.png', 'BrazilIncome_Q1_2026.png'):
        shutil.copyfile(lab/'power-bi'/name, target.parent/name)
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(lab.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc':
                info=zipfile.ZipInfo(path.relative_to(lab).as_posix(),(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())

def main():
    rows=load_income();resume();cases(rows)
    write(PUBLIC/'demos/income/data.js','window.INCOME_DATA='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n')
    package_income_lab()
    print('Built English résumé, two case studies and the pinned income data payload.')
if __name__=='__main__':main()
