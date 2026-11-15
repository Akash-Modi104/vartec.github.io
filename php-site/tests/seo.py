"""SEO audit of every public page, fetched as the real site address."""
import sys, re, json, urllib.request
from html.parser import HTMLParser
base, host = sys.argv[1], sys.argv[2]
def fetch(path):
    r = urllib.request.Request(base + path, headers={'Host': host})
    try:
        with urllib.request.urlopen(r) as f: return f.status, f.read().decode(), dict(f.headers)
    except urllib.error.HTTPError as e: return e.code, e.read().decode(), dict(e.headers)
class P(HTMLParser):
    def __init__(s): super().__init__(); s.tags=[]; s.heads=[]; s.cur=None; s.text=''; s.ld=[]; s.inld=False; s.title=''; s.intitle=False
    def handle_starttag(s,t,a):
        a=dict(a); s.tags.append((t,a))
        if t in('h1','h2','h3'): s.cur=t; s.text=''
        if t=='script' and a.get('type')=='application/ld+json': s.inld=True; s.text=''
        if t=='title': s.intitle=True
    def handle_endtag(s,t):
        if t==s.cur: s.heads.append((t,' '.join(s.text.split()))); s.cur=None
        if t=='script' and s.inld: s.ld.append(s.text); s.inld=False
        if t=='title': s.intitle=False
    def handle_data(s,d):
        if s.cur or s.inld: s.text+=d
        if s.intitle: s.title+=d
st, sm, _ = fetch('/sitemap.xml'); urls=[u.replace('https://'+host,'') for u in re.findall(r'<loc>([^<]+)',sm)]
print('sitemap', st, len(urls), 'urls;', 'robots:', fetch('/robots.txt')[1].replace('\n',' | '))
titles={}; descs={}; problems=[]
for u in urls:
    st, html, hd = fetch(u); p=P(); p.feed(html)
    meta={ (a.get('name') or a.get('property')):a.get('content') for t,a in p.tags if t=='meta' and (a.get('name') or a.get('property'))}
    link={a.get('rel'):a.get('href') for t,a in p.tags if t=='link'}
    imgs=[a for t,a in p.tags if t=='img']; h1=[h for h in p.heads if h[0]=='h1']
    d=meta.get('description',''); t=p.title.strip()
    issues=[]
    if st!=200: issues.append(f'status {st}')
    if not 30<=len(t)<=62: issues.append(f'title length {len(t)}')
    if not 70<=len(d)<=160: issues.append(f'description length {len(d)}')
    if link.get('canonical')!='https://'+host+u: issues.append('canonical '+str(link.get('canonical')))
    if meta.get('robots','').split(',')[0]!='index': issues.append('robots '+meta.get('robots',''))
    if len(h1)!=1: issues.append(f'{len(h1)} h1')
    for k in ('og:title','og:description','og:image','og:url','twitter:card','twitter:image'):
        if not meta.get(k): issues.append('missing '+k)
    if any('alt' not in a for a in imgs): issues.append('img without alt')
    if any(not(a.get('width') and a.get('height')) for a in imgs): issues.append('img without size: '+str([a.get('src') for a in imgs if not a.get('width')][:2]))
    levels=[int(h[0][1]) for h in p.heads]
    if any(b-a>1 for a,b in zip(levels,levels[1:])): issues.append('heading level skipped')
    try:
        g=[json.loads(x) for x in p.ld]; types=[n['@type'] for x in g for n in x.get('@graph',[x])]
    except Exception as e: types=[]; issues.append('bad JSON-LD '+str(e))
    if t in titles: issues.append('duplicate title with '+titles[t])
    if d in descs: issues.append('duplicate description with '+descs[d])
    titles[t]=u; descs[d]=u
    print(f"{u:38} {len(html)//1024:3}KB title[{len(t)}] desc[{len(d)}] imgs {len(imgs)} schema {types} {'| ' + '; '.join(issues) if issues else '| ok'}")
    problems+=issues
    if u in ('/','/services/epc/'): print('   title:', t); print('   desc :', d); print('   h    :', p.heads[:6])
st,html,_=fetch('/nope'); print('404 page ->', st, 'noindex' in html)
st,html,_=fetch('/services/epc'); print('no-slash ->', st)
print('TOTAL ISSUES', len(problems))
