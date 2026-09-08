import bpy,json
root='/Users/lee/GPT6test/wasteland_tanks'
for slug in ['china','france','japan','challenger','leopard','abrams']:
 bpy.ops.wm.open_mainfile(filepath=root+'/assets/blender/refined/'+slug+'.blend')
 for m in bpy.data.materials:
  if m.use_nodes:
   p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   if p and p.inputs['Base Color'].is_linked:
    for l in list(p.inputs['Base Color'].links):m.node_tree.links.remove(l)
    p.inputs['Base Color'].default_value=m.diffuse_color
 bpy.ops.wm.save_as_mainfile(filepath=root+'/assets/blender/refined/'+slug+'.blend')
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=root+'/public/models/rigged/'+slug+'.glb',export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
result={'materials':'fixed procedural base colors on all six refined models'}
