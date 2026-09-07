"""Package V12 supplemental stills, the overview edit, and rebuilt replay."""
import argparse,hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
import imageio_ffmpeg
p=argparse.ArgumentParser();p.add_argument('--fable-root',type=Path,required=True);p.add_argument('--frames',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];dest=a.output/'additions';media=dest/'media';media.mkdir(parents=True,exist_ok=True)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
def run(args):subprocess.run([ffmpeg,'-y','-loglevel','error',*map(str,args)],check=True)
for i in range(252):
 if not (a.frames/f'{i:04d}.png').is_file():raise FileNotFoundError(f'Missing overview frame {i}')
run(['-framerate','24','-i',a.frames/'%04d.png','-frames:v','252','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',media/'home-run.mp4'])
run(['-i',a.frames/'0036.png','-frames:v','1','-q:v','3',media/'home-run-poster.jpg'])
assets=json.loads((root/'sites/gallery-assets.json').read_text())
for kind,entries in assets.items():
 for name,label in entries:
  source=a.fable_root/'railyards-v4'/(f'v12-interior-{name}.png' if kind=='interiors' else f'review/v12/v12-{name}.png')
  run(['-i',source,'-vf','scale=min(1600\\,iw):-2','-frames:v','1','-q:v','3',media/f'{name}.jpg'])
if (dest/'replay').exists():shutil.rmtree(dest/'replay')
shutil.copytree(root/'sites/replay/dist',dest/'replay')
shutil.copy2(a.frames/'receipt.json',dest/'overview-receipt.json')
archive=a.output/'railyards-v12-site-additions.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(dest.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(a.output))
print(archive);print(hashlib.sha256(archive.read_bytes()).hexdigest())
