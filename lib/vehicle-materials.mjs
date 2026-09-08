import * as THREE from 'three';
const palettes={china:[0x616b43,0x8a805d,0x333d32],france:[0x576446,0x72624b,0x303734],japan:[0x566044,0x776348,0x343b31],challenger:[0x666d48,0x797451,0x414739],leopard:[0x526044,0x716049,0x303632],abrams:[0xa89b76,0x877c5d,0x6c6951]};
// Object-space pigment stays attached to armor while the hull and turret move.
export function finishVehicleMaterial(material,nation){
 if(!/painted|camouflage/i.test(material.name))return;
 material.metalness=.24;material.roughness=.83;
 material.onBeforeCompile=shader=>{
 const colors=palettes[nation]||palettes.china;
 colors.forEach((c,i)=>shader.uniforms['pigment'+i]={value:new THREE.Color(c)});
 shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 armorPosition;').replace('#include <begin_vertex>','#include <begin_vertex>\narmorPosition=position;');
 shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
 varying vec3 armorPosition;
 uniform vec3 pigment0;uniform vec3 pigment1;uniform vec3 pigment2;
 float armorHash(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
 float armorNoise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(mix(armorHash(i),armorHash(i+vec3(1,0,0)),f.x),mix(armorHash(i+vec3(0,1,0)),armorHash(i+vec3(1,1,0)),f.x),f.y),mix(mix(armorHash(i+vec3(0,0,1)),armorHash(i+vec3(1,0,1)),f.x),mix(armorHash(i+vec3(0,1,1)),armorHash(i+vec3(1,1,1)),f.x),f.y),f.z);}
 `).replace('#include <map_fragment>',`#include <map_fragment>
 float pigmentMask=armorNoise(armorPosition*1.5+vec3(2.7,1.3,0.4));
 vec3 paint=mix(pigment0,pigment1,smoothstep(.47,.50,pigmentMask));
 paint=mix(paint,pigment2,1.0-smoothstep(.32,.35,pigmentMask));
 float grain=armorNoise(armorPosition*160.0);
 diffuseColor.rgb=paint*(.88+.22*grain)*diffuse;
 `);
 // Keep material.color as a multiplier so destroyed vehicles can be darkened.
 };
 material.color.set(0xffffff);
 material.customProgramCacheKey=()=>`field-paint-v1-${nation}`;
}
