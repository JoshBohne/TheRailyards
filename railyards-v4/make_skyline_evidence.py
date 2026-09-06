"""Labelled skyline panoramas: every modelled landmark projected into the review
cameras with world_to_camera_view, written as HTML overlays over the renders
plus review/skyline-v5.json (in-frame, pixel height, occlusion by ray test).

Run on the saved scene after rendering:  blender -b railyards-v4.blend --python make_skyline_evidence.py
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT));REVIEW=OUT/'review'
import r4_geo
scene=bpy.data.scenes['Railyards v4']
landmarks=[]
for b in json.loads((OUT/'skyline-buildings.json').read_text())['buildings']:
    x,y=r4_geo.register((b['local_xy_m']['x'],b['local_xy_m']['y']));landmarks.append((b['name'],x,y,b['architectural_height_m'],'V3'))
for fn,tag in (('skyline-v4-additions.json','V4'),('skyline-v5-icons.json','V5')):
    for b in json.loads((OUT/fn).read_text())['buildings']:
        x,y=r4_geo.local_xy(b['latlon']['latitude'],b['latlon']['longitude']);landmarks.append((b['name'],x,y,b['architectural_height_m'],tag))
lake=json.loads((OUT/'lakefront-v5.json').read_text())['items']
for k,it in lake.items():
    if it.get('footprint'):
        pts=[r4_geo.register(p) for p in it['footprint']];x=sum(p[0] for p in pts)/len(pts);y=sum(p[1] for p in pts)/len(pts)
    else:x,y=r4_geo.local_xy(*it['latlon'])
    landmarks.append((k.replace('-',' ').title(),x,y,it.get('bowl_top') or it.get('hall_top') or it.get('dome_top') or it.get('roof'),'lakefront'))
cams={'home_upper_deck':('R3_home_upper_deck','interior-home_upper_deck.png',(1800,1125)),'left_field_skyline':('R3_left_field_skyline','interior-left_field_skyline.png',(1800,1125)),
      'third_base_seats':('R3_third_base_seats','interior-third_base_seats.png',(1800,1125)),'press_box':('R3_v4_press_box','review/v4-press_box.png',(1800,1125)),
      'east_lake_high':('R3_v4_east_lake_high','review/v4-east_lake_high.png',(1800,1125)),'south':('R2_south','final-south.png',(1800,1200))}
deps=bpy.context.evaluated_depsgraph_get();result={}
html=['<html><body style="font-family:Helvetica;background:#111;color:#eee"><h2>Skyline landmarks projected into the review cameras</h2><p>Label at each landmark roof point. Amber: visible (ray from camera to the roof point is unobstructed). Grey: in frame but occluded by nearer geometry. Rows without a marker are outside the frame.</p>']
for key,(camname,img,size) in cams.items():
    cam=bpy.data.objects[camname];scene.render.resolution_x,scene.render.resolution_y=size;rows=[];W=1400;sc=W/size[0]
    ov=[f'<h3>{key}</h3><div style="position:relative;width:{W}px;height:{size[1]*sc:.0f}px;margin-bottom:30px"><img src="../{img}" style="position:absolute;width:{W}px"/><svg style="position:absolute;left:0;top:0" width="{W}" height="{size[1]*sc:.0f}" font-family="Helvetica" font-size="11">']
    origin=cam.matrix_world.translation
    for name,x,y,h,tag in landmarks:
        top=Vector((x,y,8+h));q=world_to_camera_view(scene,cam,top)
        inframe=0<=q.x<=1 and 0<=q.y<=1 and q.z>0
        d=math.hypot(x-origin.x,y-origin.y);lens=cam.data.lens if cam.data.type=='PERSP' else 0
        px=(8+h-origin.z)/d*lens/36*size[0] if lens else None
        occluded=None
        if inframe:
            direction=(top-origin);hit,loc,nrm,idx,obj,mat=scene.ray_cast(deps,origin,direction.normalized(),distance=max(1.0,direction.length-70.0))  # stop short of the landmark itself
            occluded=bool(hit)
        rows.append({'name':name,'set':tag,'scene_xy':[round(x),round(y)],'height_m':h,'in_frame':inframe,'pixel':[round(q.x*size[0]),round((1-q.y)*size[1])] if inframe else None,'projected_height_px':round(px) if px else None,'occluded':occluded})
        if inframe:
            X=q.x*size[0]*sc;Y=(1-q.y)*size[1]*sc;col='#e3a350' if not occluded else '#888'
            ov.append(f'<circle cx="{X:.0f}" cy="{Y:.0f}" r="3" fill="{col}"/><text x="{X+4:.0f}" y="{Y-4:.0f}" fill="{col}" stroke="#000" stroke-width="2" paint-order="stroke">{name}</text>')
    ov.append('</svg></div>');html.append(''.join(ov));result[key]=rows
    vis=[r['name'] for r in rows if r['in_frame'] and not r['occluded']];occ=[r['name'] for r in rows if r['in_frame'] and r['occluded']]
    print(key,'visible',len(vis),'occluded',len(occ));print('   visible:',', '.join(vis));print('   occluded:',', '.join(occ))
(REVIEW/'skyline-v5.json').write_text(json.dumps({'landmarks':len(landmarks),'cameras':result},indent=1));(REVIEW/'skyline-panoramas.html').write_text('\n'.join(html)+'</body></html>')
scene.render.resolution_x,scene.render.resolution_y=1800,1198
