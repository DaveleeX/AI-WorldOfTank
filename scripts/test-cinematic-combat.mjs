import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Battle,TANKS} from '../lib/battle.mjs';
import {GRAVITY,muzzle,gunSpec,shellPosition,lowArcPitch,segmentAABB,MAX_PITCH,MIN_PITCH,killTier} from '../lib/ballistics.mjs';
import {MUSIC_THEMES,BattleMusic} from '../lib/music.mjs';
const pass=name=>console.log('PASS',name);
function sandbox(){let b=new Battle();b.obstacles=[];for(const t of b.tanks){t.x=160;t.z=t.id*9-80;t.s.speed=0;t.reload=100;}b.player.x=0;b.player.z=0;b.player.reload=0;return b;}
let b=sandbox();b.player.pitch=.12;b.fire(b.player);let s=b.shots[0],initial={...s};for(let i=0;i<10;i++)b.update(.05,{pitch:.12});let expected=shellPosition(initial,.5);assert(Math.abs(s.y-expected.y)<1e-6);assert(Math.abs(s.dy-(initial.dy-GRAVITY*.5))<1e-6);pass('Projectile parabola and gravity match analytical solution');
b=sandbox();b.update(.01,{pitch:99});assert.equal(b.player.pitch,MAX_PITCH);b.update(.01,{pitch:-99});assert.equal(b.player.pitch,MIN_PITCH);pass('Gun elevation clamps at -10 and +25 degrees');
b=sandbox();b.player.pitch=-.10;b.fire(b.player);for(let i=0;i<40;i++)b.update(.025,{pitch:-.10});assert.equal(b.shots.length,0);assert(b.events.some(e=>e.type==='impact'&&e.y<.001));pass('Depressed gun impacts actual ground');
function roof(raise){let b=sandbox();b.obstacles=[{x:0,z:35,w:12,d:5,h:3}];b.player.pitch=raise;b.fire(b.player);for(let i=0;i<8;i++)b.update(.05,{pitch:raise});return b;}
assert(roof(0).events.some(e=>e.type==='impact'&&e.z<40));assert(!roof(.18).events.some(e=>e.type==='impact'));pass('Finite-height cover blocks low rounds and permits overflight');
b=sandbox();let enemy=b.tanks[5];enemy.x=0;enemy.z=100;let gun=gunSpec(b.player.def.model);let pitch=lowArcPitch(100-gun.fore-gun.length,1.6-gun.height,b.player.s.muzzleSpeed);b.player.pitch=pitch;b.fire(b.player);for(let i=0;i<20;i++)b.update(.05,{pitch});assert(enemy.hp<enemy.s.hp);pass('AI low-arc solution hits a distant vehicle');
b=sandbox();b.obstacles=[{x:0,z:3,w:10,d:1,h:5}];assert(b.fire(b.player));assert.equal(b.shots.length,0);pass('Muzzle cannot bypass cover at close range');
b=new Battle();for(let i=0;i<5;i++){b.hit(b.tanks[5+i],99999,0);let event=b.events.filter(e=>e.type==='kill').at(-1);assert.equal(event.kills,i+1);assert.equal(killTier(event.kills).count,i+1);}assert.equal(new Set(Array.from({length:5},(_,i)=>killTier(i+1).title)).size,5);let kills=b.kills;b.hit(b.tanks[5],99999,0);assert.equal(b.kills,kills);pass('Five distinct player kill tiers, no duplicate kill credit');
// Load the actual exported GLBs using the real loader and renderer assembly code.
const testURL=new URL('../lib/.cinematic-renderer-test.mjs',import.meta.url);
fs.writeFileSync(testURL,ts.transpile(fs.readFileSync(new URL('../lib/renderer.ts',import.meta.url),'utf8'),{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}));
try{
 const {TankRenderer}=await import(testURL.href);const e=Object.create(TankRenderer.prototype);e.loaded={};e.equipment={};
 async function load(path){const data=fs.readFileSync(new URL('../public/'+path,import.meta.url));return (await new GLTFLoader().parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'')).scene;}
 for(const d of TANKS)e.loaded[d.model]=await load('models/rigged/'+d.model+'.glb');
 for(const k of ['barrel_1','barrel_2','tracks_1_5','tracks_1_6','tracks_1_7','tracks_2_5','tracks_2_6','tracks_2_7','armor_1','armor_2','ammo_0','ammo_1','ammo_2','aircraft'])e.equipment[k]=await load('equipment/'+k+'.glb');
 for(const d of TANKS){for(let tier=0;tier<3;tier++){let tank=e.tank(d,{barrel:tier,tracks:tier,armor:tier,ammo:tier});const {cannon,turret,body,spec}=tank.userData;let count=0;cannon.traverse(o=>{if(o.isMesh)count++});assert(count>0,d.name+' cannon');let bodyBefore=new THREE.Box3().setFromObject(body).clone();let gunBounds=new THREE.Box3().setFromObject(cannon);assert(Math.abs(gunBounds.max.z-(spec.fore+spec.length))<.02,d.name+' actual barrel tip not calibrated');assert(gunBounds.max.y-spec.height<.40,d.name+' barrel has a baked elevation');turret.rotation.y=.65;cannon.rotation.x=-.2;assert(new THREE.Box3().setFromObject(body).equals(bodyBefore),'aiming moved the hull');tank.position.set(12,0,25);tank.updateMatrixWorld(true);const tip=new THREE.Vector3(0,0,spec.length).applyMatrix4(cannon.matrixWorld);const sim={def:d,s:{barrel:tier},x:12,z:25,pitch:.2,aim:.65};let p=muzzle(sim);assert(tip.distanceTo(new THREE.Vector3(p.x,p.y,p.z))<1e-5,d.name+' visual muzzle differs from physics');assert(cannon.children.length);e.disposeObject(tank);}}
 pass('All 18 tank/loadout combinations have independent guns and exact visual/physics muzzle agreement');
 e.world=new THREE.Group();e.mode='garage';e.gear={};e.selected=0;e.focus=null;e.setTank(0);e.setFocus('barrel');e.previewEquipment('barrel',1);assert.equal(e.preview.userData.spec.length,5.28);assert.equal(e.gear.barrel,undefined);e.setFocus('ammo');assert(e.ammoDisplay);e.setFocus(null);assert.equal(e.ammoDisplay,null);assert.equal(e.preview.userData.spec.length,3.65*1.2);pass('Equipment preview is reversible and never purchases or alters equipped gear');
 e.camera=new THREE.PerspectiveCamera(47,1,.15,1100);e.lookTarget=new THREE.Vector3();let callbacks=0;e.beginFlyover([20,0,30],()=>callbacks++);for(let i=0;i<151&&e.flyover;i++)e.renderFlyover(.05);assert.equal(callbacks,1);assert.equal(e.aircraft,null);assert(e.camera.position.distanceTo(new THREE.Vector3(30,5.3,42.7))<.001);e.beginFlyover(undefined,()=>callbacks++);e.finishFlyover();e.finishFlyover();assert.equal(callbacks,2);pass('Flyover reaches selected tank and skip completes once without leaked aircraft');
 for(const m of Object.values(e.loaded))e.disposeObject(m);for(const m of Object.values(e.equipment))e.disposeObject(m);e.disposeObject(e.world);
}finally{fs.unlinkSync(testURL)}
// Verify scheduler lifecycle without relying on autoplay or a browser audio device.
const param=()=>({value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){},setTargetAtTime(){}});
const node=()=>({gain:param(),frequency:param(),connect(){},disconnect(){},addEventListener(){},start(){},stop(){this.onended?.();}});
const context={currentTime:0,state:'running',sampleRate:24000,destination:{},createGain:node,createOscillator:node,createDynamicsCompressor:node,createBiquadFilter:node,createBufferSource:node,createBuffer:(c,n)=>({getChannelData:()=>new Float32Array(n)})};
const music=new BattleMusic(context);try{assert.equal(new Set(MUSIC_THEMES.map(t=>t.bpm)).size,4);for(let i=0;i<4;i++){music.play(i);assert(music.active);assert.equal(music.theme.id,MUSIC_THEMES[i].id);music.setPaused(true);music.setPaused(true);assert(!music.active);music.setPaused(false);assert(music.active);music.celebrate(i+1);music.setMuted(true);music.stop();}pass('Four original music themes, pause remains silent, resume and mute work');}finally{music.dispose()}
