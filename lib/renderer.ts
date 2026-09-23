// @ts-nocheck
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import {BuildingDestruction,partitionBuildings} from './destruction.mjs';
import { TANKS, MAPS, makeObstacles } from './battle.mjs';
import { gunSpec, muzzle } from './ballistics.mjs';
const UP=new THREE.Vector3(0,1,0);
export class TankRenderer {
 constructor(host,onError){this.host=host;this.onError=onError;this.models=new Map();this.equipment={};this.focus=null;this.lookTarget=new THREE.Vector3(0,1.4,0);this.entities=new Map();this.effects=[];this.loaded={};this.mapAssets={};this.mapToken=0;this.cameraReady=false;this.active=true;this.tick=0;this.shotMeshes=[];this.scene=new THREE.Scene();this.camera=new THREE.PerspectiveCamera(47,1,.15,1100);this.camera.position.set(10,5.3,12.7);this.renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.25;host.appendChild(this.renderer.domElement);this.renderer.domElement.setAttribute('aria-label','三维坦克战场');this.world=new THREE.Group();this.scene.add(this.world);this.sun=new THREE.DirectionalLight(0xffd5a0,3.4);this.sun.position.set(-60,95,50);this.sun.castShadow=true;this.sun.shadow.mapSize.set(2048,2048);Object.assign(this.sun.shadow.camera,{left:-95,right:95,top:95,bottom:-95,near:1,far:240});this.sun.shadow.bias=-.001;this.sun.shadow.normalBias=.08;this.scene.add(this.sun,this.sun.target);this.hemi=new THREE.HemisphereLight(0xb6ccdc,0x4c3f2b,1.6);this.hemi.layers.set(1);this.camera.layers.enable(1);this.scene.add(this.hemi);this.fill=new THREE.DirectionalLight(0x83bad4,0);this.fill.position.set(20,12,-30);this.fill.layers.set(1);this.scene.add(this.fill);this.resize=()=>{let w=host.clientWidth,h=host.clientHeight;this.renderer.setSize(w,h);this.camera.aspect=w/h;this.camera.updateProjectionMatrix()};this.observer=new ResizeObserver(this.resize);this.observer.observe(host);this.resize();this.buildMap(0,true);this.setTank(0);this.ready=Promise.all([
 ...TANKS.map(async d=>{let g=await new GLTFLoader().loadAsync('/models/rigged/'+d.model+'.glb');if(!this.active){this.disposeObject(g.scene);return;}this.loaded[d.model]=g.scene;}),
 ...['barrel_1','barrel_2','tracks_1','tracks_2','armor_1','armor_2','ammo_0','ammo_1','ammo_2','aircraft'].map(async key=>{const g=await new GLTFLoader().loadAsync('/equipment/'+key+'.glb');if(!this.active){this.disposeObject(g.scene);return;}this.equipment[key]=g.scene;})
 ]).then(()=>{if(this.active&&this.mode==='garage')this.setTank(this.selected);}).catch(e=>{this.onError('坦克与装备资源加载失败，请刷新重试。');throw e;});}

 mat(color,metal=.1,rough=.85){return new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough});}
 mesh(geometry,material,parent,x=0,y=0,z=0){let m=new THREE.Mesh(geometry,material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
 box(parent,w,h,d,x,y,z,mat){return this.mesh(new THREE.BoxGeometry(w,h,d),mat,parent,x,y,z);}
 cloneAsset(source){if(!source)return new THREE.Group();const root=source.clone(true);root.traverse(o=>{if(o.isMesh){o.geometry=o.geometry.clone();o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone();o.castShadow=true;o.receiveShadow=true;o.layers.enable(1);}});return root;}
 tank(def,gear={}){
 const root=new THREE.Group(),body=new THREE.Group(),turret=new THREE.Group(),cannon=new THREE.Group(),tracks=new THREE.Group();root.add(body,turret);body.add(tracks);turret.add(cannon);
 const spec=gunSpec(def.model,gear.barrel);cannon.position.set(0,spec.height,spec.fore);
 const source=this.loaded[def.model];if(source){source.updateMatrixWorld(true);source.traverse(o=>{if(!o.isMesh)return;let n=o,kind='body';while(n){for(const k of ['cannon','turret','tracks','body'])if(n.name.startsWith(k)){kind=k;break;}if(kind!=='body'||n.name.startsWith('body'))break;n=n.parent;}
 if(kind==='cannon'&&gear.barrel||kind==='tracks'&&gear.tracks)return;
 const part=o.clone();part.geometry=o.geometry.clone();part.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone();part.applyMatrix4(o.parent.matrixWorld);part.castShadow=true;part.receiveShadow=true;({body,turret,cannon,tracks})[kind].add(part);});}
 if(gear.barrel)cannon.add(this.cloneAsset(this.equipment?.['barrel_'+gear.barrel]));
 if(gear.tracks)tracks.add(this.cloneAsset(this.equipment?.['tracks_'+gear.tracks]));
 if(gear.armor)body.add(this.cloneAsset(this.equipment?.['armor_'+gear.armor]));
 if(gear.ammo){const rack=this.cloneAsset(this.equipment?.['ammo_'+gear.ammo]);rack.scale.setScalar(.38);rack.position.set(.8,1.7,-1.5);body.add(rack);}
 root.traverse(o=>{if(o.isMesh)o.layers.enable(1)});root.userData={turret,body,cannon,tracks,spec};return root;
 }
 mergeParts(group){let batches=new Map();for(let m of [...group.children]){if(!m.isMesh)continue;m.updateMatrix();let g=m.geometry.clone().applyMatrix4(m.matrix);let key=m.material.uuid;if(!batches.has(key))batches.set(key,{mat:m.material,geos:[]});batches.get(key).geos.push(g);group.remove(m);m.geometry.dispose();}for(let b of batches.values()){let g=mergeGeometries(b.geos,false);for(let p of b.geos)p.dispose();if(g)this.mesh(g,b.mat,group);}}
 groundTexture(id){let c=document.createElement('canvas');c.width=c.height=256;let ctx=c.getContext('2d');let img=ctx.createImageData(256,256);let base=id==='snow'?[196,207,209]:id==='mud'?[94,87,65]:id==='city'?[99,100,94]:[161,139,101];for(let i=0;i<img.data.length;i+=4){let n=Math.random()*28-14;for(let k=0;k<3;k++)img.data[i+k]=base[k]+n;img.data[i+3]=255;}ctx.putImageData(img,0,0);for(let i=0;i<250;i++){ctx.strokeStyle='rgba(30,25,18,.13)';ctx.beginPath();let x=Math.random()*256,y=Math.random()*256;ctx.moveTo(x,y);ctx.lineTo(x+Math.random()*15,y+Math.random()*6);ctx.stroke();}let t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(60,60);t.colorSpace=THREE.SRGBColorSpace;return t;}
 disposeObject(obj){
  const geometries=new Set(),materials=new Set(),textures=new Set();
  obj.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)for(let m of Array.isArray(o.material)?o.material:[o.material])materials.add(m);});
  for(let m of materials){for(let value of Object.values(m))if(value?.isTexture)textures.add(value);m.dispose();}
  for(let g of geometries)g.dispose();for(let t of textures)t.dispose();
 }
 async loadMap(index){
  let id=MAPS[index].id;
  if(!this.mapAssets[id])this.mapAssets[id]=Promise.all([new GLTFLoader().loadAsync('/battlefields/'+id+'.glb'),new THREE.TextureLoader().loadAsync('/battlefields/'+id+'-indirect.png'),new THREE.TextureLoader().loadAsync('/battlefields/'+id+'-albedo.png')]).then(([g,tex,albedo])=>{tex.flipY=false;tex.colorSpace=THREE.NoColorSpace;tex.channel=0;albedo.flipY=false;albedo.colorSpace=THREE.SRGBColorSpace;return {scene:g.scene,light:tex,albedo};}).catch(e=>{delete this.mapAssets[id];throw e});
  return this.mapAssets[id];
 }
 async buildMap(index,garage=false){
  this.destruction=null;this.pendingBuildingEvents=[];let token=++this.mapToken;this.disposeObject(this.world);this.world.clear();this.preview=null;this.entities.clear();this.effects=[];this.shotMeshes=[];this.mapIndex=index;
  let d=MAPS[index];this.scene.background=new THREE.Color(d.sky);this.scene.fog=new THREE.FogExp2(d.fog,garage?.007:.0037);
  // The ground is temporary while the real Blender static scene loads.
  let placeholder=this.mesh(new THREE.PlaneGeometry(900,900),this.mat(d.color),this.world);placeholder.rotation.x=-Math.PI/2;
  this.sun.color.set(d.id==='snow'?0xdcecff:0xffd5a0);this.sun.intensity=d.id==='mud'?2.5:3.4;
  if(garage){let pad=this.mat(0x595b50,.4,.8);this.mesh(new THREE.CylinderGeometry(8.2,8.6,.16,64),pad,this.world,0,.06,0);let ring=new THREE.Mesh(new THREE.RingGeometry(7.8,7.85,80),new THREE.MeshBasicMaterial({color:0xbca26c,side:THREE.DoubleSide}));ring.rotation.x=-Math.PI/2;ring.position.y=.15;this.world.add(ring);}
  else{let border=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-178,.15,-178),new THREE.Vector3(178,.15,-178),new THREE.Vector3(178,.15,178),new THREE.Vector3(-178,.15,178)]),new THREE.LineBasicMaterial({color:0xe4ac55,transparent:true,opacity:.6}));this.world.add(border);}
  try{let asset=await this.loadMap(index);if(!this.active||token!==this.mapToken)return;let environment=asset.scene.clone(true);environment.traverse(o=>{if(o.isMesh){o.geometry=o.geometry.clone();o.material=o.material.clone();o.material.map=asset.albedo.clone();o.material.map.needsUpdate=true;o.material.color.set(0xffffff);o.material.lightMap=asset.light.clone();o.material.lightMap.needsUpdate=true;o.material.lightMapIntensity=1.25;o.material.roughness=d.id==='mud'?.52:.9;o.material.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_begin>',THREE.ShaderChunk.lights_fragment_begin.replace('#if ( NUM_HEMI_LIGHTS > 0 )','#if 0'));};o.material.customProgramCacheKey=()=> 'static-indirect-no-live-sky-v1';o.receiveShadow=true;o.castShadow=true;o.userData.staticIndirect=true;}});this.world.remove(placeholder);this.disposeObject(placeholder);this.world.add(environment);if(!garage){this.destruction=new BuildingDestruction(partitionBuildings(environment,makeObstacles(d.id)),this.world);for(const e of this.pendingBuildingEvents)this.destruction.hit(e);this.pendingBuildingEvents=[];}}
  catch(e){if(token===this.mapToken)this.onError('战场资源加载失败，请刷新重试。');}
 }

 setGear(gear){this.gear=gear;this.previewGear=null;if(this.mode==='garage')this.setTank(this.selected);}
 previewEquipment(category,index){this.previewGear={...this.gear,[category]:index};this.setTank(this.selected);}
 setFocus(category){this.focus=category;this.previewGear=null;if(this.mode==='garage')this.setTank(this.selected);}
 setTank(index){this.mode='garage';this.selected=index;if(this.preview){this.world.remove(this.preview);this.disposeObject(this.preview);}if(this.ammoDisplay){this.world.remove(this.ammoDisplay);this.disposeObject(this.ammoDisplay);this.ammoDisplay=null;}
 this.preview=this.tank(TANKS[index],this.previewGear||this.gear||{});this.preview.rotation.y=-.45;this.world.add(this.preview);
 if(this.focus==='ammo'){this.ammoDisplay=this.cloneAsset(this.equipment?.['ammo_'+((this.previewGear||this.gear)?.ammo||0)]);this.ammoDisplay.position.set(3,0,1.2);this.world.add(this.ammoDisplay);}
 }
 beginFlyover(position=new THREE.Vector3(),done=()=>{}){
 this.finishFlyover();if(Array.isArray(position))position=new THREE.Vector3(...position);this.flyover={time:0,origin:position.clone(),done};
 this.aircraft=this.cloneAsset(this.equipment.aircraft);this.world.add(this.aircraft);
 this.flightPath=new THREE.CatmullRomCurve3([new THREE.Vector3(-62,48,-68),new THREE.Vector3(-22,36,-32),new THREE.Vector3(0,22,0),new THREE.Vector3(27,38,48),new THREE.Vector3(80,54,80)].map(v=>v.add(position)));
 }
 finishFlyover(){if(!this.flyover)return;const done=this.flyover.done;this.flyover=null;if(this.aircraft){this.world.remove(this.aircraft);this.disposeObject(this.aircraft);this.aircraft=null;}this.cameraReady=false;done();}
 renderFlyover(dt){const f=this.flyover;f.time+=dt;const t=Math.min(1,f.time/7.5),a=this.flightPath.getPoint(t),ahead=this.flightPath.getPoint(Math.min(1,t+.015));this.aircraft.position.copy(a);if(t<.99)this.aircraft.lookAt(ahead);this.aircraft.rotation.z=Math.sin(t*Math.PI*2)*.15;
 const follow=a.clone().add(new THREE.Vector3(8,5,-13));const end=f.origin.clone().add(this.mode==='battle'?new THREE.Vector3(0,5.4,-14):new THREE.Vector3(10,5.3,12.7));const blend=THREE.MathUtils.smoothstep(t,.35,1);this.camera.position.copy(follow.lerp(end,blend));const target=a.clone().lerp(f.origin.clone().add(new THREE.Vector3(0,1.6,this.mode==='battle'?25:0)),blend);this.camera.lookAt(target);this.lookTarget.copy(target);this.camera.fov=48;this.camera.updateProjectionMatrix();if(t>=1)this.finishFlyover();
 }
 start(battle){this.finishFlyover();this.mode='battle';this.battle=battle;this.preview=null;this.buildMap(MAPS.indexOf(battle.map));for(let t of battle.tanks){let model=this.tank(t.def,t.id===0?this.gear||{}:{});this.world.add(model);let marker=new THREE.Mesh(new THREE.RingGeometry(2.7,2.82,24),new THREE.MeshBasicMaterial({color:t.team?0xe6684c:0x91bda0,side:THREE.DoubleSide,transparent:true,opacity:.65}));marker.rotation.x=-Math.PI/2;marker.position.y=.1;model.add(marker);this.entities.set(t.id,model);}this.cameraReady=false;}
 buildingHit(e){if(this.destruction)this.destruction.hit(e);else this.pendingBuildingEvents?.push(e);}
 burst(e){if(e.heavy){this.heavyBurst(e);return;}let kill=e.type==='kill',count=kill?25:e.type==='fire'?6:9;let mat=new THREE.MeshBasicMaterial({color:kill?0xffa23e:e.type==='fire'?0xffe6a0:0xf3b563,transparent:true});for(let i=0;i<count;i++){let m=this.mesh(new THREE.IcosahedronGeometry(kill?.4:.15,0),mat.clone(),this.world,e.x,e.y??2,e.z);this.effects.push({mesh:m,v:new THREE.Vector3((Math.random()-.5)*(kill?12:5),Math.random()*8,(Math.random()-.5)*(kill?12:5)),life:kill?1.4:.5,max:kill?1.4:.5});}mat.dispose();}
 heavyBurst(e){
 const impact=e.type==='impact';
 for(let i=0;i<(impact?46:24);i++){const mat=new THREE.MeshBasicMaterial({color:i%3?0x66e9ff:0xffdda0,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false});const m=this.mesh(new THREE.IcosahedronGeometry(i%3?.16:.32,0),mat,this.world,e.x,e.y??2,e.z);const speed=impact?20:11;this.effects.push({mesh:m,v:new THREE.Vector3((Math.random()-.5)*speed,Math.random()*speed*.65,(Math.random()-.5)*speed),life:1,max:1});}
 for(let i=0;i<3;i++){const m=this.mesh(new THREE.TorusGeometry(impact?1.4:.65,.055,6,48),new THREE.MeshBasicMaterial({color:i%2?0xffe8b4:0x61e9ff,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false}),this.world,e.x,e.y??2,e.z);m.rotation.set(Math.PI/2,i*.65,i*.7);this.effects.push({mesh:m,v:new THREE.Vector3(),life:.65,max:.65,shock:true});}
 }
 render(dt,aim=0,pitch=0,zoom=false){
 this.tick+=dt;this.destruction?.update(dt);
 if(this.mode==='garage'){
 if(this.preview){this.preview.rotation.y=-.45+(this.focus?0:Math.sin(this.tick*.18)*.09);this.preview.userData.cannon.rotation.x=this.focus==='barrel'?-.045:0;}
 let pos=new THREE.Vector3(10,5.3,12.7),target=new THREE.Vector3(-.3,1.25,0),fov=47;
 if(this.focus&&this.preview){const g=this.preview.userData.spec;const views={barrel:[[3.6,g.height+1.5,g.fore+g.length+2.3],[0,g.height,g.fore+g.length*.56]],tracks:[[6.1,1.6,3.4],[1.7,.7,0]],armor:[[5.4,2.7,1.7],[1.9,1.35,0]]};
 if(this.focus==='ammo'){pos.set(5.7,2.3,4.4);target.set(3,.9,1.2);fov=36;}else{const v=views[this.focus];pos.fromArray(v[0]).applyAxisAngle(UP,this.preview.rotation.y);target.fromArray(v[1]).applyAxisAngle(UP,this.preview.rotation.y);fov=this.focus==='barrel'?37:41;}}
 if(!this.flyover){const smooth=1-Math.exp(-dt*3.5);this.camera.position.lerp(pos,smooth);this.lookTarget.lerp(target,smooth);this.camera.fov+=(fov-this.camera.fov)*smooth;this.camera.updateProjectionMatrix();this.camera.lookAt(this.lookTarget);}
 }else if(this.battle){const b=this.battle;
 for(const t of b.tanks){const m=this.entities.get(t.id);if(!m)continue;m.position.set(t.x,0,t.z);m.rotation.y=t.yaw;m.userData.turret.rotation.y=t.aim-t.yaw;m.userData.cannon.rotation.x=-t.pitch;
 if(t.id===0){if(!m.userData.chargeGlow){const glow=new THREE.Mesh(new THREE.IcosahedronGeometry(.35,2),new THREE.MeshBasicMaterial({color:0x72efff,transparent:true,opacity:.6,blending:THREE.AdditiveBlending,depthWrite:false}));glow.position.z=m.userData.spec.length;m.userData.cannon.add(glow);m.userData.chargeGlow=glow;}const glow=m.userData.chargeGlow;glow.visible=t.alive&&b.charging;glow.scale.setScalar(.3+b.charge/1.2*(1.6+Math.sin(this.tick*25)*.15));glow.material.opacity=.25+b.charge/1.2*.6;}
 if(t.stun>0&&t.alive){if(!m.userData.stunHalo){const halo=new THREE.Mesh(new THREE.TorusGeometry(1.15,.08,6,32),new THREE.MeshBasicMaterial({color:0x78eaff,transparent:true,blending:THREE.AdditiveBlending}));halo.position.y=3.8;halo.rotation.x=Math.PI/2;m.add(halo);for(let i=0;i<3;i++){const star=new THREE.Mesh(new THREE.OctahedronGeometry(.23),halo.material);star.position.set(Math.cos(i*Math.PI*2/3)*1.15,Math.sin(i*Math.PI*2/3)*1.15,0);halo.add(star);}m.userData.stunHalo=halo;}m.userData.stunHalo.visible=true;m.userData.stunHalo.rotation.z+=dt*5;}else if(m.userData.stunHalo)m.userData.stunHalo.visible=false;
 if(!t.alive&&!m.userData.dead){m.userData.dead=true;m.traverse(o=>{if(o.isMesh&&o.material?.color)o.material.color.multiplyScalar(.23);});}if(t.alive)m.rotation.z=Math.sin(this.tick*15+t.id)*Math.min(Math.abs(t.speed)*.0008,.012);}
 const p=b.player.alive?b.player:b.tanks.find(t=>t.team===0&&t.alive)||b.player;const viewPitch=p===b.player?pitch:p.pitch,viewAim=p===b.player?aim:p.aim;const gun=muzzle(p);let dist=zoom?2:14;
 const desired=zoom?new THREE.Vector3(gun.x-Math.sin(viewAim)*dist,gun.y+.32,gun.z-Math.cos(viewAim)*dist):new THREE.Vector3(p.x-Math.sin(viewAim)*dist,5.4-Math.sin(viewPitch)*6,p.z-Math.cos(viewAim)*dist);
 for(const o of b.obstacles){const u=segmentBoxLocal(p.x,p.z,desired.x-p.x,desired.z-p.z,o);if(u!==null&&desired.y<o.h+1){desired.x=p.x+(desired.x-p.x)*Math.max(.18,u-.1);desired.z=p.z+(desired.z-p.z)*Math.max(.18,u-.1);}}
 if(!this.flyover){if(!this.cameraReady){this.camera.position.copy(desired);this.cameraReady=true;}else this.camera.position.lerp(desired,1-Math.exp(-dt*12));this.camera.fov+=((zoom?24:55)-this.camera.fov)*Math.min(1,dt*12);this.camera.updateProjectionMatrix();this.camera.lookAt(gun.x+Math.sin(viewAim)*Math.cos(viewPitch)*120,gun.y+Math.sin(viewPitch)*120,gun.z+Math.cos(viewAim)*Math.cos(viewPitch)*120);}
 this.sun.position.set(p.x-60,95,p.z+50);this.sun.target.position.set(p.x,0,p.z);
 for(const m of this.shotMeshes){this.world.remove(m);m.geometry.dispose();m.material.dispose();}this.shotMeshes=[];
 for(const s of b.shots){const m=this.mesh(new THREE.BoxGeometry(s.heavy?.32:.10,s.heavy?.32:.10,s.heavy?4.5:2.2),new THREE.MeshBasicMaterial({color:s.heavy?0x9af6ff:[0xffe8a8,0x96e9ff,0xff824e][s.ammo||0]}),this.world,s.x,s.y,s.z);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),new THREE.Vector3(s.dx,s.dy,s.dz).normalize());this.shotMeshes.push(m);}
 }
 if(this.flyover)this.renderFlyover(dt);
 for(const e of this.effects){e.life-=dt;e.mesh.position.addScaledVector(e.v,dt);if(!e.shock)e.v.y-=9.81*dt;e.mesh.material.opacity=Math.max(0,e.life/e.max);e.mesh.scale.multiplyScalar(1+dt*(e.shock?5:1));if(e.life<=0){this.world.remove(e.mesh);e.mesh.geometry.dispose();e.mesh.material.dispose();}}this.effects=this.effects.filter(e=>e.life>0);this.renderer.render(this.scene,this.camera);
 }
 aimProjection(){if(!this.battle?.player.alive)return null;const t=this.battle.player,g=muzzle(t),d=100;const v=new THREE.Vector3(g.x+Math.sin(t.aim)*Math.cos(t.pitch)*d,g.y+Math.sin(t.pitch)*d,g.z+Math.cos(t.aim)*Math.cos(t.pitch)*d).project(this.camera);return {x:(v.x*.5+.5)*this.host.clientWidth,y:(-.5*v.y+.5)*this.host.clientHeight};}

 project(x,z){let v=new THREE.Vector3(x,4.4,z).project(this.camera);return{x:(v.x*.5+.5)*this.host.clientWidth,y:(-.5*v.y+.5)*this.host.clientHeight,visible:v.z<1&&v.z>-1&&Math.abs(v.x)<1&&Math.abs(v.y)<1};}
 dispose(){this.active=false;this.observer.disconnect();this.disposeObject(this.scene);for(let m of Object.values(this.equipment))this.disposeObject(m);for(let m of Object.values(this.loaded))this.disposeObject(m);for(let promise of Object.values(this.mapAssets))promise.then(a=>{this.disposeObject(a.scene);a.light.dispose();a.albedo.dispose()}).catch(()=>{});this.renderer.dispose();this.renderer.domElement.remove();}
}
function segmentBoxLocal(x,z,dx,dz,o){let lo=0,hi=1;for(let[v,d,c,s]of[[x,dx,o.x,o.w/2+1],[z,dz,o.z,o.d/2+1]]){if(Math.abs(d)<1e-6){if(v<c-s||v>c+s)return null;}else{let a=(c-s-v)/d,b=(c+s-v)/d;if(a>b)[a,b]=[b,a];lo=Math.max(lo,a);hi=Math.min(hi,b);if(lo>hi)return null;}}return lo;}
