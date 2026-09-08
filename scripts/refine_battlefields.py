import bpy,bmesh,math,json,time
ROOT='/Users/lee/GPT6test/wasteland_tanks';reports=[]
for slug in ['desert','city','mud','snow']:
 s=bpy.data.scenes.get('IRON FRONT static '+slug);bpy.context.window.scene=s;static=next(o for o in s.objects if o.type=='MESH')
 bm=bmesh.new();bm.from_mesh(static.data)
 dead=[]
 for f in bm.faces:
  c=f.calc_center_median()+static.location;m=static.data.materials[f.material_index]
  if 'Sedimentary rock' in m.name and math.hypot(c.x,c.y)>205:dead.append(f)
 bmesh.ops.delete(bm,geom=dead,context='FACES');bm.to_mesh(static.data);bm.free()
 # A continuous eroded mountain belt, with far denser silhouette than primitive props.
 vs=[];fs=[];N=192;R=26
 for j in range(R+1):
  q=j/R;r=206+q*210
  for i in range(N):
   a=i/N*math.tau
   profile=math.sin(q*math.pi)**1.45
   ridge=39+16*math.sin(a*5+.4)+11*math.sin(a*11)+6*math.sin(a*19+q*8)
   z=profile*ridge+profile*3*math.sin(a*61+q*31)
   vs.append((r*math.sin(a),r*math.cos(a),z-.2))
 for j in range(R):
  for i in range(N):
   ni=(i+1)%N;fs.append((j*N+i,(j+1)*N+i,(j+1)*N+ni,j*N+ni))
 me=bpy.data.meshes.new('Eroded continuous mountain terrain');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('Continuous atmospheric ridgeline',me);s.collection.objects.link(ob)
 stone=next(m for m in static.data.materials if 'Sedimentary rock' in m.name);me.materials.append(stone)
 for p in me.polygons:p.use_smooth=True
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);static.select_set(True);bpy.context.view_layer.objects.active=static;bpy.ops.object.join()
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.003,area_weight=.65);bpy.ops.object.mode_set(mode='OBJECT')
 # World-scale procedural staining is authored in Blender, then baked to an albedo atlas.
 for m in static.data.materials:
  n=m.node_tree.nodes;links=m.node_tree.links;p=n.get('Principled BSDF');base=m.diffuse_color[:3]
  coord=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.22;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.75;links.new(coord.outputs['Position'],noise.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*(v*.48 for v in base),1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*(min(1,v*1.25) for v in base),1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=7;fine.inputs['Detail'].default_value=2;links.new(coord.outputs['Position'],fine.inputs['Vector']);links.new(fine.outputs['Fac'],bump.inputs['Height']);bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.025;links.new(bump.outputs[0],p.inputs['Normal'])
 s.cycles.samples=16;s.cycles.use_denoising=True;s.render.bake.margin=8
 for suffix,indirect in [('albedo',False),('indirect',True)]:
  img=bpy.data.images.new(slug+'_'+suffix+'_final',width=2048,height=2048,alpha=False);img.colorspace_settings.name='Linear Rec.709' if indirect else 'sRGB'
  for m in static.data.materials:
   n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=img;m.node_tree.nodes.active=n
  s.render.bake.use_pass_direct=False;s.render.bake.use_pass_indirect=indirect;s.render.bake.use_pass_color=not indirect
  bpy.ops.object.bake(type='DIFFUSE');img.filepath_raw=ROOT+'/public/maps/'+slug+'-'+suffix+'.png';img.file_format='PNG';img.save();img.pack()
 # Keep authored procedural shaders in the .blend; portable runtime uses the albedo atlas.
 bpy.data.libraries.write(ROOT+'/assets/blender/'+slug+'-world.blend',{s},fake_user=True,compress=True)
 for m in static.data.materials:
  p=m.node_tree.nodes.get('Principled BSDF')
  for name in ['Base Color','Normal']:
   for link in list(p.inputs[name].links):m.node_tree.links.remove(link)
  p.inputs['Base Color'].default_value=m.diffuse_color
 bpy.ops.export_scene.gltf(filepath=ROOT+'/public/maps/'+slug+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
 reports.append({'map':slug,'faces':len(static.data.polygons),'bake':'Cycles diffuse indirect only + separate albedo','resolution':2048,'samples':16,'dynamic_objects':0,'continuous_ridge':True})
 open(ROOT+'/assets/blender/bake-report-final.json','w').write(json.dumps(reports,indent=2));print('REFINED',slug,flush=True)
result=reports
