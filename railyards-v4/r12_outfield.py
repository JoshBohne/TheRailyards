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
    # The east face is covered by the river gallery (build_river_deck).
    seats,fans=rows.instance(scene,batch.collection(group),'Right-field corner individual')
    return {'seats':seats,'spectators':fans,'rows':12,'tread':C_TREAD,'rise':C_RISE,'top_aisle_z':top}


# ------------------------------------------------------------ right-field river gallery
DECK_X0=111.9;DECK_X1=117.6;DECK_Y0=-62.0;DECK_Y1=57.0
L1_Z=11.3;L2_Z=16.5;CANOPY_Z=20.7;QUAY_Z=4.95


def build_river_deck(scene,batch,spec,materials,rng):
    """Two-level open gallery on slender posts along the river between the
    clock tower and the board (north aerial: stacked lit terraces with people,
    festoons below).  The gallery stays a strip over the riverwalk: the bridge
    source shows the board sitting on the arcade building with patrons on its
    arch levels, not on a raised walkway beside it, so the upper deck no longer
    widens to the outfield wall.  Dimensions and levels are inferred."""
    group='V12 River gallery';post='bark' if 'bark' in batch.materials else 'metal'
    def slab_box(x0,x1,y0,y1,z,thick,mat):
        batch.box(group,mat,((x0+x1)/2,(y0+y1)/2,z-thick/2),(x1-x0,y1-y0,thick))
    # Strip over the riverwalk: both levels, full length.
    slab_box(DECK_X0,DECK_X1,DECK_Y0,DECK_Y1,L1_Z,.32,'concrete');slab_box(DECK_X0+.1,DECK_X1-.1,DECK_Y0,DECK_Y1,L1_Z+.05,.05,'paving')
    slab_box(DECK_X0,DECK_X1,DECK_Y0,DECK_Y1,L2_Z,.32,'concrete');slab_box(DECK_X0+.1,DECK_X1-.1,DECK_Y0,DECK_Y1,L2_Z+.05,.05,'paving')
    slab_box(DECK_X0-.3,DECK_X1+.6,DECK_Y0,DECK_Y1,CANOPY_Z,.22,'roof')
    # Posts: two river-side rows from the quay through both decks to the canopy.
    y=DECK_Y0+1.5
    while y<DECK_Y1-1:
        for x in (DECK_X0+.6,DECK_X1-.6):
            batch.cylinder(group,post,(x,y,QUAY_Z),(x,y,CANOPY_Z),.19,sides=8)
        y+=6.0
    # Beams under each slab, river side.
    for z in (L1_Z-.32,L2_Z-.32,CANOPY_Z-.22):
        for x in (DECK_X0+.6,DECK_X1-.6):
            batch.box(group,post,(x,(DECK_Y0+DECK_Y1)/2,z-.18),(.3,DECK_Y1-DECK_Y0,.36))
    # Rails on the river side of both decks and on the field side of the upper deck.
    rail(batch,group,(DECK_X1-.15,DECK_Y0,L1_Z),(DECK_X1-.15,DECK_Y1,L1_Z))
    rail(batch,group,(DECK_X1-.15,DECK_Y0,L2_Z),(DECK_X1-.15,DECK_Y1,L2_Z))
    rail(batch,group,(DECK_X0+.15,DECK_Y0,L2_Z),(DECK_X0+.15,DECK_Y1,L2_Z))
    for y0,y1 in ((DECK_Y0,DECK_Y0),(DECK_Y1,DECK_Y1)):
        rail(batch,group,(DECK_X0,y0,L1_Z),(DECK_X1,y1,L1_Z));rail(batch,group,(DECK_X0,y0,L2_Z),(DECK_X1,y1,L2_Z))
    # Stairs: quay -> L1 at both ends, L1 -> L2 mid-run.
    from r11_circulation import stairs as _stairs
    _stairs(batch,group,(DECK_X0+2.8,DECK_Y0+14,L1_Z),(DECK_X0+2.8,DECK_Y0+1.5,QUAY_Z),2.4,1)
    _stairs(batch,group,(DECK_X0+2.8,DECK_Y1-14,L1_Z),(DECK_X0+2.8,DECK_Y1-1.5,QUAY_Z),2.4,1)
    _stairs(batch,group,(DECK_X0+2.8,-8,L2_Z),(DECK_X0+2.8,3,L1_Z),2.4,1)
    # Festoons under the lower deck and along the upper rail.
    for z,x in ((L1_Z-.6,DECK_X1-1.2),(L2_Z+2.4,DECK_X1-.4)):
        y=DECK_Y0+2
        while y<DECK_Y1-2:
            chain=[(x,y+k*1.5,z-.25*math.sin(math.pi*k/4)) for k in range(5)]
            batch.line(group,'metal',chain,.012,sides=4)
            for k in (1,3):batch.ellipsoid(group,'lamp',chain[k],(.07,.07,.09),6,4)
            y+=6
    # People on both decks.
    walkers=[w for w in [bpy.data.objects.get(n) for n in ['D2_Walking visitor','D2_Walking visitor cloth_white','D2_Walking visitor cloth_black','D2_Walking visitor cloth_blue','D2_Walking visitor cloth_red']] if w]
    if walkers:
        buckets=[[] for _ in walkers];rots=[[] for _ in walkers]
        for i in range(350):
            x,y,z=rng.uniform(DECK_X0+.8,DECK_X1-.8),rng.uniform(DECK_Y0+1,DECK_Y1-1),(L1_Z if i%2==0 else L2_Z)+.05
            k=rng.choices(range(len(walkers)),[30,28,22,12,8][:len(walkers)])[0];buckets[k].append((x,y,z));rots[k].append((0,0,rng.random()*math.tau))
        for k,w in enumerate(walkers):
            if buckets[k]:instances(scene,batch.collection(group),'River gallery visitors '+str(k),w,buckets[k],rots[k])
    return {'levels':[L1_Z,L2_Z],'canopy':CANOPY_Z,'x':[DECK_X0,DECK_X1],'y':[DECK_Y0,DECK_Y1]}


# --------------------------------------------------------------- tower end
EXT_TIERS=[(.55,.65,33,36,9),(.70,.93,39,47,18)]   # tiers 3 and 4 of build_blockout / r2_seating
EXT_T_MAX=1.0


def build_tower_end(scene,batch,spec,materials,rng,endpoint_mapper=None):
    """Carry the upper two tiers past the bowl's traced end to the clock tower.

    The north aerial shows the upper decks running straight into the tower
    with a crowded flat platform beside it; V12 stopped them at the traced end
    line, leaving a brick link block and empty air.  Each row is extended along
    its own end-line step (front[0]-front[1] blended with back[0]-back[1]) until
    it meets the face west of the shaft (r4_rf_structure.link_east_x), where a
    brick end wall closes it.  The platform is the link block's paved roof.
    Row counts and rakes match the bowl; the extension itself is inferred."""
    from r4_rf_structure import link_east_x,tier_top,PLATFORM_Z,END_WALL_BASE
    group='V12 Tower end'
    front=[Vector(p) for p in spec['bowl_front']];back=[Vector(p) for p in spec['bowl_back']]
    f0,f1,b0,b1=front[0],front[1],back[0],back[1];x_face=link_east_x(spec)
    def step(t):return f0.lerp(b0,t)-f1.lerp(b1,t)
    def count(t):
        d=step(t);x=f0.lerp(b0,t).x
        return max(0.0,(x_face-x)/d.x) if d.x>1e-6 else 0.0
    def at(t,z,s):
        """Point on depth t, s in [0,1] from the end line to the tower face."""
        start=f0.lerp(b0,t)
        end=start+step(t)*count(t)
        if endpoint_mapper is not None:end=Vector(endpoint_mapper(t,end))
        p=start.lerp(end,s);return Vector((p.x,p.y,z))
    N=8
    def strip(mat,t0,z0,t1,z1):
        for i in range(N):
            sa,sb=i/N,(i+1)/N
            batch.quad(group,mat,[tuple(at(t0,z0,sa)),tuple(at(t0,z0,sb)),tuple(at(t1,z1,sb)),tuple(at(t1,z1,sa))])
            batch.quad(group,mat,[tuple(at(t1,z1,sa)),tuple(at(t1,z1,sb)),tuple(at(t0,z0,sb)),tuple(at(t0,z0,sa))])
    seats=[];rot=[];fans=[[] for _ in range(6)];fanrot=[[] for _ in range(6)]
    for ta,tb,za,zb,rows in EXT_TIERS:
        strip('concrete',ta,za-.9,ta,za)                       # fascia
        for row in range(rows):
            t0=ta+(tb-ta)*row/rows;t1=ta+(tb-ta)*(row+1)/rows;z=za+(zb-za)*row/rows
            strip('concrete',t0,z,t1,z);strip('concrete',t1,z,t1,z+(zb-za)/rows)
            t=ta+(tb-ta)*(row+.48)/rows;d=at(t,z,1)-at(t,z,0);length=d.length
            tangent=-d.normalized();angle=math.atan2(tangent.y,tangent.x)
            for k in range(int((length-.6)/.54)):
                p=at(t,z,(.6+k*.54)/max(length,1e-6));seats.append(tuple(p));rot.append((0,0,angle))
                if rng.random()<.75:
                    c=rng.choices(range(6),[32,27,18,15,5,3])[0];fans[c].append(tuple(p));fanrot[c].append((0,0,angle+rng.uniform(-.07,.07)))
    # Concourse slab between the two tiers and the rear wall along the traced back.
    strip('concrete',EXT_TIERS[0][1],36.0,EXT_TIERS[1][0],36.0);strip('concrete',EXT_TIERS[0][1],35.65,EXT_TIERS[1][0],35.65)
    strip('brick',EXT_T_MAX,END_WALL_BASE,EXT_T_MAX,47.6);strip('concrete',EXT_TIERS[1][1],47.0,EXT_T_MAX,47.6)
    strip('stone',EXT_T_MAX,47.6,EXT_T_MAX,47.9)
    # End wall on the tower face: from the platform up to each tier's parapet.
    samples=[EXT_TIERS[0][0]+(EXT_T_MAX-EXT_TIERS[0][0])*k/36 for k in range(37)]
    for ta,tb in zip(samples,samples[1:]):
        pa,pb=at(ta,0,1.0),at(tb,0,1.0);topa,topb=tier_top(ta)+1.1,tier_top(tb)+1.1
        for x0,x1 in ((0.0,.6),):
            verts=[(pa.x+x0,pa.y,END_WALL_BASE),(pb.x+x0,pb.y,END_WALL_BASE),(pb.x+x1,pb.y,END_WALL_BASE),(pa.x+x1,pa.y,END_WALL_BASE),
                   (pa.x+x0,pa.y,topa),(pb.x+x0,pb.y,topb),(pb.x+x1,pb.y,topb),(pa.x+x1,pa.y,topa)]
            batch.add(group,'brick',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        batch.add(group,'stone',[(pa.x-.08,pa.y,topa),(pb.x-.08,pb.y,topb),(pb.x+.68,pb.y,topb),(pa.x+.68,pa.y,topa),
                                 (pa.x-.08,pa.y,topa+.3),(pb.x-.08,pb.y,topb+.3),(pb.x+.68,pb.y,topb+.3),(pa.x+.68,pa.y,topa+.3)],
                  [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    # Platform: rails on the open edges of the link roof and a standing crowd.
    tx,ty,_=spec['anchors']['tower_roof'];y_north=ty+30.0;y_face=at(EXT_TIERS[0][0],0,0).y
    def x_on_line(y):return f0.x+(b0.x-f0.x)*(y-f0.y)/(b0.y-f0.y)
    rail(batch,group,(x_on_line(y_north)+.9,y_north,PLATFORM_Z),(x_face,y_north,PLATFORM_Z))
    rail(batch,group,(x_face-.2,y_north,PLATFORM_Z),(x_face-.2,y_face+.5,PLATFORM_Z))
    walkers=[w for w in [bpy.data.objects.get(n) for n in ['D2_Walking visitor','D2_Walking visitor cloth_white','D2_Walking visitor cloth_black','D2_Walking visitor cloth_blue','D2_Walking visitor cloth_red']] if w]
    if walkers:
        buckets=[[] for _ in walkers];rots=[[] for _ in walkers];placed=0;tries=0
        while placed<70 and tries<2000:
            tries+=1;y=rng.uniform(y_face+.8,y_north-.8);x=rng.uniform(x_on_line(y)+1.6,x_face-.8)
            if x<=x_on_line(y)+1.6:continue
            k=rng.choices(range(len(walkers)),[30,28,22,12,8][:len(walkers)])[0];buckets[k].append((x,y,PLATFORM_Z+.05));rots[k].append((0,0,rng.random()*math.tau));placed+=1
        for k,w in enumerate(walkers):
            if buckets[k]:instances(scene,batch.collection(group),'Tower platform visitors '+str(k),w,buckets[k],rots[k])
    source=bpy.data.objects.get('D2_Seat source')
    if source and seats:instances(scene,batch.collection(group),'Tower end seats',source,seats,rot)
    for k,color in enumerate(['cloth_black','cloth_white','cloth_gray','navy','cloth_blue','cloth_red']):
        person=bpy.data.objects.get('D2_Seated fan '+color)
        if person and fans[k]:instances(scene,batch.collection(group),'Tower end spectators '+color,person,fans[k],fanrot[k])
    return {'seats':len(seats),'spectators':sum(map(len,fans)),'face_x':round(x_face,2),'platform_z':PLATFORM_Z,'rows':[t[4] for t in EXT_TIERS],'reach_m':round(count(EXT_TIERS[1][1])*step(EXT_TIERS[1][1]).length,1)}


# ------------------------------------------------------- terrace front and grand stair
STAIR_X=(80.0,100.0)   # grand stair on the river side of the arches (bridge rendering)


def build_terrace_surface_v12(batch,polygons,step_lines,stair_x=STAIR_X):
    """V11 terrace union split at the level change: south of the arcade face
    the surface is the outfield terrace (22.0); north of it the plaza is flat
    at street level right up to the arcade, except the grand-stair opening."""
    from mathutils.geometry import delaunay_2d_cdt
    from collections import Counter
    from r3_public_realm import STAIR_Y_TOP,STAIR_Y_BOTTOM,ROAD_Z,PLAZA_GRADE,ROAD_Y
    points=[];edges=[]
    for poly in polygons:
        start=len(points);points.extend(Vector(p) for p in poly)
        edges.extend((start+i,start+(i+1)%len(poly)) for i in range(len(poly)))
    for y in step_lines:
        start=len(points);points.extend([Vector((-20,y)),Vector((130,y))]);edges.append((start,start+1))
    for x in stair_x:
        start=len(points);points.extend([Vector((x,STAIR_Y_BOTTOM-.001)),Vector((x,STAIR_Y_TOP+.001))]);edges.append((start,start+1))
    vertices,_,faces,*_=delaunay_2d_cdt(points,edges,[],0,.0001)
    plaza=lambda y:ROAD_Z+PLAZA_GRADE*(ROAD_Y-max(y,STAIR_Y_TOP))
    lower=[];upper=[]
    for face in faces:
        c=sum((vertices[i] for i in face),Vector((0,0)))/len(face)
        if not any(inside(tuple(c),poly) for poly in polygons):continue
        if c.y<STAIR_Y_BOTTOM:upper.append(tuple(face))
        elif STAIR_Y_BOTTOM<=c.y<=STAIR_Y_TOP and stair_x[0]<c.x<stair_x[1]:continue
        else:lower.append(tuple(face))
    for selected,zf in ((upper,terrace_z),(lower,plaza)):
        if not selected:continue
        top=[(p.x,p.y,zf(p.y)) for p in vertices];bottom=[(p.x,p.y,zf(p.y)-.5) for p in vertices]
        batch.add('V11 Continuous terrace','paving',top,selected)
        batch.add('V11 Continuous terrace','concrete',bottom,[tuple(reversed(face)) for face in selected])
        counts=Counter(tuple(sorted((a,b))) for face in selected for a,b in zip(face,face[1:]+face[:1]))
        for (a,b),count in counts.items():
            if count==1:batch.quad('V11 Continuous terrace','stone',[bottom[a],bottom[b],top[b],top[a]])


def build_terrace_front(scene,batch,spec,materials,park,roof):
    """The outfield terrace is the roof of a two-storey brick arcade building
    facing the street-level plaza (bridge and north renderings).  A grand stair
    beside the arches climbs from the plaza to the terrace; the stair band is
    the same one deck_z uses, so the walking route is continuous."""
    from r3_public_realm import STAIR_Y_TOP,STAIR_Y_BOTTOM,TERRACE_Z,deck_z
    from r11_circulation import stairs as _stairs
    group='V12 Terrace front'
    plaza_z=deck_z(STAIR_Y_TOP);y_face=STAIR_Y_BOTTOM
    # The plaza is flat at plaza_z up to this face; deck_z's linear band only guides the walking route down the stair.
    xs=[q[0] for q in park];x0=min(xs)+1.0;x1=max(max(xs),max(q[0] for q in roof if q[1]>150))
    x1=min(x1,113.0)
    stair_x0,stair_x1=STAIR_X
    # Terrace face: brick from the ground to the terrace, along y = y_face.
    batch.box(group,'brick',((x0+x1)/2,y_face+.3,(8+TERRACE_Z-.4)/2),(x1-x0,1.0,TERRACE_Z-.4-8))
    batch.box(group,'stone',((x0+x1)/2,y_face+.3,TERRACE_Z-.22),(x1-x0+.2,1.3,.36))
    # Arches on the plaza face (left normal of tangent (1,0) is +Y: the plaza side).
    bay=6.4
    for x in [x0+bay*(k+.5) for k in range(int((x1-x0)/bay))]:
        if stair_x0-2.5<x<stair_x1+2.5:continue
        _arch_bay(batch,group,Vector((x,y_face+.8,0)),Vector((1,0,0)),4.3,plaza_z+.05,5.4,TERRACE_Z-.4,.5,materials)
    # Grand stair from the plaza (y 172) to the terrace (y 160), 20 m wide, one landing.
    _stairs(batch,group,(( stair_x0+stair_x1)/2,y_face,TERRACE_Z),((stair_x0+stair_x1)/2,STAIR_Y_TOP+.6,plaza_z),stair_x1-stair_x0,1)
    # Landing at the stair head: covers the sliver between the roof and park traces.
    batch.box(group,'paving',((stair_x0+stair_x1)/2,y_face-3.0,TERRACE_Z-.25),(stair_x1-stair_x0+1.4,7.0,.5))
    # Brick cheek walls either side of the stair, following the run.
    for x in (stair_x0-.35,stair_x1+.35):
        n=12
        for k in range(n):
            ya=y_face+(STAIR_Y_TOP-y_face)*k/n;yb=y_face+(STAIR_Y_TOP-y_face)*(k+1)/n;z=deck_z((ya+yb)/2)+.9
            batch.box(group,'brick',(x,(ya+yb)/2,(8+z)/2),(.7,(yb-ya)+.02,z-8))
    # Parapet rail along the terrace edge either side of the stair.
    for xa,xb in ((x0,stair_x0-.7),(stair_x1+.7,x1)):
        rail(batch,group,(xa,y_face-.3,TERRACE_Z),(xb,y_face-.3,TERRACE_Z))
    # Plaza slab under the flat park is otherwise open to the ground: close its
    # visible north-east and west faces with brick so the park reads as a deck.
    return {'face_y':y_face,'plaza_z':round(plaza_z,2),'terrace_z':TERRACE_Z,'stair_x':[stair_x0,stair_x1],'face_x':[round(x0,1),round(x1,1)]}
