import './node-image-bitmap.mjs';
import fs from 'node:fs';
import assert from 'node:assert/strict';
import ts from 'typescript';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Box3,Vector3,Group,Mesh,BoxGeometry,MeshStandardMaterial,Texture} from 'three';
let path=new URL('../lib/.renderer-test.mjs',import.meta.url);
fs.writeFileSync(path,ts.transpile(fs.readFileSync(new URL('../lib/renderer.ts',import.meta.url),'utf8'),{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}));
try{
const {TankRenderer}=await import(path.href);const {TANKS}=await import('../lib/battle.mjs');
let engine=Object.create(TankRenderer.prototype);engine.loaded={};
for(let n of ['abrams','challenger','leopard','china','france','japan']){let data=fs.readFileSync(new URL('../public/models/rigged/'+n+'.glb',import.meta.url));let g=await new GLTFLoader().parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'');engine.loaded[n]=g.scene;}
for(let def of TANKS){let model=engine.tank(def);assert(model.userData.turret.children.length>3,def.name+' missing turret');let before=new Box3().setFromObject(model.userData.turret).getSize(new Vector3());model.userData.turret.rotation.y=Math.PI/2;let after=new Box3().setFromObject(model.userData.turret).getSize(new Vector3());assert(Math.abs(before.z-after.x)<.01,def.name+' rotation invalid');console.log('PASS',def.name,'turret rotates independently',model.userData.body.children.length,'body meshes');engine.disposeObject(model);}
const group=new Group(),geo=new BoxGeometry(),tex=new Texture(),light=new Texture(),mat=new MeshStandardMaterial({map:tex,lightMap:light});
let freed={geometry:0,material:0,map:0,lightMap:0};
for(let [resource,key] of [[geo,'geometry'],[mat,'material'],[tex,'map'],[light,'lightMap']])resource.addEventListener('dispose',()=>freed[key]++);
group.add(new Mesh(geo,mat),new Mesh(geo,mat));engine.disposeObject(group);
assert.deepEqual(freed,{geometry:1,material:1,map:1,lightMap:1});
console.log('PASS shared geometry, materials, albedo and indirect maps disposed exactly once');
}finally{fs.unlinkSync(path)}
