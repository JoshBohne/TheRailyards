"""Package the native V14 stills, completed night film and same-scene replay.

Run after all native frames finish. Generated files live outside source control.
"""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=ROOT/'work/night-game');p.add_argument('--ffmpeg',required=True);p.add_argument('--film-frames',type=Path)
    p.add_argument('--version',type=int,choices=[14,15],default=14);p.add_argument('--static',type=Path);p.add_argument('--social',type=Path);args=p.parse_args()
    work=args.work.resolve();frames=args.film_frames.resolve() if args.film_frames else work/'tracked-frames';model=ROOT/'sites/replay/public/model'
    animated=ROOT/f'railyards-v4/railyards-v{args.version}.blend';static=args.static or ROOT/f'railyards-v4/railyards-v{args.version}-site-static.blend'
    social_image=args.social or work/'og-home-run-layout2.png'
    receipt=json.loads((frames/'receipt.json').read_text());replay=json.loads((model/'replay.json').read_text());social=json.loads(social_image.with_suffix('.json').read_text())
    if replay['version']!=args.version:raise ValueError('Replay version does not match requested release')
    if receipt['renderedFrames']!=list(range(receipt['frames'])):raise ValueError('The full night film has not finished')
    if receipt['sceneSha256']!=sha(animated) or replay['sourceStaticSha256']!=sha(static) or social['sourceSceneSha256']!=sha(static):raise ValueError('Scene provenance does not match')
    if social['imageSha256']!=sha(social_image):raise ValueError('Social card does not match its receipt')
    for i in range(receipt['frames']):
        if not (frames/f'{i:04d}.png').is_file():raise FileNotFoundError(frames/f'{i:04d}.png')
    dest=work/'release';media=dest/'media';media.mkdir(parents=True,exist_ok=True)
    for source in (work/'stills').glob('*.png'):
        if source.name.startswith('before-'):continue
        evidence=json.loads(source.with_suffix('.render.json').read_text())
        if evidence['sourceStaticSha256']!=sha(static) or evidence['imageSha256']!=sha(source):raise ValueError(f'Stale still: {source}')
        shutil.copy2(source,media/f'v{args.version}-{source.name}')
    def run(options):subprocess.run([args.ffmpeg,'-y','-loglevel','error',*map(str,options)],check=True)
    run(['-framerate',24,'-i',frames/'%04d.png','-frames:v',receipt['frames'],'-c:v','libx264','-crf',19,'-pix_fmt','yuv420p','-movflags','+faststart',media/'home-run.mp4'])
    run(['-i',frames/'0202.png','-frames:v',1,'-q:v',2,media/'home-run-poster.jpg'])
    social_name='og-home-run-v14-layout2.jpg' if args.version==14 else f'og-home-run-v{args.version}.jpg'
    run(['-i',social_image,'-vf','scale=1200:630','-frames:v',1,'-q:v',2,media/social_name])
    for name,file in [('north','aecom-north-aerial.png'),('south','aecom-south-aerial.jpg'),('bridge','user-bridge-view.png')]:
        run(['-i',ROOT/'reconstruction-references'/file,'-vf','scale=min(1600\\,iw):-2','-frames:v',1,'-q:v',2,media/f'source-{name}.jpg'])
    shutil.copytree(model,dest/'model',dirs_exist_ok=True)
    release={'sceneVersion':args.version,'sourceStaticSha256':sha(static),'sourceAnimatedSha256':sha(animated),'seatCount':replay['seatCount'],'waterDistanceFt':replay['waterDistanceFt'],'splashDistanceFt':replay['splashDistanceFt'],'socialCard':social,'film':{'fps':24,'frames':288,'duration':12,'shots':receipt['shots'],'tracker':receipt.get('tracker'),'posterFrame':202},'files':[{'path':str(p.relative_to(dest)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='release.json']}
    (dest/'release.json').write_text(json.dumps(release,indent=2)+'\n')
    print(json.dumps({'release':str(dest),'files':len(release['files']),'film':release['film']}))
if __name__=='__main__':main()
