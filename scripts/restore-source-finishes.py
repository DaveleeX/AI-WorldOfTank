# Preserve original miniature geometry and authored material colors via Blender MCP.
# Only pigment is sampled; dynamic vehicles never bake direct/indirect illumination.
import bpy,math,os,json
from mathutils import Matrix,Vector
ROOT='/Users/lee/GPT6test';OUT=ROOT+'/wasteland_tanks'
rigs=[('china',OUT+'/assets/blender/china.blend',(0,-1.45,2.25)),('france',OUT+'/assets/blender/france.blend',(0,-1.47,2.25)),('japan',OUT+'/assets/blender/japan.blend',(0,-1.4,2.2)),('challenger',ROOT+'/tank_series/01_challenger2.blend',(0,-1.43,2.37)),('leopard',ROOT+'/tank_series/02_leopard2a7.blend',(0,-1.22,2.31)),('abrams',ROOT+'/tank_series/04_abramsx.blend',(0,-1.66,2.4))]
report=[]
for slug,path,hinge in rigs:
 bpy.ops.wm.open_mainfile(filepath=path);s=max(bpy.data.scenes,key=lambda s:len(s.objects));bpy.context.window.scene=s
 tip=next(o for o in s.objects if o.name.startswith('Open annular muzzle'));delta=tip.matrix_world.translation-Vector(hinge);elev=math.atan2(delta.z,-delta.y)
 parts={'body':[],'turret':[],'cannon':[],'tracks':[]}
 for o in list(s.objects):
  cs=' '.join(c.name for c in o.users_collection);n=o.name.lower()
  if o.type not in ('MESH','CURVE','FONT') or not any(k in cs for k in ['01 •','02 •','03 •','04 •']):continue
  cannon=any(n.startswith(k) for k in ['main gun','gun flexible','barrel band','bore evacuator','open annular','dark bore','thermal sleeve','raised dark barrel','sand colored gun'])
  kind='cannon' if cannon else 'tracks' if '02 •' in cs else 'turret' if '03 •' in cs or ('04 •' in cs and any(k in n for k in ['turret','basket','antenna'])) else 'body'
  parts[kind].append(o)
 joined=[]
 for kind,objs in parts.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=kind;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  mod=o.modifiers.new('Original matching game LOD','DECIMATE');mod.ratio=.38;bpy.ops.object.modifier_apply(modifier=mod.name)
  o.data.color_attributes.new(name='SourcePigment',type='FLOAT_COLOR',domain='CORNER');joined.append(o)
 # Evaluate the source shader's actual base-color graph, including original camo colors.
 outputs=[]
 for m in {m for o in joined for m in o.data.materials if m}:
  if not m.use_nodes:continue
  p=m.node_tree.nodes.get('Principled BSDF');out=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
  if not p or not out:continue
  old=[(l.from_socket,l.to_socket) for l in out.inputs['Surface'].links]
  emit=m.node_tree.nodes.new('ShaderNodeEmission');emit.inputs['Strength'].default_value=1
  if p.inputs['Base Color'].is_linked:m.node_tree.links.new(p.inputs['Base Color'].links[0].from_socket,emit.inputs['Color'])
  else:emit.inputs['Color'].default_value=p.inputs['Base Color'].default_value
  m.node_tree.links.new(emit.outputs[0],out.inputs['Surface']);outputs.append((m,p,emit,old))
 s.render.engine='CYCLES';s.cycles.samples=1;s.render.bake.target='VERTEX_COLORS';s.render.bake.use_selected_to_active=False
 bpy.ops.object.select_all(action='DESELECT')
 for o in joined:o.select_set(True)
 rebuilt=[];pigment_maps=[]
 for o in joined:
  name=o.name;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
  pieces=list(bpy.context.selected_objects)
  for part in pieces:
   bpy.ops.object.select_all(action='DESELECT');part.select_set(True);bpy.context.view_layer.objects.active=part;bpy.ops.object.material_slot_remove_unused()
   source_shader=part.active_material.node_tree.nodes.get('Principled BSDF')
   if source_shader and not source_shader.inputs['Base Color'].is_linked:
    color=source_shader.inputs['Base Color'].default_value
    for entry in part.data.color_attributes['SourcePigment'].data:entry.color=color
   else:bpy.ops.object.bake(type='EMIT')
   if any(n.type=='VALTORGB' and len(n.color_ramp.elements)>2 for n in part.active_material.node_tree.nodes):
    mat=part.active_material.copy();part.data.materials[0]=mat
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
    img=bpy.data.images.new(slug+'_'+name+'_source_pigment',width=1024,height=1024);img.colorspace_settings.name='sRGB'
    target=mat.node_tree.nodes.new('ShaderNodeTexImage');target.image=img;mat.node_tree.nodes.active=target
    s.render.bake.target='IMAGE_TEXTURES';s.render.bake.margin=8;bpy.ops.object.bake(type='EMIT');s.render.bake.target='VERTEX_COLORS'
    pigment_maps.append((part,mat,img))
  for i,part in enumerate(pieces):part.name=name+'_material_'+str(i);rebuilt.append(part)
 joined=rebuilt
 bpy.ops.object.select_all(action='DESELECT')
 for o in joined:o.select_set(True)
 for m,p,emit,old in outputs:
  m.node_tree.nodes.remove(emit)
  for a,b in old:m.node_tree.links.new(a,b)
  for inp in ['Base Color','Normal','Roughness','Metallic']:
   for link in list(p.inputs[inp].links):m.node_tree.links.remove(link)
  p.inputs['Base Color'].default_value=(1,1,1,1)
  pigment=m.node_tree.nodes.new('ShaderNodeVertexColor');pigment.layer_name='SourcePigment';m.node_tree.links.new(pigment.outputs['Color'],p.inputs['Base Color'])
 for part,mat,img in pigment_maps:
  p=mat.node_tree.nodes.get('Principled BSDF');out=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
  mat.node_tree.links.new(p.outputs[0],out.inputs['Surface'])
  for inp in ['Base Color','Normal','Roughness','Metallic']:
   for link in list(p.inputs[inp].links):mat.node_tree.links.remove(link)
  tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);img.pack()
  for entry in part.data.color_attributes['SourcePigment'].data:entry.color=(1,1,1,1)
 for o in joined:
  if o.name.startswith('cannon'):o.data.transform(Matrix.Rotation(elev,4,'X') @ Matrix.Translation(-Vector(hinge)))
 bpy.ops.export_scene.gltf(filepath=OUT+'/public/models/rigged/'+slug+'.glb',export_format='GLB',export_vertex_color='NAME',export_vertex_color_name='SourcePigment',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False)
 report.append({'model':slug,'source':path,'shape':'unscaled original geometry','finish':'source base-color graph; original camouflage pigment textures and vertex colors','lighting_baked':False})
with open(OUT+'/assets/source-style-report.json','w') as f:json.dump(report,f,indent=2)
result={'restored_source_finishes':report}
