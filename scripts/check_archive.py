#!/usr/bin/env python3
"""Check roster coverage, award classification, metadata and local navigation."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://reininghalloffame.com'
data = json.loads((ROOT / 'data/honorees.json').read_text())
rows = data['honorees']
errors = []
redirects = []
for line in (ROOT / '_redirects').read_text().splitlines():
    if line.strip() and not line.startswith('#'):
        source, target, status = line.split()
        redirects.append((source, target))
        assert status == '301'

def local_exists(path):
    p = ROOT / unquote(path).lstrip('/')
    return p.is_file() or (p / 'index.html').is_file()

for _, target in redirects:
    if not local_exists(target): errors.append('Missing redirect target: ' + target)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.canonical=[]; self.ids=[]; self.h1=0
        self.json=False; self.jsontext=''; self.schemas=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag=='link' and a.get('rel')=='stylesheet': self.links.append(a['href'])
        if tag=='link' and a.get('rel')=='canonical': self.canonical.append(a['href'])
        if a.get('id'): self.ids.append(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='script' and a.get('type')=='application/ld+json': self.json=True; self.jsontext=''
    def handle_data(self,text):
        if self.json:self.jsontext+=text
    def handle_endtag(self,tag):
        if tag=='script' and self.json:
            self.schemas.append(json.loads(self.jsontext));self.json=False

pages=list(ROOT.rglob('index.html'))
for file in pages:
    path='/' + str(file.relative_to(ROOT)).removesuffix('index.html')
    text=file.read_text(); p=Page();p.feed(text)
    if p.h1!=1:errors.append(f'{path}: expected one H1, got {p.h1}')
    if p.canonical != [BASE+path] and not (path=='/' and p.canonical==[BASE]):errors.append(path+': wrong canonical')
    if len(p.ids)!=len(set(p.ids)):errors.append(path+': duplicate IDs')
    for href in p.links:
        u=urlparse(urljoin(BASE+path,href))
        if u.netloc=='reininghalloffame.com' and not local_exists(u.path):errors.append(f'{path}: missing link {href}')
    if 'gabriel-diano' in text:errors.append(path+': unsupported induction reference')

paths=set()
for r in rows:
    path=('lifetime-achievement/' if r['category']=='award' else 'hall-of-fame/')+r['slug']+'/index.html'
    if path in paths:errors.append('Duplicate roster record: '+path)
    paths.add(path)
    text=(ROOT/path).read_text()
    if r['category']=='award' and 'HOF '+str(r['year']) in text:errors.append(path+': award mislabeled as induction')
    if r['year']==2026 and 'December 2, 2026' not in text:errors.append(path+': missing forthcoming ceremony date')
for slug in ['mike-hancock','tom-mccutcheon','bob-santagata','americasnextgunmodel','this-chicsdundreamin']:
    assert any(r['slug']==slug and r['year']==2026 and r['category']!='award' for r in rows)
for slug in ['dan-huss','duane-latimer','jeff-petska','larry-kasten']:
    assert any(r['slug']==slug and r['category']=='award' for r in rows)
home=(ROOT/'index.html').read_text()
for unsupported in ['1949','Taris Little Step','Dell Bell','200+','Ima Cool Skip','Score: 231']:
    if unsupported in home:errors.append('Uncorrected homepage content: '+unsupported)
assert '30289' in home, 'Existing advertising zone must be preserved'
urls=ET.parse(ROOT/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')
assert len(urls)==len(pages)
for url in urls:
    loc=url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
    if not local_exists(urlparse(loc).path):errors.append('Missing sitemap destination: '+loc)
if errors: raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, {len(rows)} recognition records, all internal links, JSON-LD, canonicals, redirects and sitemap.')
