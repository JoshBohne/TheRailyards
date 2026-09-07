"""Build two self-contained static sites from saved-scene render artifacts.

Run: uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --encode
Both outputs live under work/web-dist, outside Git. No Blender UI is needed.
"""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'railyards-v4'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--encode',action='store_true');parser.add_argument('--replay',action='store_true');parser.add_argument('--scene-version',type=int,choices=[9,11],default=11);args=parser.parse_args()
    current=MODEL/f'review/v{args.scene_version}'
    import imageio_ffmpeg
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    movies=current/'movies';movies.mkdir(exist_ok=True)
    if args.encode:
        for name,count in [('arrival',192),('left_center',192),('boat',192),('river',168)]:
            folder=current/name
            missing=[f'{i:04d}.png' for i in range(count) if not (folder/f'{i:04d}.png').is_file()]
            if missing:raise FileNotFoundError(f'{name}: missing {len(missing)} rendered frames; first {missing[0]}')
            target=movies/f'{name}.mp4'
            if target.exists() and target.stat().st_mtime>max((folder/f'{i:04d}.png').stat().st_mtime for i in range(count)):continue
            subprocess.run([ffmpeg,'-y','-loglevel','error','-framerate','24','-i',str(folder/'%04d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    if args.replay:
        subprocess.run(['pnpm','--dir',str(ROOT/'sites/replay'),'build'],check=True)
    images={name:current/f'{name}.png' for name in ['arrival','left_center','boat','skyline_west','skyline_east']}
    images['river-poster']=current/'river/0110.png'
    images['v8-left_center']=MODEL/'review/v8-experiences/left_center.png'
    for name in ['willis','regis','pru']:
        for version in ['before','after']:images[f'{name}-{version}']=MODEL/f'review/v9/forms/{name}-{version}.png'
    sources={'north':'aecom-north-aerial.png','south':'aecom-south-aerial.jpg','bridge':'user-bridge-view.png'}
    for name,file in sources.items():
        images[f'source-{name}']=ROOT/'reconstruction-references'/file
        images[f'v9-{name}']=MODEL/f'v9-{name}.png'
        images[f'v8-{name}']=MODEL/f'final-{name}.png'
        images[f'v3-{name}']=ROOT/f'railyards-v3/final-{name}.png'
    if args.scene_version==11:
        for name in sources:images[f'v11-{name}']=MODEL/f'v11-{name}.png'
        for name,file in {'entrance-before':'entrance-before.png','entrance-after':'C_entrance_landing.png','riverwalk-before':'riverwalk-before.png','riverwalk-after':'F_riverwalk_under_deck.png','corner-stair':'I_corner_stair_close.png','lf-stair':'M_lf_stair_side.png','rf-stair':'K_rf_stair.png'}.items():images[name]=current/file
    images['model-north']=images[f'v{args.scene_version}-north']
    for kind in ['public','review']:
        dest=ROOT/'work/web-dist'/kind;dest.mkdir(parents=True,exist_ok=True)
        for file in (ROOT/'sites'/kind).iterdir():
            if file.is_file():shutil.copy2(file,dest/file.name)
        media=dest/'media';media.mkdir(exist_ok=True)
        chosen=images if kind=='review' else {k:v for k,v in images.items() if k in ['arrival','left_center','boat','skyline_west','skyline_east','river-poster','source-north','model-north']}
        for name,source in chosen.items():
            if not source.is_file():raise FileNotFoundError(source)
            target=media/f'{name}.jpg'
            if not target.exists() or target.stat().st_mtime<source.stat().st_mtime:
                subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(source),'-vf','scale=min(1600\\,iw):-2','-frames:v','1','-q:v','3',str(target)],check=True)
        for name in ['arrival','left_center','boat','river']:
            source=movies/f'{name}.mp4'
            if not source.is_file():raise FileNotFoundError(source)
            shutil.copy2(source,media/source.name)
        if kind=='public' and args.replay:
            if (dest/'replay').exists():shutil.rmtree(dest/'replay')
            shutil.copytree(ROOT/'sites/replay/dist',dest/'replay')
        manifest={'site':kind,'sceneVersion':args.scene_version,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'workingTreeDirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),'files':[{'path':str(p.relative_to(dest)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='build-manifest.json']}
        (dest/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'{kind}: {dest} ({len(manifest["files"])} files)')

if __name__=='__main__':main()
