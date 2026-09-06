"""Finite mapped outfield corridor; heights and facade inference stay explicit."""
import json, math, random
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt


def _inside(p, ring):
    x,y=p;inside=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside


def build_outfield_context(scene,spec,batch,materials):
    records=json.loads((Path(__file__).parent/'outfield-context.json').read_text())['buildings']
    rng=random.Random(4702)
    for record in records:
        foot=record['footprint'];holes=record.get('footprint_holes',[])
        z0=record.get('base_z',8);z1=z0+record['height_m']
        group='Outfield city '+record['name']
        material='stone' if record['name']=='River City' else 'brick_light' if record['height_m']<40 else 'stone'
        if holes:
            points=[];edges=[]
            for ring in [foot]+holes:
                start=len(points);points.extend(Vector(p) for p in ring)
                edges.extend((start+i,start+(i+1)%len(ring)) for i in range(len(ring)))
            verts,_,faces,*_=delaunay_2d_cdt(points,edges,[],0,0.0001)
            roof_faces=[]
            for face in faces:
                center=sum((verts[i] for i in face),Vector((0,0)))/len(face)
                if _inside(center,foot) and not any(_inside(center,hole) for hole in holes):roof_faces.append(tuple(face))
            batch.add(group,'roof',[(p.x,p.y,z1) for p in verts],roof_faces)
            for ring in [foot]+holes:
                for a,b in zip(ring,ring[1:]+ring[:1]):batch.quad(group,material,[(*a,z0),(*b,z0),(*b,z1),(*a,z1)])
        else:batch.prism(group,material,foot,z0,z1)
        # Repeated windows describe facade scale, not surveyed facade designs.
        for ring in [foot]+holes:
            signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))
            for a,b in zip(ring,ring[1:]+ring[:1]):
                a,b=Vector((*a,0)),Vector((*b,0));delta=b-a;length=delta.length
                if length<1:continue
                tangent=delta/length;normal=Vector((tangent.y,-tangent.x,0))*(1 if signed>0 else -1)
                if ring is not foot:normal=-normal
                angle=math.atan2(delta.y,delta.x);count=max(1,int(length/4.8));floors=max(1,round((z1-z0)/3.8))
                for floor in range(floors):
                    for k in range(count):
                        p=a.lerp(b,(k+.5)/count)+normal*.12;p.z=z0+(floor+.57)*(z1-z0)/floors
                        batch.box(group,'glass_lit' if rng.random()<.14 else 'glass',p,(length/count*.65,.12,(z1-z0)/floors*.61),angle)
    scene['outfield_context_count']=len(records)
    scene['outfield_context_note']='Mapped OSM footprints; per-building sourced or level-derived heights in outfield-context.json. Repeated facades inferred. River City courtyard remains open.'
