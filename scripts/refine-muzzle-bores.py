import bpy
root='/Users/lee/GPT6test/wasteland_tanks'
for slug in ['china','france','japan','challenger','leopard','abrams','barrel_1','barrel_2']:
 isgun=slug.startswith('barrel');path=root+('/public/equipment/' if isgun else '/public/models/rigged/')+slug+'.glb'
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=path)
 dark=bpy.data.materials.new('Recessed gun bore');dark.diffuse_color=(.003,.004,.004,1);dark.use_nodes=True;p=dark.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=dark.diffuse_color;p.inputs['Roughness'].default_value=.98
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and (isgun or o.name.startswith('cannon')):
   o.data.materials.append(dark);end=min(v.co.y for v in o.data.vertices)
   for f in o.data.polygons:
    if f.center.y<end+.025 and f.normal.y<-.7:f.material_index=len(o.data.materials)-1
 bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_apply=True)
 if not isgun:bpy.ops.wm.save_as_mainfile(filepath=root+'/assets/blender/refined/'+slug+'.blend')
result={'muzzle_bores':8}
