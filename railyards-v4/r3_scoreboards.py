"""Two-sided native-vector video boards and exposed support frames."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from r2_geometry import text

def build_scoreboards(scene,spec,batch,materials):
    col=batch.collection('Scoreboards')
    contours=json.loads((Path(__file__).parent/'assets/sox-contours.json').read_text())['contours']
    def logo(name,position,scale,angle):
        curve=bpy.data.curves.new('D2_'+name,'CURVE');curve.dimensions='2D';curve.fill_mode='BOTH';curve.resolution_u=1;curve.extrude=.018
        for points in contours:
            spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
            for p,xy in zip(spline.points,points):p.co=(xy[0]*scale,xy[1]*scale,0,1)
            spline.use_cyclic_u=True
        curve.materials.append(materials['screen_ink']);obj=bpy.data.objects.new('D2_'+name,curve);col.objects.link(obj);obj.location=position;obj.rotation_euler=(math.pi/2,0,angle)
    rf=spec.get('rf_scoreboard',{})
    for key,width,angle in [('cf_scoreboard_top',31,math.radians(135)),('rf_scoreboard_top',rf.get('width_m',39),math.radians(rf.get('angle_deg',90)))]:
        top=Vector(spec['anchors'][key]);h=18 if key.startswith('cf')else rf.get('height_m',20)
        support_base=rf.get('support_base_z',13.0) if key.startswith('rf') else 13.0
        t=Vector((math.cos(angle),math.sin(angle),0));normal=Vector((t.y,-t.x,0))
        is_rf=key.startswith('rf')
        batch.box('Scoreboards','metal',(top.x,top.y,top.z-h/2),(width+1,2,h+1),angle)
        if not is_rf:
            batch.box('Scoreboards','metal',(top.x,top.y,top.z+1.35),(width+1,2.25,2.7),angle)
        for side in [-1,1]:
            facing=angle if side==1 else angle+math.pi
            across=t*side
            def pos(u,z,depth=1.14):
                return top+across*u+normal*(depth*side)+Vector((0,0,z))
            batch.box('Scoreboards','screen',pos(0,-h/2,1.06),(width,.08,h),angle)
            if not is_rf:
                text(scene,col,key+' header '+str(side),'THE RAILYARDS',pos(0,.9),3.4,materials['screen_ink'],(math.pi/2,0,facing))
            if not is_rf and side==1:
                logo(key+' exterior logo',pos(0,-h/2),12,facing)
            else:
                # Both RF faces show the same illustrative game layout in the
                # north/south concept art. CF's park face carries the Sox mark.
                logo(key+' game Sox '+str(side),pos(width*.36,-h*.33),5.7,facing)
                text(scene,col,key+' visitors '+str(side),'D',pos(-width*.38,-h*.35),4.4,materials['screen_ink'],(math.pi/2,0,facing))
                text(scene,col,key+' player '+str(side),'Joe\nSmith',pos(width*.02,-h*.26),1.45,materials['screen_ink'],(math.pi/2,0,facing))
                # A deliberately simple native player portrait matches the
                # source panel's placement; facial detail is unresolved.
                batch.ellipsoid('Scoreboards','skin',pos(-width*.16,-h*.19,1.2),(.66,.21,.84),12,8)
                batch.box('Scoreboards','white',pos(-width*.16,-h*.32,1.2),(2.5,.12,1.5),angle)
                batch.box('Scoreboards','navy',pos(-width*.16,-h*.145,1.25),(1.45,.14,.25),angle)
                text(scene,col,key+' player stats '+str(side),'PITCHER    46',pos(width*.025,-h*.43),.45,materials['screen_ink'],(math.pi/2,0,facing))
                labels=[('INNING',-.54),('DETROIT TIGERS',-.68),('WHITE SOX',-.82)]
                for row,(label,zf) in enumerate(labels):
                    text(scene,col,key+' label '+str(side)+str(row),label,pos(-width*.34,h*zf),.49,materials['screen_ink'],(math.pi/2,0,facing))
                    values=['1  2  3  4  5  6  7  8  9    R  H  E','0  0  1  0  0  0  0  0  0    1  5  0','0  1  0  0  0  0  1  0  0    2  2  1']
                    text(scene,col,key+' innings '+str(side)+str(row),values[row],pos(width*.105,h*zf),.57,materials['screen_ink'],(math.pi/2,0,facing))
            for dz in [0,-h]:
                batch.cylinder('Scoreboards','aluminum',pos(-width/2,dz),pos(width/2,dz),.10,sides=6)
        # Source RF screen has two separate floodlight banks above its frame.
        if is_rf:
            for bank in [-1,1]:
                c=top+t*(bank*width*.255)+Vector((0,0,2.25))
                batch.box('Scoreboards','metal',c,(width*.41,1.5,3.2),angle)
                data=bpy.data.lights.new('D2_Field light RF '+str(bank),'AREA')
                data.shape='RECTANGLE';data.size=width*.41;data.size_y=2.6
                data.spread=math.radians(115);data.color=(.88,.93,1);data.energy=120000
                light=bpy.data.objects.new(data.name,data);batch.collection('Lighting').objects.link(light)
                light.location=c-normal*.95
                light.rotation_euler=(Vector((-25,15,29))-light.location).to_track_quat('-Z','Y').to_euler()

                for i in range(21):
                    for row in range(4):
                        q=c+t*((i-10)*width*.018)+Vector((0,0,(row-1.5)*.65))
                        for side in [-1,1]:
                            batch.box('Scoreboards','stadium_lamp',q+normal*(side*.79),(.50,.08,.42),angle)
        # Deep lattice along the side edges, a service deck, and supports.
        base=top.copy();base.z-=h+.9
        batch.box('Scoreboards','metal',base,(width+1.8,3.7,.24),angle)
        for u in [-width/2-.35,width/2+.35]:
            p=top+t*u
            for depth in [-1.4,1.4]:
                a=p+normal*depth;a.z=top.z-h-.5
                b=p+normal*depth;b.z=top.z+.5
                batch.cylinder('Scoreboards','metal',a,b,.18,sides=8)
            for k in range(7):
                za=top.z-h+k*h/7;zb=za+h/7
                for side in [-1,1]:
                    a=p+normal*(1.4*side);a.z=za
                    b=p-normal*(1.4*side);b.z=zb
                    batch.cylinder('Scoreboards','metal',a,b,.085,sides=6)
        if is_rf:
            # V12: the RF board bears on a brick board house standing on the
            # podium ring behind the outfield wall.  The north and south
            # artwork show the board rising from a low brick block, not
            # from lattice legs.  The field face keeps the V4 wall clearance.
            house_top=top.z-h-.25
            def hp(u,d):
                q=top+t*u+normal*d;return (q.x,q.y)
            batch.prism('Scoreboards','brick',[hp(-width/2-.6,-1.6),hp(width/2+.6,-1.6),hp(width/2+.6,3.0),hp(-width/2-.6,3.0)],support_base-.05,house_top)
            batch.prism('Scoreboards','stone',[hp(-width/2-.8,-1.8),hp(width/2+.8,-1.8),hp(width/2+.8,3.2),hp(-width/2-.8,3.2)],house_top,house_top+.35)
            batch.prism('Scoreboards','stone',[hp(-width/2-.7,-1.7),hp(width/2+.7,-1.7),hp(width/2+.7,3.1),hp(-width/2-.7,3.1)],support_base+2.6,support_base+3.0)
            from r3_envelope import _arch_bay
            count=max(2,round(width/7.5))
            for k in range(count):
                c=top+t*((k+.5)/count*width-width/2)+normal*3.0
                # _arch_bay opens toward the left normal of its tangent; -t faces the river.
                _arch_bay(batch,'Scoreboards',Vector((c.x,c.y,0)),-t,4.2,support_base+.3,4.4,house_top,.5,materials)
                c=top+t*((k+.5)/count*width-width/2)+normal*(-1.6)
                batch.box('Scoreboards','glass_dim',(c.x,c.y,support_base+3.4),(3.0,.12,1.6),angle)
        else:
          for u in [-width*.33,width*.33]:
            p=top+t*u
            batch.box('Scoreboards','metal',(p.x,p.y,(support_base+top.z-h)/2),(1.15,2.7,max(.4,top.z-h-support_base)),angle)
