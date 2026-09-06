"""V5 facade palette: curated colours for known buildings, a deterministic mix for the rest,
and finished roof tops (parapet + mechanical penthouse) for flat prisms.

Only 8 of 114 mapped ways carry OSM colour/material tags, so real facades are
recorded here by name (verified against photographs/Wikipedia descriptions) and
everything else draws from an era-weighted mix of Loop materials.  Pairs are
(wall material, window material).
"""
import hashlib,math
from mathutils import Vector

NAMED={
 'Old Chicago Post Office':('limestone','glass_grey'),'Kluczynski Federal Building':('black_steel','glass_bronze'),
 'Dirksen Federal Building and US Courthouse':('black_steel','glass_bronze'),'Chicago Federal Building':('black_steel','glass_bronze'),
 'Harold Washington Library Center':('brick','glass_green'),'Chicago Board of Trade Building':('limestone','glass_grey'),
 'BMO Tower':('glass_white','glass_blue'),'Union Station Multiplex':('black_steel','glass_dark'),'Chicago Union Station':('limestone','glass_grey'),
 'Ralph H. Metcalfe Federal Building':('granite_grey','glass_dark'),'Federal Reserve Bank of Chicago':('limestone','glass_grey'),
 'Fifth Third Center':('granite_grey','glass_dark'),'Field Building':('limestone','glass_grey'),'Bankers Building':('brick_light','glass_grey'),
 '425 South Financial Place':('brick_dark','glass_bronze'),'200 South Wacker':('glass_white','glass_blue'),'150 South Wacker':('precast','glass_dark'),
 '235 West Van Buren Street':('precast','glass_grey'),'300 South Wacker':('precast','glass_bronze'),'Northern Trust Bank':('limestone','glass_grey'),
 'Wells Street Tower':('precast','glass_green'),'TransUnion Building':('glass_blue','glass_blue'),'Vetro':('glass_blue','glass_blue'),
 'Gateway Center IV':('glass_grey','glass_dark'),'Imprint':('glass_white','glass_blue'),'Burnham Pointe':('precast','glass_green'),
 'Metropolitan Correctional Center':('precast','glass_dark'),'200 West Jackson':('glass_dark','glass_dark'),'River City':('precast','glass_grey'),
 'The Rookery':('terracotta','glass_grey'),'Monadnock Building':('brick_dark','glass_grey'),'Fisher Building':('terracotta','glass_grey'),
 'Manhattan Building':('granite_grey','glass_grey'),'Old Colony Building':('limestone','glass_grey'),'Marquette Building':('terracotta','glass_grey'),
 'Congress Center':('limestone','glass_grey'),'One Congress Center':('terracotta','glass_grey'),'Library Tower':('glass_white','glass_blue'),
 'Essex on the Park':('glass_white','glass_blue'),'The Columbian':('precast','glass_green'),'The Blackstone, Autograph Collection':('brick_dark','glass_grey'),
 'Columbia College South Campus Building':('brick_dark','glass_grey'),'Sky55':('precast','glass_blue'),'Museum Tower':('glass_blue','glass_blue'),
 '1001 South State':('glass_white','glass_blue'),'Arrive Michigan Avenue':('glass_grey','glass_blue'),'Astoria Tower':('glass_white','glass_blue'),
 '1400 Museum Park':('glass_blue','glass_blue'),'1111 South Wabash':('precast','glass_green'),'Alta Grand Central':('glass_white','glass_blue'),
 'Roosevelt Collection':('precast','glass_grey'),'Union Station Power Plant':('brick_dark','glass_dark'),'1000 South Clark':('glass_white','glass_blue'),
}
# Era-weighted mix for unnamed buildings: (wall, window, weight).
MIX=[('limestone','glass_grey',22),('terracotta','glass_grey',10),('brick_light','glass_grey',12),('brick_dark','glass_grey',8),
     ('precast','glass_dark',16),('granite_grey','glass_dark',8),('glass_dark','glass_dark',7),('glass_blue','glass_blue',7),
     ('glass_white','glass_blue',6),('glass_bronze','glass_bronze',4)]


def _hash(key):
    return int(hashlib.sha1(str(key).encode()).hexdigest()[:8],16)


def facade(name,osm_way=None,height=0.0,start_date=None):
    """Return (wall material, window material) for a building."""
    if name in NAMED:return NAMED[name]
    h=_hash(osm_way or name)
    mix=list(MIX)
    if start_date:
        try:
            year=int(str(start_date)[:4])
            if year<1940:mix=[m for m in mix if m[0] in ('limestone','terracotta','brick_light','brick_dark')]
            elif year<1985:mix=[m for m in mix if m[0] in ('precast','granite_grey','glass_dark','glass_bronze')]
            else:mix=[m for m in mix if m[0] in ('glass_blue','glass_white','granite_grey','precast')]
        except ValueError:pass
    if height>=120:  # tall post-war towers are rarely masonry
        mix=[m for m in mix if m[0] not in ('brick_light','brick_dark','terracotta')]+[('glass_blue','glass_blue',6),('glass_dark','glass_dark',6)]
    total=sum(w for _,_,w in mix);pick=h%total
    for wall,window,w in mix:
        pick-=w
        if pick<0:return wall,window
    return mix[-1][:2]


def window_ratio(name,osm_way=None):
    """Fraction of a facade that is glazing; varies by era so not every block is a checkerboard."""
    return .45+(_hash(('w',osm_way or name))%40)/100.0


def tops(batch,group,footprint,z1,wall,name=None,osm_way=None,height=0.0):
    """Parapet and a mechanical penthouse so flat prisms read as finished roofs."""
    pts=[Vector(p) for p in footprint]
    if len(pts)<3:return
    area=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(pts,pts[1:]+pts[:1]))/2)
    batch.prism(group,wall,footprint,z1,z1+.9)
    if height<18 or area<250:return
    c=sum(pts,Vector((0,0)))/len(pts);s=math.sqrt(area)
    h=_hash(('p',osm_way or name))
    w=min(s*.42,28);d=min(s*.34,22);ph=3.5+(h%3)*1.2
    batch.box(group,'precast',(c.x+(h%7-3)*s*.03,c.y+((h//7)%7-3)*s*.03,z1+.9+ph/2),(w,d,ph))
    if height>=90:
        batch.box(group,'metal',(c.x,c.y,z1+.9+ph+.6),(w*.35,d*.35,1.2))
