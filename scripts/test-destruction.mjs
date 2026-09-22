import './node-image-bitmap.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Battle,makeObstacles} from '../lib/battle.mjs';
import {partitionBuildings,BuildingDestruction} from '../lib/destruction.mjs';
function battle(h,type='building',z=25){const b=new Battle();for(const t of b.tanks){t.x=150;t.z=t.id*10-80;t.s.speed=0;t.reload=100;}b.player.x=0;b.player.z=0;b.player.reload=0;b.obstacles=[{id:91,x:0,z,w:10,d:6,h,type,hits:0,maxHits:h>10?3:2}];return b;}
function shoot(b){b.player.reload=0;b.fire(b.player);for(let i=0;i<8;i++)b.update(.05);}
for(const h of [6,18]){const b=battle(h),n=h>10?3:2;for(let i=1;i<=n;i++){shoot(b);assert.equal(b.obstacles.length,i===n?0:1);assert.equal(b.events.filter(e=>e.type==='collapse').length,i===n?1:0);}assert.equal(b.events.filter(e=>e.type==='crack').length,n-1);assert.equal(b.kills,0);assert(b.clearLine({x:0,z:0},{x:0,z:50}));}
const close=battle(6,'building',3);shoot(close);shoot(close);assert.equal(close.obstacles.length,0);
const rock=battle(6,'rock');for(let i=0;i<4;i++)shoot(rock);assert.equal(rock.obstacles.length,1);assert(!rock.events.some(e=>e.type==='collapse'));
assert(makeObstacles('city').every(o=>o.hits===0));console.log('PASS 2/3 projectile hits, close-muzzle hits, indestructible rocks, cleared collision and fresh rounds');
for(const id of ['city','mud','desert','snow']){
 const data=fs.readFileSync(new URL('../public/battlefields/'+id+'.glb',import.meta.url));const {scene}=await new GLTFLoader().parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'');
 let before=0;scene.traverse(m=>{if(m.isMesh)before+=(m.geometry.index?.count??m.geometry.attributes.position.count)});
 const buildings=partitionBuildings(scene,makeObstacles(id));let after=0;scene.traverse(m=>{if(m.isMesh&&![...buildings.values()].some(b=>b.intact===m))after+=m.geometry.attributes.position.count});assert.equal(before,after,'geometry must be conserved');
 const world=new THREE.Group();world.add(scene);const fx=new BuildingDestruction(buildings,world);
 for(const [key,b] of buildings){assert(b.pieces.length>0,`${id} missing building ${key}`);assert(b.pieces.every(m=>m.material.lightMap===null));fx.hit({type:'crack',building:key,obstacle:{hits:1},x:b.o.x,y:2,z:b.o.z});assert(b.cracks.children.length>0);fx.hit({type:'collapse',building:key,obstacle:{hits:3},x:b.o.x,y:2,z:b.o.z});}
 for(let i=0;i<100;i++)fx.update(.05);assert([...buildings.values()].every(b=>b.settled));assert.equal(fx.clouds.length,0);scene.traverse(m=>{if(m.isMesh)assert(Number.isFinite(m.position.y))});
 console.log(`PASS ${id}: ${buildings.size} original buildings partitioned, no lost triangles, live lighting, collapse and dust cleanup`);
}
