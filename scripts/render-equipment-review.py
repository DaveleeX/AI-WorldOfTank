import bpy,math,os
from mathutils import Vector
root='/Users/lee/GPT6test/wasteland_tanks'
s=bpy.data.scenes.new('Equipment review');bpy.context.window.scene=s
keys=['barrel_1','barrel_2','tracks_1','tracks_2','armor_1','armor_2','ammo_0','ammo_1','ammo_2','aircraft']
for i,key in enumerate(keys):
 before=set(s.objects);bpy.ops.import_scene.gltf(filepath=root+'/public/equipment/'+key+'.glb')
 for o in set(s.objects)-before:
  if o.parent is None:o.location+=Vector(((i%5)*7,(i//5)*10,0))
 text=bpy.data.curves.new(key,'FONT');text.body=key;text.size=.6;text.align_x='CENTER';ob=bpy.data.objects.new(key+' label',text);s.collection.objects.link(ob);ob.location=((i%5)*7,(i//5)*10-4,0)
world=bpy.data.worlds.new('Review sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.2,.24,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7;s.world=world
bpy.ops.mesh.primitive_plane_add(size=200,location=(14,5,-.2));floor=bpy.context.object;m=bpy.data.materials.new('Review floor');m.diffuse_color=(.16,.19,.21,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;floor.data.materials.append(m)
bpy.ops.object.light_add(type='AREA',location=(8,-5,18));bpy.context.object.data.energy=4200;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=15
bpy.ops.object.light_add(type='AREA',location=(20,15,14));bpy.context.object.data.energy=3000;bpy.context.object.data.size=12
bpy.ops.object.camera_add(location=(33,-33,35));camera=bpy.context.object;camera.rotation_euler=(Vector((14,4,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=43;s.camera=camera
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1700;s.render.resolution_y=1050;s.render.resolution_percentage=100;s.render.filepath=root+'/assets/equipment-review.png';bpy.ops.render.render(write_still=True)
result={'image':s.render.filepath}
