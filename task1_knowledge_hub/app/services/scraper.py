import csv
import io
import ipaddress
import re
import socket
from urllib.parse import urlsplit, urljoin
import requests
from bs4 import BeautifulSoup
from app import config

URL_PATTERN = re.compile(r'^https?://', re.I)

def validate_public_url(url):
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Only public HTTP(S) URLs are allowed')
    if parsed.port and parsed.port not in (80,443):
        raise ValueError('Nonstandard ports are not allowed')
    try:
        addresses = socket.getaddrinfo(parsed.hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError('Hostname could not be resolved') from exc
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Private or non-public destination is blocked')
    return url

def parse_urls(filename, data):
    suffix = filename.lower().rsplit('.',1)[-1]
    if suffix == 'csv':
        try: rows = list(csv.reader(io.StringIO(data.decode('utf-8-sig'))))
        except UnicodeError as exc: raise ValueError('CSV must be UTF-8 encoded') from exc
    elif suffix == 'xlsx':
        from openpyxl import load_workbook
        try:
            book=load_workbook(io.BytesIO(data),read_only=True,data_only=True)
            rows=list(book.active.iter_rows(values_only=True))
            book.close()
        except Exception as exc: raise ValueError('Invalid Excel workbook') from exc
    else:
        raise ValueError('Upload .csv or .xlsx')
    if not rows: raise ValueError('No rows in file')
    head=[str(x or '').strip().lower() for x in rows[0]]
    column=next((i for i,h in enumerate(head) if h in ('url','urls','website','link')),None)
    if column is None: raise ValueError('File needs a URL column heading')
    seen=set();out=[]
    for row in rows[1:]:
        value=str(row[column] or '').strip() if len(row)>column else ''
        if not value or value in seen: continue
        if not URL_PATTERN.match(value): raise ValueError(f'Invalid URL: {value[:80]}')
        seen.add(value);out.append(value)
        if len(out)>config.MAX_URLS: raise ValueError(f'Maximum {config.MAX_URLS} unique URLs')
    if not out: raise ValueError('No URLs found')
    return out

def harvest(url):
    entry={'url':url,'status_code':None,'title':'','description':'','raw_html':'',
           'extracted_text':'','error':None}
    try:
        current=url
        session=requests.Session();session.trust_env=False
        for _ in range(5):
            validate_public_url(current)
            response=session.get(current,timeout=(6,15),allow_redirects=False,headers={
                'User-Agent':'KnowledgeHubAssignment/1.0 (educational research)'},stream=True)
            entry['status_code']=response.status_code
            if response.is_redirect:
                location=response.headers.get('Location')
                response.close()
                if not location: raise ValueError('Redirect has no Location')
                current=urljoin(current,location)
                continue
            ctype=response.headers.get('content-type','')
            if 'text/html' not in ctype and 'text/plain' not in ctype:
                response.close();raise ValueError('URL is not HTML or text')
            raw=b''
            for block in response.iter_content(65536):
                raw+=block
                if len(raw)>config.MAX_HTML: raise ValueError('HTML exceeds 4 MB limit')
            response.close()
            html=raw.decode(response.encoding or 'utf-8',errors='replace')
            soup=BeautifulSoup(html,'html.parser')
            title=soup.title.get_text(' ',strip=True) if soup.title else ''
            meta=soup.find('meta',attrs={'name':'description'})
            desc=meta.get('content','') if meta else ''
            for node in soup(['script','style','nav','footer','header','noscript']): node.decompose()
            main=soup.find('main') or soup.find('article') or soup.body or soup
            content=' '.join(main.stripped_strings)
            entry.update(title=title[:500],description=desc[:1500],raw_html=html,
                         extracted_text=content[:500000])
            if response.status_code>=400: entry['error']=f'HTTP {response.status_code}'
            elif not content: entry['error']='No extractable text (possibly JavaScript rendered)'
            return entry
        raise ValueError('Too many redirects')
    except (requests.RequestException, ValueError, OSError) as exc:
        entry['error']=str(exc)[:350]
        return entry
