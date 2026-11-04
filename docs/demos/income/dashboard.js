'use strict';
(() => {
  const rows = window.INCOME_DATA;
  const $ = (id) => document.getElementById(id);
  const money = new Intl.NumberFormat('en-US', {minimumFractionDigits:2,maximumFractionDigits:2});
  const pct = (v) => v === null ? 'Unavailable' : `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;
  const mean = (values) => values.length ? values.reduce((s,r)=>s+r.income_real_brl,0)/values.length : null;
  const quarters = [...new Set(rows.map(r=>r.quarter_code))].sort();
  const states = [...new Map(rows.map(r=>[r.state_code,r])).values()].sort((a,b)=>a.state.localeCompare(b.state,'en'));
  const lookup = new Map(rows.map(r=>[`${r.quarter_code}:${r.state_code}`,r]));
  const option = (value,text) => { const o=document.createElement('option');o.value=value;o.textContent=text;return o; };
  quarters.slice().reverse().forEach(q=>$('quarter').append(option(q,rows.find(r=>r.quarter_code===q).quarter)));
  [...new Set(rows.map(r=>r.region))].sort().forEach(r=>$('region').append(option(r,r)));
  function rebuildStates(){
    const previous=$('state').value; $('state').replaceChildren(option('','All federal units'));
    states.filter(r=>!$('region').value||r.region===$('region').value).forEach(r=>$('state').append(option(String(r.state_code),r.state)));
    if([...$('state').options].some(o=>o.value===previous))$('state').value=previous;
  }
  function selected(r){return (!$('region').value||r.region===$('region').value)&&(!$('state').value||String(r.state_code)===$('state').value);}
  function prior(r){const code=String((r.year-1)*100+r.quarter_number);return lookup.get(`${code}:${r.state_code}`);}
  function yoy(r){const p=prior(r);return p&&p.income_real_brl!==0?(r.income_real_brl/p.income_real_brl-1)*100:null;}
  const svgNS='http://www.w3.org/2000/svg';
  function el(tag,attrs,text){const n=document.createElementNS(svgNS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text!==undefined)n.textContent=text;return n;}
  function trend(){
    const s=$('trend');s.replaceChildren(el('title',{id:'trend-title'},'Real monthly income in BRL across 20 quarters for the selected geography.'));
    const data=quarters.map(q=>mean(rows.filter(r=>r.quarter_code===q&&selected(r))));
    const max=Math.ceil(Math.max(...data.filter(v=>v!==null))/1000)*1000;
    for(let j=0;j<=4;j++){
      const y=230-j*50;s.append(el('line',{x1:62,x2:480,y1:y,y2:y,stroke:'#dce1e9'}));
      s.append(el('text',{x:54,y:y+4,'text-anchor':'end',fill:'#5c6578','font-size':12},String(Math.round(max*j/4))));
    }
    const points=data.map((v,i)=>`${62+i*418/(data.length-1)},${230-v/max*200}`).join(' ');
    s.append(el('polyline',{points,fill:'none',stroke:'#233de5','stroke-width':3}));
    data.forEach((v,i)=>{const c=el('circle',{cx:62+i*418/(data.length-1),cy:230-v/max*200,r:3,fill:'#233de5'});c.append(el('title',{},`${rows.find(r=>r.quarter_code===quarters[i]).quarter}: BRL ${money.format(v)}`));s.append(c);});
    s.append(el('text',{x:62,y:260,fill:'#5c6578','font-size':12},'Q2 2021'));
    s.append(el('text',{x:480,y:260,'text-anchor':'end',fill:'#5c6578','font-size':12},'Q1 2026'));
  }
  function render(){
    const view=rows.filter(r=>r.quarter_code===$('quarter').value&&selected(r)).sort((a,b)=>b.income_real_brl-a.income_real_brl);
    const current=mean(view);const previous=view.map(prior).filter(Boolean);const full=previous.length===view.length;
    $('income').textContent=money.format(current);$('income-label').textContent=view.length===1?'Selected federal-unit income':'Unweighted mean of displayed federal units';
    $('change').textContent=full?pct((current/mean(previous)-1)*100):'Unavailable';
    $('comparison').textContent=full?`${previous.length} of ${view.length} exact prior-year matches`:`${previous.length} of ${view.length} prior-year matches; no full comparison`;
    $('coverage').textContent=String(view.length);$('period').textContent=view[0].quarter;
    $('scope').textContent=`${view[0].quarter} · ${$('region').value||'All regions'} · ${$('state').selectedOptions[0].textContent}`;
    $('ranking').replaceChildren();$('details').replaceChildren();
    for(const r of view){
      const li=document.createElement('li');li.className='bar-row';const line=document.createElement('span');const label=document.createElement('span');label.textContent=r.state;const value=document.createElement('span');value.textContent=money.format(r.income_real_brl);line.append(label,value);const bar=document.createElement('div');bar.className='bar';bar.style.width=`${r.income_real_brl/view[0].income_real_brl*100}%`;li.append(line,bar);$('ranking').append(li);
      const tr=document.createElement('tr');[r.quarter,r.state,r.region,money.format(r.income_real_brl),pct(yoy(r))].forEach(t=>{const td=document.createElement('td');td.textContent=t;tr.append(td);});$('details').append(tr);
    }
    trend();
  }
  $('region').addEventListener('change',()=>{rebuildStates();render();});['quarter','state'].forEach(id=>$(id).addEventListener('change',render));
  $('reset').addEventListener('click',()=>{$('quarter').value=quarters.at(-1);$('region').value='';$('state').value='';rebuildStates();render();});
  $('export').addEventListener('click',()=>{
    const cols=['quarter_code','quarter','state_code','state','region','income_real_brl'];const chosen=rows.filter(r=>r.quarter_code===$('quarter').value&&selected(r));
    const quote=(v)=>'"'+String(v).replaceAll('"','""')+'"';
    const text=cols.join(',')+'\r\n'+chosen.map(r=>cols.map(k=>quote(r[k])).join(',')).join('\r\n')+'\r\n';
    const url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`income-view-${$('quarter').value}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  rebuildStates();render();
})();
