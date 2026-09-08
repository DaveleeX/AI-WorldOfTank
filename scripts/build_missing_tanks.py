# Executed by the running Blender MCP; reuse the accepted miniature modeling library.
exec(open('/Users/lee/GPT6test/wasteland_tanks/scripts/tank_common.py').read())
import json
OUT='/Users/lee/GPT6test/wasteland_tanks'
reports=[]
for slug,title,col,wheels in [('china','99A',(.24,.30,.14),6),('france','Leclerc',(.30,.32,.19),6),('japan','Type 10',(.22,.28,.18),5)]:
 setup(slug,title,70+wheels,col)
 chassis(wheels,'panels');turret_base();group('03 • Turret and main gun')
 if slug=='china':
  outline=[(-1.35,-1.18),(-.55,-1.52),(.55,-1.52),(1.35,-1.18),(1.44,.9),(.95,1.35),(-.95,1.35),(-1.44,.9)]
  loft('99A welded angular turret',outline,1.84,2.60,PAINT,(.84,.84),b=.045)
  for side in [-1,1]:
   for row in range(2):
    for i in range(4):
     o=box('99A arrowhead reactive armor',(side*(.37+i*.28),-1.37+row*.18,2.05+row*.28),(.265,.42,.25),PAINT,.018);o.rotation_euler.x=-.38
     bolt((side*(.37+i*.28),-1.60+row*.18,2.07+row*.28),(0,-1,0),.018)
  gun((0,-1.45,2.25),3.65,0,True)
  box('Laser countermeasure head',(.77,.55,2.88),(.36,.35,.36),EDGE)
  optic((.77,.36,2.89),.28,.22,EDGE,True)
 elif slug=='france':
  outline=[(-1.13,-1.32),(-.52,-1.53),(.52,-1.53),(1.13,-1.32),(1.37,.65),(1.24,1.58),(-1.24,1.58),(-1.37,.65)]
  loft('Leclerc narrow faceted turret',outline,1.83,2.62,PAINT,(.88,.86),b=.035)
  box('Leclerc autoloader bustle',(0,1.25,2.26),(2.5,1.20,.71),PAINT,.065)
  for side in [-1,1]:
   prism('Leclerc cheek module',[(-1.53,1.94),(-1.27,2.64),(-.30,2.60),(-.15,1.94)],.63,PAINT,x=side*.83)
   for i in range(5):box('Bustle vent',(side*1.267,.87+i*.17,2.30),(.026,.08,.28),EDGE,.006)
  gun((0,-1.47,2.25),3.45,0,True)
  optic((-.67,-.72,2.68),.47,.31,EDGE,True)
 else:
  outline=[(-1.26,-.9),(-.65,-1.42),(.65,-1.42),(1.26,-.9),(1.35,.8),(.94,1.37),(-.94,1.37),(-1.35,.8)]
  loft('Type 10 compact modular turret',outline,1.83,2.47,PAINT,(.73,.79),b=.055)
  for side in [-1,1]:
   prism('Type 10 swept modular cheek',[(-1.49,1.97),(-1.05,2.55),(.3,2.50),(.62,1.96)],.86,PAINT,x=side*.87)
   for i in range(4):
    box('Type 10 external storage module',(side*1.20,.28+i*.29,2.20),(.23,.27,.48),PAINT,.018)
    handle((side*1.2,.28+i*.29,2.46),'Y',.16)
  gun((0,-1.4,2.2),3.15,0,False)
  optic((.64,-.32,2.64),.46,.35,EDGE,True)
 # Uniform detail density: hardware, hatches, sights, smoke launchers, bustle cages.
 group('03 • Turret and main gun')
 for side in [-1,1]:
  cylinder('Crew hatch',(side*.60,.2,2.53),(side*.60,.2,2.64),.34,EDGE,n=40)
  handle((side*.60,.2,2.65))
  for i in range(4):
   cylinder('Smoke grenade tube',(side*1.24,-.16+i*.15,2.42),(side*1.48,-.35+i*.15,2.53),.060,EDGE,n=24)
  pipe('Turret stowage basket',[(side*1.05,.78,2.48),(side*1.37,1.65,2.48),(side*.1,1.70,2.48)],.025,EDGE)
  for i in range(6):pipe('Basket vertical bar',[(side*(.15+i*.23),1.67,2.1),(side*(.15+i*.23),1.67,2.48)],.014,EDGE)
  cylinder('Flexible radio antenna',(side*.9,1,2.55),(side*.9,1,4.02),.017,EDGE,r2=.007,n=10)
  for y in [-.55,.05,.65]:
   for x in [.32,.92]:bolt((side*x,y,2.62),r=.019)
 optic((.6,.23,2.86),.31,.34,PAINT,True)
 remote_station((-.48,.30,2.65),PAINT,False)
 group('01 • Hull and armor')
 # Small flush camouflage plates retain color in portable glTF without baked lighting.
 CAMO=material(title+' matte camouflage',(.11,.15,.10),.2,.82,False)
 for side in [-1,1]:
  for i in range(7):
   if i%2==0:box('Camouflage side patch',(side*1.897,-1.92+i*.66,1.26),(.014,.32,.42),CAMO,.005)
  side_text({'china':'99A','france':'LECLERC','japan':'10'}[slug],(side*1.91,.25,1.24),.16,side,WHITE)
  for i in range(4):box('Field repair link',(side*.98,1.83,1.8+i*.025),(.52,.21,.035),TRACK,.005)
 S['dynamic']=True;S['baked_indirect']=False
 bpy.data.libraries.write(OUT+'/assets/blender/'+slug+'.blend',{S},fake_user=True,compress=True)
 parts={'body':[],'turret':[]}
 for o in list(S.objects):
  if o.type in ('MESH','CURVE','FONT'):
   parts['turret' if any('03 •' in c.name for c in o.users_collection) else 'body'].append(o)
 source_count=sum(map(len,parts.values()));joined=[]
 for kind,objs in parts.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=kind
  mod=o.modifiers.new('Same game LOD as original tanks','DECIMATE');mod.ratio=.38;bpy.ops.object.modifier_apply(modifier=mod.name)
  joined.append(o)
 for o in joined:
  for mat in o.data.materials:
   if mat and mat.use_nodes:
    p=mat.node_tree.nodes.get('Principled BSDF')
    if p:
     for inp in ['Base Color','Normal']:
      for link in list(p.inputs[inp].links):mat.node_tree.links.remove(link)
     p.inputs['Base Color'].default_value=mat.diffuse_color
 bpy.ops.object.select_all(action='DESELECT')
 for o in joined:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=OUT+'/public/models/'+slug+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
 reports.append({'tank':slug,'source_objects':source_count,'game_faces':sum(len(o.data.polygons) for o in joined),'dynamic':True,'light_baked':False})
 print('COMPLETE',reports[-1],flush=True)
open(OUT+'/assets/blender/tank-report.json','w').write(json.dumps(reports,indent=2))
result=reports
