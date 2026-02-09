import requests
from bs4 import BeautifulSoup

BASE = 'http://127.0.0.1:10000'
PAGES = ['/', '/about', '/services', '/portfolio', '/contact', '/admin/login']

print('Running simple smoke tests...')
for p in PAGES:
    url = BASE + p
    try:
        r = requests.get(url, timeout=5)
        ok = r.status_code == 200
        status = 'OK' if ok else 'FAIL'
        print(f"{p:12} -> {r.status_code} {status}")
        if ok:
            title = BeautifulSoup(r.text, 'html.parser').title
            print('  Title:', title.string.strip() if title else 'NO TITLE')
    except Exception as e:
        print(f'{p:12} -> ERROR: {e}')

print('Smoke tests complete.')
