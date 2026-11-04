"""Build the pinned DataFlow frontend with a sample-only, network-free API boundary."""
from __future__ import annotations
import argparse, hashlib, io, json, shutil, subprocess, tempfile, urllib.request, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMIT='d61eaf9780238b1bacc741eec4f645e2f53c4360'

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'public/demos/dataflow');args=parser.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        work=Path(temp)
        request=urllib.request.Request(f'https://api.github.com/repos/MauricioTaguchi/data-analytics-platform/zipball/{COMMIT}',headers={'User-Agent':'portfolio-demo-build'})
        with urllib.request.urlopen(request,timeout=60) as response:data=response.read(30_000_000)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for item in archive.infolist():
                parts=Path(item.filename).parts[1:]
                if not parts or item.is_dir():continue
                relative=Path(*parts)
                if '..' in relative.parts:raise ValueError('Unsafe source archive path')
                if str(relative).startswith('frontend/') or str(relative)=='LICENSE':
                    dest=work/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(archive.read(item))
        front=work/'frontend';app=front/'src/App.tsx'
        original=app.read_text()
        old='onConnect={() => setConnectionOpen(true)}'
        if old not in original:raise ValueError('Pinned connection hook changed')
        adapted=original.replace(old,'onConnect={() => setNotice("This public demo uses sample data only. API connections are disabled.")}')
        adapted=adapted.replace('disabled={combinedBusy} onChange={(event) => { const file', 'disabled={true} onChange={(event) => { const file')
        app.write_text(adapted)
        main=front/'src/main.tsx';main.write_text('import "./demo-boundary";\n'+main.read_text())
        (front/'src/demo-boundary.ts').write_text('import { apiClient } from "./api-client";\napiClient.interceptors.request.use(() => { throw new Error("The public demonstration has no API connection. Use a local checkout for server-backed workflows."); });\n')
        subprocess.run(['pnpm','install','--frozen-lockfile'],cwd=front,check=True)
        subprocess.run(['pnpm','typecheck'],cwd=front,check=True)
        subprocess.run(['pnpm','exec','vite','build','--base','/demos/dataflow/app/'],cwd=front,check=True)
        output=args.output;output.mkdir(parents=True,exist_ok=True)
        shutil.copytree(front/'dist',output/'app',dirs_exist_ok=True)
        # No upload/account endpoint is reachable; the CSP is additional defense.
        p=output/'app/index.html';html=p.read_text();html=html.replace('<head>','<head>\n<meta http-equiv="Content-Security-Policy" content="connect-src \'none\'; form-action \'none\'; object-src \'none\'; base-uri \'self\'">',1);p.write_text(html)
        notices=[]
        for file in sorted((front/'node_modules/.pnpm').glob('*/node_modules/*/LICENSE*')):
            if file.is_file():notices.append(str(file.relative_to(front/'node_modules'))+'\n'+file.read_text(errors='replace'))
        if (work/'LICENSE').exists():notices.insert(0,'DataFlow project\n'+(work/'LICENSE').read_text())
        (output/'THIRD-PARTY-NOTICES.txt').write_text('\n\n'.join(notices))
        (output/'source.json').write_text(json.dumps({'repository':'MauricioTaguchi/data-analytics-platform','commit':COMMIT,'mode':'Synthetic sample only; in-memory transformations; API requests and file upload disabled.','adaptations':['Connection button displays a demo notice','File input disabled','API interceptor rejects all requests','connect-src and form-action disabled'],'source_archive_sha256':hashlib.sha256(data).hexdigest()},indent=2))
        if any(p.suffix.lower() in {'.ttf','.woff','.woff2','.otf'} for p in output.rglob('*')):raise ValueError('Unexpected font files in output')
        print('Built isolated sample-only DataFlow frontend from '+COMMIT)
if __name__=='__main__':main()
