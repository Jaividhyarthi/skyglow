import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse,FileResponse,Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import httpx
from .engine import investigate,history,get_report,explain,parse_repo,init_db
from .osv_scan import scan_npm_lockfile
ROOT=Path(__file__).resolve().parents[1]
@asynccontextmanager
async def lifespan(app):
    init_db();yield
app=FastAPI(title='Skyglow Investigation API',version='1.0',lifespan=lifespan)
app.mount('/assets',StaticFiles(directory=str(ROOT/'frontend')),name='assets')
class RepoInput(BaseModel):url:str=Field(min_length=3,max_length=300)
class AskInput(BaseModel):report_id:int=Field(gt=0);question:str=Field(min_length=1,max_length=1000)
class VoiceInput(BaseModel):text:str=Field(min_length=1,max_length=2000)
@app.get('/api/health')
def health():return {'status':'ok','github_token_configured':bool(os.getenv('GITHUB_TOKEN')),'elevenlabs_configured':bool(os.getenv('ELEVENLABS_API_KEY'))}
@app.post('/api/analyze')
async def analyze(data:RepoInput):
    try:return await investigate(data.url)
    except ValueError as e:raise HTTPException(400,str(e))
    except httpx.HTTPStatusError as e:raise HTTPException(502,f'GitHub HTTP {e.response.status_code}')
    except (RuntimeError,httpx.RequestError) as e:raise HTTPException(503,str(e))
@app.get('/api/security/{owner}/{repo}')
async def security(owner:str,repo:str):
    try:
        name=parse_repo(owner+'/'+repo)
        return await scan_npm_lockfile(name)
    except ValueError as e:
        raise HTTPException(400,str(e))
    except httpx.RequestError:
        raise HTTPException(503,'Security scan service unavailable')
@app.get('/api/history')
def past():return history()
@app.get('/api/report/{report_id}')
def report(report_id:int):
    r=get_report(report_id)
    if not r:raise HTTPException(404,'Report not found')
    return r
@app.post('/api/ask')
def ask(data:AskInput):
    r=get_report(data.report_id)
    if not r:raise HTTPException(404,'Analyze a repository first')
    return {'answer':explain(r,data.question),'evidence_ids':[e['id'] for e in r['evidence'][:3]],'tool':'inspect_evidence','source':'structured Skyglow report'}
@app.post('/api/voice')
async def voice(data:VoiceInput):
    key=os.getenv('ELEVENLABS_API_KEY')
    if not key:raise HTTPException(503,'Set ELEVENLABS_API_KEY in .env to enable voice output')
    voice_id=os.getenv('ELEVENLABS_VOICE_ID','JBFqnCBsd6RMkjVDRZzb')
    async with httpx.AsyncClient(timeout=35) as c:
        r=await c.post(f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',headers={'xi-api-key':key,'Content-Type':'application/json'},json={'text':data.text,'model_id':'eleven_multilingual_v2'})
    if r.status_code>=400:raise HTTPException(502,f'ElevenLabs returned HTTP {r.status_code}')
    return Response(content=r.content,media_type='audio/mpeg')
PAGES={'':'investigation_home','home':'investigation_home','workspace':'investigation_workspace','network':'network_explorer','voice':'voice_investigator','reputation':'reputation_profile','research':'research_lab','extension-preview':'extension_preview'}
@app.get('/{page:path}',response_class=HTMLResponse)
def ui(page:str=''):
    page=page.strip('/')
    if page not in PAGES:raise HTTPException(404,'Page not found')
    source=ROOT/'frontend'/'stitch'/PAGES[page]/'code.html'
    html=source.read_text(encoding='utf-8')
    injection='<link rel="stylesheet" href="/assets/skyglow.css"><script defer src="/assets/skyglow.js"></script>'
    return HTMLResponse(html.replace('</body>',injection+'</body>'))
