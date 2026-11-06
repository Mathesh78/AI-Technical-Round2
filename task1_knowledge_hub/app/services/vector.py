"""FAISS index reconstructed from SQLite chunks for consistent mapping."""
import threading
import numpy as np
import faiss
import httpx
from app import config
from .storage import all_chunks

_guard=threading.RLock()

class ModelError(RuntimeError): pass

def embed(texts):
    result=[]
    for start in range(0,len(texts),16):
        try:
            with httpx.Client(timeout=180) as client:
                response=client.post(config.OLLAMA_URL+'/api/embed',json={
                    'model':config.EMBED,'input':texts[start:start+16]})
                response.raise_for_status()
                vectors=response.json()['embeddings']
            if len(vectors)!=len(texts[start:start+16]): raise ValueError('Wrong vector count')
            result.extend(vectors)
        except (httpx.HTTPError,KeyError,ValueError) as exc:
            raise ModelError(f'Ollama embedding model is not ready: {exc}') from exc
    return result

def rebuild():
    with _guard:
        rows=all_chunks()
        if not rows:
            if config.INDEX.exists(): config.INDEX.unlink()
            return 0
        vectors=np.asarray(embed([r['content'] for r in rows]),dtype='float32')
        faiss.normalize_L2(vectors)
        index=faiss.IndexFlatIP(vectors.shape[1]);index.add(vectors)
        config.DATA.mkdir(parents=True,exist_ok=True)
        temporary=config.INDEX.with_suffix('.tmp')
        faiss.write_index(index,str(temporary));temporary.replace(config.INDEX)
        return len(rows)

def search(query,k=5):
    with _guard:
        rows=all_chunks()
        if not rows or not config.INDEX.exists(): return []
        index=faiss.read_index(str(config.INDEX))
        if index.ntotal!=len(rows): raise ModelError('Index out of date. Run the rebuild script.')
        needle=np.asarray(embed([query]),dtype='float32')
        if needle.shape[1]!=index.d: raise ModelError('Embedding model changed; rebuild the index')
        faiss.normalize_L2(needle)
        distances,indices=index.search(needle,min(k,len(rows)))
        return [{'citation':f'[{i}]','url':rows[pos]['url'],'title':rows[pos]['title'],
                 'chunk':rows[pos]['chunk_no'],'text':rows[pos]['content'],
                 'score':round(float(score),4)}
                for i,(pos,score) in enumerate(zip(indices[0],distances[0]),1) if pos>=0]
