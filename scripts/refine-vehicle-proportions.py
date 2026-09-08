# Blender MCP: preserve source detail, correct silhouettes, rebuild circular running gear.
import bpy,math,os,shutil,json
from mathutils import Matrix,Vector
OUT='/Users/lee/GPT6test/wasteland_tanks'
exec(open(OUT+'/scripts/tank_common.py').read())
os.makedirs(OUT+'/assets/refinement-inputs',exist_ok=True);os.makedirs(OUT+'/assets/blender/refined',exist_ok=True)
models={'china':6,'france':6,'japan':5,'challenger':6,'leopard':7,'abrams':7}
for slug in models:
 path=OUT+'/assets/refinement-inputs/'+slug+'.glb'
 if not os.path.exists(path):shutil.copy2(OUT+'/public/models/rigged/'+slug+'.glb',path)
for name in ['barrel_1','barrel_2','armor_1','armor_2']:
 path=OUT+'/assets/refinement-inputs/'+name+'.glb'
 if not os.path.exists(path):shutil.copy2(OUT+'/public/equipment/'+name+'.glb',path)
def flatten(o):
 matrix=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Identity(4);o.data.transform(matrix)
def export(path,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
def join(objs,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);return o
def running_gear(wheels,tier=0):
 before=set(S.objects);group('02 • Operational running gear')
 rubber=material('Vulcanized rubber sidewalls',(.016,.019,.018),.03,.96,False);steel=material('Worn manganese track steel',(.13,.14,.13),.76,.6,False);paint=material('Wheel hub painted armor',(.14,.18,.11),.3,.73,False);dark=material('Suspension shadow',(.023,.026,.024),.2,.86,False)
 L=2.73 if wheels!=5 else 2.5;R=.52;zc=.65;total=4*L+2*math.pi*R;count=104
 def path(t):
  if t<2*L:return -L+t,zc+R,0
  t-=2*L
  if t<math.pi*R:a=t/R;return L+R*math.sin(a),zc+R*math.cos(a),-a
  t-=math.pi*R
  if t<2*L:return L-t,zc-R,math.pi
  t-=2*L;a=math.pi+t/R;return -L+R*math.sin(a),zc+R*math.cos(a),-a
 for side in [-1,1]:
  x=side*1.52;width=.76 if tier==1 else .66
  for j in range(count):
   y,z,a=path(j*total/count);o=box('Steel articulated track shoe',(x,y,z),(width,total/count*.88,.065),steel,.009);o.rotation_euler.x=a
   for dx in [-.16,.16]:
    o=box('Replaceable rubber tread pad',(x+dx,y-math.sin(a)*.05,z+math.cos(a)*.05),(.255,total/count*.67,.040),rubber,.006);o.rotation_euler.x=a
   for dx in [-width/2,width/2]:cylinder('Track link pin',(x+dx-.018,y,z),(x+dx+.018,y,z),.026,steel,n=12)
  radius=.445 if wheels==6 else .395 if wheels==7 else .475;center=radius+.10
  for j in range(wheels):
   y=-(L-.44)+j*(2*(L-.44))/(wheels-1);face=x+side*.325
   cylinder('Double road wheel rubber tire',(x-.25,y,center),(x+.25,y,center),radius,rubber,n=64,soft=True)
   cylinder('Recessed wheel rim',(face-side*.06,y,center),(face,y,center),radius*.80,steel,n=48,soft=True)
   cylinder('Conical forged wheel dish',(face,y,center),(face+side*.043,y,center),radius*.69,paint,r2=radius*.57,n=48,soft=True)
   cylinder('Hub cap',(face+side*.045,y,center),(face+side*.11,y,center),radius*.25,steel,r2=radius*.20,n=32)
   for k in range(10):
    a=k/10*math.tau;bolt((face+side*.048,y+radius*.45*math.cos(a),center+radius*.45*math.sin(a)),(side,0,0),.024,steel)
  for y in [-L,L]:
   face=x+side*.33;cylinder('End idler tire',(x-.25,y,zc),(x+.25,y,zc),.445,steel,n=48)
   cylinder('Idler recessed dish',(face-side*.015,y,zc),(face+side*.035,y,zc),.32,dark,n=48)
   cylinder('Idler axle',(face+side*.038,y,zc),(face+side*.085,y,zc),.135,steel,n=32)
   for k in range(8):
    a=k/8*math.tau;ob=box('Idler radial rib',(face+side*.04,y+.2*math.cos(a),zc+.2*math.sin(a)),(.06,.23,.055),steel,.008);ob.rotation_euler.x=a
  box('Suspension housing',(x-side*.24,0,.85),(.18,2*L,.5),dark,.02)
  if tier==2:
   box('Turbo final drive housing',(x,2.9,1.15),(.66,.7,.40),paint,.07)
   cylinder('Turbo exhaust nozzle',(x,3.10,1.14),(x,3.42,1.14),.16,steel,n=40)
   cylinder('Sooted exhaust recess',(x,3.42,1.14),(x,3.425,1.14),.12,dark,n=32)
 return join(list(set(S.objects)-before),'tracks')
reports=[]
for slug,wheels in models.items():
 setup('refined-'+slug,'Refined '+slug,114,(.16,.2,.12))
 bpy.ops.import_scene.gltf(filepath=OUT+'/assets/refinement-inputs/'+slug+'.glb')
 objects=[]
 for o in list(S.objects):
  if o.type!='MESH':continue
  if o.name.startswith('tracks'):bpy.data.objects.remove(o,do_unlink=True);continue
  flatten(o)
  kind=o.name.split('.')[0]
  if kind=='body':o.data.transform(Matrix.Diagonal((1,1.40 if slug!='japan' else 1.3,.86,1)))
  elif kind=='turret':
   for v in o.data.vertices:
    if v.co.z>2.65:v.co.z=2.65+(v.co.z-2.65)*.62
   o.data.transform(Matrix.Diagonal((1,1.12,.86,1)))
  elif kind=='cannon':o.data.transform(Matrix.Diagonal((.87,1.2,.87,1)))
  objects.append(o)
 objects.append(running_gear(wheels))
 # Mesh details on the new long glacis: towing cable, welded seams, tread spares.
 before=set(S.objects);group('01 • Field fittings')
 for side in [-1,1]:
  pipe('Tow cable',[(side*1.28,y,1.51) for y in [-2.2,-1.4,-.4,.5,1.5,2.2]],.033,STEEL)
  for y in [-2.2,-1.0,.2,1.4,2.2]:box('Cable retaining strap',(side*1.28,y,1.535),(.16,.10,.05),EDGE,.006)
  for j in range(5):
   box('Rear deck spare track',(side*.62,2.5+j*.12,1.52),(.5,.10,.09),TRACK,.008)
 added=list(set(S.objects)-before)
 if added:
  extra=join(added,'body_field_fittings');objects.append(extra)
 S['dynamic']=True;S['baked_indirect']=False
 export(OUT+'/public/models/rigged/'+slug+'.glb',objects)
 bpy.data.libraries.write(OUT+'/assets/blender/refined/'+slug+'.blend',{S},fake_user=True,compress=True)
 reports.append({'model':slug,'road_wheels_per_side':wheels,'body_length_scale':1.4 if slug!='japan' else 1.3,'height_scale':.86})
for wheels in [5,6,7]:
 for tier in [1,2]:
  setup('tracks','Track upgrade',62,(.15,.18,.12));o=running_gear(wheels,tier);export(OUT+f'/public/equipment/tracks_{tier}_{wheels}.glb',[o])
for name in ['barrel_1','barrel_2','armor_1','armor_2']:
 setup(name,name,72,(.15,.18,.12));bpy.ops.import_scene.gltf(filepath=OUT+'/assets/refinement-inputs/'+name+'.glb')
 objs=[o for o in S.objects if o.type=='MESH']
 for o in objs:
  flatten(o);o.data.transform(Matrix.Diagonal((.87,1.2,.87,1)) if name.startswith('barrel') else Matrix.Diagonal((1,1.4,.86,1)))
 export(OUT+'/public/equipment/'+name+'.glb',objs)
with open(OUT+'/assets/vehicle-refinement.json','w') as f:json.dump(reports,f,indent=2)
result={'refined':reports}
