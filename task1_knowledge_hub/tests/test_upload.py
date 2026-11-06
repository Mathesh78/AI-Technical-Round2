from fastapi.testclient import TestClient
from app import main
from app.services.scraper import parse_urls

client=TestClient(main.app)

def test_csv_parsing():
    assert parse_urls('urls.csv',b'ID,URL\n1,https://example.com\n2,https://example.com\n') == ['https://example.com']

def test_invalid_csv():
    try: parse_urls('urls.csv',b'name\nFoo')
    except ValueError: pass
    else: raise AssertionError('missing URL heading was accepted')

def test_home(): assert client.get('/').status_code==200

def test_bad_file():
    assert client.post('/api/upload',files={'file':('x.txt',b'hello')}).status_code==400

def test_search_mock(monkeypatch):
    monkeypatch.setattr(main,'search',lambda question,k:[{'citation':'[1]','text':'A is CEO','title':'Demo','url':'https://example.com','score':.9,'chunk':0}])
    monkeypatch.setattr(main,'answer',lambda question,sources:'A is CEO [1]')
    response=client.post('/api/search',json={'question':'Who is CEO?'})
    assert response.status_code==200
    assert response.json()['sources'][0]['citation']=='[1]'
