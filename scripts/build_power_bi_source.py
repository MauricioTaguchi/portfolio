"""Author a portable Power BI project source; Desktop validation remains separate."""
from __future__ import annotations
import base64,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'content/hiring/income-lab/power-bi'
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/'
def save(name,data):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def source(values,typ):
    encoded=base64.b64encode(json.dumps(values,ensure_ascii=False).encode()).decode()
    return ['let',f'    Source = Table.FromRows(Json.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64)), type table [{typ}])','in','    Source']
def table(name,cols,values,typ,measures=None):
    return {'name':name,'columns':[{'name':n,'dataType':t,'sourceColumn':n,'summarizeBy':'none'} for n,t in cols], 'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':source(values,typ)}}],**({'measures':measures} if measures else {})}
def projection(entity,prop,measure=False):
    kind='Measure' if measure else 'Column'
    return {'field':{kind:{'Expression':{'SourceRef':{'Entity':entity}},'Property':prop}},'queryRef':f'{entity}.{prop}','nativeQueryRef':prop}
def visual(name,kind,x,y,w,h,roles,title):
    title_properties = {
        'show': {'expr': {'Literal': {'Value': 'true'}}},
        'text': {'expr': {'Literal': {'Value': "'" + title + "'"}}},
    }
    return {
        '$schema': SCHEMA+'item/report/definition/visualContainer/1.0.0/schema.json',
        'name': name,
        'position': {'x':x,'y':y,'z':0,'width':w,'height':h,'tabOrder':0},
        'visual': {
            'visualType': kind,
            'query': {'queryState': {k:{'projections':v} for k,v in roles.items()}},
            'visualContainerObjects': {'title': [{'properties':title_properties}]},
            'drillFilterOtherVisuals': True,
        },
    }
def main():
    with (ROOT/'public/case-studies/data/income.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
    states={int(r['state_code']):(r['state'],r['region']) for r in rows};quarters={int(r['quarter_code']):r['quarter'] for r in rows}
    measures=[
      {'name':'Income - unweighted state mean','expression':'VAR p = MAX(Quarters[quarter_code]) RETURN CALCULATE(AVERAGE(Income[income_real_brl]), REMOVEFILTERS(Quarters), Quarters[quarter_code] = p)','formatString':'"BRL "#,0.00'},
      {'name':'Federal units in view','expression':'VAR p = MAX(Quarters[quarter_code]) RETURN CALCULATE(DISTINCTCOUNT(Income[state_code]), REMOVEFILTERS(Quarters), Quarters[quarter_code] = p)','formatString':'0'},
      {'name':'Prior year income','expression':'VAR p = MAX(Quarters[quarter_code]) - 100 RETURN CALCULATE(AVERAGE(Income[income_real_brl]), REMOVEFILTERS(Quarters), Quarters[quarter_code] = p)','formatString':'"BRL "#,0.00'},
      {'name':'Prior year federal units','expression':'VAR p = MAX(Quarters[quarter_code]) - 100 RETURN CALCULATE(DISTINCTCOUNT(Income[state_code]), REMOVEFILTERS(Quarters), Quarters[quarter_code] = p)','formatString':'0'},
      {'name':'YoY change','expression':'IF([Federal units in view] = [Prior year federal units] && [Prior year federal units] > 0, DIVIDE([Income - unweighted state mean] - [Prior year income], [Prior year income]), BLANK())','formatString':'0.00%;-0.00%;0.00%'},
    ]
    fact=table('Income',[('quarter_code','int64'),('state_code','int64'),('income_real_brl','double')],[[int(r['quarter_code']),int(r['state_code']),float(r['income_real_brl'])] for r in rows],'quarter_code=Int64.Type, state_code=Int64.Type, income_real_brl=number',measures)
    model={'name':'BrazilIncome','compatibilityLevel':1567,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'en-US','tables':[fact,table('States',[('state_code','int64'),('state','string'),('region','string')],[[k,*v] for k,v in sorted(states.items())],'state_code=Int64.Type, state=text, region=text'),table('Quarters',[('quarter_code','int64'),('quarter','string')],[[k,v] for k,v in sorted(quarters.items())],'quarter_code=Int64.Type, quarter=text')],'relationships':[{'name':'IncomeStates','fromTable':'Income','fromColumn':'state_code','toTable':'States','toColumn':'state_code','fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'},{'name':'IncomeQuarters','fromTable':'Income','fromColumn':'quarter_code','toTable':'Quarters','toColumn':'quarter_code','fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'}],'annotations':[{'name':'__PBI_TimeIntelligenceEnabled','value':'0'}]}}
    model['model']['tables'][2]['columns'][1]['sortByColumn']='quarter_code'
    save('BrazilIncome.pbip',{'$schema':SCHEMA+'pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'BrazilIncome.Report'}}],'settings':{'enableAutoRecovery':True}})
    save('BrazilIncome.SemanticModel/definition.pbism',{'$schema':SCHEMA+'item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.0','settings':{}})
    save('BrazilIncome.SemanticModel/model.bim',model)
    save('BrazilIncome.Report/definition.pbir',{'$schema':SCHEMA+'item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../BrazilIncome.SemanticModel'}}})
    save('BrazilIncome.Report/definition/version.json',{'$schema':SCHEMA+'item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
    save('BrazilIncome.Report/definition/report.json',{'$schema':SCHEMA+'item/report/definition/report/1.0.0/schema.json','layoutOptimization':'None','themeCollection':{'baseTheme':{'name':'CY24SU06','reportVersionAtImport':'5.55','type':'SharedResources'}}})
    save('BrazilIncome.Report/definition/pages/pages.json',{'$schema':SCHEMA+'item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':['overview'],'activePageName':'overview'})
    save('BrazilIncome.Report/definition/pages/overview/page.json',{'$schema':SCHEMA+'item/report/definition/page/1.0.0/schema.json','name':'overview','displayName':'Income - unweighted state estimates','displayOption':'FitToPage','height':720,'width':1280})
    visuals=[
      visual('quarter','slicer',20,20,230,110,{'Values':[projection('Quarters','quarter')]},'Quarter (latest selected quarter used)'),
      visual('region','slicer',270,20,230,110,{'Values':[projection('States','region')]},'Region'),
      visual('income','card',530,20,330,110,{'Values':[projection('Income','Income - unweighted state mean',True)]},'Unweighted state mean - BRL'),
      visual('change','card',890,20,330,110,{'Values':[projection('Income','YoY change',True)]},'Year-over-year change'),
      visual('ranking','clusteredBarChart',20,160,600,530,{'Category':[projection('States','state')],'Y':[projection('Income','Income - unweighted state mean',True)]},'Federal-unit comparison - BRL'),
      visual('trend','lineChart',650,160,590,330,{'Category':[projection('Quarters','quarter')],'Y':[projection('Income','Income - unweighted state mean',True)]},'Income in the selected quarter scope'),
      visual('coverage','card',650,520,590,150,{'Values':[projection('Income','Federal units in view',True)]},'Federal units represented'),
    ]
    for v in visuals:save('BrazilIncome.Report/definition/pages/overview/visuals/'+v['name']+'/visual.json',v)
    (OUT/'measures.dax').write_text('\n\n'.join(m['name']+' =\n'+m['expression'] for m in measures)+'\n')
    (OUT/'README.md').write_text('''# Power BI project source — Desktop validation pending

This is an authored PBIP/PBIR source project, not a verified PBIX or a published service report. The current delivery environment did not expose the installed plugin's browser controls. DAX, Power Query refresh, interactions and rendering have NOT been executed inside Power BI.

The model contains 540 income observations, 27 state dimension rows and 20 quarter rows. Its M partitions embed the exact reviewed snapshot, so no file paths, account credentials or live API access are required. Embedded data is intentionally static. The model has one-to-many state and quarter relationships, with single-direction filtering. State means are not additive.

## Acceptance checklist in Power BI Desktop

1. Open BrazilIncome.pbip with a Power BI Desktop version supporting PBIP and PBIR.
2. Refresh the embedded import tables. Confirm 540 Income, 27 States and 20 Quarters rows.
3. Check the two relationships and sort Quarters[quarter] by quarter_code.
4. Inspect every visual; correct any reported schema/visual compatibility errors before publishing.
5. Select Q1 2026 and all regions. The unweighted state mean should be BRL 3,437.41. This is NOT the official national average.
6. Filter to Distrito Federal. Q1 2026 income should be BRL 6,720.00. Select Q2 2021: the prior-year comparison must be blank.
7. Check that the quarter slicer limits the trajectory; clear it to see the full snapshot. Measures use the latest selected quarter when more than one is selected.
8. Save the verified report as PBIX only after refresh and visual checks. Record the actual Desktop version and result; do not mark this checklist complete in advance.

The browser dashboard is a separate, tested implementation, not a substitute for these native checks. No account, workspace, license purchase or Publish to web operation has been created.

References:
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset
''')
    print('Authored Power BI project source; native refresh and visual validation remain pending.')
if __name__=='__main__':main()
