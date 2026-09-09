"""Roosevelt composition study using the existing powerhouse as a foreground anchor.

The original camera was fitted before the powerhouse existed and before the
clock tower moved. The fit balances the original stadium/bridge controls with
an approximate roof-corner reading from the source; residuals remain visible.
Landmark geometry is never moved to satisfy the image.
"""
import math
import bpy
from mathutils import Vector

PARAMETERS=(285.7894373734686,666.414906276847,98.6726361591113,
            4.310210517834714,.06032645493213214,-.01,1531.2267083427564)


def apply():
    camera=bpy.data.objects['R2_bridge']
    old={'position':list(camera.location),'rotation':list(camera.rotation_euler),'lens':camera.data.lens}
    x,y,z,azimuth,elevation,roll,focal=PARAMETERS
    direction=Vector((math.cos(azimuth)*math.cos(elevation),math.sin(azimuth)*math.cos(elevation),-math.sin(elevation)))
    camera.location=(x,y,z)
    camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    camera.rotation_euler.rotate_axis('Z',roll)
    camera.data.lens=focal*36/1440
    return {'before':old,'after':{'position':list(camera.location),'rotation':list(camera.rotation_euler),'lens':camera.data.lens},
            'basis':'Original image controls plus approximate powerhouse southeast roof corner (1080,740) in 1440x959 source.',
            'fit_residuals_px':{'tower':27.1,'west_lantern':44.9,'centerfield_board':15.1,'rightfield_board':10.5,
                                'leftfield_roof':64.9,'bridge_west_end':29.2,'bridge_east_end':15.7,'powerhouse_roof':27.2},
            'limitation':'Composition study, not survey calibration; source architecture and rebuilt geometry differ.'}


def build(scene,batch,root):
    return apply()
