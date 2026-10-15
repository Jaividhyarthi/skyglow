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


def summarize_star_sample(records, total_stars):
    from collections import Counter
    timestamps = [
        item.get('starred_at') for item in records
        if isinstance(item, dict) and item.get('starred_at')
    ]
    days = Counter(t[:10] for t in timestamps)
    daily = [
        {'date': day, 'stars': count}
        for day, count in sorted(days.items())
    ]
    peak = max(daily, key=lambda row: row['stars']) if daily else None
    return {
        'sample_size': len(timestamps),
        'total_stars': total_stars,
        'coverage_percent': round(100 * len(timestamps) / total_stars, 2) if total_stars else 0,
        'sample_scope': 'GitHub API first page, not complete repository history',
        'daily_counts': daily,
        'peak_sample_day': peak,
        'full_history': False
    }


def summarize_star_history(records):
    """Normalize GitHub aggregate history without inferring star authenticity."""
    if not isinstance(records, list):
        return {'status': 'unavailable', 'reason': 'Unexpected history response',
                'daily': [], 'weekly': [], 'spikes': []}

    from collections import defaultdict
    daily_map = {}
    weekly = []

    for row in records:
        if not isinstance(row, dict):
            continue

        week = row.get('week')
        days = row.get('days')
        total = row.get('total')

        if (type(week) is not int or type(total) is not int
                or total < 0 or not isinstance(days, list)
                or len(days) != 7
                or any(type(n) is not int or n < 0 for n in days)
                or sum(days) != total):
            continue

        try:
            start = datetime.datetime.fromtimestamp(
                week, datetime.timezone.utc
            )
        except (ValueError, OverflowError, OSError):
            continue

        date = start.date().isoformat()
        weekly.append({'date': date, 'stars': total})

        for offset, count in enumerate(days):
            day = (start + datetime.timedelta(days=offset)).date().isoformat()
            daily_map[day] = count

    weekly.sort(key=lambda row: row['date'])
    daily = [
        {'date': date, 'stars': count}
        for date, count in sorted(daily_map.items())
    ]

    if not weekly:
        return {'status': 'unavailable', 'reason': 'No valid weekly records',
                'daily': [], 'weekly': [], 'spikes': []}

    # Relative activity observations, not fraud predictions.
    spikes = []
    for index in range(4, len(weekly)):
        baseline = [
            row['stars'] for row in weekly[index - 4:index]
        ]
        average = sum(baseline) / len(baseline)
        current = weekly[index]['stars']

        if average >= 10 and current >= 2.5 * average:
            spikes.append({
                'date': weekly[index]['date'],
                'stars': current,
                'baseline': round(average, 1),
                'ratio': round(current / average, 2)
            })

    return {
        'status': 'available',
        'source': 'GitHub aggregate stargazer history',
        'scope': 'Returned historical weeks; completeness not guaranteed',
        'daily': daily,
        'weekly': weekly,
        'spikes': spikes[-10:]
    }


async def investigate(value):
    name=parse_repo(value)
    headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'Skyglow-Evidence-First/1.0'}
    if os.getenv('GITHUB_TOKEN'): headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    async with httpx.AsyncClient(headers=headers,timeout=18,follow_redirects=True) as client:
        repo=await github_json(client,'/repos/'+name)
        commits=[]; releases=[]; contributors=[]; stargazers=[]; raw_star_history=None
        errors=[]
        for label,path in [('commits',f'/repos/{name}/commits'),('releases',f'/repos/{name}/releases'),('contributors',f'/repos/{name}/contributors')]:
            try:
                val=await github_json(client,path,{'per_page':15})
                if label=='commits':commits=val if isinstance(val,list) else []
                elif label=='releases':releases=val if isinstance(val,list) else []
                else:contributors=val if isinstance(val,list) else []
            except Exception as e: errors.append(f'{label}: {str(e)[:100]}')
        try:
            star_res = await client.get(
                'https://api.github.com/repos/' + name + '/stargazers',
                params={'per_page': 100},
                headers={'Accept': 'application/vnd.github.star+json'}
            )
            star_res.raise_for_status()
            star_data = star_res.json()
            if isinstance(star_data, list):
                stargazers = star_data
            else:
                errors.append('stargazers: unexpected API response')
        except Exception as exc:
            errors.append('stargazers: ' + str(exc)[:100])
        try:
            async with httpx.AsyncClient(
                headers={
                    'Accept': 'application/vnd.github+json',
                    'User-Agent': 'Skyglow-Evidence-First/1.0'
                },
                timeout=18,
                follow_redirects=True
            ) as public_client:
                history_res = await public_client.get(
                    'https://api.github.com/repos/' +
                    name + '/stargazers/history'
                )
                if history_res.status_code == 200:
                    raw_star_history = history_res.json()
                else:
                    errors.append(
                        'aggregate star history: HTTP ' +
                        str(history_res.status_code)
                    )
        except Exception as exc:
            errors.append('aggregate star history: ' + str(exc)[:100])
    age=days_ago(repo.get('created_at'))
    pushed=days_ago(repo.get('pushed_at'))
    stars=repo.get('stargazers_count',0)
    forks=repo.get('forks_count',0)
    issues=repo.get('open_issues_count',0)
    star_activity = summarize_star_sample(stargazers, stars)
    aggregate_history = summarize_star_history(raw_star_history)
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
    if star_activity['sample_size']:
        peak = star_activity['peak_sample_day']
        if peak and peak['stars'] >= 20:
            add(
                'context',
                'Concentrated star activity in sampled records',
                f"{peak['stars']} of {star_activity['sample_size']} sampled star events occurred on {peak['date']}. This is a partial sample, not proof of manipulation.",
                repo['html_url'] + '/stargazers',
                0
            )
    report={
        'repo':repo['full_name'],'url':repo['html_url'],'description':repo.get('description'),
        'analyzed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source':'GitHub REST API (live)', 'coverage':{'metadata':True,'commits':bool(commits),'releases':bool(releases),'contributors':bool(contributors),'individual_stargazers':bool(star_activity['sample_size']),'star_event_timeline':bool(star_activity['sample_size']),'aggregate_star_history':aggregate_history['status']=='available','full_code_scan':False},
        'star_activity':star_activity,
        'aggregate_star_history':aggregate_history,
        'metrics':{'stars':stars,'forks':forks,'open_issues':issues,'age_days':age,'days_since_push':pushed,'contributors_sample':len(contributors),'recent_commits_sample':len(commits),'releases_sample':len(releases)},
        'risks':{'popularity':{'score':popularity if popularity else None,'status':'heuristic review signals; not a fake-star probability' if popularity else 'no triggered signals; authenticity unverified'},'promotion_network':{'score':None,'status':'insufficient data'},'code_security':{'score':None,'status':'not scanned'},'maintenance':{'score':maintenance if maintenance else None,'status':'metadata-based maintenance concerns' if maintenance else 'no triggered maintenance concerns'}},
        'verdict':'Review signals detected' if popularity>=20 else 'Insufficient evidence to verify star authenticity',
        'evidence':evidence,'graph':graph,'limitations':['Stargazer timestamps, when available, are sampled from the first API page only; the complete history and coordinated behavior remain unverified.','Popularity anomalies are not evidence of malware or wrongdoing.','Code was not scanned; security is unverified.','Scores are heuristics, not validated fake-star probabilities.']+errors,
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
