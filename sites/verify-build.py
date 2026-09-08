"""Verify generated local links, media identity, scene alignment, and social cards."""
import argparse,hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[];self.meta={};self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for key in ['src','href','poster']:
            if key in a:self.urls.append(a[key])
        if 'id' in a:self.ids.add(a['id'])
        if tag=='meta':self.meta[a.get('property',a.get('name',''))]=a.get('content','')
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);args=p.parse_args();root=args.directory.resolve()
manifest=json.loads((root/'build-manifest.json').read_text());assert manifest['sceneVersion']==14
for item in manifest['files']:
    f=root/item['path'];assert f.is_file(),f;assert hashlib.sha256(f.read_bytes()).hexdigest()==item['sha256'],f
assert json.loads((root/'replay/model/replay.json').read_text())['sourceStaticSha256']==manifest['sourceStaticSha256']
for page in root.glob('*.html'):
    text=page.read_text();parser=Links();parser.feed(text)
    for url in parser.urls:
        parsed=urlparse(url)
        if parsed.scheme or parsed.netloc:continue
        path=(page.parent/unquote(parsed.path)).resolve() if parsed.path else page
        if path.is_dir():path/= 'index.html'
        assert path.is_relative_to(root) and path.exists(),(page,url)
        if parsed.fragment and path.suffix=='.html' and '=' not in parsed.fragment:
            other=Links();other.feed(path.read_text());assert parsed.fragment in other.ids,(page,url)
    if 'og:image' in parser.meta:
        assert parser.meta['og:image'].endswith('/media/og-home-run-v14-layout2.jpg')
        assert parser.meta['twitter:image']==parser.meta['og:image']
        assert parser.meta['og:image:width']=='1200' and parser.meta['og:image:height']=='630'
    assert not re.search(r'media/(?:model-|v12-|v13-)',text),page
    if '<nav ' in text:
        for label in ['Overview','Choose your seat','Gallery','How it was made']:assert label in text,page
print(json.dumps({'pages':len(list(root.glob('*.html'))),'files':len(manifest['files']),'sourceStaticSha256':manifest['sourceStaticSha256'],'seatCount':manifest['seatCount'],'status':'PASS'}))
