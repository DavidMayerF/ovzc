#!/usr/bin/env python3
"""Generate OVZC static message pages from messages/data/*.json (stdlib only)."""
import argparse
import datetime as dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'messages' / 'data'
OUT = ROOT / 'docs' / 'messages'
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
CSS = '''
:root{--ochre:#c97900;--dark:#9f6100;--paper:#fbf6ea;--ink:#2d2112;--muted:#705332}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(90deg,var(--ochre),var(--dark));color:var(--ink);font:18px/1.7 Georgia,"Times New Roman",serif}
.page{max-width:860px;min-height:100vh;margin:auto;background:var(--paper);padding:clamp(28px,7vw,76px);box-shadow:0 0 70px #42260030}
a{color:#6b3d00;text-underline-offset:3px}h1{font-size:clamp(2.2rem,5vw,3.8rem);line-height:1.13;font-weight:400;margin:18px 0 24px}p{white-space:pre-wrap}nav{font-size:.95rem;margin-bottom:40px}nav a{margin-right:20px}.eyebrow{color:var(--muted);font-size:.92rem}.rule{width:110px;height:3px;background:var(--ochre);margin:25px 0 35px;opacity:.65}.entry{padding:22px 0;border-bottom:1px solid #70533233}.entry h2{font-size:1.45rem;font-weight:400;margin:0 0 5px}.entry p{margin:4px 0}.entry .date{font-size:.9rem;color:var(--muted)}footer{border-top:1px solid #70533233;margin-top:70px;padding-top:24px;color:var(--muted);font-size:.9rem}img.attachment{max-width:100%;height:auto;display:block;margin:26px 0;border-radius:4px}@media(max-width:860px){body{background:var(--paper)}}
'''

def esc(s): return html.escape(str(s), quote=True)
def page(title, content, nested=False):
    home = '../../' if nested else '../'
    directory = '../' if nested else './'
    return f'''<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} — Ojai Valley Zen Center</title><style>{CSS}</style></head><body><main class="page"><nav><a href="{home}">← Home</a><a href="{directory}">Messages &amp; Announcements</a></nav>{content}<footer>Ojai Valley Zen Center · Zen Practice in the Ojai Valley</footer></main></body></html>\n'''

def load_messages():
    messages=[]
    for path in sorted(DATA.glob('*.json')):
        m=json.loads(path.read_text(encoding='utf-8'))
        for field in ('id','title','date','body'):
            if not isinstance(m.get(field),str) or not m[field].strip():
                raise ValueError(f'{path.name}: missing/invalid {field}')
        if not SLUG.fullmatch(m['id']): raise ValueError(f'{path.name}: unsafe id')
        dt.date.fromisoformat(m['date'])
        if m.get('expires'): dt.date.fromisoformat(m['expires'])
        if m.get('images') is not None:
            if not isinstance(m['images'],list): raise ValueError(f'{path.name}: images must be list')
            for name in m['images']:
                if not isinstance(name,str) or not re.fullmatch(r'[a-zA-Z0-9_-]+\.(?:png|jpg|jpeg|webp|gif)',name):
                    raise ValueError(f'{path.name}: invalid image filename')
                if not (OUT / 'images' / name).is_file():
                    raise ValueError(f'{path.name}: missing docs/messages/images/{name}')
        messages.append(m)
    ids=[m['id'] for m in messages]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate message IDs')
    return sorted(messages,key=lambda m:(m['date'],m['id']),reverse=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--as-of',help='Date for directory expiration filtering, YYYY-MM-DD (default today)')
    args=parser.parse_args()
    today=dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    messages=load_messages()
    OUT.mkdir(parents=True,exist_ok=True)
    for m in messages:
        body=f'<div class="eyebrow">{esc(m["date"])}</div><h1>{esc(m["title"])}</h1><div class="rule"></div>'
        for paragraph in m['body'].strip().split('\n\n'):
            body+=f'<p>{esc(paragraph.strip())}</p>'
        for name in m.get('images',[]):
            body+=f'<img class="attachment" src="../images/{esc(name)}" alt="Attachment for {esc(m["title"])}">'
        destination=OUT/m['id']/'index.html'
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(page(m['title'],body,nested=True),encoding='utf-8')
    visible=[m for m in messages if not m.get('expires') or dt.date.fromisoformat(m['expires'])>=today]
    entries=''.join(f'<article class="entry"><div class="date">{esc(m["date"])}</div><h2><a href="{esc(m["id"])}/">{esc(m["title"])}</a></h2></article>' for m in visible)
    content='<div class="eyebrow">Ojai Valley Zen Center</div><h1>Messages &amp; Announcements</h1><div class="rule"></div>'+(entries or '<p>No announcements have been posted yet.</p>')
    (OUT/'index.html').write_text(page('Messages & Announcements',content),encoding='utf-8')
    print(f'Generated {len(messages)} message page(s); {len(visible)} shown in directory as of {today}.')
    print('Review docs/messages/ before committing. No messages were sent.')

if __name__=='__main__': main()
