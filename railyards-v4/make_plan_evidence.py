"""Labelled RF plan and source-image overlays proving the board/support setback.

Run inside Blender on the saved V4 scene.  Writes review/rf-plan-evidence.json
(clearances in metres), review/rf-plan.svg (labelled plan, metres) and
review/rf-source-overlays.html (field polygon, board footprint and pylon bases
projected into the three calibrated source cameras with world_to_camera_view).
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parent;REVIEW=OUT/'review';REVIEW.mkdir(exist_ok=True)
scene=bpy.data.scenes['Railyards v4'];spec=json.loads((OUT/'scene-spec.json').read_text())
field=[(p[0],p[1]) for p in spec['field_boundary']];home=(0.0,0.0)
polygon=[home]+field  # playable area: foul lines from home plus the traced outfield wall
rf=spec['rf_scoreboard'];top=Vector(spec['anchors']['rf_scoreboard_top']);w=rf['width_m'];h=rf['height_m'];angle=math.radians(rf['angle_deg'])
t=Vector((math.cos(angle),math.sin(angle),0));n=Vector((t.y,-t.x,0))
screen_depth=1.14+.04  # screen face offset used by r3_scoreboards
board=[top+t*u+n*d for u,d in [(-w/2-.5,-1.3),(w/2+.5,-1.3),(w/2+.5,1.3),(-w/2-.5,1.3)]]
screens=[top+t*u+n*d for u,d in [(-w/2,-screen_depth),(w/2,-screen_depth),(w/2,screen_depth),(-w/2,screen_depth)]]
service=[top+t*u+n*d for u,d in [(-w/2-.9,-1.85),(w/2+.9,-1.85),(w/2+.9,1.85),(-w/2-.9,1.85)]]
pylons=[]
for u in (-w*rf.get('pylon_fraction',.33),w*rf.get('pylon_fraction',.33)):
    p=top+t*u
    pylons.append([p+t*du+n*dd for du,dd in [(-1.6,-1.8),(1.6,-1.8),(1.6,1.8),(-1.6,1.8)]])
def seg_dist(p,a,b):
    a,b,p=Vector(a),Vector(b),Vector(p);ab=b-a
    if ab.length<1e-9:return (p-a).length
    s=max(0,min(1,(p-a).dot(ab)/ab.length_squared));return (p-(a+ab*s)).length
def inside(p,ring):
    x,y=p;v=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:v=not v
    return v
def clearance(pts):
    out=[]
    for p in pts:
        d=min(seg_dist((p.x,p.y),a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1]))
        out.append({'xy':[round(p.x,2),round(p.y,2)],'inside_playable':inside((p.x,p.y),polygon),'distance_to_boundary_m':round(d,2)})
    return out
track=15*0.3048
evidence={'playable_polygon':polygon,'warning_track_width_m':track,'warning_track_note':'The warning track is inset inside the traced boundary (r3_field), so any footprint outside the polygon clears it by construction; clearance below is to the wall line, add %.2f m to reach the track edge.'%track,
 'board_frame_corners':clearance(board),'screen_corners':clearance(screens),'service_platform_corners':clearance(service),
 'pylon_footprints':[clearance(p) for p in pylons],'anchor':list(top),'width_m':w,'height_m':h,'angle_deg':rf['angle_deg'],'bottom_z':top.z-h,'support_base_z':rf['support_base_z'],
 'v3_anchor':[96.86961510459159,25.39420437817199,38.0],'v3_anchor_inside_playable':inside((96.87,25.39),polygon)}
allpts=evidence['board_frame_corners']+evidence['screen_corners']+evidence['service_platform_corners']+[c for p in evidence['pylon_footprints'] for c in p]
evidence['all_outside_playable']=all(not c['inside_playable'] for c in allpts)
evidence['min_clearance_m']=min(c['distance_to_boundary_m'] for c in allpts)
(REVIEW/'rf-plan-evidence.json').write_text(json.dumps(evidence,indent=2))
# Labelled plan SVG (metres; x right, y up).
X0,X1,Y0,Y1=55,135,-30,80;S=12
def sx(x):return (x-X0)*S
def sy(y):return (Y1-y)*S
def poly(pts,style):return '<polygon points="%s" %s/>'%(' '.join(f'{sx(p[0]):.1f},{sy(p[1]):.1f}' for p in pts),style)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{(X1-X0)*S}" height="{(Y1-Y0)*S}" font-family="Helvetica,Arial" font-size="12">','<rect width="100%" height="100%" fill="#f4f2ee"/>']
for x in range(X0,X1+1,10):svg.append(f'<line x1="{sx(x)}" y1="0" x2="{sx(x)}" y2="{(Y1-Y0)*S}" stroke="#ddd"/><text x="{sx(x)+2}" y="12" fill="#888">x{x}</text>')
for y in range(Y0,Y1+1,10):svg.append(f'<line x1="0" y1="{sy(y)}" x2="{(X1-X0)*S}" y2="{sy(y)}" stroke="#ddd"/><text x="2" y="{sy(y)-2}" fill="#888">y{y}</text>')
svg.append(poly(polygon,'fill="#cfe8c4" stroke="#2f7d32" stroke-width="2"'))
inner=[(p[0]-track*Vector((p[0],p[1])).normalized().x if p!=home else 0,p[1]-track*Vector((p[0],p[1])).normalized().y if p!=home else 0) for p in polygon]
svg.append(poly(inner,'fill="none" stroke="#b8862b" stroke-width="1.5" stroke-dasharray="6,4"'))
ring=[(Vector(p)+Vector(p).normalized()*10.0) for p in field]
svg.append(poly([(p.x,p.y) for p in ring]+[(2.3,103.9),(75.2,-20.9)],'fill="none" stroke="#7a7a7a" stroke-width="1" stroke-dasharray="3,3"'))
svg.append(f'<rect x="{sx(112)}" y="{sy(80)}" width="{12*S}" height="{110*S}" fill="#e6e0d3" stroke="none"/><rect x="{sx(128)}" y="{sy(80)}" width="{7*S}" height="{110*S}" fill="#a9c4d8"/>')
svg.append(poly([(p.x,p.y) for p in service],'fill="#ffe08a" stroke="#a37b00"'))
svg.append(poly([(p.x,p.y) for p in board],'fill="#3a3a3a" stroke="#000"'))
svg.append(poly([(p.x,p.y) for p in screens],'fill="#111" stroke="none"'))
for p in pylons:svg.append(poly([(q.x,q.y) for q in p],'fill="#c0392b" stroke="#000"'))
svg.append(f'<circle cx="{sx(96.87)}" cy="{sy(25.39)}" r="5" fill="none" stroke="#c0392b" stroke-width="2"/><text x="{sx(96.87)-70}" y="{sy(25.39)+18}" fill="#c0392b">V3 anchor (inside field)</text>')
svg.append(f'<text x="{sx(top.x)+8}" y="{sy(top.y)}" fill="#000" font-weight="bold">RF board {w:.0f}x{h:.1f} m, top z{top.z}, bottom z{top.z-h:.1f}</text>')
svg.append(f'<text x="{sx(100)+4}" y="{sy(0)+14}" fill="#2f7d32">RF foul pole (100,0)</text><text x="{sx(60)}" y="{sy(60)}" fill="#2f7d32" font-size="14">playable area</text>')
svg.append(f'<text x="{sx(104)}" y="{sy(64)}" fill="#7a7a7a">podium ring / bleacher zone (10 m)</text><text x="{sx(112.5)}" y="{sy(76)}" fill="#555">riverwalk z4.95</text><text x="{sx(128.5)}" y="{sy(76)}" fill="#246">river</text>')
svg.append(f'<text x="{sx(60)}" y="{sy(-24)}" fill="#000">min clearance to wall {evidence["min_clearance_m"]} m; all footprints outside playable: {evidence["all_outside_playable"]}</text>')
svg.append('</svg>');(REVIEW/'rf-plan.svg').write_text('\n'.join(svg))
# Source overlays.
images={'north':('../reconstruction-references/aecom-north-aerial.png',(1944,1294)),'south':('../reconstruction-references/aecom-south-aerial.jpg',(5000,3333)),'bridge':('../reconstruction-references/user-bridge-view.png',(1440,959))}
html=['<html><body style="font-family:Helvetica;background:#111;color:#eee"><h2>RF board / support footprints projected into the calibrated source cameras</h2><p>Green: playable polygon at z12. Black: board frame at its bottom (z%.1f) and top. Red: pylon footprints at the podium ring (z13.4). Orange: V3 anchor.</p>'%(top.z-h)]
def project(cam,size,p):
    scene.render.resolution_x,scene.render.resolution_y=size
    q=world_to_camera_view(scene,cam,Vector(p));return q.x*size[0],(1-q.y)*size[1]
for name,(src,size) in images.items():
    cam=bpy.data.objects['R2_'+name];W=1400;sc=W/size[0]
    def pl(pts,style):return '<polyline points="%s" %s/>'%(' '.join('%.1f,%.1f'%(x*sc,y*sc) for x,y in [project(cam,size,p) for p in pts]),style)
    ov=[f'<div style="position:relative;width:{W}px;height:{size[1]*sc:.0f}px;margin-bottom:30px"><img src="{src}" style="position:absolute;width:{W}px"/>',f'<svg style="position:absolute;left:0;top:0" width="{W}" height="{size[1]*sc:.0f}">']
    ov.append(pl([(p[0],p[1],12) for p in polygon+[polygon[0]]],'fill="none" stroke="#39ff5a" stroke-width="2"'))
    ov.append(pl([(p.x,p.y,top.z-h) for p in board]+[(board[0].x,board[0].y,top.z-h)],'fill="none" stroke="#000" stroke-width="2"'))
    ov.append(pl([(p.x,p.y,top.z) for p in board]+[(board[0].x,board[0].y,top.z)],'fill="none" stroke="#fff" stroke-width="1.5"'))
    for p in pylons:ov.append(pl([(q.x,q.y,13.4) for q in p]+[(p[0].x,p[0].y,13.4)],'fill="none" stroke="#ff3b30" stroke-width="2"'))
    x,y=project(cam,size,(96.87,25.39,38));ov.append(f'<circle cx="{x*sc:.1f}" cy="{y*sc:.1f}" r="6" fill="none" stroke="#ff9f0a" stroke-width="2"/>')
    ov.append('</svg></div>');html.append(f'<h3>{name}</h3>'+''.join(ov))
html.append('</body></html>');(REVIEW/'rf-source-overlays.html').write_text('\n'.join(html))
scene.render.resolution_x,scene.render.resolution_y=1800,1198
print(json.dumps({k:evidence[k] for k in ['all_outside_playable','min_clearance_m','v3_anchor_inside_playable']}))
