"""Validate authored PBIR JSON schemas; this does not run the Power BI runtime."""
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen
from jsonschema import Draft7Validator, RefResolver
ROOT=Path(__file__).resolve().parents[1]/'content/hiring/income-lab/power-bi'
CACHE={}
def retrieve(url):
    p=urlsplit(url)
    if p.scheme!='https' or p.hostname!='developer.microsoft.com' or not p.path.startswith('/json-schemas/fabric/'):
        raise ValueError('Unexpected schema origin: '+url)
    if url not in CACHE:
        with urlopen(url,timeout=30) as response:CACHE[url]=json.load(response)
    return CACHE[url]
count=0
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.suffix not in ('.json','.pbip','.pbir','.pbism'):continue
    doc=json.loads(p.read_text());url=doc.get('$schema')
    if not url:continue
    schema=retrieve(url);resolver=RefResolver(base_uri=url,referrer=schema,handlers={'https':retrieve})
    errors=list(Draft7Validator(schema,resolver=resolver).iter_errors(doc))
    if errors:raise ValueError(str(p.relative_to(ROOT))+': '+'; '.join(e.message for e in errors[:5]))
    count+=1
print(json.dumps({'status':'passed','schema_documents_checked':count,'native_power_bi_runtime':'not executed'},indent=2))
