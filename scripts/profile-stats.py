import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from urllib.request import Request, urlopen

COLORS = {'JavaScript':'#f7d46e','HTML':'#ffa78e','PHP':'#aba4ff','Python':'#82c9ff','Jupyter Notebook':'#80efd0'}

def fetch_repos(owner):
    repos = []
    page = 1
    while True:
        request = Request(f'https://api.github.com/users/{owner}/repos?type=owner&per_page=100&page={page}', headers={'Accept':'application/vnd.github+json','User-Agent':'github-profile-stats','X-GitHub-Api-Version':'2022-11-28'})
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1

def render(repos, owner, mobile=False):
    public = [r for r in repos if not r.get('private') and not r.get('fork')]
    languages = Counter(r['language'] for r in public if r.get('language'))
    stars = sum(r.get('stargazers_count', 0) for r in public)
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    def text(x,y,label,size=18,color='#a9b8d4',weight=400):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(label))}</text>'
    if mobile:
        body='<rect x="1" y="1" width="598" height="458" rx="18" fill="#111929" stroke="#293650"/>'
        body+=text(26,38,'GITHUB / PUBLIC REPOSITORIES',15,'#80efd0',700)
        for x,value,label in [(26,len(public),'Public repos'),(229,stars,'Repo stars'),(420,len(languages),'Languages')]:
            body+=text(x,116,value,54,'#eff3ff',700)+text(x,151,label,21)
        body+='<path d="M26 181H574" stroke="#293650"/>'
        body+=text(26,216,'REPOS BY PRIMARY LANGUAGE',16,'#71809b',700)
        x=26
        total=sum(languages.values()) or 1
        for language,count in languages.most_common():
            width=548*count/total
            body+=f'<rect x="{x:.2f}" y="240" width="{width:.2f}" height="12" fill="{COLORS.get(language,"#a9b8d4")}"/>'
            x+=width
        for i,(language,count) in enumerate(languages.most_common()):
            x=26+(i%2)*282
            y=297+(i//2)*44
            body+=f'<circle cx="{x+4}" cy="{y-6}" r="4" fill="{COLORS.get(language,"#a9b8d4")}"/>'+text(x+16,y,f'{language} · {count}',19)
        body+=text(26,431,'Updated '+stamp+' UTC',15,'#71809b')
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="460" viewBox="0 0 600 460" role="img" aria-label="{escape(owner)} public repository statistics"><style>text{{font-family:Arial,Helvetica,sans-serif}}</style>{body}</svg>'
    body='<rect x="1" y="1" width="1198" height="302" rx="18" fill="#111929" stroke="#293650"/>'
    body+=text(32,35,'GITHUB / PUBLIC REPOSITORIES',13,'#80efd0',700)+text(967,35,'Updated '+stamp,13,'#71809b')
    for x,value,label in [(32,len(public),'Public repositories'),(365,stars,'Stars across repositories'),(808,len(languages),'Primary languages')]:
        body+=text(x,104,value,45,'#eff3ff',700)+text(x,137,label,18)
    body+='<path d="M328 61V143M763 61V143M32 169H1168" stroke="#293650"/>'
    body+=text(32,199,'REPOSITORIES BY PRIMARY LANGUAGE',12,'#71809b',700)
    x=32
    total=sum(languages.values()) or 1
    for language,count in languages.most_common():
        width=1136*count/total
        body+=f'<rect x="{x:.2f}" y="218" width="{width:.2f}" height="10" fill="{COLORS.get(language,"#a9b8d4")}"/>'
        x+=width
    x=32
    for language,count in languages.most_common():
        label=f'{language} · {count}'
        body+=f'<circle cx="{x+4}" cy="263" r="4" fill="{COLORS.get(language,"#a9b8d4")}"/>'+text(x+17,268,label,15)
        x+=len(label)*8+54
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="304" viewBox="0 0 1200 304" role="img" aria-labelledby="title desc"><title id="title">{escape(owner)} public GitHub repository statistics</title><desc id="desc">{len(public)} public non-fork repositories, {stars} stars, {len(languages)} primary languages. The language bar counts repositories, not code volume. Updated {stamp} UTC.</desc><style>text{{font-family:Arial,Helvetica,sans-serif}}</style>{body}</svg>'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--owner',default='ALPHARIET')
    parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path,default=Path('dist/stats.svg'))
    args=parser.parse_args()
    repos=json.loads(args.input.read_text()) if args.input else fetch_repos(args.owner)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(render(repos,args.owner))
    args.output.with_name(args.output.stem+'-mobile.svg').write_text(render(repos,args.owner,mobile=True))
    print(f'Updated {args.output} from public repository metadata.')

if __name__=='__main__':
    main()
