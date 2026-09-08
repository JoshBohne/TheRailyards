"""Project the authored ball history through each fixed night-film camera.

Run with Blender against the animated scene; writes data only, never the scene.
"""
import bpy,json,hashlib,os
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path(__file__).resolve().parents[1]
work=Path(os.environ.get('RAILYARDS_TRACKER_WORK',str(root/'work/night-game')))
receipt=json.loads((work/'frames/receipt.json').read_text())
replay_path=root/'sites/replay/public/model/replay.json'
replay=json.loads(replay_path.read_text())
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==receipt['sceneSha256']
scene=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=scene
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
cam=bpy.data.objects.new('Tracker projection',bpy.data.cameras.new('Tracker projection'));scene.collection.objects.link(cam)
samples=replay['ballSamples']
def position(t):
    at=min(len(samples)-1,max(0,t/replay['duration']*(len(samples)-1)));i=int(at);a=Vector(samples[i]);b=Vector(samples[min(i+1,len(samples)-1)]);p=a.lerp(b,at-i)
    return Vector((p.x,-p.z,p.y))
frames=[]
for frame in range(receipt['frames']):
    t=round(frame/24*60)/60
    shot=next(s for s in reversed(receipt['shots']) if frame/24>=s['startSeconds'])
    cam.location=shot['position'];cam.rotation_euler=(Vector(shot['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=shot['lens'];bpy.context.view_layer.update()
    points=[]
    if replay['contact']<=t<replay['splash']:
        start=max(replay['contact'],t-.45)
        for i in range(25):
            p=world_to_camera_view(scene,cam,position(start+(t-start)*i/24))
            points.append([p.x*1280,(1-p.y)*720,p.z])
    frames.append(points)
(work/'tracker-projections.json').write_text(json.dumps({'sceneSha256':receipt['sceneSha256'],'replaySha256':hashlib.sha256(replay_path.read_bytes()).hexdigest(),'frames':frames})+'\n')
print('Projected 288 tracker frames from the authored flight and film cameras')
