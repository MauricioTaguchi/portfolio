"""Build the pinned DataFlow frontend with a sample-only, network-free API boundary."""
from __future__ import annotations
import argparse, hashlib, io, json, shutil, subprocess, tempfile, urllib.request, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMIT='5c06cf8fe97eb0b1158e5d347f92dd845f7bc3b8'

def replace_once(source, before, after):
    if source.count(before) != 1:
        raise ValueError('Pinned demo boundary changed: ' + before)
    return source.replace(before, after)

def adapt_app(source):
    for before, after in [
        ('onConnect={() => openSignIn()}', 'onConnect={() => setNotice("This public demo uses sample data only. Accounts and API connections are unavailable here.")}'),
        ('disabled={combinedBusy} onChange={(event) => { const file', 'disabled={true} onChange={(event) => { const file'),
        ('Explore the sample, or sign in to save your datasets and return to your work later.', 'Explore the sample data here. To save datasets, jobs, and lineage, run the full platform.'),
        ('Explore the sample, or sign in to save and reopen your own work.', 'The sample is ready to explore. Changes stay in this tab and reset when you reload.'),
        ('The service is unavailable right now. You can keep exploring the sample.', 'This demo runs without a backend. Use the full platform for server features.'),
        ('className={`primary file-button${combinedBusy ? " disabled" : ""}`} aria-disabled={combinedBusy}', 'className="primary file-button disabled" aria-disabled={true} title="File uploads are available in the full platform."'),
        ('"Upload dataset"', '"Upload disabled"'),
    ]:
        source = replace_once(source, before, after)
    return source

def adapt_main(source):
    source = replace_once(source,
        'const passwordResetToken = consumePasswordResetToken(window.location, window.history);',
        'consumePasswordResetToken(window.location, window.history);')
    source = replace_once(source, '<App initialResetToken={passwordResetToken} />', '<App />')
    return 'import "./demo-boundary";\n' + source

def verify_chart_scope(source):
    if ' chart records loaded' not in source or ' from the local preview' not in source:
        raise ValueError('Pinned dashboard no longer identifies its preview scope')
    if 'Remaining data is not plotted.' not in source:
        raise ValueError('Pinned dashboard no longer identifies truncated results')
    if 'Pie charts support sum or count only.' not in source or 'Metric definition' not in source:
        raise ValueError('Pinned dashboard no longer explains additive metric semantics')

def source_archive(checkout=None):
    if checkout is not None:
        # Archive the pinned commit, never uncommitted files from a working tree.
        return subprocess.run(['git', '-C', str(checkout), 'archive', '--format=zip', '--prefix=dataflow/', COMMIT, 'frontend', 'LICENSE'], check=True, capture_output=True).stdout
    request=urllib.request.Request(f'https://api.github.com/repos/MauricioTaguchi/data-analytics-platform/zipball/{COMMIT}',headers={'User-Agent':'portfolio-demo-build'})
    with urllib.request.urlopen(request,timeout=60) as response:
        data=response.read(30_000_001)
    if len(data)>30_000_000:
        raise ValueError('Source archive exceeds the size limit')
    return data

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'public/demos/dataflow');parser.add_argument('--source-checkout',type=Path,help='Read the pinned commit from a local Git checkout instead of downloading it');args=parser.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        work=Path(temp)
        data=source_archive(args.source_checkout)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for item in archive.infolist():
                parts=Path(item.filename).parts[1:]
                if not parts or item.is_dir():continue
                relative=Path(*parts)
                if '..' in relative.parts:raise ValueError('Unsafe source archive path')
                if relative.parts[0]=='frontend' or relative==Path('LICENSE'):
                    dest=work/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(archive.read(item))
        front=work/'frontend';app=front/'src/App.tsx'
        app.write_text(adapt_app(app.read_text(encoding='utf-8')),encoding='utf-8')
        sidebar=front/'src/components/WorkspaceSidebar.tsx'
        sidebar_text=sidebar.read_text(encoding='utf-8')
        sidebar.write_text(replace_once(sidebar_text,'"Sign in"','"About this demo"'),encoding='utf-8')
        styles=front/'src/styles.css'
        styles.write_text(styles.read_text(encoding='utf-8')+'\n'+(ROOT/'scripts/dataflow-demo.css').read_text(encoding='utf-8'),encoding='utf-8')
        dashboard=front/'src/components/DashboardWorkspace.tsx'
        verify_chart_scope(dashboard.read_text(encoding='utf-8'))
        main=front/'src/main.tsx';main.write_text(adapt_main(main.read_text(encoding='utf-8')),encoding='utf-8')
        (front/'src/demo-boundary.ts').write_text('import { apiClient } from "./api-client";\napiClient.interceptors.request.use(() => { throw new Error("The public demonstration has no API connection. Use a local checkout for server-backed workflows."); });\n')
        pnpm=shutil.which('pnpm') or 'pnpm'
        subprocess.run([pnpm,'install','--frozen-lockfile'],cwd=front,check=True)
        subprocess.run([pnpm,'typecheck'],cwd=front,check=True)
        subprocess.run([pnpm,'exec','vite','build','--base','/demos/dataflow/app/'],cwd=front,check=True)
        output=args.output;output.mkdir(parents=True,exist_ok=True)
        if (output/'app').exists():shutil.rmtree(output/'app')
        shutil.copytree(front/'dist',output/'app')
        # No upload/account endpoint is reachable; the CSP is additional defense.
        p=output/'app/index.html';html=p.read_text();html=html.replace('<head>','<head>\n<meta http-equiv="Content-Security-Policy" content="connect-src \'none\'; form-action \'none\'; object-src \'none\'; base-uri \'self\'">',1);p.write_text(html)
        notices=[]
        for file in sorted((front/'node_modules/.pnpm').glob('*/node_modules/*/LICENSE*')):
            if file.is_file():notices.append(str(file.relative_to(front/'node_modules'))+'\n'+file.read_text(errors='replace'))
        if (work/'LICENSE').exists():notices.insert(0,'DataFlow project\n'+(work/'LICENSE').read_text())
        (output/'THIRD-PARTY-NOTICES.txt').write_text('\n\n'.join(notices))
        (output/'source.json').write_text(json.dumps({'repository':'MauricioTaguchi/data-analytics-platform','commit':COMMIT,'mode':'Synthetic sample only; in-memory transformations; account actions, API requests and file upload disabled.','adaptations':['About this demo button displays a scope notice','File input disabled with a visible unavailable state','Password reset fragments are removed without opening account actions','API interceptor rejects all requests','connect-src and form-action disabled','Upstream metric definitions, chart limits, totals and preview scope remain unchanged','Guided tour and status explain the sample-only scope','Supporting labels use readable sizes on small screens'],'source_archive_sha256':hashlib.sha256(data).hexdigest()},indent=2))
        if any(p.suffix.lower() in {'.ttf','.woff','.woff2','.otf'} for p in output.rglob('*')):raise ValueError('Unexpected font files in output')
        print('Built isolated sample-only DataFlow frontend from '+COMMIT)
if __name__=='__main__':main()
