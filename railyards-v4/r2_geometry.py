"""Small deterministic mesh builders shared by the stadium and district modules."""
import math
from collections import defaultdict
import bpy
from mathutils import Vector

class MeshBatch:
    def __init__(self,scene,materials,prefix='D2_'):
        self.scene=scene;self.materials=materials;self.prefix=prefix
        self.vertices=defaultdict(list);self.faces=defaultdict(list);self.uvs=defaultdict(list)
        self.collections={}
    def add(self,group,mat,vertices,faces,uvs=None):
        key=(group,mat);start=len(self.vertices[key]);self.vertices[key].extend(vertices)
        self.faces[key].extend([tuple(start+i for i in face)for face in faces])
        if uvs is None:
            uvs=[]
            for face in faces:
                pts=[Vector(vertices[i])for i in face]
                u=(pts[1]-pts[0]).normalized() if len(pts)>1 else Vector((1,0,0))
                normal=(pts[1]-pts[0]).cross(pts[-1]-pts[0]).normalized() if len(pts)>2 else Vector((0,0,1))
                v=normal.cross(u)
                uvs.extend([((p-pts[0]).dot(u),(p-pts[0]).dot(v))for p in pts])
        self.uvs[key].extend(uvs)
    def quad(self,group,mat,points,uv=None):self.add(group,mat,points,[(0,1,2,3)],uv)
    def box(self,group,mat,center,size,angle=0):
        x,y,z=center;w,d,h=(v/2 for v in size);co,si=math.cos(angle),math.sin(angle)
        vs=[(x+a*w*co-b*d*si,y+a*w*si+b*d*co,z+c*h)for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.add(group,mat,vs,[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
    def prism(self,group,mat,footprint,z0,z1):
        n=len(footprint);vs=[(x,y,z)for z in [z0,z1]for x,y in footprint]
        self.add(group,mat,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)])
    def cylinder(self,group,mat,a,b,r0,r1=None,sides=10):
        a,b=Vector(a),Vector(b);d=b-a
        if d.length<1e-5:return
        d.normalize();helper=Vector((0,0,1)) if abs(d.z)<.92 else Vector((1,0,0));u=d.cross(helper).normalized();v=d.cross(u);r1=r0 if r1 is None else r1
        vs=[]
        for pos,r in [(a,r0),(b,r1)]:
            vs.extend([tuple(pos+r*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*v))for i in range(sides)])
        fs=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides)for i in range(sides)]
        self.add(group,mat,vs,fs)
    def line(self,group,mat,points,r,sides=6):
        for a,b in zip(points,points[1:]):self.cylinder(group,mat,a,b,r,sides=sides)
    def ellipsoid(self,group,mat,center,radii,segments=10,rings=6):
        x,y,z=center;rx,ry,rz=radii;vs=[]
        for j in range(rings+1):
            phi=math.pi*j/rings
            for i in range(segments):
                theta=math.tau*i/segments;vs.append((x+rx*math.sin(phi)*math.cos(theta),y+ry*math.sin(phi)*math.sin(theta),z+rz*math.cos(phi)))
        fs=[]
        for j in range(rings):
            for i in range(segments):fs.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
        self.add(group,mat,vs,fs)
    def collection(self,name):
        if name not in self.collections:
            col=bpy.data.collections.new(self.prefix+name);self.scene.collection.children.link(col);self.collections[name]=col
        return self.collections[name]
    def flush(self):
        objects=[]
        for (group,mat),verts in self.vertices.items():
            data=bpy.data.meshes.new(self.prefix+group+' '+mat);data.from_pydata(verts,[],self.faces[(group,mat)]);data.materials.append(self.materials[mat]);data.update()
            layer=data.uv_layers.new(name='Physical meters')
            for loop,uv in zip(layer.data,self.uvs[(group,mat)]):loop.uv=uv
            obj=bpy.data.objects.new(self.prefix+group+' '+mat,data);self.collection(group).objects.link(obj);objects.append(obj)
            if mat in ['bark','foliage','leaf_light','leaf_dark','skin','water']:
                for polygon in data.polygons:polygon.use_smooth=True
        self.vertices.clear();self.faces.clear();self.uvs.clear()
        return objects

def resample(path,spacing):
    points=[Vector(p)for p in path];distances=[0]
    for a,b in zip(points,points[1:]):distances.append(distances[-1]+(b-a).length)
    count=max(1,round(distances[-1]/spacing));result=[];j=0
    for i in range(count+1):
        s=distances[-1]*i/count
        while j<len(points)-2 and distances[j+1]<s:j+=1
        t=(s-distances[j])/max(1e-8,distances[j+1]-distances[j]);result.append(points[j].lerp(points[j+1],t))
    return result

def text(scene,group,name,body,position,size,material,rotation=(math.pi/2,0,0),align='CENTER'):
    data=bpy.data.curves.new('D2_'+name,'FONT');data.body=body;data.size=size;data.align_x=align;data.extrude=.014;data.bevel_depth=.007;data.materials.append(material)
    obj=bpy.data.objects.new('D2_'+name,data);group.objects.link(obj);obj.location=position;obj.rotation_euler=rotation;return obj

def instances(scene,collection,name,prototype,positions,rotations=None,scales=None):
    data=bpy.data.meshes.new('D2_'+name);data.from_pydata(positions,[],[]);data.update()
    rotations=rotations or [(0,0,0)]*len(positions);scales=scales or [(1,1,1)]*len(positions)
    for attr,values in [('rotation',rotations),('scale',scales)]:
        layer=data.attributes.new(attr,'FLOAT_VECTOR','POINT')
        layer.data.foreach_set('vector',[c for value in values for c in value])
    obj=bpy.data.objects.new('D2_'+name,data);collection.objects.link(obj)
    nodes=bpy.data.node_groups.new('D2_'+name+' instances','GeometryNodeTree')
    nodes.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');nodes.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    source=nodes.nodes.new('NodeGroupInput');out=nodes.nodes.new('NodeGroupOutput');info=nodes.nodes.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=prototype
    inst=nodes.nodes.new('GeometryNodeInstanceOnPoints');nodes.links.new(source.outputs['Geometry'],inst.inputs['Points']);nodes.links.new(info.outputs['Geometry'],inst.inputs['Instance']);nodes.links.new(inst.outputs['Instances'],out.inputs['Geometry'])
    for attr,socket in [('rotation','Rotation'),('scale','Scale')]:
        node=nodes.nodes.new('GeometryNodeInputNamedAttribute');node.data_type='FLOAT_VECTOR';node.inputs['Name'].default_value=attr;nodes.links.new(node.outputs['Attribute'],inst.inputs[socket])
    modifier=obj.modifiers.new('Linked instances','NODES');modifier.node_group=nodes
    obj['instance_count']=len(positions);return obj
