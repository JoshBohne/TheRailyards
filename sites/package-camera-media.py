"""Replace film/stills while preserving the published replay and other media."""
import argparse,hashlib,subprocess,zipfile
from pathlib import Path
import imageio_ffmpeg
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--frames',type=Path,required=True);p.add_argument('--east',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
for i in range(252):
 if not (a.frames/f'{i:04d}.png').is_file():raise FileNotFoundError(f'Missing frame {i}')
ff=imageio_ffmpeg.get_ffmpeg_exe()
def run(args):subprocess.run([ff,'-y','-loglevel','error',*map(str,args)],check=True)
run(['-framerate',24,'-i',a.frames/'%04d.png','-frames:v',252,'-c:v','libx264','-crf',18,'-pix_fmt','yuv420p','-movflags','+faststart',a.frames/'home-run.mp4'])
run(['-i',a.frames/'0000.png','-frames:v',1,'-q:v',3,a.frames/'home-run-poster.jpg'])
replacements={f'additions/media/{name}':a.frames/name for name in ['home-run.mp4','home-run-poster.jpg']}
replacements.update({f'additions/media/{f.name}':f for f in a.east.glob('*.jpg')})
replacements['additions/overview-receipt.json']=a.frames/'receipt.json'
replacements['additions/east-bank-receipt.json']=a.east/'east-bank-receipt.json'
with zipfile.ZipFile(a.base) as old,zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as new:
 for item in old.infolist():
  if item.filename not in replacements:new.writestr(item,old.read(item))
 for name,path in replacements.items():new.write(path,name)
print(hashlib.sha256(a.output.read_bytes()).hexdigest())
