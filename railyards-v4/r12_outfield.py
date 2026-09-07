"""V12 outfield proportions: left-center bank and right-field corner.

Applied after the V11 circulation on the corrected V12 bowl.  The north
artwork shows the Roosevelt plaza flowing down into left-center bleachers
and the right-field corner as a solid brick block under the board with
seating wrapping the foul pole.  Row counts, rakes, cut lines and the
understructure are inferred; nothing here is an engineering design.
"""
import math,random
import bpy
from mathutils import Vector
from r2_geometry import instances
from r3_public_realm import inside
from r11_circulation import terrace_z,rail,slab
from r3_envelope import _arch_bay

TREAD=.78;RISE=.467;LC_ROWS=18   # left-center bank, about 31 deg: 8.4 m drop inside the 16.8 m minimum plaza-to-wall depth
C_TREAD=.85;C_RISE=.40      # right-field corner bank
LC_AISLE=2.4                # cross-aisle at plaza level
LC_EXTEND=10.0              # bank continues past the plaza edge toward the LF corner
LC_EAST=-8.0                # ... and east of the plaza corner, stopping short of the batter's eye
CLEAR=1.6                   # rows stay this far behind the outfield wall
CORNER_X_MAX=111.5;CORNER_Y_MAX=6.5;CORNER_END_CLEAR=1.8


def footprint(spec):
    return [tuple(p[:2]) for p in spec['bowl_front']]+[tuple(p[:2]) for p in reversed(spec['field_boundary'])]


def _dist(p,poly):
    best=1e9
    for a,b in zip(poly,poly[1:]+poly[:1]):
        a=Vector(a);b=Vector(b);d=b-a;u=max(0,min(1,(p-a).dot(d)/d.length_squared));best=min(best,(p-a-d*u).length)
    return best


def _clear_of_field(p,poly):
    return not inside((p.x,p.y),poly) and _dist(p,poly)>=CLEAR


class Rows:
    """Straight rows parallel to a datum line, clipped by an ``allowed`` test.

    ``origin``/``along`` define the datum; ``rear`` is the unit normal pointing
    away from the field.  Offsets are measured from the datum toward the
    field when ``inward`` is True (left-center: rows hang off the plaza edge)
    or away from it otherwise (corner: rows climb away from the field edge).
    """
    def __init__(self,batch,group,origin,along,rear,inward,allowed,base,facing):
        self.batch=batch;self.group=group;self.o=Vector(origin);self.a=Vector(along).normalized()
        self.rear=Vector(rear).normalized();self.sign=-1 if inward else 1;self.allowed=allowed;self.base=base
        self.angle=facing;self.seats=[];self.rot=[];self.fans=[[] for _ in range(6)];self.fanrot=[[] for _ in range(6)]
    def point(self,u,off):
        return self.o+self.a*u+self.rear*(self.sign*off)
    def row(self,u0,u1,off0,off1,level,aisles=(),seats=True,material='concrete',rng=None,step=.25,surface=None):
        """Build one row between offsets off0 (field side) and off1 (rear)."""
        mid=(off0+off1)/2;samples=[];u=u0
        while u<=u1+1e-6:
            samples.append(u);u+=step
        runs=[];start=None
        for u in samples+[None]:
            ok=u is not None and self.allowed(self.point(u,mid))
            if ok and start is None:start=u
            if not ok and start is not None:
                if u is None:u=samples[-1]
                if u-start>.6:runs.append((start,u))
                start=None
        for ra,rb in runs:
            cuts=sorted({ra,rb}|{c for a in aisles for c in (a-.775,a+.775) if ra<c<rb})
            for pa,pb in zip(cuts,cuts[1:]):
                is_aisle=any(pa>=a-.78 and pb<=a+.78 for a in aisles)
                poly=[self.point(pa,off0),self.point(pb,off0),self.point(pb,off1),self.point(pa,off1)]
                poly=[(p.x,p.y) for p in poly]
                slab(self.batch,self.group,material,poly,level,lambda y:self.base)
                if surface:slab(self.batch,self.group,surface,poly,lambda y:level(y)+.05,level)
                if seats and not is_aisle:
                    n=int((pb-pa)/.58)
                    for k in range(n):
                        p=self.point(pa+.29+k*.58,off0+(off1-off0)*.45);z=level(p.y)
                        self.seats.append((p.x,p.y,z));self.rot.append((0,0,self.angle))
                        if rng and rng.random()<.78:
                            c=rng.choices(range(6),[32,27,18,15,5,3])[0]
                            self.fans[c].append((p.x,p.y,z));self.fanrot[c].append((0,0,self.angle))
        return runs
    def instance(self,scene,collection,label):
        source=bpy.data.objects.get('D2_Seat source')
        if source and self.seats:instances(scene,collection,label+' seats',source,self.seats,self.rot)
        for k,color in enumerate(['cloth_black','cloth_white','cloth_gray','navy','cloth_blue','cloth_red']):
            person=bpy.data.objects.get('D2_Seated fan '+color)
            if person and self.fans[k]:instances(scene,collection,label+' spectators '+color,person,self.fans[k],self.fanrot[k])
        return len(self.seats),sum(map(len,self.fans))


def facing(tangent,toward_field):
    """Seat prototypes face the left of the row tangent (r3_outfield convention)."""
    t=Vector(tangent).normalized();left=Vector((-t.y,t.x))
    if left.dot(Vector(toward_field))<0:t=-t
    return math.atan2(t.y,t.x)


def edge_wall(batch,group,p0,p1,outward,level_at,base,material='brick',parapet=1.05):
    """Brick wall along a cut face; its top follows the seating rake plus a parapet."""
    p0=Vector(p0);p1=Vector(p1);length=(p1-p0).length
    if length<.3:return
    count=max(1,int(length/.5));t=(p1-p0).normalized();angle=math.atan2(t.y,t.x)
    for k in range(count):
        c=p0.lerp(p1,(k+.5)/count)+Vector(outward)*.22;z=level_at(c)+parapet
        batch.box(group,material,(c.x,c.y,(base+z)/2),(length/count+.02,.44,z-base),angle)


def batter_eye(spec):
    """Centre-field batter's eye segment as built by r3_outfield (26 m wide, 12 m behind the wall)."""
    boundary=[Vector(p[:2]) for p in spec['field_boundary']];i=len(boundary)//2;c=boundary[i]
    t=(boundary[i+1]-boundary[i-1]).normalized();r=c.normalized();e=c+r*12.0
    return e-t*13.0,e+t*13.0


def _seg_dist(p,a,b):
    d=b-a;u=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-d*u).length


# ---------------------------------------------------------------- left-center
def lc_frame(front_terrace):
    e0=Vector(front_terrace[0]);e1=Vector(front_terrace[1]);along=(e1-e0).normalized()
    n=Vector((along.y,-along.x))
    if n.dot(-e0)<0:n=-n          # toward home plate / the field
    return e0,e1,along,n,(e1-e0).length


def in_lc_bank(p,front_terrace):
    e0,e1,along,n,length=lc_frame(front_terrace);d=Vector(p)-e0
    u=d.dot(along);off=d.dot(n)
    return LC_EAST-.5<=u<=length+LC_EXTEND and -.4<=off<=LC_AISLE+(LC_ROWS+1)*TREAD


def build_lc_bank(scene,batch,spec,front_terrace,roof,rng):
    group='V12 Left-center bank';poly=footprint(spec)
    e0,e1,along,n,length=lc_frame(front_terrace)
    eye_a,eye_b=batter_eye(spec);roof=[tuple(q) for q in roof]
    allowed=lambda p:_clear_of_field(p,poly) and not inside((p.x,p.y),roof) and _seg_dist(p,eye_a,eye_b)>=1.3
    rows=Rows(batch,group,e0,along,-n,True,allowed,7.9,facing(along,n))
    u0,u1=LC_EAST,length+LC_EXTEND
    aisles=[-3.0]+[6.0+14.0*k for k in range(int((u1-6)/14)+1)]
    # Plaza-level cross-aisle: the terrace surface simply continues onto the
    # top of the bank, so there is no rail or step between plaza and seats.
    # Rows are level (seat IDs group by row height); the cross-aisle twists
    # gently from the graded plaza edge to the flat top row (<0.2 m over 2.4 m).
    top_level=terrace_z((e0.y+e1.y)/2)
    c=[rows.point(u0,0.0),rows.point(u1,0.0),rows.point(u1,LC_AISLE),rows.point(u0,LC_AISLE)]
    verts=[(c[0].x,c[0].y,terrace_z(c[0].y)),(c[1].x,c[1].y,terrace_z(c[1].y)),(c[2].x,c[2].y,top_level),(c[3].x,c[3].y,top_level)]
    verts+=[(v[0],v[1],7.9) for v in verts]
    batch.add(group,'paving',verts,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    for k in range(LC_ROWS):
        front=LC_AISLE+(k+1)*TREAD;back=LC_AISLE+k*TREAD;level=top_level-(k+1)*RISE
        rows.row(u0,u1,front,back,lambda y,level=level:level,aisles,True,'concrete',rng)
    # Past the plaza the bank is backed by a brick wall with a coping instead of open air.
    if u1>length:
        wall=[rows.point(length,-0.05),rows.point(u1,-0.05),rows.point(u1,-0.5),rows.point(length,-0.5)]
        slab(batch,group,'brick',[(p.x,p.y) for p in wall],lambda y:terrace_z(y)+1.05,lambda y:7.9)
        cap=[rows.point(length-.05,0.05),rows.point(u1+.05,0.05),rows.point(u1+.05,-0.6),rows.point(length-.05,-0.6)]
        slab(batch,group,'stone',[(p.x,p.y) for p in cap],lambda y:terrace_z(y)+1.2,lambda y:terrace_z(y)+1.05)
        # End wall on the far side following the rake.
        end=[rows.point(u1,-0.5),rows.point(u1+.4,-0.5),rows.point(u1+.4,LC_AISLE+LC_ROWS*TREAD),rows.point(u1,LC_AISLE+LC_ROWS*TREAD)]
        def rake(y,pts=end):
            # offset from the plaza edge at this y along the end line
            p=Vector(pts[0]);q=Vector(pts[3]);t=0 if abs(q.y-p.y)<1e-6 else max(0,min(1,(y-p.y)/(q.y-p.y)))
            off=LC_AISLE+LC_ROWS*TREAD*t
            return top_level-max(0,(off-LC_AISLE)/TREAD)*RISE+1.0
        slab(batch,group,'brick',[(p.x,p.y) for p in end],rake,lambda y:7.9)
    # East end: a brick end wall following the rake, and a paved landing that
    # joins the top cross-aisle to the plaza corner and the restaurant roof edge
    # (V11 bridged this void with a narrow elevated path).
    def lc_level(p):
        off=(Vector(p)-e0).dot(n);return top_level-max(0,min(LC_ROWS,(off-LC_AISLE)/TREAD))*RISE
    edge_wall(batch,group,rows.point(u0,LC_AISLE+LC_ROWS*TREAD+.3),rows.point(u0,-0.3),(-along.x,-along.y),lc_level,7.9)
    corner=min(roof,key=lambda q:(Vector(q)-rows.point(u0,0)).length)
    landing=[tuple(rows.point(u0,0)),tuple(rows.point(-.5,0)),tuple(e0),corner]
    slab(batch,group,'paving',landing,lambda y:terrace_z(y),lambda y:7.9)
    rail(batch,group,(landing[0][0],landing[0][1],terrace_z(landing[0][1])),(corner[0],corner[1],terrace_z(corner[1])))
    seats,fans=rows.instance(scene,batch.collection(group),'Left-center bank individual')
    return {'seats':seats,'spectators':fans,'rows':LC_ROWS,'tread':TREAD,'rise':RISE,'plaza_edge':[tuple(e0),tuple(e1)]}


# ------------------------------------------------------------ right-field corner
def corner_frame(spec):
    a=Vector(spec['bowl_front'][0][:2]);b=Vector(spec['field_boundary'][0][:2]);d=(b-a).normalized()
    m=Vector((d.y,-d.x))
    if m.dot(Vector((50,50))-a)>0:m=-m      # away from the field
    back=Vector(spec['bowl_back'][0][:2]);line=(back-a).normalized();east=Vector((-line.y,line.x))
    if east.x<0:east=-east
    return a,b,d,m,east


def in_corner_bank(p,spec):
    a,b,d,m,east=corner_frame(spec);q=Vector(p)-a
    return east.dot(q)>=CORNER_END_CLEAR-.3 and -.2<=m.dot(q)<=15.2 and p[1]<=CORNER_Y_MAX+.5 and p[0]<=CORNER_X_MAX+.5


def build_rf_corner(scene,batch,spec,materials,rng):
    group='V12 Right-field corner';poly=footprint(spec)
    a,b,d,m,east=corner_frame(spec)
    def allowed(p):
        q=p-a
        return (_clear_of_field(p,poly) and east.dot(q)>=CORNER_END_CLEAR and p.y<=CORNER_Y_MAX and p.x<=CORNER_X_MAX)
    base=3.4   # buried in the z8 ground; exposed only above the lower riverwalk cut
    rows=Rows(batch,group,a,d,m,False,allowed,base,facing(d,-m))
    u0,u1=-30.0,60.0;aisles=[4.0,22.0]
    for k in range(12):
        rows.row(u0,u1,C_TREAD*k+CLEAR,C_TREAD*(k+1)+CLEAR,lambda y,k=k:13.65+k*C_RISE,aisles,True,'concrete',rng)
    rear0=CLEAR+12*C_TREAD;rear1=rear0+2.4;top=13.65+12*C_RISE
    rows.row(u0,u1,rear0,rear1,lambda y:top,seats=False,material='brick',surface='paving')
    # Brick parapet along the rear aisle and the two cut sides, following the rake.
    rows.row(u0,u1,rear1,rear1+.45,lambda y:top+1.1,seats=False,material='brick',surface='stone')
    def level_at(p):
        off=m.dot(Vector(p)-a);return min(top,13.65+max(0,(off-CLEAR)/C_TREAD)*C_RISE)
    # east cut (x = CORNER_X_MAX): from the front row to the rear parapet
    def u_at_x(x,off):return (x-(a.x+m.x*off))/d.x
    p_front=rows.point(u_at_x(CORNER_X_MAX,CLEAR),CLEAR);p_rear=rows.point(u_at_x(CORNER_X_MAX,rear1+.45),rear1+.45)
    y_cut=CORNER_Y_MAX
    if p_front.y>y_cut:
        # the y cut meets the east cut: wall along y = y_cut from the front row to x = CORNER_X_MAX, then down the east face
        def u_at_y(y,off):return (y-(a.y+m.y*off))/d.y
        q_front=rows.point(u_at_y(y_cut,CLEAR),CLEAR);q_corner=Vector((CORNER_X_MAX,y_cut))
        edge_wall(batch,group,q_front,q_corner,(0,1),level_at,base)
        edge_wall(batch,group,q_corner,p_rear,(1,0),level_at,base)
    else:
        edge_wall(batch,group,p_front,p_rear,(1,0),level_at,base)
    # Arches on the exposed faces: rear (south-east, toward the tower forecourt,
    # ground z8) and east (over the lower riverwalk, z4.95).
    def arcade(p0,p1,tangent,bottom,height,wall_top):
        p0=Vector(p0);p1=Vector(p1);length=(p1-p0).length;count=max(1,round(length/6.6))
        for k in range(count):
            c=p0.lerp(p1,(k+.5)/count);_arch_bay(batch,group,Vector((c.x,c.y,0)),Vector((tangent.x,tangent.y,0)),min(4.4,length/count*.68),bottom,height,wall_top,.45,materials)
    # rear face: runs along d at offset rear1+.45; visible between the end-wall cut and x limit
    off=rear1+.45+.02
    ua=(CORNER_END_CLEAR-east.dot(m)*off)/east.dot(d) if abs(east.dot(d))>1e-6 else u0
    ub=(CORNER_X_MAX-(a.x+m.x*off))/d.x
    if ub-ua>4:
        # _arch_bay opens toward the left normal of its tangent; -d puts it on the +m side.
        arcade(rows.point(ua,off),rows.point(ub,off),-d,8.3,4.6,top)
    # east face at x = CORNER_X_MAX between the rear corner and y = CORNER_Y_MAX / front row
    yb=rows.point(ub,off).y;yt=min(CORNER_Y_MAX,rows.point((CORNER_X_MAX-(a.x+m.x*CLEAR))/d.x,CLEAR).y)
    if yt-yb>4:
        arcade((CORNER_X_MAX+.47,yb),(CORNER_X_MAX+.47,yt),Vector((0,-1)),5.3,6.4,13.4)
    seats,fans=rows.instance(scene,batch.collection(group),'Right-field corner individual')
    return {'seats':seats,'spectators':fans,'rows':12,'tread':C_TREAD,'rise':C_RISE,'top_aisle_z':top}
