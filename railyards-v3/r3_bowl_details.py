"""Resolvable bowl circulation, team benches, protection and tower flags."""
import json,math
from pathlib import Path
from mathutils import Vector
from r2_geometry import resample


def build_bowl_details(scene,spec,batch,materials):
    front=[Vector(p)for p in spec['bowl_front']];back=[Vector(p)for p in spec['bowl_back']]
    tiers=[(0,.34,14,24),(.40,.49,27,30),(.55,.65,33,36),(.70,.93,39,47)]
    for k,(ta,tb,za,zb) in enumerate(tiers):
        # Portal rhythm follows the same normalized section divisions as seats.
        for section in range(1,27):
            index=round(section/27*(len(front)-1));a,b=front[index],back[index]
            before=front[max(0,index-1)].lerp(back[max(0,index-1)],tb)
            after=front[min(len(front)-1,index+1)].lerp(back[min(len(front)-1,index+1)],tb)
            tangent=(after-before).normalized();angle=math.atan2(tangent.y,tangent.x)
            if k<3:
                p=a.lerp(b,tb+.025);p.z=zb+1.2
                batch.box('Concourse entries','interior',p,(2.8,.20,2.35),angle)
                batch.box('Concourse entries','stone',(p.x,p.y,zb+2.5),(3.1,.35,.20),angle)
            p=a.lerp(b,ta);q=a.lerp(b,tb);p.z=za+.85;q.z=zb+.85
            for offset in [-.52,.52]:
                u=p+tangent*offset;v=q+tangent*offset
                batch.line('Aisle handrails','metal',[u,v],.026,sides=5)
                for f in [.1,.5,.9]:
                    c=u.lerp(v,f);batch.cylinder('Aisle handrails','metal',(c.x,c.y,c.z-.84),c,.024,sides=5)
    # Team benches sit against the first/third-base seating fronts. Exact
    # hidden rooms are not inferred; only visible roofs, posts and benches.
    for x,y,angle,length in [(38,-11.4,0,20),(-4.5,41,math.pi/2,17)]:
        z=12.05;t=Vector((math.cos(angle),math.sin(angle),0));normal=Vector((-t.y,t.x,0))
        c=Vector((x,y,z))
        batch.box('Team dugouts','interior',(x,y,z+.7),(length,2.6,1.4),angle)
        batch.box('Team dugouts','roof',(x,y,z+2.2),(length+1.2,3.2,.23),angle)
        for off in [-length*.46,0,length*.46]:
            p=c+t*off+normal*1.2
            batch.cylinder('Team dugouts','metal',p,p+Vector((0,0,2.1)),.08,sides=6)
        p=c-normal*.8
        batch.box('Team dugouts','seat',(p.x,p.y,z+.43),(length-.8,.42,.13),angle)
        for f in range(12):
            p=c+t*((f-5.5)*length/12)-normal*.8
            batch.box('Team dugouts','seat',(p.x,p.y,z+.77),(.43,.07,.45),angle)
    # Thin native net lines remain subtle in aerial views and visible inside.
    protection=[front[i]for i in range(25,116,15)]
    for p in protection:batch.cylinder('Backstop protection','metal',(p.x,p.y,13.5),(p.x,p.y,22),.05,sides=6)
    for z in [14,16,18,20,22]:batch.line('Backstop protection','metal',[(p.x,p.y,z)for p in protection],.009,sides=4)
    for a,b in zip(protection,protection[1:]):
        for f in range(max(1,int((b-a).length))):
            p=a.lerp(b,f/max(1,int((b-a).length)))
            batch.line('Backstop protection','metal',[(p.x,p.y,13.5),(p.x,p.y,22)],.006,sides=4)
    # Chicago civic flag and black team pennant beside the source clock lantern.
    tx,ty,tz=spec['anchors']['tower_roof'];x,y=tx+9.2,ty+2.0
    batch.cylinder('Clock tower flags','stone',(x,y,tz-12),(x,y,tz+4),.08,sides=8)
    batch.ellipsoid('Clock tower flags','yellow',(x,y,tz+4.1),(.18,.18,.18),10,6)
    def flag_point(u,v,top):return (x+u,y+.30*math.sin(u*2.1+v),top-v-.15*u)
    for name,top,width,height in [('city',tz+3,4.4,2.6),('team',tz-1.2,3.8,2.4)]:
        for col in range(22):
            for row in range(13):
                u0,u1=width*col/22,width*(col+1)/22;v0,v1=height*row/13,height*(row+1)/13
                material='white'if name=='city'else'screen'
                if name=='city'and(row in [3,4,9,10]):material='cloth_blue'
                batch.quad('Clock tower flags',material,[flag_point(u0,v0,top),flag_point(u1,v0,top),flag_point(u1,v1,top),flag_point(u0,v1,top)])
        if name=='city':
            for i in range(4):
                u=width*(.22+i*.2);v=height*.52;verts=[]
                for j in range(12):
                    r=.25 if j%2==0 else .105;a=math.pi/2+j*math.pi/6
                    q=list(flag_point(u+math.cos(a)*r,v+math.sin(a)*r,top));q[1]-=.025;verts.append(q)
                batch.add('Clock tower flags','cloth_red',verts,[tuple(range(12))])
        else:
            contours=json.loads((Path(__file__).parent/'assets/sox-contours.json').read_text())['contours']
            for points in contours:
                verts=[]
                for a,b in points:
                    q=list(flag_point(width*.5+a*1.65,height*.5-b*1.65,top));q[1]-=.025;verts.append(q)
                batch.add('Clock tower flags','white',verts,[tuple(range(len(verts)))])
