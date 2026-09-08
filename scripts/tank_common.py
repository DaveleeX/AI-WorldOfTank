import bpy, math, random
from mathutils import Vector, Matrix
from math import sin, cos, pi
from pathlib import Path
ROOT='/Users/lee/GPT6test/tank_series'
S=None; C=None; PARTS={}; SEED=12

def group(name):
 global C
 if name not in PARTS:
  C=bpy.data.collections.new(name);S.collection.children.link(C);PARTS[name]=C
 else:C=PARTS[name]
 return C

def material(name,col,metal=.2,rough=.76,texture=True):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=37;t.inputs['Detail'].default_value=3
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(x*.88 for x in col),1);ramp.color_ramp.elements[1].color=(*(min(1,x*1.08) for x in col),1)
  m.node_tree.links.new(t.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs[0],p.inputs['Base Color'])
  b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.012;m.node_tree.links.new(t.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs[0],p.inputs['Normal'])
 return m

def camouflage(name,cols):
 m=material(name,cols[0]);n=m.node_tree.nodes;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=1.65;t.inputs['Detail'].default_value=1.1;t.inputs['Roughness'].default_value=.63
 tc=n.new('ShaderNodeTexCoord');anchor=bpy.data.objects.new(name+' world pattern origin',None);C.objects.link(anchor);tc.object=anchor
 mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,1,.68)
 m.node_tree.links.new(tc.outputs['Object'],mapping.inputs[0]);m.node_tree.links.new(mapping.outputs[0],t.inputs['Vector'])
 r=n.new('ShaderNodeValToRGB');r.color_ramp.interpolation='CONSTANT';r.color_ramp.elements.remove(r.color_ramp.elements[1]);r.color_ramp.elements[0].position=0;r.color_ramp.elements[0].color=(*cols[0],1)
 for pos,col in zip([.44,.60],cols[1:]):r.color_ramp.elements.new(pos).color=(*col,1)
 m.node_tree.links.new(t.outputs['Fac'],r.inputs[0]);m.node_tree.links.new(r.outputs[0],p.inputs['Base Color']);return m

def mesh(name,verts,faces,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o)
 if ma:o.data.materials.append(ma)
 return o

def bevel(o,w=.035):
 if w:
  b=o.modifiers.new('Rounded miniature edges','BEVEL');b.width=w;b.segments=3
  b=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');b.keep_sharp=True;b.weight=35
 return o

def box(name,loc,dim,ma,b=.025):
 x,y,z=[v/2 for v in dim];verts=[(a*x,c*y,d*z) for a,c,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 o=mesh(name,verts,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],ma);o.location=loc;return bevel(o,b)

def cylinder(name,a,b,r,ma,r2=None,n=32,soft=False):
 a=Vector(a);b=Vector(b);d=b-a;r2=r if r2 is None else r2
 vs=[(rad*cos(2*pi*i/n),rad*sin(2*pi*i/n),z) for z,rad in [(-d.length/2,r),(d.length/2,r2)] for i in range(n)]
 o=mesh(name,vs,[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],ma);o.location=(a+b)/2;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y')
 if soft:
  for p in o.data.polygons:
   if len(p.vertices)==4:p.use_smooth=True
 return o

def sphere(name,loc,scale,ma,n=20,rings=12):
 vs=[(scale[0]*sin(pi*j/rings)*cos(2*pi*i/n),scale[1]*sin(pi*j/rings)*sin(2*pi*i/n),scale[2]*cos(pi*j/rings)) for j in range(rings+1) for i in range(n)]
 fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(rings) for i in range(n)]
 o=mesh(name,vs,fs,ma);o.location=loc
 for p in o.data.polygons:p.use_smooth=True
 return o

def pipe(name,points,r,ma):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);C.objects.link(o);o.data.materials.append(ma);return o

def prism(name,pts,width,ma,x=0,b=.025):
 n=len(pts);o=mesh(name,[(xx,y,z) for xx in [-width/2,width/2] for y,z in pts],[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],ma);o.location.x=x;return bevel(o,b)

def loft(name,outline,z0,z1,ma,topscale=(1,1),offset=(0,0),b=.035):
 n=len(outline);vs=[(x,y,z0) for x,y in outline]+[(x*topscale[0]+offset[0],y*topscale[1]+offset[1],z1) for x,y in outline]
 return bevel(mesh(name,vs,[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],ma),b)

def bolt(loc,axis=(0,0,1),r=.021,ma=None):
 v=Vector(axis)*.018;return cylinder('Armor bolt',Vector(loc)-v*.25,Vector(loc)+v,r,ma or EDGE,n=6)

def handle(loc,axis='X',width=.19,ma=None):
 x,y,z=loc
 if axis=='X':pts=[(x-width/2,y,z),(x-width/2,y,z+.055),(x+width/2,y,z+.055),(x+width/2,y,z)]
 else:pts=[(x,y-width/2,z),(x,y-width/2,z+.055),(x,y+width/2,z+.055),(x,y+width/2,z)]
 return pipe('Grab handle',pts,.012,ma or EDGE)

def front_text(text,loc,size,ma=None):
 cu=bpy.data.curves.new(text,'FONT');cu.body=text;cu.size=size;cu.align_x='CENTER';cu.extrude=.0005
 o=bpy.data.objects.new(text,cu);C.objects.link(o);o.location=loc;o.rotation_euler=(pi/2,0,0);o.data.materials.append(ma or WHITE);return o

def side_text(text,loc,size,side=-1,ma=None):
 o=front_text(text,loc,size,ma)
 o.rotation_euler=Matrix(((0,0,side),(side,0,0),(0,1,0))).to_euler();return o

def setup(slug,title,seed,col):
 global S,C,PARTS,PAINT,EDGE,TRACK,PAD,DARK,GLASS,WHITE,RED,LENS,STEEL
 random.seed(seed);PARTS={};S=bpy.data.scenes.new(title);bpy.context.window.scene=S;group('01 • Hull and armor')
 PAINT=material(title+' | painted armor',col);EDGE=material(title+' | edge metal',tuple(v*.72 for v in col),.45)
 TRACK=material(title+' | steel track links',(.075,.078,.067),.68,.72);PAD=material(title+' | rubber',(.028,.032,.030),.05,.89)
 DARK=material(title+' | cavity shadow',(.008,.011,.013),.25,.45,False);GLASS=material(title+' | optical blue glass',(.042,.17,.205),.7,.2,False)
 WHITE=material(title+' | ivory lettering',(.83,.83,.76),0,.74,False);RED=material(title+' | hub red',(.32,.074,.034),.25)
 STEEL=material(title+' | bare hardware',(.25,.27,.25),.8,.42)
 LENS=material(title+' | warm headlamp',(.9,.82,.53),.2,.21,False);p=LENS.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.78,.4,1);p.inputs['Emission Strength'].default_value=.45
 S['output_slug']=slug;S['style']='Same rounded, matte painted miniature style as the accepted first tank. Distinct photo-inspired exterior, inferred unseen details.'
 return S

def chassis(wheels=6,skirts='panels',paint=None):
 ma=paint or PAINT;group('01 • Hull and armor')
 prism('Sloped lower hull',[(-2.37,.65),(-2.53,1.10),(-1.8,1.53),(2.16,1.44),(2.3,.68)],2.7,ma)
 prism('Upper hull with glacis',[(-2.58,1.13),(-1.68,1.69),(1.92,1.69),(2.43,1.43),(2.43,1.18)],2.91,ma,b=.045)
 for side in [-1,1]:
  prism('Broad track fender',[(-2.48,1.35),(-2.1,1.61),(2.45,1.61),(2.46,1.45)],.68,ma,x=side*1.51)
  if skirts=='panels':
   for i in range(7):
    yy=-1.93+i*.66
    box('Segmented side armor',(side*1.824,yy,1.25),(.12,.635,.71),ma,.03)
    for y in [yy-.26,yy+.26]:bolt((side*1.893,y,1.49),(side,0,0),.02)
  if skirts=='deep':
   for i in range(7):
    yy=-1.95+i*.65
    box('Deep armored skirt',(side*1.83,yy,1.20),(.17,.627,.96),ma,.035)
    box('Flexible bottom skirt',(side*1.84,yy,.67),(.07,.63,.30),ma,.018)
    for z in [.77,1.57]:bolt((side*1.924,yy,z),(side,0,0),.022)
  # lifting eyes and rear deck ventilation
  for yy in [-1.5,1.4,2.05]:handle((side*1.4,yy,1.72),axis='Y')
 for x in [-.83,.83]:
  for i in range(11):box('Engine grille louver',(x,.96+i*.093,1.735),(.6,.045,.026),EDGE,.006)
 box('Driver roof hatch',(0,-1.22,1.735),(.74,.62,.095),ma,.08)
 box('Driver periscope bezel',(0,-1.50,1.82),(.45,.12,.13),EDGE)
 box('Driver glass strip',(0,-1.567,1.83),(.35,.014,.068),GLASS,.007)
 handle((0,-1.08,1.80))
 group('02 • Tracks and running gear')
 R=.60;L=1.81;zc=.70;total=4*L+2*pi*R;count=78
 def path(t):
  if t<2*L:return -L+t,zc+R,0
  t-=2*L
  if t<pi*R:
   a=t/R;return L+R*sin(a),zc+R*cos(a),-a
  t-=pi*R
  if t<2*L:return L-t,zc-R,pi
  t-=2*L;a=pi+t/R;return -L+R*sin(a),zc+R*cos(a),-a
 for side in [-1,1]:
  x=side*1.49
  for i in range(count):
   yy,zz,a=path(total*i/count)
   o=box('Track shoe %s %02d'%(side,i),(x,yy,zz),(.64,total/count*.9,.074),TRACK,.009);o.rotation_euler.x=a
   # correct outward normal from the tangent frame
   for dx in [-.15,.15]:
    o=box('Twin rubber traction pad',(x+dx,yy-sin(a)*.048,zz+cos(a)*.048),(.24,total/count*.65,.025),PAD,.007);o.rotation_euler.x=a
   for dx in [-.302,.302]:cylinder('Track hinge pin',(x+dx-.021,yy,zz),(x+dx+.021,yy,zz),.033,STEEL,n=10)
  for j in range(wheels):
   yy=-1.55+j*3.1/(wheels-1);rad=.425 if wheels==6 else .367
   cylinder('Road wheel tire',(x-.26,yy,.56),(x+.26,yy,.56),rad,PAD,n=40,soft=True)
   xo=x+side*.27
   cylinder('Dish wheel outer lip',(xo-side*.035,yy,.56),(xo,yy,.56),rad*.87,EDGE,n=40,soft=True)
   cylinder('Pressed wheel dish',(xo,yy,.56),(xo+side*.017,yy,.56),rad*.77,ma,r2=rad*.68,n=40,soft=True)
   cylinder('Axle hub',(xo+side*.015,yy,.56),(xo+side*.095,yy,.56),rad*.23,ma,n=24,soft=True)
   for k in range(8):
    a=k*pi/4;bolt((xo+side*.022,yy+rad*.47*cos(a),.56+rad*.47*sin(a)),(side,0,0),.012,EDGE)
  for yy in [-L,L]:
   xo=x+side*.275
   cylinder('Track end wheel',(x-.25,yy,zc),(x+.25,yy,zc),.51,TRACK,n=40)
   cylinder('End wheel face',(xo-side*.03,yy,zc),(xo,yy,zc),.435,ma,n=40)
   cylinder('End wheel hub',(xo,yy,zc),(xo+side*.05,yy,zc),.125,EDGE,n=24)
   for k in range(8):
    a=k*pi/4;cylinder('End wheel hole',(xo+side*.001,yy+.29*cos(a),zc+.29*sin(a)),(xo+side*.004,yy+.29*cos(a),zc+.29*sin(a)),.058,DARK,n=12)
  # shadowed running gear mounting wall
  box('Interior suspension wall',(x-side*.22,0,.99),(.14,3.6,.3),PAD)
 group('01 • Hull and armor')
 for x in [-1.15,1.15]:
  box('Front headlamp body',(x,-2.075,1.475),(.31,.16,.19),EDGE)
  box('Headlamp glass',(x,-2.16,1.485),(.225,.02,.115),LENS,.026)
  pipe('Headlamp protective hoop',[(x-.2,-2.2,1.40),(x-.2,-2.2,1.63),(x+.2,-2.2,1.63),(x+.2,-2.2,1.40)],.018,EDGE)
 for x in [-.87,.87]:
  pipe('Front towing shackle',[(x-.1,-2.4,.91),(x-.1,-2.55,.91),(x+.1,-2.55,.91),(x+.1,-2.4,.91)],.04,EDGE)
 for x in [-1.25,-.83,-.42,0,.42,.83,1.25]:bolt((x,-2.18,1.36),(0,-.6,.8),.023)

def turret_base(ma=None):
 group('03 • Turret and main gun');cylinder('Black turret rotation gap',(0,.14,1.66),(0,.14,1.79),1.2,PAD,n=64)
 cylinder('Turret bearing metal rim',(0,.14,1.75),(0,.14,1.82),1.16,ma or PAINT,n=64)

def gun(root=(0,-1.15,2.24),length=3.3,elev=.13,sleeve=False,ma=None):
 ma=ma or PAINT;root=Vector(root);d=Vector((0,-cos(elev),sin(elev)))
 cylinder('Gun flexible root boot',root-d*.06,root+d*.27,.245,PAD,r2=.19,n=48,soft=True)
 cylinder('Main gun thermal shroud',root+d*.20,root+d*length,.128,ma,r2=.087,n=48,soft=True)
 cylinder('Bore evacuator',root+d*(length*.40),root+d*(length*.57),.178,ma,r2=.164,n=48,soft=True)
 for t in [.28,.65,1.07,1.64,2.10,length-.14]:
  if t<length:
   cylinder('Barrel band',root+d*t,root+d*(t+.035),.137 if t<length*.58 else .109,EDGE,n=40)
 if sleeve:
  for ang in [0,pi/2,pi,3*pi/2]:
   u=Vector((cos(ang),sin(ang)*sin(elev),sin(ang)*cos(elev)))
   pipe('Thermal sleeve seam',[root+d*.3+u*.13,root+d*(length-.05)+u*.096],.012,EDGE)
 # annular muzzle plus a recessed interior, not a plugged cylinder
 r=.101;inner=.071;end=root+d*length
 verts=[(rad*cos(2*pi*i/48),rad*sin(2*pi*i/48),zz) for zz,rad in [(0,r),(0,inner),(-.20,inner)] for i in range(48)]
 faces=[(i,(i+1)%48,(i+1)%48+48,i+48) for i in range(48)]+[(48+i,48+(i+1)%48,96+(i+1)%48,96+i) for i in range(48)]
 o=mesh('Open annular muzzle',verts,faces,STEEL);o.location=end;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y')
 cylinder('Dark bore depth',end-d*.21,end-d*.208,inner,DARK,n=40)
 return root,d

def optic(loc,width=.32,height=.32,ma=None,twolens=False):
 x,y,z=loc;ma=ma or PAINT
 box('Rounded armored optical housing',(x,y,z),(width,.30,height),ma,.045)
 box('Optical dark recess',(x,y-.158,z),(width*.76,.015,height*.68),DARK,.022)
 if twolens:
  for dx in [-width*.18,width*.18]:
   cylinder('Optical lens rim',(x+dx,y-.17,z),(x+dx,y-.187,z),width*.135,STEEL,n=32)
   cylinder('Blue optical lens',(x+dx,y-.189,z),(x+dx,y-.191,z),width*.10,GLASS,n=32)
 else:box('Optical glass',(x,y-.17,z),(width*.56,.01,height*.48),GLASS,.015)
 box('Optics rain eyebrow',(x,y-.02,z+height*.51),(width+.03,.35,.035),EDGE,.009)

def cupola(x,y,z,ma=None):
 ma=ma or PAINT;cylinder('Commander cupola',(x,y,z),(x,y,z+.14),.34,ma,n=48)
 cylinder('Cupola lid',(x,y,z+.14),(x,y,z+.2),.315,ma,n=48);handle((x,y,z+.21))
 for a in range(6):
  t=a*pi/3;ob=box('Cupola periscope',(x+.285*cos(t),y+.285*sin(t),z+.11),(.11,.07,.06),GLASS,.009);ob.rotation_euler.z=t+pi/2

def antenna(x,y,z,height=1.2):
 cylinder('Antenna base',(x,y,z),(x,y,z+.11),.055,EDGE,n=20)
 pipe('Slender whip aerial',[(x,y,z+.1),(x+.014,y,z+height*.65),(x+.03,y+.02,z+height)],.007,TRACK)

def smoke_cluster(x,y,z,side,count=4):
 for i in range(count):
  a=Vector((x+(i-(count-1)/2)*.085,y+abs(i-(count-1)/2)*.025,z));d=Vector((side*(.17+(i-(count-1)/2)*.09),-.20,.26))
  cylinder('Smoke discharger tube',a,a+d,.065,EDGE,n=20);cylinder('Smoke tube dark cap',a+d,a+d*1.014,.051,PAD,n=20)
 box('Smoke launcher mounting bracket',(x,y+.045,z-.04),(.36,.13,.1),PAINT)

def remote_station(loc,ma=None,heavy=False):
 x,y,z=loc;ma=ma or PAINT
 cylinder('Remote weapon turntable',(x,y,z),(x,y,z+.10),.24,ma,n=40)
 box('Remote station pedestal',(x,y,z+.31),(.27,.28,.43),ma,.035)
 box('Remote weapon receiver',(x,y-.14,z+.60),(.20,.54,.18),TRACK)
 cylinder('Remote weapon barrel',(x,y-.4,z+.61),(x,y-1.02,z+.66),.032,TRACK,r2=.022,n=24)
 cylinder('Remote barrel tip',(x,y-1.02,z+.66),(x,y-1.07,z+.665),.029,DARK,n=20)
 box('Remote ammunition box',(x+.22,y,z+.58),(.24,.31,.25),ma)
 optic((x-.23,y-.14,z+.54),.21,.28,ma,True)
 if heavy:
  for dx in [-.35,.35]:box('Remote armored side shield',(x+dx,y+.04,z+.63),(.065,.40,.51),ma)
  # arched articulated feed belt
  pts=[(x+.33,y+.05-.13*sin(t*pi/24),z+.63+.46*sin(t*pi/24)) for t in range(25)]
  for i,p in enumerate(pts):
   ob=box('Ammunition feed belt link',p,(.14,.06,.045),STEEL,.006);ob.rotation_euler.x=pi*i/24

def environment(slug,title,desert=True,cam_side=-1,target_z=1.57):
 group('05 • Miniature display environment')
 soil=material(title+' | sandy earth',(.32,.265,.16) if desert else (.24,.265,.22),0,.96)
 concrete=material(title+' | warm concrete',(.45,.42,.33),0,.91)
 box('Matte outdoor ground',(0,0,-.12),(200,200,.14),soil,0)
 box('Thin display slab',(0,-.20,-.005),(4.35,5.4,.13),concrete,.055)
 grass=material(title+' | dry grass',(.30,.27,.14) if desert else (.2,.25,.12),0,.95)
 vs=[];fs=[]
 for i in range(4000):
  x=random.uniform(-15,15);y=random.uniform(-15,15)
  if abs(x)<2.25 and abs(y+.2)<2.8:continue
  h=random.uniform(.03,.12);w=.013;k=len(vs);vs.extend([(x-w,y,0),(x+w,y,0),(x+.02,y+.008,h)]);fs.append((k,k+1,k+2))
 mesh('Sparse stylized grass',vs,fs,grass)
 # Camera intentionally has the same miniature presentation as the first model.
 camdata=bpy.data.cameras.new(title+' camera');cam=bpy.data.objects.new(title+' camera',camdata);C.objects.link(cam);cam.location=(cam_side*8.5,-10.6,5.4);cam.rotation_euler=(Vector((0,-.62,target_z))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=49;S.camera=cam
 world=bpy.data.worlds.new(title+' soft blue sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.50,.70,.93,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;S.world=world
 ld=bpy.data.lights.new(title+' sun','SUN');o=bpy.data.objects.new(title+' sun',ld);C.objects.link(o);o.rotation_euler=(.45,-.4,-.35);ld.energy=2.5;ld.angle=.14
 ld=bpy.data.lights.new(title+' soft sky fill','AREA');o=bpy.data.objects.new(title+' soft sky fill',ld);C.objects.link(o);o.location=(-4,-6,8);o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler();ld.energy=650;ld.shape='DISK';ld.size=7
 S.render.engine='CYCLES';S.cycles.samples=40;S.cycles.use_denoising=True;S.render.resolution_x=1400;S.render.resolution_y=1050;S.render.resolution_percentage=75;S.view_settings.view_transform='AgX';S.render.image_settings.file_format='PNG';S.render.filepath=ROOT+'/'+slug+'.png'

def finish(slug,ref):
 img=bpy.data.images.load(ref,check_existing=True);img.pack()
 group('06 • Reference image')
 o=bpy.data.objects.new('Original user photo — viewport reference',None);C.objects.link(o);o.empty_display_type='IMAGE';o.data=img;o.hide_render=True;o.hide_viewport=True
 S['original_reference']=ref
 for a in bpy.context.screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.color_type='MATERIAL'
 # Each library contains exactly this model scene and its dependencies.
 bpy.data.libraries.write(ROOT+'/'+slug+'.blend',{S},fake_user=True,compress=True)
 bpy.ops.render.render(write_still=True)
 result={'scene':S.name,'objects':len(S.objects),'blend':ROOT+'/'+slug+'.blend','render':S.render.filepath}
 print(result)
 return result
