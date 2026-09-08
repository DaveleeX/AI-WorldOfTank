# Run through Blender MCP after build_missing_tanks.py.
import bpy,math,random,json,os,time
from mathutils import Vector
ROOT='/Users/lee/GPT6test/wasteland_tanks';reports=[]
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.88;p.inputs['Metallic'].default_value=metal;return m
def cube(n,loc,dim,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def cyl(n,loc,r,depth,m,vertices=12):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(m);return o
def beam(n,a,b,r,m):
 a=Vector(a);b=Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,8);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
for desc in json.load(open(ROOT+'/assets/blender/maps.json')):
 start=time.time();slug=desc['id'];random.seed(912)
 s=bpy.data.scenes.new('IRON FRONT static '+slug);bpy.context.window.scene=s
 base={'desert':(.39,.29,.17),'city':(.24,.25,.23),'mud':(.19,.16,.095),'snow':(.65,.72,.76)}[slug]
 ground=mat(slug+' earth',base);concrete=mat('Weathered concrete',(.31,.30,.26));dark=mat('Shadow cavities',(.045,.055,.05));rust=mat('Oxidized steel',(.24,.105,.045),.4);wood=mat('Dead timber',(.12,.10,.067));stone=mat('Sedimentary rock',(.34,.255,.16) if slug!='snow' else (.48,.58,.63));pale=mat('Exposed edges',(.43,.40,.31) if slug!='snow' else (.8,.85,.88));asphalt=mat('Asphalt and mud rut',(.11,.105,.075));paint=mat('Faded hazard ochre',(.53,.31,.075))
 cube('Continuous drivable terrain',(0,0,-.16),(440,440,.30),ground)
 for j,o in enumerate(desc['obstacles']):
  x,y,w,d,h=o['x'],-o['z'],o['w'],o['d'],o['h']
  if o['type']=='building':
   # Solid lower footprint matches collision; upper stories have real broken windows.
   cube('Rubble-filled building foundation',(x,y,1.1),(w,d,2.2),concrete)
   floors=max(1,int(h/3.7))
   for f in range(floors):
    z=2.3+f*3.7
    cube('Exposed floor slab',(x,y,z),(w,d,.30),pale)
    for side in [-1,1]:
     cube('Window sill band',(x,y+side*(d/2-.25),z+.7),(w,.5,1.1),concrete)
     for k in range(max(2,int(w/2.6))+1):
      xx=x-w/2+k*w/max(2,int(w/2.6))
      if f==floors-1 and (k+j)%4==0:continue
      cube('Cracked facade pier',(xx,y+side*(d/2-.25),z+1.8),(.58,.65,3.2),concrete)
     cube('Side party wall',(x+side*(w/2-.3),y,z+1.6),(.6,d,3.2),concrete)
   for k in range(7):
    xx=x+random.uniform(-w*.4,w*.4);yy=y+random.uniform(-d*.4,d*.4)
    ob=cube('Broken roof concrete',(xx,yy,h*.65),(random.uniform(1,3),random.uniform(1,2),.3),pale);ob.rotation_euler=(random.random(),random.random(),random.random())
   if slug=='mud':
    for side in [-1,1]:
     ob=cube('Broken corrugated farm roof',(x+side*w*.22,y,h+1),(w*.62,d+1,.18),rust);ob.rotation_euler.y=side*.5
  else:
   # Keep silhouette inside collider; no visually passable invisible overhangs.
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,h*.35));ob=bpy.context.object;ob.name='Wind carved escarpment';ob.scale=(w*.49,d*.49,h*.65);ob.data.materials.append(stone)
   for v in ob.data.vertices:v.co*=random.uniform(.92,1.06)
   for k in range(3):
    ob=cube('Erosion strata',(x,y,h*(.22+k*.19)),(w*.85,d*.78,.12),pale);ob.rotation_euler.z=.05
 # Distinct map landmarks sit beyond the 360m combat area.
 for i in range(28):
  a=i/28*math.tau;r=245+(i%4)*17
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(math.sin(a)*r,math.cos(a)*r,8));ob=bpy.context.object;ob.name='Distant wasteland ridge';ob.scale=(35,40,25+i%6*5);ob.data.materials.append(stone)
 if slug=='city':
  cube('Main avenue',(0,0,.006),(19,360,.025),asphalt);cube('Cross avenue',(0,0,.008),(360,16,.025),asphalt)
  for y in range(-172,180,12):cube('Worn lane marking',(0,y,.029),(.18,4,.012),paint)
  for x in [-22,22]:
   for y in range(-150,180,45):
    beam('Bent streetlight',(x,y,0),(x+.4,y,8),.12,rust);beam('Streetlight arm',(x+.4,y,8),(x+3,y,8),.09,rust)
 elif slug=='desert':
  for x in [-80,-35,35,80]:
   y=194
   for side in [-1,1]:beam('Oil derrick truss',(x+side*3,y,0),(x,y,13),.22,rust)
   beam('Oil pump walking beam',(x-5,y,12),(x+6,y,14),.34,rust);beam('Oil pump rod',(x+6,y,14),(x+6,y,1),.12,rust)
   cyl('Abandoned fuel silo',(x+12,y,6),4,12,rust,24)
   for z in [2,6,10]:cyl('Fuel silo seam',(x+12,y,z),4.08,.12,dark,24)
 elif slug=='mud':
  for i in range(60):
   x=math.sin(i*5.32)*164;y=math.cos(i*12.3)*160
   if abs(x)<25:continue
   if any(abs(x-o['x'])<o['w']/2+3 and abs(y+o['z'])<o['d']/2+3 for o in desc['obstacles']):continue
   beam('Dead tree trunk',(x,y,0),(x+.3,y,5.5),.17,wood)
   for side in [-1,1]:beam('Dead tree fork',(x,y,3),(x+side*1.4,y+.2,6),.085,wood)
  for x in [-4,4]:cube('Deep vehicle mud rut',(x,0,.006),(1.3,355,.018),asphalt)
 else:
  for x in [-65,0,65]:
   cube('Abandoned snow outpost',(x,195,3),(20,10,6),concrete);cube('Snow covered roof',(x,195,6.1),(21,11,.7),pale)
   for xx in [-6,-2,2,6]:cube('Outpost shutter',(x+xx,189.94,3.5),(2,.06,1.5),dark)
   beam('Frozen radio mast',(x+15,194,0),(x+15,194,20),.15,rust)
 # Static debris, small enough to drive across, distributed within collision footprints.
 for o in desc['obstacles'][::2]:
  for i in range(5):
   ob=cube('Scattered scrap',(o['x']+random.uniform(-o['w']/2,o['w']/2),-o['z']+random.uniform(-o['d']/2,o['d']/2),.25),(random.uniform(.4,1.8),.65,.4),rust);ob.rotation_euler.z=random.random()*6
 objects=list(s.objects);bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();static=bpy.context.object;static.name='static_environment';static['baked_indirect']=True
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.003,area_weight=.65);bpy.ops.object.mode_set(mode='OBJECT')
 img=bpy.data.images.new(slug+'_indirect',width=2048,height=2048,alpha=False);img.colorspace_settings.name='Linear Rec.709'
 for m in static.data.materials:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=img;m.node_tree.nodes.active=n
 world=bpy.data.worlds.new(slug+' atmospheric sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.57,.69,.8,1) if slug=='snow' else (.67,.72,.78,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7;s.world=world
 ld=bpy.data.lights.new('Sun direct excluded from bake','SUN');sun=bpy.data.objects.new('Sun',ld);s.collection.objects.link(sun);sun.rotation_euler=(.6,-.4,-.55);ld.energy=3.4;ld.angle=.09
 s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.max_bounces=3;s.render.bake.use_pass_direct=False;s.render.bake.use_pass_indirect=True;s.render.bake.use_pass_color=False;s.render.bake.margin=8
 bpy.context.view_layer.objects.active=static;static.select_set(True)
 bpy.ops.object.bake(type='DIFFUSE')
 img.filepath_raw=ROOT+'/public/maps/'+slug+'-indirect.png';img.file_format='PNG';img.save();img.pack()
 s['bake_policy']='DIFFUSE indirect only, no direct, no albedo. Static only. No vehicles/projectiles/effects present.'
 bpy.data.libraries.write(ROOT+'/assets/blender/'+slug+'-world.blend',{s},fake_user=True,compress=True)
 bpy.ops.object.select_all(action='DESELECT');static.select_set(True)
 bpy.ops.export_scene.gltf(filepath=ROOT+'/public/maps/'+slug+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
 reports.append({'map':slug,'source_objects':len(objects),'faces':len(static.data.polygons),'bake':'Cycles DIFFUSE / INDIRECT only','resolution':2048,'samples':16,'dynamic_objects':0,'seconds':round(time.time()-start)})
 open(ROOT+'/assets/blender/bake-report.json','w').write(json.dumps(reports,indent=2));print('MAP COMPLETE',reports[-1],flush=True)
result=reports
