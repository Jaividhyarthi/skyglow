/* Progressive enhancement: Stitch artwork remains, verified live results come from FastAPI. */
(()=>{'use strict';
const routes={'investigation-home':'/','workspace':'/workspace','network-explorer':'/network','voice-investigator':'/voice','reputation-profile':'/reputation','research-lab':'/research','extension-preview':'/extension-preview'};
let report=null,loading=false;
const liveWorkspace=document.createElement('section');liveWorkspace.id='sg-workspace';liveWorkspace.setAttribute('aria-label','Verified repository investigation');
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Hide unverified Stitch forensic claims until corresponding real-data modules exist.
// Keep the navigation, live evidence panel, and real API-backed workspace accessible.
const style=document.createElement('style');
style.textContent='body.sg-no-demo main,body.sg-no-demo [role="main"]{visibility:hidden}body.sg-no-demo #sg-workspace,body.sg-no-demo #sg-panel,body.sg-no-demo #sg-open,body.sg-no-demo #sg-live-banner{visibility:visible}';
document.head.append(style);
if(location.pathname!=='/workspace')document.body.classList.add('sg-no-demo');
const notice=document.createElement('section');
notice.id='sg-data-notice';
notice.setAttribute('role','status');
notice.textContent='Verified analysis only: legacy sample dossiers and synthetic forensic claims are hidden. Use Live Evidence to investigate a public GitHub repository.';
if(location.pathname!=='/workspace')document.body.append(notice);
const banner=document.createElement('div');banner.id='sg-live-banner';banner.innerHTML='<strong>Evidence-first analysis</strong> · Workspace results are fetched from GitHub. Unscanned dimensions remain unverified.';document.body.append(banner);
// Neutralize stale decorative telemetry from the static Stitch shell.
for(const el of document.querySelectorAll('body *')){
 if(el.children.length>2)continue;
 const value=(el.textContent||'').trim();
 if(value==='42ms'||value==='SYNC: 14:02:18 UTC'||value==='VERIFIED'||value==='Live Feed: Active'||value==='LIVE TELEMETRY'){
   el.textContent=value==='42ms'?'—':value==='VERIFIED'?'UNVERIFIED':value==='Live Feed: Active'?'GitHub API · On demand':value==='LIVE TELEMETRY'?'ON-DEMAND ANALYSIS':'No live sync';
 }
}
// Replace broken logo images with accessible typographic brand marks.
for(const img of document.querySelectorAll('img')){
 if(/skyglow lens logo/i.test(img.alt||'')){
   const mark=document.createElement('span');mark.className='sg-brand-mark';mark.textContent='S';mark.setAttribute('role','img');mark.setAttribute('aria-label','Skyglow monogram');img.replaceWith(mark);
 }
}
const open=document.createElement('button');open.id='sg-open';open.textContent='◉ Live Evidence / Ask Skyglow';document.body.append(open);
const panel=document.createElement('aside');panel.id='sg-panel';panel.setAttribute('aria-label','Live investigation panel');document.body.append(panel);
if(location.pathname==='/workspace'){(document.querySelector('main')||document.body).replaceChildren(liveWorkspace);workspaceEmpty();}

function workspaceEmpty(){
 liveWorkspace.innerHTML='<div class="sg-ws-hero"><span class="sg-label">REPOSITORY INTELLIGENCE / LIVE</span><h2>Investigate with evidence, not assumptions.</h2><p>Search a public GitHub repository to inspect its metadata, heuristic signals, and documented limitations.</p><form id="sg-ws-form" class="sg-ws-form"><input id="sg-ws-input" aria-label="GitHub repository" placeholder="owner/repo — e.g. tailwindlabs/tailwindcss" required maxlength="300"><button type="submit">Run investigation →</button></form><p id="sg-ws-status" role="status">Ready to investigate · No sample findings displayed</p></div><div class="sg-ws-empty"><strong>What Skyglow can verify today</strong><p>Repository metadata, recent activity samples, and limited heuristic signals. Stargazer coordination and code security are not yet verified.</p></div>';
 document.querySelector('#sg-ws-form').onsubmit=e=>{e.preventDefault();run($('#sg-ws-input').value)};
}

function renderStarHistory(r){
 const history=r.aggregate_star_history;
 const section=document.createElement('section');
 section.className='sg-ws-star-history';
 section.style.cssText='margin:24px 0;padding:22px;border:1px solid #b8c8d0;border-radius:12px';

 const heading=document.createElement('h3');
 heading.textContent='Star activity intelligence';
 section.append(heading);

 if(!history||history.status!=='available'){
   const note=document.createElement('p');
   note.textContent='Aggregate star history unavailable for this repository.';
   section.append(note);
   return section;
 }

 const note=document.createElement('p');
 note.textContent='GitHub aggregate history. Activity spikes are not proof of manipulation.';
 section.append(note);

 const controls=document.createElement('div');
 controls.style.cssText='display:flex;gap:10px;margin:12px 0';

 const chart=document.createElement('div');
 chart.style.cssText='display:flex;align-items:end;gap:3px;height:180px;overflow-x:auto;border-bottom:1px solid #999;padding:8px 0';

 const summary=document.createElement('p');

 function draw(period){
   chart.replaceChildren();
   const rows=(period==='daily'?history.daily:history.weekly).slice(-60);
   const maximum=Math.max(1,...rows.map(x=>x.stars));

   for(const row of rows){
     const bar=document.createElement('div');
     bar.style.cssText='flex:1 0 6px;min-width:6px;background:#31877d;border-radius:3px 3px 0 0';
     bar.style.height=Math.max(2,160*row.stars/maximum)+'px';
     bar.title=row.date+': '+row.stars+' stars';
     bar.setAttribute('aria-label',bar.title);
     chart.append(bar);
   }

   summary.textContent=rows.length+
     ' '+period+' records displayed. Hover over bars for values.';
 }

 for(const period of ['weekly','daily']){
   const button=document.createElement('button');
   button.type='button';
   button.textContent=period==='weekly'?'Weekly':'Daily';
   button.onclick=()=>draw(period);
   controls.append(button);
 }

 section.append(controls,chart,summary);

 if(history.spikes?.length){
   const spikes=document.createElement('p');
   spikes.textContent=history.spikes.length+
     ' unusually high weekly activity periods identified against preceding four-week averages.';
   section.append(spikes);
 }

 draw('weekly');
 return section;
}

function workspaceReport(r){
 const metric=(label,value)=>'<div class="sg-ws-metric"><span class="sg-label">'+label+'</span><strong>'+esc(Number(value??0).toLocaleString())+'</strong></div>';
 const risks=Object.entries(r.risks||{}).map(([k,v])=>'<div class="sg-ws-risk"><span class="sg-label">'+esc(k.replaceAll('_',' '))+'</span><strong>'+(v.score==null?'N/A':esc(v.score)+'/100')+'</strong><small>'+esc(v.status)+'</small></div>').join('');
 const evidence=(r.evidence||[]).map(e=>'<article class="sg-ws-finding"><span class="sg-pill">'+esc(e.kind)+'</span><h4>'+esc(e.title)+'</h4><p>'+esc(e.description)+'</p><a href="'+esc(e.source)+'" target="_blank" rel="noopener noreferrer">Inspect GitHub source ↗</a></article>').join('');
 const coverage=Object.entries(r.coverage||{}).map(([k,v])=>'<li><span>'+(v?'✓':'—')+'</span> '+esc(k.replaceAll('_',' '))+'</li>').join('');
 liveWorkspace.innerHTML='<div class="sg-ws-hero"><span class="sg-label">LIVE REPOSITORY DOSSIER / REPORT #'+esc(r.id)+'</span><h2>'+esc(r.repo)+'</h2><p>'+esc(r.description||'No repository description provided')+'</p><p class="sg-ws-verdict">'+esc(r.verdict)+'</p><p class="sg-label">Retrieved '+esc(new Date(r.analyzed_at).toLocaleString())+' · <a href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer">GitHub source ↗</a></p><form id="sg-ws-form" class="sg-ws-form"><input id="sg-ws-input" aria-label="Analyze another repository" placeholder="Analyze another owner/repo" required maxlength="300"><button type="submit">Investigate →</button></form><p id="sg-ws-status" role="status"></p></div><div class="sg-ws-metrics">'+metric('STARS',r.metrics.stars)+metric('FORKS',r.metrics.forks)+metric('OPEN ISSUES',r.metrics.open_issues)+metric('DAYS SINCE PUSH',r.metrics.days_since_push==null?0:r.metrics.days_since_push)+'</div><h3>Risk diagnostics <small>Heuristic estimates, not probabilities</small></h3><div class="sg-ws-risks">'+risks+'</div><section class="sg-ws-security"><h3>Dependency security · OSV</h3><p>On-demand npm dependency advisory lookup; not a full code scan.</p><button id="sg-security-run" type="button">Scan npm dependencies</button><div id="sg-security-output" role="status">Not scanned</div></section><h3>Traceable findings</h3><div class="sg-ws-findings">'+evidence+'</div><div class="sg-ws-bottom"><section><h3>Data coverage</h3><ul>'+coverage+'</ul></section><section><h3>Limitations</h3>'+(r.limitations||[]).map(x=>'<p>'+esc(x)+'</p>').join('')+'</section></div>';
 $('#sg-ws-form').onsubmit=e=>{e.preventDefault();run($('#sg-ws-input').value)};
 liveWorkspace.querySelector('.sg-ws-security')?.before(renderStarHistory(r));
 const scan=$('#sg-security-run');if(scan)scan.onclick=async()=>{scan.disabled=true;const out=$('#sg-security-output');out.textContent='Checking pinned npm dependencies against OSVΓÇª';try{const data=await api('/api/security/'+encodeURIComponent(r.repo.split('/')[0])+'/'+encodeURIComponent(r.repo.split('/')[1]));out.replaceChildren();const total=Number.isFinite(data.total_packages)?data.total_packages:null;const scanned=Number(data.packages_scanned)||0;const coverage=total&&total>0?Math.round(scanned/total*100):null;const findings=Array.isArray(data.findings)?data.findings:[];const stats=document.createElement('div');stats.className='sg-osv-stats';const fields=[['Status',data.status||'unknown'],['Lockfile',data.lockfile||'Not identified'],['Detected',total===null?'Unknown':String(total)],['Queried',String(scanned)],['Coverage',coverage===null?'N/A':coverage+'%'],['Advisory matches',data.status==='completed'||data.status==='partial'?String(findings.length)+(data.findings_truncated?'+':''):'Not assessed']];for(const [label,value] of fields){const card=document.createElement('div');const small=document.createElement('span');small.textContent=label;const strong=document.createElement('strong');strong.textContent=value;card.append(small,strong);stats.append(card)}out.append(stats);if(coverage!==null){const meter=document.createElement('progress');meter.max=total;meter.value=scanned;meter.setAttribute('aria-label','Dependency query coverage');out.append(meter)}const summary=document.createElement('p');summary.textContent=data.reason||'No scan explanation available.';out.append(summary);if(data.status==='partial'){const warning=document.createElement('p');warning.className='sg-osv-warning';warning.textContent='Partial scan: '+(total===null?'Some':Math.max(0,total-scanned))+' detected package versions were not queried. Unqueried dependencies remain unassessed.';out.append(warning)}if(data.status==='unsupported'||data.status==='unavailable'){const warning=document.createElement('p');warning.className='sg-osv-warning';warning.textContent='No dependency security conclusion is available for this scan.';out.append(warning)}const grouped=new Map();for(const finding of findings){if(!finding||typeof finding.id!=='string')continue;let group=grouped.get(finding.id);if(!group){group={id:finding.id,url:finding.url,versions:new Set(),details:finding.details||null};grouped.set(finding.id,group)}if(!group.details&&finding.details)group.details=finding.details;group.versions.add(String(finding.package)+'@'+String(finding.version))}if(grouped.size){const heading=document.createElement('h4');heading.textContent='Advisory investigation · '+grouped.size+' distinct IDs';out.append(heading);const note=document.createElement('p');note.textContent='Advisory matches from OSV, not verified exploitability. Affected package versions may be development-only or unreachable.';out.append(note);const filter=document.createElement('input');filter.type='search';filter.placeholder='Filter by advisory ID, package, CVE or severity';filter.setAttribute('aria-label','Filter OSV advisories');filter.style.cssText='width:100%;padding:10px;margin:8px 0;border:1px solid #b6b6b6;border-radius:6px';out.append(filter);const list=document.createElement('div');list.className='sg-osv-advisories';filter.addEventListener('input',()=>{const q=filter.value.trim().toLowerCase();for(const item of list.children)item.hidden=!item.dataset.search.includes(q)});for(const group of [...grouped.values()].sort((a,b)=>a.id.localeCompare(b.id))){const item=document.createElement('details');item.dataset.search=[group.id,...group.versions,group.details?.severity_label||'',...(group.details?.aliases||[])].join(' ').toLowerCase();const title=document.createElement('summary');title.textContent=group.id+' · '+group.versions.size+' package/version '+(group.versions.size===1?'match':'matches');item.append(title);const versions=document.createElement('p');versions.textContent=[...group.versions].sort().join(', ');item.append(versions);if(group.details){if(group.details.summary){const desc=document.createElement('p');desc.textContent=group.details.summary;item.append(desc)}const info=document.createElement('p');info.textContent='OSV severity: '+(group.details.severity_label||'Not provided')+' · CVE: '+(group.details.aliases?.join(', ')||'Not provided')+' · Same-major fixed versions (if reported): '+(group.details.fixed_versions?.join(', ')||'Not provided');item.append(info);const scores=group.details.severity_scores||[];const sev=document.createElement('p');sev.textContent=scores.length?'Reported severity vectors: '+scores.map(x=>x.type+' '+x.score).join(' · '):'Severity score not provided in OSV record';item.append(sev)}else{const unknown=document.createElement('p');unknown.textContent='Severity not retrieved; do not assume low risk.';item.append(unknown)}const link=document.createElement('a');link.textContent='Inspect OSV advisory ↗';link.href='https://osv.dev/vulnerability/'+encodeURIComponent(group.id);link.target='_blank';link.rel='noopener noreferrer';item.append(link);list.append(item)}out.append(list)}if(data.status==='completed'&&!data.findings.length){const p=document.createElement('p');p.textContent='No OSV advisories returned for the queried versions. This does not prove the code is safe.';out.append(p)}}catch(e){out.textContent='Scan unavailable: '+e.message}finally{scan.disabled=false}};
}

function shell(){panel.innerHTML=`<div class="sg-flex" style="justify-content:space-between"><h2>Live investigation</h2><button id="sg-close" aria-label="Close panel">Γ£ò</button></div><p class="sg-label">Evidence-first GitHub intelligence</p><form id="sg-form" class="sg-flex"><input id="sg-url" placeholder="owner/repo or GitHub URL" aria-label="Repository URL" required><button class="sg-primary" id="sg-run">Investigate</button></form><div id="sg-status">Enter a public GitHub repository to begin.</div><div id="sg-output"></div><h3>Ask Skyglow</h3><form id="sg-ask-form" class="sg-flex"><input id="sg-question" placeholder="Why is this suspicious?" aria-label="Ask a question"><button class="sg-primary">Ask</button></form><div class="sg-controls"><button id="sg-mic">≡ƒÄÖ Speak question</button><button id="sg-speak">Γû╢ ElevenLabs answer</button><button id="sg-stop">Γûá Stop</button></div><p id="sg-answer" aria-live="polite">Analyze a repository before asking.</p><h3>Recent investigations</h3><div id="sg-history"></div>`;
$('#sg-close').onclick=()=>panel.classList.remove('open');$('#sg-form').onsubmit=e=>{e.preventDefault();run($('#sg-url').value)};$('#sg-ask-form').onsubmit=e=>{e.preventDefault();ask($('#sg-question').value)};$('#sg-speak').onclick=()=>speak($('#sg-answer').textContent);$('#sg-stop').onclick=()=>{if(window.sgAudio)window.sgAudio.pause();speechSynthesis?.cancel?.()};$('#sg-mic').onclick=listen;loadHistory();}
shell();open.onclick=()=>panel.classList.toggle('open');
async function api(path,opts={}){let r=await fetch(path,opts);let data=await r.json().catch(()=>({}));if(!r.ok)throw Error(data.detail||`Request failed (${r.status})`);return data}
async function loadHistory(){try{const rows=await api('/api/history');$('#sg-history').innerHTML=rows.length?rows.slice(0,10).map(x=>`<div class="sg-item"><button data-report="${x.id}" style="width:100%;text-align:left">${esc(x.repo)}<br><span class="sg-label">${esc(x.created_at.slice(0,16))}</span></button></div>`).join(''):'<p class="sg-label">No saved investigations yet.</p>';document.querySelectorAll('[data-report]').forEach(b=>b.onclick=async()=>{try{render(await api('/api/report/'+b.dataset.report))}catch(e){status(e.message,true)}})}catch(e){$('#sg-history').textContent='History unavailable'}}
function status(s,error=false){$('#sg-status').textContent=s;$('#sg-status').className=error?'sg-error':''}
async function run(url){if(loading)return;loading=true;if(location.pathname!=='/workspace')panel.classList.add('open');$('#sg-url').value=url;$('#sg-run').disabled=true;status('Connecting to GitHub and gathering available evidenceΓÇª');if($('#sg-ws-status'))$('#sg-ws-status').textContent='Retrieving live GitHub dataΓÇª';$('#sg-output').innerHTML='';try{render(await api('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})}));loadHistory()}catch(e){status(e.message,true);if($('#sg-ws-status'))$('#sg-ws-status').textContent=e.message}finally{loading=false;$('#sg-run').disabled=false}}
function render(r){report=r;const target=location.pathname==='/workspace'?document.querySelector('header select'):null;if(target){target.replaceChildren();const opt=document.createElement('option');opt.value=r.repo;opt.textContent=r.repo;target.append(opt)}status(`Live GitHub data · ${new Date(r.analyzed_at).toLocaleString()} · Report #${r.id}`);const scores=Object.entries(r.risks).map(([k,v])=>`<div class="sg-score"><span class="sg-label">${esc(k.replaceAll('_',' '))}</span><strong>${v.score===null?'N/A':v.score+'/100'}</strong><small>${esc(v.status)}</small></div>`).join('');$('#sg-output').innerHTML=`<h3><a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${esc(r.repo)} ↗</a></h3><p>${esc(r.description||'No repository description')}</p><p><strong>${esc(r.verdict)}</strong></p><p class="sg-label">${r.metrics.stars.toLocaleString()} stars · ${r.metrics.forks.toLocaleString()} forks · ${r.metrics.open_issues.toLocaleString()} open issues</p><div class="sg-scores">${scores}</div><h3>Traceable findings</h3>${r.evidence.map(e=>`<div class="sg-item sg-evidence" tabindex="0"><span class="sg-pill">${esc(e.kind)}</span><p><strong>${esc(e.title)}</strong></p><p>${esc(e.description)}</p><a href="${esc(e.source)}" target="_blank" rel="noopener noreferrer">Source ↗</a></div>`).join('')}<h3>Coverage & limitations</h3><div class="sg-note">${Object.entries(r.coverage).map(([k,v])=>`${v?'✓':'—'} ${esc(k.replaceAll('_',' '))}`).join('<br>')}</div>${r.limitations.map(x=>`<p class="sg-label">• ${esc(x)}</p>`).join('')}<h3>Public contributor sample</h3><p>${r.contributors.length?r.contributors.map(x=>esc(x.login)).join(', '):'Not available'}</p><p class="sg-note">No real-world identity attribution. No account-level promotion graph is asserted without authorized data.</p>`;if(location.pathname==='/workspace'){workspaceReport(r);panel.classList.remove('open')}$('#sg-answer').textContent='Ask about the evidence, security coverage, or limitations.';}
async function ask(question){if(!report){$('#sg-answer').textContent='Please investigate a repository first.';return}if(!question.trim())return;$('#sg-answer').textContent='Retrieving report evidenceΓÇª';try{let a=await api('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report_id:report.id,question})});$('#sg-answer').textContent=a.answer;document.querySelector('.sg-evidence')?.scrollIntoView({behavior:'smooth',block:'nearest'})}catch(e){$('#sg-answer').textContent=e.message}}
async function speak(text){if(!text||!report)return;try{const r=await fetch('/api/voice',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});if(!r.ok){let d=await r.json();throw Error(d.detail||'Voice unavailable')}const url=URL.createObjectURL(await r.blob());if(window.sgAudio)window.sgAudio.pause();window.sgAudio=new Audio(url);window.sgAudio.onended=()=>URL.revokeObjectURL(url);await window.sgAudio.play()}catch(e){status('ElevenLabs: '+e.message,true)}}
function listen(){const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){status('Speech recognition not supported by this browser; type your question instead.',true);return}const rec=new SR();rec.lang='en-US';rec.onresult=e=>{$('#sg-question').value=e.results[0][0].transcript;ask($('#sg-question').value)};rec.onerror=e=>status('Microphone: '+e.error,true);rec.start();status('ListeningΓÇª')}
window.triggerScan=()=>run($('#repo-target-input')?.value||$('#sg-url').value);
for(const a of document.querySelectorAll('nav a[data-path]')){const p=a.dataset.path;if(routes[p]){a.href=routes[p];a.removeAttribute('onclick')}}
for(const a of document.querySelectorAll('a[data-path]')){if(routes[a.dataset.path])a.href=routes[a.dataset.path]}
const current=location.pathname;document.querySelectorAll('nav a[data-path]').forEach(a=>{if(a.href.endsWith(current)&&current!=='/')a.setAttribute('aria-current','page')});
const queryRepo=new URLSearchParams(location.search).get('repo');if(queryRepo)run(queryRepo);
if(location.pathname==='/workspace'){const target=document.querySelector('header select');if(target){target.replaceChildren();const opt=document.createElement('option');opt.textContent='Select a repository after investigation';target.append(opt);target.onchange=()=>{if(target.value.includes('/'))run(target.value)}}}
const input=$('#repo-target-input');if(input){input.value='';input.placeholder='https://github.com/owner/repository';}
// Stitch HTML is retained as visual reference; backend-linked findings always appear in the live panel.
})();
