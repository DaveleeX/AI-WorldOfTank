import bpy,math,json
from mathutils import Vector
ROOT='/Users/lee/GPT6test/wasteland_tanks'
def camera(s,loc,target,res=(1100,700)):
 c=bpy.data.cameras.new('Review camera');o=bpy.data.objects.new('Review camera',c);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();c.lens=40;s.camera=o
 s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
s=bpy.data.scenes.new('Six nation new model review');bpy.context.window.scene=s
for i,slug in enumerate(['china','france','japan']):
 with bpy.data.libraries.load(ROOT+'/assets/blender/'+slug+'.blend',link=False) as (a,b):b.scenes=a.scenes
 original=b.scenes[0]
 for obj in original.objects:
  if obj.type in ['MESH','CURVE','FONT']:
   o=obj.copy();s.collection.objects.link(o);o.location.x+=(i-1)*6.3
w=bpy.data.worlds.new('Review sky');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);w.node_tree.nodes['Background'].inputs[1].default_value=.6;s.world=w
l=bpy.data.lights.new('Review sun','SUN');l.energy=3;l.angle=.2;o=bpy.data.objects.new('Review sun',l);s.collection.objects.link(o);o.rotation_euler=(.5,-.4,-.3)
camera(s,(12,-20,11),(0,-.4,1.5),(1500,700));s.render.filepath=ROOT+'/assets/blender/tanks-review.png';bpy.ops.render.render(write_still=True)
for slug in ['desert','city','mud','snow']:
 s=bpy.data.scenes.get('IRON FRONT static '+slug);bpy.context.window.scene=s
 camera(s,(13,156,10),(0,60,2));s.render.filepath=ROOT+'/public/maps/'+slug+'-preview.png';bpy.ops.render.render(write_still=True)
result={'review':'complete'}
