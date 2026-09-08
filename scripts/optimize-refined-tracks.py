import bpy
root='/Users/lee/GPT6test/wasteland_tanks'
def reduce():
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o.name.startswith('tracks'):
   if len(o.data.polygons)>55000:
    bpy.context.view_layer.objects.active=o
    m=o.modifiers.new('Gameplay mesh budget','DECIMATE');m.ratio=.60;bpy.ops.object.modifier_apply(modifier=m.name)
def export(path):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
for slug in ['china','france','japan','challenger','leopard','abrams']:
 path=root+'/assets/blender/refined/'+slug+'.blend';bpy.ops.wm.open_mainfile(filepath=path);reduce();bpy.ops.wm.save_as_mainfile(filepath=path);export(root+'/public/models/rigged/'+slug+'.glb')
for tier in [1,2]:
 for wheels in [5,6,7]:
  bpy.ops.wm.read_factory_settings(use_empty=True)
  path=root+f'/public/equipment/tracks_{tier}_{wheels}.glb';bpy.ops.import_scene.gltf(filepath=path);reduce();export(path)
result={'optimized':True}
