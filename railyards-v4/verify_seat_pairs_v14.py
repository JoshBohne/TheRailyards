"""Diagnose transformed chair-mesh intersections missed by architectural rays.

BVH pairs include surface contact as well as penetration; inspect representative
triangles/renders before classifying a contact. Nonzero counts block a broad
collision-free seating claim. This script never changes placements.
"""
import bpy,json,math,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
s=bpy.data.scenes['Railyards v4'];bpy.context.window.scene=s
points=[]
for o in s.objects:
 if o.type!='MESH' or o.data.polygons or 'seat' not in o.name.lower() or 'source' in o.name.lower() or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 scale=o.data.attributes.get('scale');rot=o.data.attributes.get('rotation')
 for i,v in enumerate(o.data.vertices):
  if scale and scale.data[i].vector.length<.1:continue
  points.append((o.matrix_world@v.co,o.name,i,rot.data[i].vector.z if rot else 0))
k=KDTree(len(points))
for i,p in enumerate(points):k.insert(p[0],i)
k.balance();pairs=[]
# Conservative oriented rectangular chair footprint uses the submitted foot extents.
def overlap(a,b):
 pa,_,_,aa=a;pb,_,_,ab=b
 axes=[Vector((math.cos(t),math.sin(t))) for t in [aa,aa+math.pi/2,ab,ab+math.pi/2]]
 corners=[]
 for p,_,_,t in [a,b]:corners.append([Vector((p.x+dx*math.cos(t)-dy*math.sin(t),p.y+dx*math.sin(t)+dy*math.cos(t))) for dx,dy in [(-.2475,-.15),(.2475,-.15),(.2475,.15),(-.2475,.15)]])
 for axis in axes:
  x=[q.dot(axis) for q in corners[0]];y=[q.dot(axis) for q in corners[1]]
  if max(x)<=min(y)+.001 or max(y)<=min(x)+.001:return False
 return True
for i,a in enumerate(points):
 for co,j,d in k.find_range(a[0],.6):
  if j<=i:continue
  b=points[j]
  if abs(a[0].z-b[0].z)<.15 and overlap(a,b):pairs.append({'a':[a[1],a[2],list(a[0])],'b':[b[1],b[2],list(b[0])],'distance':d})

from mathutils import Matrix
from mathutils.bvhtree import BVHTree
source=bpy.data.objects['D2_Seat source'];verts=[v.co.copy()for v in source.data.vertices];faces=[tuple(p.vertices)for p in source.data.polygons]
cache={}
def mesh(i):
 if i not in cache:
  p,name,n,a=points[i];obj=bpy.data.objects[name];scale=obj.data.attributes['scale'].data[n].vector
  matrix=obj.matrix_world@Matrix.Translation(obj.data.vertices[n].co)@Matrix.Rotation(a,4,'Z')@Matrix.Diagonal((*scale,1))
  cache[i]=BVHTree.FromPolygons([matrix@v for v in verts],faces)
 return cache[i]
# Twice the largest transformed local radius conservatively covers possible
# mesh intersections across differently rotated or scaled chair instances.
max_scale=max(bpy.data.objects[p[1]].data.attributes['scale'].data[p[2]].vector.length for p in points)
pair_radius=2*max(v.length for v in verts)*max_scale
confirmed=[]
for i,a in enumerate(points):
 for co,j,d in k.find_range(a[0],pair_radius):
  if j<=i:continue
  intersections=mesh(i).overlap(mesh(j))
  if intersections:confirmed.append({'a':[a[1],a[2],list(a[0])],'b':[points[j][1],points[j][2],list(points[j][0])],'distance':d,'intersecting_face_pairs':len(intersections)})
representatives=[]
for label,name,ids in [('rf','D2_RF return individual seats',[408,486]),('main','D2_Individual seats',[151,152])]:
 ii=[next(i for i,p in enumerate(points)if p[1]==name and p[2]==n)for n in ids];o=bpy.data.objects[name];records=[]
 for i in ii:
  p,_,n,angle=points[i];scale=o.data.attributes['scale'].data[n].vector
  matrix=o.matrix_world@Matrix.Translation(o.data.vertices[n].co)@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((*scale,1))
  records.append({'index':n,'matrix':[list(row)for row in matrix],'rotation':list(o.data.attributes['rotation'].data[n].vector),'scale':list(scale),'vertices':[list(matrix@v)for v in verts]})
 rep_pairs=mesh(ii[0]).overlap(mesh(ii[1]));representatives.append({'label':label,'object':name,'instances':records,'intersecting_source_polygon_pairs':rep_pairs,'source_polygons':faces})
Path('work/audit-fixes-v14/independent-phase3/representative-chair-triangles.json').write_text(json.dumps(representatives,indent=2))
result={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'pair_search_radius':pair_radius,'active_visible_seats' :len(points),'close_overlapping_footprints':len(pairs),'pairs':pairs,'actual_mesh_intersections':confirmed,'source_bounds':[(min(p[i]for p in verts),max(p[i]for p in verts))for i in range(3)]}
(Path(__file__).resolve().parent/'review/v14/seat-pair-diagnostics.json').write_text(json.dumps(result,indent=2));print('RESULT',len(points),len(pairs),'ACTUAL',len(confirmed));print(collections.Counter((p['a'][0],p['b'][0])for p in confirmed))
