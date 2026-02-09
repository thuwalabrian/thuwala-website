import urllib.request
import urllib.error
import re

BASE = 'http://127.0.0.1:10000'
PAGES = ['/', '/about', '/services', '/portfolio', '/contact', '/admin/login']

title_re = re.compile(r'<title[^>]*>(.*?)</title>', re.I|re.S)

def fetch(path):
    url = BASE + path
    try:
        with urllib.request.urlopen(url, timeout=6) as r:
            code = r.getcode()
            body = r.read(1024*64).decode('utf-8', errors='replace')
            m = title_re.search(body)
            title = m.group(1).strip() if m else 'NO TITLE'
            return code, title
    except urllib.error.HTTPError as e:
        return e.code, f'HTTPError: {e.reason}'
    except Exception as e:
        return None, f'ERROR: {e}'

def main():
    print('Running minimal smoke tests...')
    for p in PAGES:
        code, info = fetch(p)
        if code == 200:
            print(f"{p:12} -> 200 OK    Title: {info}")
        elif code is None:
            print(f"{p:12} -> ERROR     {info}")
        else:
            print(f"{p:12} -> {code}       {info}")
    print('Smoke tests complete.')

if __name__ == '__main__':
    main()
