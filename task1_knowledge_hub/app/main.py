"""Knowledge Base Hub: CSV/XLSX -> SQLite -> FAISS -> Ollama."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app import config
from app.services.storage import initialize, save_url, replace_chunks, all_urls
from app.services.scraper import parse_urls, harvest
from app.services.chunking import chunk_text
from app.services.vector import rebuild, search, ModelError
from app.services.llm import answer

from app.core.logging_config import setup_logging

logger = setup_logging()
logger.info("Application started")

logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)
BASE=Path(__file__).parent

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield

app=FastAPI(title='Leadership Knowledge Base Hub',version='1.0.0',lifespan=lifespan)
app.mount('/static',StaticFiles(directory=str(BASE/'static')),name='static')

class Query(BaseModel):
    question:str=Field(min_length=2,max_length=2000)
    top_k:int=Field(default=5,ge=1,le=10)

@app.get('/')
def home(): return FileResponse(BASE/'static'/'index.html')

@app.get('/api/health')
def health(): return {'status':'ok','app':'leadership-knowledge-hub'}

@app.get('/api/urls/')
def urls():
    # Includes complete raw_html as required (this endpoint can produce large payloads).
    return {'count':len(all_urls()),'results':all_urls()}

@app.post('/api/upload')
async def upload(file:UploadFile=File(...)):
    filename=Path(file.filename or '').name
    if Path(filename).suffix.lower() not in ('.csv','.xlsx'):
        raise HTTPException(400,'Please upload CSV or XLSX')
    raw=await file.read(config.MAX_FILE+1)
    await file.close()
    if not raw or len(raw)>config.MAX_FILE: raise HTTPException(400,'File must be 1 byte to 2 MB')
    try: url_list=parse_urls(filename,raw)
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc
    report=[]
    for url in url_list:
        page=harvest(url)
        row_id=save_url(page)
        chunks=chunk_text(page['extracted_text']) if not page['error'] else []
        replace_chunks(row_id,chunks)
        report.append({'url':url,'status_code':page['status_code'],
                       'title':page['title'],'chunks':len(chunks),'error':page['error']})
    try: total=rebuild()
    except ModelError as exc:
        raise HTTPException(503,{'message':'Scraping saved in SQLite but indexing failed. Check Ollama, then run rebuild_index.py',
                                 'details':str(exc),'harvest_results':report}) from exc
    return {'processed':len(report),'indexed_chunks':total,'results':report}

@app.post('/api/search')
def query(request:Query):
    try:
        matches=search(request.question,request.top_k)
        if not matches: return {'answer':'No indexed content yet. Upload a URL spreadsheet first.','sources':[]}
        return {'answer':answer(request.question,matches),'sources':matches}
    except ModelError as exc: raise HTTPException(503,str(exc)) from exc
