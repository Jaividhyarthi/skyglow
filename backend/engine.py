"""Evidence-first analysis: heuristics are not fake-star or malware verdicts."""
import os,re,json,sqlite3,datetime,math
from urllib.parse import urlparse
from pathlib import Path
import httpx

ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.getenv('SKYGLOW_DB',str(ROOT/'skyglow.db')))
REPO=re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')

def parse_repo(value):
    """Accept only canonical public GitHub repository identifiers and URLs."""
    if not isinstance(value, str):
        raise ValueError('Enter a GitHub repository URL or owner/repo')
    value = value.strip()
    if value.startswith(('https://', 'http://')):
        u = urlparse(value)
        if (u.scheme != 'https' or u.hostname != 'github.com'
                or u.username or u.password or u.port
                or u.query or u.fragment):
            raise ValueError('Only canonical HTTPS github.com repository URLs are supported')
        parts = u.path.strip('/').split('/')
        if len(parts) < 2 or any(not part for part in parts):
            raise ValueError('Enter a GitHub repository URL or owner/repo')
        value = '/'.join(parts[:2])
    value = value.removesuffix('.git')
    if not REPO.fullmatch(value) or any(p in ('.', '..') for p in value.split('/')):
        raise ValueError('Enter a GitHub repository URL or owner/repo')
    return value


def init_db():
    DB.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(DB) as c:
        c.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, repo TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL)')
        c.execute('CREATE INDEX IF NOT EXISTS reports_repo_idx ON reports(repo)')

def save(report):
    init_db()
    with sqlite3.connect(DB) as c:
        cur=c.execute('INSERT INTO reports(repo,created_at,payload) VALUES (?,?,?)',(report['repo'],report['analyzed_at'],json.dumps(report)))
        return cur.lastrowid

def history(limit=20):
    init_db()
    with sqlite3.connect(DB) as c:
        rows=c.execute('SELECT id,repo,created_at,payload FROM reports ORDER BY id DESC LIMIT ?', (min(limit,100),)).fetchall()
    return [{'id':i,'repo':r,'created_at':d,'verdict':json.loads(p)['verdict']} for i,r,d,p in rows]

def get_report(report_id):
    init_db()
    with sqlite3.connect(DB) as c:
        row=c.execute('SELECT payload FROM reports WHERE id=?',(report_id,)).fetchone()
    return json.loads(row[0]) if row else None

async def github_json(client,path,params=None):
    res=await client.get('https://api.github.com'+path,params=params)
    if res.status_code==404: raise ValueError('Repository not found or not publicly accessible')
    if res.status_code in (403,429): raise RuntimeError('GitHub rate limit or access restriction; add GITHUB_TOKEN or try later')
    if res.status_code in (301, 302, 307, 308):
        raise RuntimeError('GitHub API redirect could not be resolved safely')
    res.raise_for_status()
    return res.json()

def days_ago(iso):
    if not iso:return None
    return max(0,(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(iso.replace('Z','+00:00'))).days)

async def investigate(value):
    name=parse_repo(value)
    headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'Skyglow-Evidence-First/1.0'}
    if os.getenv('GITHUB_TOKEN'): headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    async with httpx.AsyncClient(headers=headers,timeout=18,follow_redirects=True) as client:
        repo=await github_json(client,'/repos/'+name)
        commits=[]; releases=[]; contributors=[]
        errors=[]
        for label,path in [('commits',f'/repos/{name}/commits'),('releases',f'/repos/{name}/releases'),('contributors',f'/repos/{name}/contributors')]:
            try:
                val=await github_json(client,path,{'per_page':15})
                if label=='commits':commits=val if isinstance(val,list) else []
                elif label=='releases':releases=val if isinstance(val,list) else []
                else:contributors=val if isinstance(val,list) else []
            except Exception as e: errors.append(f'{label}: {str(e)[:100]}')
    age=days_ago(repo.get('created_at'))
    pushed=days_ago(repo.get('pushed_at'))
    stars=repo.get('stargazers_count',0)
    forks=repo.get('forks_count',0)
    issues=repo.get('open_issues_count',0)
    evidence=[]
    def add(kind,title,description,source,weight=0):
        evidence.append({'id':f'e{len(evidence)+1}','kind':kind,'title':title,'description':description,'source':source,'weight':weight})
    if age is not None and age<30 and stars>=1000:
        add('review','High stars for a recently created repository',f'{stars:,} stars with a repository age of {age} days. Viral growth is a plausible benign explanation.',repo['html_url'],30)
    if age is not None and age<7 and stars>=200:
        add('review','Rapid early popularity',f'{stars:,} stars in the first {age+1} days; investigate promotion sources before drawing conclusions.',repo['html_url'],20)
    if stars>=500 and forks<=max(2,round(stars*.002)):
        add('context','Low fork-to-star ratio',f'{forks:,} forks versus {stars:,} stars. This is contextual only; many legitimate tools have low fork rates.',repo['html_url'],5)
    if pushed is not None and pushed>365:
        add('maintenance','Repository has not been pushed recently',f'Last push was approximately {pushed} days ago.',repo['html_url'],0)
    if repo.get('archived'):add('maintenance','Repository is archived','Maintainer has marked the repository archived.',repo['html_url'],0)
    if repo.get('disabled'):add('maintenance','Repository is disabled','GitHub indicates this repository is disabled.',repo['html_url'],0)
    if not evidence:add('context','No major heuristic anomalies identified','Available metadata did not trigger the limited checks. This does not verify star authenticity or code safety.',repo['html_url'],0)
    popularity=min(100,sum(e['weight'] for e in evidence))
    maintenance=min(100,(45 if pushed is not None and pushed>365 else 0)+(35 if repo.get('archived') else 0)+(20 if not releases and age and age>180 else 0))
    graph={'status':'unavailable','reason':'No authorized account-level stargazer graph was retrieved. Account coordination cannot be assessed.','nodes':[],'edges':[]}
    report={
        'repo':repo['full_name'],'url':repo['html_url'],'description':repo.get('description'),
        'analyzed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source':'GitHub REST API (live)', 'coverage':{'metadata':True,'commits':bool(commits),'releases':bool(releases),'contributors':bool(contributors),'individual_stargazers':False,'star_event_timeline':False,'full_code_scan':False},
        'metrics':{'stars':stars,'forks':forks,'open_issues':issues,'age_days':age,'days_since_push':pushed,'contributors_sample':len(contributors),'recent_commits_sample':len(commits),'releases_sample':len(releases)},
        'risks':{'popularity':{'score':popularity,'status':'limited heuristic estimate'},'promotion_network':{'score':None,'status':'insufficient data'},'code_security':{'score':None,'status':'not scanned'},'maintenance':{'score':maintenance,'status':'metadata heuristic estimate'}},
        'verdict':'Review signals detected' if popularity>=20 else 'Insufficient evidence to verify star authenticity',
        'evidence':evidence,'graph':graph,'limitations':['No individual stargazer identities or event-level star timestamps were collected.','Popularity anomalies are not evidence of malware or wrongdoing.','Code was not scanned; security is unverified.','Scores are heuristics, not validated fake-star probabilities.']+errors,
        'recent_commits':[{'sha':x.get('sha','')[:9],'message':(x.get('commit') or {}).get('message','').splitlines()[0][:120]} for x in commits[:8]],
        'contributors':[{'login':x.get('login'),'contributions':x.get('contributions')} for x in contributors[:12]],
        'is_demo':False
    }
    report['id']=save(report)
    return report

def explain(report,question):
    q=question.lower()
    if any(w in q for w in ['safe','malware','vulnerab','security']):
        return 'Code safety is not verified. This investigation did not perform a complete code or dependency scan. Popularity signals cannot establish that code is safe or malicious.'
    if any(w in q for w in ['account','network','who','person','cluster','boost']):
        return 'Account-level promotion attribution is unavailable for this live investigation. We cannot identify promoters or infer real-world identities from repository metadata.'
    if any(w in q for w in ['limit','confidence','missing','uncertain']):
        return 'The analysis uses limited live repository metadata. Individual stargazers, star-event timing, and full code-security scanning are unavailable. Results are not proof of fake popularity.'
    points='; '.join(x['title'] for x in report['evidence'][:3])
    return f"For {report['repo']}, the observed signals are: {points}. Verdict: {report['verdict']}. These are heuristic observations, not a confirmed fake-star finding."
