"""Reproduce the income case study using only Python's standard library."""
from __future__ import annotations
import argparse, csv, json, sqlite3
from contextlib import contextmanager
from pathlib import Path
ROOT=Path(__file__).resolve().parent

@contextmanager
def load(path:Path):
    connection=sqlite3.connect(':memory:');connection.row_factory=sqlite3.Row
    connection.execute('CREATE TABLE income(quarter_code TEXT, quarter TEXT, year INTEGER, quarter_number INTEGER, state_code INTEGER, state TEXT, region TEXT, income_real_brl REAL CHECK(income_real_brl>0), PRIMARY KEY(quarter_code,state_code))')
    with path.open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            connection.execute('INSERT INTO income VALUES(?,?,?,?,?,?,?,?)',(r['quarter_code'],r['quarter'],int(r['year']),int(r['quarter_number']),int(r['state_code']),r['state'],r['region'],float(r['income_real_brl'])))
    try:
        yield connection
    finally:
        connection.close()

def queries(path:Path):
    for chunk in path.read_text().split('-- query:')[1:]:
        name,query=chunk.split('\n',1);yield name.strip(),query.strip()

def analyze():
    with load(ROOT/'income.csv') as db:
        result={name:[dict(r) for r in db.execute(sql)] for name,sql in queries(ROOT/'queries.sql')}
        result['snapshot']={'rows':db.execute('SELECT COUNT(*) FROM income').fetchone()[0], 'latest_quarter':db.execute('SELECT MAX(quarter_code) FROM income').fetchone()[0], 'scope':'Fixed source snapshot; not a live release.'}
        return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path);args=parser.parse_args()
    result=analyze()
    if args.output_dir:
        # An existing directory is refused to preserve any earlier evidence.
        args.output_dir.mkdir(parents=False,exist_ok=False)
        for name,rows in result.items():
            if isinstance(rows,list):
                with (args.output_dir/(name+'.csv')).open('x',newline='',encoding='utf-8') as f:
                    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        (args.output_dir/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
