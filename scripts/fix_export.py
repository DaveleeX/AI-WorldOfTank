import bpy
out='/Users/lee/GPT6test/wasteland_tanks/public/models/'
for slug,title in [('china','99A'),('france','Leclerc'),('japan','Type 10')]:
 s=bpy.data.scenes.get(title);bpy.context.window.scene=s
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=out+slug+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
result={'done':True}
