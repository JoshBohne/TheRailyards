"""Composite a tapered yellow broadcast tracker into the native film frames.

uv run --with pillow python sites/compose-ball-tracker.py
The trail is a screen graphic projected from the actual authored flight.
"""
import json,hashlib,shutil,argparse
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=Path(__file__).resolve().parents[1]/'work/night-game');args=p.parse_args()
work=args.work;source=work/'frames';dest=work/'tracked-frames';dest.mkdir(exist_ok=True)
receipt=json.loads((source/'receipt.json').read_text());projections=json.loads((work/'tracker-projections.json').read_text())
assert receipt['sceneSha256']==projections['sceneSha256']
replay=Path(__file__).resolve().parents[1]/'sites/replay/public/model/replay.json'
assert hashlib.sha256(replay.read_bytes()).hexdigest()==projections['replaySha256']
assert len(projections['frames'])==receipt['frames']
for frame,points in enumerate(projections['frames']):
    src=source/f'{frame:04d}.png';target=dest/src.name
    if not points:shutil.copy2(src,target);continue
    with Image.open(src) as image:
        overlay=Image.new('RGBA',(image.width*2,image.height*2));draw=ImageDraw.Draw(overlay)
        for i,(a,b) in enumerate(zip(points,points[1:])):
            if min(a[2],b[2])<=0:continue
            strength=(i+1)/(len(points)-1);line=[(a[0]*2,a[1]*2),(b[0]*2,b[1]*2)];width=max(2,round((1+3*strength)*2))
            draw.line(line,fill=(65,45,0,round(90*strength)),width=width+3)
            draw.line(line,fill=(255,212,35,round(235*strength)),width=width)
        overlay=overlay.resize(image.size,Image.Resampling.LANCZOS)
        Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB').save(target)
receipt['tracker']={'color':'#ffd423','tailSeconds':.45,'projectionSha256':hashlib.sha256((work/'tracker-projections.json').read_bytes()).hexdigest(),'note':'Projected broadcast graphic; hidden before contact and after splash.'}
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'Composited {len(projections["frames"])} frames into {dest}')
