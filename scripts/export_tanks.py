import bpy, os
ROOT='/Users/lee/GPT6test'
for slug,out in [('01_challenger2','challenger'),('02_leopard2a7','leopard'),('04_abramsx','abrams')]:
 bpy.ops.wm.open_mainfile(filepath=f'{ROOT}/tank_series/{slug}.blend')
 scene=next((s for s in bpy.data.scenes if any('01 • Hull' in c.name for c in s.collection.children)),bpy.context.scene)
 bpy.context.window.scene=scene
 parts={'body':[],'turret':[]}
 for o in list(scene.objects):
  cs=' '.join(c.name for c in o.users_collection)
  if o.type not in ('MESH','CURVE','FONT') or not any(x in cs for x in ['01 •','02 •','03 •','04 •']):continue
  kind='turret' if '03 •' in cs or ('04 •' in cs and any(w in o.name.lower() for w in ['turret','basket','antenna'])) else 'body'
  parts[kind].append(o)
 bpy.ops.object.select_all(action='DESELECT')
 joined=[]
 for kind,objs in parts.items():
  for o in objs:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0]
  bpy.ops.object.convert(target='MESH')
  bpy.ops.object.join();o=bpy.context.object;o.name=kind
  mod=o.modifiers.new('Game LOD','DECIMATE');mod.ratio=.38
  bpy.ops.object.modifier_apply(modifier=mod.name)
  joined.append(o);bpy.ops.object.select_all(action='DESELECT')
 for mat in bpy.data.materials:
  if mat.use_nodes:
   p=mat.node_tree.nodes.get('Principled BSDF')
   if p:
    for inp in ['Base Color','Normal','Roughness','Metallic']:
     for link in list(p.inputs[inp].links):mat.node_tree.links.remove(link)
    p.inputs['Base Color'].default_value=mat.diffuse_color
 for o in joined:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=f'{ROOT}/wasteland_tanks/public/models/{out}.glb',export_format='GLB',use_selection=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 print('EXPORTED',out,len(parts['body']),len(parts['turret']))
