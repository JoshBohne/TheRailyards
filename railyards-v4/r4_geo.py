"""Single V4 geographic registration shared by terrain, lake, roads-era data and skyline.

Audit (2026-09-06): the scene frame is X east, Y north, Z up with river water at
z0.  ``skyline-buildings.json`` records the local tangent projection
``x = dlon*111320*cos(lat) + home_offset``; ``site-context.json``,
``outfield-context.json`` and ``site-roads.json`` (and therefore the modelled
river at x 128-191 and Canal Street at x -220) additionally carry the
``+33 m`` X registration adjustment described in ``scene-spec.json``.

Checks against the recorded site anchors (formula + 33 m vs. scene):
  Roosevelt / river centre   154.7 m vs. river centre 159.5 m  (4.8 m)
  Roosevelt / Canal centre  -219.0 m vs. canal_x     -220.0 m  (1.0 m)
  311 South Wacker (OSM)      77.0 m vs. outfield-context 78 m (1.0 m)

Therefore the +33 m shift is correct for the scene and the 14 legacy skyline
landmarks were 33 m too far west.  V4 applies the shift exactly once, here.
Nothing else in V4 may add its own registration constant.
"""
import json,math
from pathlib import Path

LAT0=41.8645;LON0=-87.6362
HOME_OFFSET=(-0.735682,-4.452813)
REGISTRATION_X_M=33.0
REGISTRATION_Y_M=0.0
KX=111320.0*math.cos(math.radians(LAT0));KY=110900.0
OUT=Path(__file__).resolve().parent

# Vertical datums (conceptual, from scene-spec): river water z0, site ground z8,
# field z12.  The Chicago River is held slightly below Lake Michigan by the
# controlling works; the lake surface is placed 0.5 m above the river datum.
WATER_Z=0.0
LAKE_Z=0.5
GROUND_Z=8.0


def formula_xy(lat,lon):
    """Raw local tangent projection without the site registration shift."""
    return ((lon-LON0)*KX+HOME_OFFSET[0],(lat-LAT0)*KY+HOME_OFFSET[1])


def local_xy(lat,lon):
    """Scene coordinates: formula plus the audited +33 m X registration."""
    x,y=formula_xy(lat,lon)
    return (x+REGISTRATION_X_M,y+REGISTRATION_Y_M)


def register(point):
    """Shift a point that was projected with the raw formula into scene space."""
    return (float(point[0])+REGISTRATION_X_M,float(point[1])+REGISTRATION_Y_M)


def lake_rings():
    """Lake Michigan rings in scene space (already registered)."""
    data=json.loads((OUT/'lake-michigan-local.json').read_text())
    return [[register(p) for p in ring] for ring in data['rings_local']],data


def clip_polygon(polygon,x0,y0,x1,y1):
    """Sutherland-Hodgman clip of a (possibly concave) polygon to a rectangle."""
    def clip(points,inside,intersect):
        result=[]
        if not points:return result
        prev=points[-1]
        for cur in points:
            if inside(cur):
                if not inside(prev):result.append(intersect(prev,cur))
                result.append(cur)
            elif inside(prev):result.append(intersect(prev,cur))
            prev=cur
        return result
    def ix(a,b,x):
        t=(x-a[0])/(b[0]-a[0]);return (x,a[1]+(b[1]-a[1])*t)
    def iy(a,b,y):
        t=(y-a[1])/(b[1]-a[1]);return (a[0]+(b[0]-a[0])*t,y)
    pts=list(polygon)
    pts=clip(pts,lambda p:p[0]>=x0,lambda a,b:ix(a,b,x0))
    pts=clip(pts,lambda p:p[0]<=x1,lambda a,b:ix(a,b,x1))
    pts=clip(pts,lambda p:p[1]>=y0,lambda a,b:iy(a,b,y0))
    pts=clip(pts,lambda p:p[1]<=y1,lambda a,b:iy(a,b,y1))
    return pts


def inside(point,ring):
    x,y=point;value=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:value=not value
    return value


def dedupe(points,tolerance=0.5):
    out=[]
    for p in points:
        if not out or math.dist(p,out[-1])>tolerance:out.append(p)
    if len(out)>1 and math.dist(out[0],out[-1])<=tolerance:out.pop()
    return out
