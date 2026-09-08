# Execute in the isolated Blender MCP instance; original .blend sources remain unchanged.
import bpy,math,os,json
from mathutils import Matrix,Vector
ROOT='/Users/lee/GPT6test';OUT=ROOT+'/wasteland_tanks';os.makedirs(OUT+'/public/models/rigged',exist_ok=True);os.makedirs(OUT+'/public/equipment',exist_ok=True)
rigs=[('china',OUT+'/assets/blender/china.blend',(0,-1.45,2.25),0),('france',OUT+'/assets/blender/france.blend',(0,-1.47,2.25),0),('japan',OUT+'/assets/blender/japan.blend',(0,-1.4,2.2),0),('challenger',ROOT+'/tank_series/01_challenger2.blend',(0,-1.43,2.37),.065),('leopard',ROOT+'/tank_series/02_leopard2a7.blend',(0,-1.22,2.31),.235),('abrams',ROOT+'/tank_series/04_abramsx.blend',(0,-1.66,2.4),.095)]
report=[]
for slug,path,hinge,elev in rigs:
 bpy.ops.wm.open_mainfile(filepath=path);s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s
 tip=next(o for o in s.objects if o.name.startswith('Open annular muzzle'));delta=tip.matrix_world.translation-Vector(hinge);elev=math.atan2(delta.z,-delta.y)
 parts={'body':[],'turret':[],'cannon':[],'tracks':[]}
 for o in list(s.objects):
  cs=' '.join(c.name for c in o.users_collection);n=o.name.lower()
  if o.type not in ('MESH','CURVE','FONT') or not any(k in cs for k in ['01 •','02 •','03 •','04 •']):continue
  cannon=any(n.startswith(k) for k in ['main gun','gun flexible','barrel band','bore evacuator','open annular','dark bore','thermal sleeve','raised dark barrel','sand colored gun'])
  kind='cannon' if cannon else 'tracks' if '02 •' in cs else 'turret' if '03 •' in cs or ('04 •' in cs and any(k in n for k in ['turret','basket','antenna'])) else 'body'
  parts[kind].append(o)
 joined=[]
 for kind,objs in parts.items():
  if not objs:raise Exception(slug+' missing '+kind)
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=kind
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  if kind=='cannon':o.data.transform(Matrix.Rotation(elev,4,'X') @ Matrix.Translation(-Vector(hinge)))
  mod=o.modifiers.new('Original matching game LOD','DECIMATE');mod.ratio=.38;bpy.ops.object.modifier_apply(modifier=mod.name);joined.append(o)
 for m in bpy.data.materials:
  if m.use_nodes:
   p=m.node_tree.nodes.get('Principled BSDF')
   if p:
    for inp in ['Base Color','Normal','Roughness','Metallic']:
     for link in list(p.inputs[inp].links):m.node_tree.links.remove(link)
    p.inputs['Base Color'].default_value=m.diffuse_color
 bpy.ops.object.select_all(action='DESELECT')
 for o in joined:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=OUT+'/public/models/rigged/'+slug+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
 report.append({'tank':slug,'parts':{k:len(v) for k,v in parts.items()},'hinge':[hinge[0],hinge[2],-hinge[1]]})
# One editable library with distinctly authored modular equipment and escort aircraft.
exec(open(OUT+'/scripts/tank_common.py').read())
setup('equipment','IRON FRONT equipment and aircraft',94,(.23,.27,.18));library=S;made={}
BRASS=material('Machined brass',(.53,.31,.07),.8,.34,False);CYAN=material('Turbine ceramic blue',(.08,.30,.35),.6,.35,False);RED=material('HE identification red',(.45,.06,.025),.3,.6,False)
def build(name,fn):
 before=set(S.objects);group(name);fn();objs=list(set(S.objects)-before)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 for m in o.data.materials:
  if m and m.use_nodes:
   shader=m.node_tree.nodes.get('Principled BSDF')
   if shader:
    for inp in ['Base Color','Normal','Roughness','Metallic']:
     for link in list(shader.inputs[inp].links):m.node_tree.links.remove(link)
    shader.inputs['Base Color'].default_value=m.diffuse_color
 bpy.ops.export_scene.gltf(filepath=OUT+'/public/equipment/'+name+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
 made[name]=len(o.data.polygons);o.hide_set(True)
def barrel(tier):
 length=4.4 if tier==1 else 2.75
 gun((0,0,0),length,0,True,PAINT if tier==1 else TRACK)
 if tier==1:
  for side in [-1,1]:
   box('Longitudinal reinforcement',(side*.18,-2.15,0),(.08,2.8,.13),EDGE,.018)
   for j in range(12):bolt((side*.23,-.9-j*.2,0),(side,0,0),.024)
  cylinder('Muzzle brass collar',(0,-4.1,0),(0,-4.25,0),.16,BRASS,n=48)
 else:
  for side in [-1,1]:
   cylinder('Hydraulic recoil return',(side*.22,-.2,.11),(side*.22,-1.5,.11),.10,STEEL,n=32)
   for j in range(10):box('Heat sink fin',(side*.17,-.6-j*.14,0),(.1,.065,.38),EDGE,.009)
  for j in range(6):cylinder('Rapid fire cooling sleeve',(0,-.5-j*.26,0),(0,-.57-j*.26,0),.225,CYAN,n=48)
def tracks(tier):
 for side in [-1,1]:
  for j in range(34):
   t=j/34*math.tau;y=2.3*math.cos(t);z=.68+.54*math.sin(t)
   box('Wide articulated cleat',(side*1.72,y,z),(.95 if tier==1 else .76,.20,.12),TRACK,.022)
   for x in [-.26,.26]:box('Raised traction teeth',(side*1.72+x,y,z+.09),(.12,.15,.12),STEEL,.013)
  for j in range(6):
   y=-1.95+j*.78;cylinder('Road wheel forged rim',(side*1.93,y,.68),(side*2.12,y,.68),.39,EDGE,n=40)
   cylinder('Armored wheel hub',(side*2.12,y,.68),(side*2.18,y,.68),.18,PAINT if tier==1 else CYAN,n=32)
   for k in range(8):
    t=k/8*math.tau;bolt((side*2.19,y+.27*math.cos(t),.68+.27*math.sin(t)),(side,0,0),.025)
  if tier==2:
   box('Turbine drive housing',(side*1.64,2.27,1.28),(.85,1.05,.65),EDGE,.12)
   cylinder('Turbine exhaust',(side*1.64,2.5,1.3),(side*1.64,2.98,1.3),.25,STEEL,n=40)
   cylinder('Recessed ceramic exhaust',(side*1.64,2.99,1.3),(side*1.64,3,1.3),.19,CYAN,n=32)
def armor(tier):
 for side in [-1,1]:
  for j in range(6):
   box('Reactive armor module',(side*2.0,-2.1+j*.76,1.36),(.26,.65,.60),PAINT,.045)
   for y in [-.22,.22]:bolt((side*2.14,-2.1+j*.76+y,1.36),(side,0,0),.032)
   if tier==2:box('Spaced ceramic face',(side*2.19,-2.1+j*.76,1.36),(.10,.60,.48),EDGE,.02)
  if tier==2:
   for j in range(10):box('Rear cage slat',(side*2.30,1+j*.13,1.32),(.035,.04,.8),STEEL,.005)
def ammo(tier):
 box('Ammunition field crate',(0,0,.13),(1.45,1.05,.26),EDGE,.04)
 for x in [-.44,0,.44]:
  cylinder('Cartridge brass case',(x,0,.28),(x,0,1.04),.13,BRASS,n=40)
  cylinder('Projectile body',(x,0,1.04),(x,0,1.43),.12,STEEL if tier<2 else RED,n=40)
  cylinder('Ballistic nose',(x,0,1.43),(x,0,1.76 if tier==1 else 1.60),.12,STEEL,r2=.012,n=40)
  cylinder('Identification band',(x,0,1.1),(x,0,1.16),.128,[PAINT,CYAN,RED][tier],n=40)
  if tier==1:
   for ang in range(4):
    o=box('Stabilizing fin',(x,0,1.23),(.28,.025,.15),STEEL,.006);o.rotation_euler.z=ang*math.pi/2
  bolt((x,0,.29),r=.045)
def aircraft():
 loft('Armored fuselage',[(-.6,-3.2),(.6,-3.2),(1,-1.2),(.7,2.8),(-.7,2.8),(-1,-1.2)],-.4,.6,PAINT,(.64,.8),b=.09)
 box('Smoked cockpit',(0,-2,.65),(.8,1.15,.22),GLASS,.11)
 for side in [-1,1]:
  o=box('Swept wing',(side*2.15,.3,.1),(3.5,1.15,.2),EDGE,.09);o.rotation_euler.z=side*-.2
  cylinder('Jet nacelle',(side*2.6,-1.1,0),(side*2.6,1.9,0),.46,PAINT,n=48)
  cylinder('Dark exhaust cavity',(side*2.6,1.90,0),(side*2.6,1.95,0),.34,DARK,n=40)
  cylinder('Exhaust glow core',(side*2.6,1.96,0),(side*2.6,2.0,0),.24,CYAN,n=32)
  o=box('Canted tail',(side*.8,2.1,.8),(.14,1.4,1.6),PAINT,.04);o.rotation_euler.y=side*.35
  box('Ochre wing stripe',(side*2.4,.2,.22),(.3,.9,.03),BRASS,.008)
  for j in range(8):bolt((side*1.4,.0+j*.19,.23),r=.03)
for tier in [1,2]:
 build('barrel_'+str(tier),lambda t=tier:barrel(t));build('tracks_'+str(tier),lambda t=tier:tracks(t));build('armor_'+str(tier),lambda t=tier:armor(t))
for tier in range(3):build('ammo_'+str(tier),lambda t=tier:ammo(t))
build('aircraft',aircraft)
for i,key in enumerate(made):
 o=S.objects[key];o.hide_set(False);o.location=((i%5)*7,(i//5)*10,0)
S['dynamic']=True;S['baked_indirect']=False
bpy.data.libraries.write(OUT+'/assets/blender/equipment-library.blend',{S},fake_user=True,compress=True)
with open(OUT+'/assets/equipment-report.json','w') as f:json.dump({'rigs':report,'equipment_faces':made,'dynamic':True,'light_baked':False},f,indent=2)
result={'rigs':report,'equipment':made}
