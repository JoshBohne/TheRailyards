"""Lake Michigan, the lakefront landforms and the near-South-Loop context.

Replaces the V3 east background box (which paved over the lake).  Land is the
window east of the mapped district minus the USGS NHD Lake Michigan polygon;
water sits on a separate plane at the lake datum.  Grant Park, Museum Campus
and Northerly Island come from the shoreline itself; lawn areas and the four
museum-campus masses are inferred approximations and are labelled so.
"""
import json,math,random
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
import r4_geo

OUT=Path(__file__).resolve().parent
LAND_GROUP='Lakefront land'
WATER_GROUP='Lake Michigan'
CONTEXT_GROUP='Near South Loop context'
# Land window: from the east edge of the mapped district out past the harbor.
X0,X1,Y0,Y1=1000.0,20000.0,-20000.0,20000.0


def _triangulate(ring,holes=()):
    points=[];edges=[]
    for loop in [ring]+list(holes):
        start=len(points);points.extend(Vector(p) for p in loop)
        edges.extend((start+i,start+(i+1)%len(loop)) for i in range(len(loop)))
    verts,_e,faces,*_=delaunay_2d_cdt(points,edges,[],0,0.01)
    return verts,faces


def build_geography(scene,spec,batch,materials):
    rings,data=r4_geo.lake_rings()
    main=max(rings,key=len)
    clipped=r4_geo.dedupe(r4_geo.clip_polygon(main,X0,Y0,X1,Y1),1.0)
    if len(clipped)<3:raise RuntimeError('Lake polygon does not reach the land window')
    # Land = window minus lake.  Triangulate the window with the shoreline as
    # constraint edges, then keep faces whose centroid is outside the lake.
    window=[(X0,Y0),(X1,Y0),(X1,Y1),(X0,Y1)]
    points=[Vector(p) for p in window]+[Vector(p) for p in clipped]
    edges=[(i,(i+1)%4) for i in range(4)]+[(4+i,4+(i+1)%len(clipped)) for i in range(len(clipped))]
    verts,_e,faces,*_=delaunay_2d_cdt(points,edges,[],0,0.05)
    land=[];water=[]
    for face in faces:
        c=sum((verts[i] for i in face),Vector((0,0)))/len(face)
        (water if r4_geo.inside((c.x,c.y),clipped) else land).append(tuple(face))
    z=r4_geo.GROUND_Z
    batch.add(LAND_GROUP,'paving',[(v.x,v.y,z) for v in verts],land)
    batch.add(LAND_GROUP,'paving',[(v.x,v.y,-2.0) for v in verts],[tuple(reversed(f)) for f in land])
    # Shoreline wall down to the water so the edge reads as a seawall.
    for a,b in zip(clipped,clipped[1:]+clipped[:1]):
        if abs(a[0]-X0)<1e-6 and abs(b[0]-X0)<1e-6:continue
        batch.quad(LAND_GROUP,'stone',[(a[0],a[1],z),(b[0],b[1],z),(b[0],b[1],r4_geo.LAKE_Z-1.5),(a[0],a[1],r4_geo.LAKE_Z-1.5)])
        batch.quad(LAND_GROUP,'stone',[(a[0],a[1],r4_geo.LAKE_Z-1.5),(b[0],b[1],r4_geo.LAKE_Z-1.5),(b[0],b[1],z),(a[0],a[1],z)])
    lz=r4_geo.LAKE_Z
    batch.quad(WATER_GROUP,'water',[(X0,Y0,lz),(X1,Y0,lz),(X1,Y1,lz),(X0,Y1,lz)])
    # Lawn areas: Grant Park between Michigan Avenue and the shore, and the
    # Museum Campus.  Boundaries are approximate street-grid readings, not
    # parcel data; they exist so the lakefront is not one grey plane.
    lawns={'Grant Park (approx.)':[(985,330),(1560,330),(1640,720),(1660,1560),(985,1560)],
           'Museum Campus (approx.)':[(1560,-520),(2000,-520),(2060,330),(1560,330)]}
    for name,poly in lawns.items():
        batch.prism(LAND_GROUP+' lawn','lawn',poly,z-.02,z+.12)
    # Museum-campus masses (inferred sizes from published plans; recognizable
    # low silhouettes east of the stadium, kept separate from OSM records).
    masses=[('Field Museum (inferred mass)',41.8663,-87.6170,215,110,26,'stone'),
            ('Shedd Aquarium (inferred mass)',41.8676,-87.6140,95,95,22,'stone'),
            ('Soldier Field (inferred mass)',41.8623,-87.6167,205,125,42,'concrete'),
            ('Adler Planetarium (inferred mass)',41.8663,-87.6069,60,60,18,'stone')]
    for name,lat,lon,w,d,h,mat in masses:
        x,y=r4_geo.local_xy(lat,lon)
        batch.box(LAND_GROUP+' museum campus',mat,(x,y,z+h/2),(w,d,h))
        batch.box(LAND_GROUP+' museum campus','roof',(x,y,z+h+.2),(w*.9,d*.9,.4))
    # Near South Loop: OSM buildings between the mapped district and the lake
    # (heights from tags or levels).  Buildings modelled as dedicated skyline
    # silhouettes are skipped here so nothing is represented twice.
    records=json.loads((OUT/'near-south-loop-context.json').read_text())
    skip=set(records.get('skip_names',[]));rng=random.Random(4711)
    count=0
    for rec in records['buildings']:
        if rec.get('name') in skip or rec['osm_way'] in records.get('skip_ways',[]):continue
        foot=[r4_geo.register(p) for p in rec['footprint']]
        cx=sum(p[0] for p in foot)/len(foot)
        if cx<830:continue  # already covered by site-context / outfield-context
        h=float(rec['height_m']);z1=z+h
        mat='stone' if h>=60 else 'brick_light'
        batch.prism(CONTEXT_GROUP,mat,foot,z,z1)
        batch.prism(CONTEXT_GROUP,'roof',foot,z1,z1+.25)
        signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(foot,foot[1:]+foot[:1]))
        floors=max(1,round(h/3.6))
        for a,b in zip(foot,foot[1:]+foot[:1]):
            a,b=Vector((*a,0)),Vector((*b,0));length=(b-a).length
            if length<3:continue
            t=(b-a)/length;n=Vector((t.y,-t.x,0))*(1 if signed>0 else -1);angle=math.atan2(t.y,t.x)
            n_win=max(1,int(length/4.6))
            for f in range(floors):
                zz=z+(f+.55)*h/floors
                for k in range(n_win):
                    p=a.lerp(b,(k+.5)/n_win)+n*.12;p.z=zz
                    batch.box(CONTEXT_GROUP,'glass_lit' if rng.random()<.15 else 'glass',p,(length/n_win*.62,.10,h/floors*.58),angle)
        count+=1
    scene['lake_source']=data['source'];scene['lake_source_url']=data['source_url']
    scene['lake_registration']='formula + %.0f m X (r4_geo)'%r4_geo.REGISTRATION_X_M
    scene['lake_datum_z']=lz;scene['near_south_loop_context_count']=count
    scene['lakefront_note']='Shoreline from USGS NHD (City of Chicago ArcGIS layer 22 timed out on 2026-09-06; City Hydro portal export agrees within ~10 m). Lawns and museum masses are inferred.'
    return {'shoreline_points':len(clipped),'land_faces':len(land),'water_faces':len(water),'context_buildings':count}
