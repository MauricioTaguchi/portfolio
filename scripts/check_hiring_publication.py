"""Wait for the exact reviewed hiring resources, not just an HTTP 200 response."""
import json,time
from pathlib import Path
from urllib.request import HTTPRedirectHandler,Request,build_opener
from urllib.parse import quote,urlsplit
ROOT=Path(__file__).resolve().parents[1]
HOST='mauriciotaguchi.com.br'
class SameOrigin(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        p=urlsplit(newurl)
        if p.scheme!='https' or p.netloc!=HOST:raise ValueError('Unexpected publication redirect')
        return super().redirect_request(req,fp,code,msg,headers,newurl)
files=[ROOT/'docs/index.html']
for folder in ['resume','case-studies','demos']:
    files.extend(p for p in (ROOT/'docs'/folder).rglob('*') if p.is_file())
if len(files)<10:raise ValueError('Incomplete publication inventory')
expected={str(p.relative_to(ROOT/'docs')):p.read_bytes() for p in files}
deadline=time.monotonic()+240;attempts=0;reason='No response'
while time.monotonic()<deadline:
    attempts+=1
    try:
        for name,data in expected.items():
            remaining=deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Publication deadline exceeded')
            request=Request('https://'+HOST+'/'+quote(name,safe='/'),headers={'Cache-Control':'no-cache','User-Agent':'Portfolio-hiring-check'})
            with build_opener(SameOrigin()).open(request,timeout=min(15,remaining)) as response:
                if response.status!=200 or response.read(len(data)+1)!=data:raise ValueError('Content mismatch: '+name)
        print(json.dumps({'status':'passed','files_compared':len(files),'attempts':attempts}));break
    except (OSError,ValueError) as error:reason=str(error)
    time.sleep(min(8,max(0,deadline-time.monotonic())))
else:raise TimeoutError('Published hiring resources did not match: '+reason)
