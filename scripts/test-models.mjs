import fs from 'node:fs';
import assert from 'node:assert/strict';
import ts from 'typescript';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Box3,Vector3} from 'three';
let path=new URL('../lib/.renderer-test.mjs',import.meta.url);
fs.writeFileSync(path,ts.transpile(fs.readFileSync(new URL('../lib/renderer.ts',import.meta.url),'utf8'),{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}));
try{
const {TankRenderer}=await import(path.href);const {TANKS}=await import('../lib/battle.mjs');
let engine=Object.create(TankRenderer.prototype);engine.loaded={};
for(let n of ['abrams','challenger','leopard','china','france','japan']){let data=fs.readFileSync(new URL('../public/models/'+n+'.glb',import.meta.url));let g=await new GLTFLoader().parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'');engine.loaded[n]=g.scene;}
for(let def of TANKS){let model=engine.tank(def);assert(model.userData.turret.children.length>3,def.name+' missing turret');let before=new Box3().setFromObject(model.userData.turret).getSize(new Vector3());model.userData.turret.rotation.y=Math.PI/2;let after=new Box3().setFromObject(model.userData.turret).getSize(new Vector3());assert(Math.abs(before.z-after.x)<.01,def.name+' rotation invalid');console.log('PASS',def.name,'turret rotates independently',model.userData.body.children.length,'body meshes');engine.disposeObject(model);}
}finally{fs.unlinkSync(path)}
