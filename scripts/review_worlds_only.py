import bpy,os
src=open('/Users/lee/GPT6test/wasteland_tanks/scripts/render_asset_review.py').read();exec(src[:src.index("s=bpy.data.scenes.new('Six nation")])
for slug in ['desert','city','mud','snow']:
 path=ROOT+'/assets/blender/'+slug+'-world.blend'
 if not os.path.exists(path):continue
 if os.path.exists(ROOT+'/public/maps/'+slug+'-preview.png'):continue
 with bpy.data.libraries.load(path,link=False) as (a,b):b.scenes=a.scenes
 s=b.scenes[0];bpy.context.window.scene=s
 camera(s,(13,156,10),(0,60,2));s.render.filepath=ROOT+'/public/maps/'+slug+'-preview.png';bpy.ops.render.render(write_still=True)
