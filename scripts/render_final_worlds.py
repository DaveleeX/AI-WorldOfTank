import bpy
exec(open('/Users/lee/GPT6test/wasteland_tanks/scripts/render_asset_review.py').read().split("s=bpy.data.scenes.new('Six nation")[0])
for slug in ['desert','city','mud','snow']:
 with bpy.data.libraries.load(ROOT+'/assets/worlds/'+slug+'.blend',link=False) as (a,b):b.scenes=a.scenes
 s=b.scenes[0];bpy.context.window.scene=s
 camera(s,(13,156,10),(0,60,2));s.render.filepath=ROOT+'/public/battlefields/'+slug+'-preview.png';bpy.ops.render.render(write_still=True)
