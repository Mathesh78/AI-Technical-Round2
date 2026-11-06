"""SQLite raw URL rows and chunks; no SQL string interpolation."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from app import config

@contextmanager
def connection():
    config.DATA.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.DB, timeout=30)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()

def initialize():
    with connection() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS harvested_urls (
              id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE NOT NULL,
              status_code INTEGER, title TEXT, description TEXT, raw_html TEXT NOT NULL,
              extracted_text TEXT NOT NULL, error TEXT, harvested_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chunks (
              id INTEGER PRIMARY KEY AUTOINCREMENT, url_id INTEGER NOT NULL,
              chunk_no INTEGER NOT NULL, content TEXT NOT NULL,
              FOREIGN KEY(url_id) REFERENCES harvested_urls(id));
        """)

def save_url(item):
    now = datetime.now(timezone.utc).isoformat()
    with connection() as db:
        db.execute("""INSERT INTO harvested_urls
          (url,status_code,title,description,raw_html,extracted_text,error,harvested_at)
          VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET
          status_code=excluded.status_code,title=excluded.title,
          description=excluded.description,raw_html=excluded.raw_html,
          extracted_text=excluded.extracted_text,error=excluded.error,
          harvested_at=excluded.harvested_at""",
          (item['url'],item.get('status_code'),item.get('title',''),
           item.get('description',''),item.get('raw_html',''),
           item.get('extracted_text',''),item.get('error'),now))
        return db.execute('SELECT id FROM harvested_urls WHERE url=?',(item['url'],)).fetchone()['id']

def all_urls():
    with connection() as db:
        return [dict(r) for r in db.execute('SELECT * FROM harvested_urls ORDER BY id DESC')]

def all_chunks():
    with connection() as db:
        return [dict(r) for r in db.execute("""SELECT c.id,c.content,c.chunk_no,u.url,u.title
         FROM chunks c JOIN harvested_urls u ON c.url_id=u.id ORDER BY c.id""")]

def replace_chunks(url_id, chunks):
    with connection() as db:
        db.execute('DELETE FROM chunks WHERE url_id=?',(url_id,))
        db.executemany('INSERT INTO chunks(url_id,chunk_no,content) VALUES(?,?,?)',
                       [(url_id,i,text) for i,text in enumerate(chunks)])
