export const GRAVITY=9.81;
export const MIN_PITCH=-Math.PI/18,MAX_PITCH=Math.PI/7.2;
export const GUNS={china:{height:2.25,fore:1.45,length:3.65},france:{height:2.25,fore:1.47,length:3.45},japan:{height:2.2,fore:1.4,length:3.15},challenger:{height:2.37,fore:1.43,length:3.05},leopard:{height:2.31,fore:1.22,length:3.25},abrams:{height:2.4,fore:1.66,length:2.6}};
export function gunSpec(model,barrel=0){return {...GUNS[model],length:barrel===1?4.4:barrel===2?2.75:GUNS[model].length};}
export function muzzle(t){const g=gunSpec(t.def.model,t.s.barrel);const pitch=t.pitch||0,range=g.fore+Math.cos(pitch)*g.length;return {x:t.x+Math.sin(t.aim)*range,y:g.height+Math.sin(pitch)*g.length,z:t.z+Math.cos(t.aim)*range};}
export function lowArcPitch(distance,height,speed){const v2=speed*speed,disc=v2*v2-GRAVITY*(GRAVITY*distance*distance+2*height*v2);if(distance<.01||disc<0)return null;return Math.atan((v2-Math.sqrt(disc))/(GRAVITY*distance));}
// Swept 3D segment versus a finite box. Prevents tunneling and permits roof overflight.
export function segmentAABB(p,d,min,max){let lo=0,hi=1;for(const axis of ['x','y','z']){if(Math.abs(d[axis])<1e-9){if(p[axis]<min[axis]||p[axis]>max[axis])return null;}else{let a=(min[axis]-p[axis])/d[axis],b=(max[axis]-p[axis])/d[axis];if(a>b)[a,b]=[b,a];lo=Math.max(lo,a);hi=Math.min(hi,b);if(lo>hi)return null;}}return lo;}
export function shellPosition(s,t){return {x:s.x+s.dx*t,y:s.y+s.dy*t-.5*GRAVITY*t*t,z:s.z+s.dz*t};}
export const KILL_TIERS=[{title:'敌车击毁',en:'TARGET DESTROYED',color:'#e5b566'},{title:'双杀 · 势不可挡',en:'DOUBLE KILL',color:'#ffba58'},{title:'三杀 · 钢铁猎手',en:'TRIPLE KILL',color:'#ff8552'},{title:'四杀 · 战场主宰',en:'QUADRA KILL',color:'#ff556a'},{title:'五杀 · 全场制霸',en:'PENTA KILL',color:'#f3d28a'}];
export function killTier(kills){return {...KILL_TIERS[Math.min(5,Math.max(1,kills))-1],count:Math.min(5,Math.max(1,kills))};}
