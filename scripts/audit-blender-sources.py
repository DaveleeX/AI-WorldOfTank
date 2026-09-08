import bpy,json,os
root='/Users/lee/GPT6test/wasteland_tanks'
report=[]
for slug in ['china','france','japan']:
 bpy.ops.wm.open_mainfile(filepath=root+'/assets/blender/'+slug+'.blend')
 report.append({'tank':slug,'meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'file':bpy.data.filepath})
for slug in ['desert','city','mud','snow']:
 bpy.ops.wm.open_mainfile(filepath=root+'/assets/worlds/'+slug+'.blend')
 s=bpy.context.scene;b=s.render.bake
 report.append({'map':slug,'engine':s.render.engine,'indirect':b.use_pass_indirect,'direct':b.use_pass_direct,'color':b.use_pass_color,'dynamic_meshes':[o.name for o in s.objects if any(k in o.name.lower() for k in ['turret','projectile','tank_body'])]})
with open(root+'/assets/source-audit.json','w') as f:json.dump(report,f,indent=2)
result={"assets":report}
