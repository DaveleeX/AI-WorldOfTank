import fs from 'node:fs';
import assert from 'node:assert/strict';
const root=new URL('../',import.meta.url);
function glb(path){let b=fs.readFileSync(new URL(path,root));assert.equal(b.readUInt32LE(0),0x46546c67);return JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString().trim());}
let report=[];
for(let slug of ['china','abrams','challenger','france','leopard','japan']){
 let g=glb('public/models/rigged/'+slug+'.glb');assert.equal(g.scenes.length,1,slug+' accidentally exported extra scenes');
 assert(g.nodes.some(n=>n.name?.startsWith('body')));assert(g.nodes.some(n=>n.name?.startsWith('turret')));assert(g.nodes.some(n=>n.name?.startsWith('cannon')));assert(g.nodes.some(n=>n.name?.startsWith('tracks')));
 let triangles=g.meshes.flatMap(m=>m.primitives).reduce((n,p)=>n+g.accessors[p.indices].count/3,0);assert(triangles>15000,slug+' lost source detail');assert(triangles<150000,slug+' excessive duplicate geometry');
 report.push({tank:slug,triangles});
}
for(let slug of ['desert','city','mud','snow']){
 let g=glb('public/battlefields/'+slug+'.glb');assert.equal(g.scenes.length,1);assert(!g.cameras?.length);assert(!g.nodes.some(n=>/turret|body|projectile/i.test(n.name||'')));
 for(let p of g.meshes.flatMap(m=>m.primitives))assert(p.attributes.TEXCOORD_0!==undefined,slug+' missing lightmap UV');
 let png=fs.readFileSync(new URL('public/battlefields/'+slug+'-indirect.png',root));assert.equal(png.readUInt32BE(16),2048);assert.equal(png.readUInt32BE(20),2048);assert(png.length>50000,'empty indirect bake');
}
console.log('PASS six single-scene high-detail GLBs; four UV-mapped static worlds and 2048px indirect bakes',report);
