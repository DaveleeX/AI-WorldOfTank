import {GRAVITY,MIN_PITCH,MAX_PITCH,gunSpec,muzzle,lowArcPitch,segmentAABB,shellPosition} from './ballistics.mjs';
export const TANKS = [
 {id:'china',nation:'中国',flag:'🇨🇳',name:'99A',label:'主战坦克',tag:'均衡突击',hp:1200,speed:17,damage:220,reload:2.5,armor:3,color:0x69704a,model:'china'},
 {id:'usa',nation:'美国',flag:'🇺🇸',name:'AbramsX',label:'先进主战坦克',tag:'火力压制',hp:1300,speed:16,damage:240,reload:2.8,armor:4,color:0xa5936c,model:'abrams'},
 {id:'uk',nation:'英国',flag:'🇬🇧',name:'挑战者 2',label:'重装主战坦克',tag:'重装壁垒',hp:1500,speed:13,damage:235,reload:3.0,armor:5,color:0x656952,model:'challenger'},
 {id:'france',nation:'法国',flag:'🇫🇷',name:'勒克莱尔',label:'主战坦克',tag:'快速装填',hp:1000,speed:19,damage:190,reload:1.9,armor:2,color:0x777750,model:'france'},
 {id:'germany',nation:'德国',flag:'🇩🇪',name:'豹 2A7',label:'主战坦克',tag:'精准猎手',hp:1300,speed:16,damage:250,reload:2.8,armor:4,color:0x847557,model:'leopard'},
 {id:'japan',nation:'日本',flag:'🇯🇵',name:'10 式',label:'轻量主战坦克',tag:'机动侧袭',hp:1000,speed:21,damage:195,reload:2.2,armor:2,color:0x58684d,model:'japan'}
];
export const MAPS = [
 {id:'desert',name:'灼热荒原',en:'THE DUSTLANDS',desc:'沙丘 · 油井 · 废弃工业区',color:0xa18a64,sky:0x9d998c,fog:0xb1a187,grip:1},
 {id:'city',name:'破碎之城',en:'FALLEN CITY',desc:'废墟 · 街巷 · 混凝土掩体',color:0x666660,sky:0x7d898b,fog:0x939a96,grip:1},
 {id:'mud',name:'泥泞边境',en:'NO MAN’S LAND',desc:'泥地 · 农舍 · 枯木林',color:0x5d5641,sky:0x879182,fog:0x879182,grip:.78},
 {id:'snow',name:'极寒战线',en:'WHITE SILENCE',desc:'雪原 · 冰川 · 军事哨所',color:0xc3cccb,sky:0x8fa5b4,fog:0xb4c6ce,grip:.88}
];
export const EQUIPMENT={
 barrel:[{name:'标准炮管',price:0,desc:'标准火力',damage:1,reload:1},{name:'长身倍径炮',price:600,desc:'伤害 +20% · 装填慢 8%',damage:1.2,reload:1.08},{name:'速射炮组',price:900,desc:'装填快 25% · 伤害 −5%',damage:.95,reload:.75}],
 tracks:[{name:'标准履带',price:0,desc:'标准机动',speed:1,energy:1},{name:'越野宽履带',price:450,desc:'速度 +15% · 地形减速减半',speed:1.15,energy:1},{name:'涡轮驱动履带',price:850,desc:'速度 +25% · 能量 +40%',speed:1.25,energy:1.4}],
 ammo:[{name:'穿甲弹 AP',price:0,desc:'标准穿甲伤害',damage:1},{name:'尾翼穿甲弹',price:650,desc:'伤害 +25%',damage:1.25},{name:'高爆弹 HE',price:800,desc:'伤害 +10% · 6 米溅射',damage:1.1,splash:6}],
 armor:[{name:'基础复合装甲',price:0,desc:'原车防护',hp:1},{name:'反应装甲 I',price:500,desc:'生命值 +25%',hp:1.25},{name:'复合装甲 II',price:1000,desc:'生命值 +50%',hp:1.5}]
};
export function purchaseEquipment(save,category,index){
 const item=EQUIPMENT[category]?.[index];
 if(!item||!save.owned?.[category])return {ok:false,reason:'invalid'};
 const owned=save.owned[category].includes(index);
 if(!owned&&save.credits<item.price)return {ok:false,reason:'credits'};
 return {ok:true,purchased:!owned,save:{...save,credits:save.credits-(owned?0:item.price),owned:{...save.owned,[category]:owned?save.owned[category]:[...save.owned[category],index]},gear:{...save.gear,[category]:index}}};
}
export function stats(def,gear={}) {let b=EQUIPMENT.barrel[gear.barrel||0],t=EQUIPMENT.tracks[gear.tracks||0],a=EQUIPMENT.ammo[gear.ammo||0],r=EQUIPMENT.armor[gear.armor||0];return {...def,barrel:gear.barrel||0,ammo:gear.ammo||0,muzzleSpeed:gear.barrel===1?180:gear.barrel===2?135:150,hp:Math.round(def.hp*r.hp),damage:Math.round(def.damage*b.damage*a.damage),reload:def.reload*b.reload,speed:def.speed*t.speed,maxEnergy:100*t.energy,splash:a.splash||0,offroad:gear.tracks===1};}
export function makeObstacles(map){let a=[];let seed=42;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};for(let i=0;i<68;i++){let x=(rnd()-.5)*330,z=(rnd()-.5)*290;if(Math.abs(x)<15||Math.abs(z)>110&&Math.abs(x)<65)continue;let building=map==='city'||(map==='mud'&&i%3===0);a.push({x,z,w:building?10+rnd()*10:5+rnd()*10,d:building?10+rnd()*10:5+rnd()*9,h:building?(map==='mud'?4+rnd()*3:8+rnd()*19):3+rnd()*7,type:building?'building':map==='snow'?'ice':'rock',tone:rnd()});}return a.map((o,id)=>({...o,id,hits:0,maxHits:o.type==='building'?(o.h>10?3:2):0}));}
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export function segmentCircle(x,z,dx,dz,cx,cz,r){let a=dx*dx+dz*dz;if(!a)return null;let px=x-cx,pz=z-cz,b=2*(px*dx+pz*dz),c=px*px+pz*pz-r*r,d=b*b-4*a*c;if(d<0)return null;let t=(-b-Math.sqrt(d))/(2*a);return t>=0&&t<=1?t:null;}
export function segmentBox(x,z,dx,dz,o,pad=0){let lo=0,hi=1;for(let [v,d,c,s] of [[x,dx,o.x,o.w/2+pad],[z,dz,o.z,o.d/2+pad]]){if(Math.abs(d)<1e-8){if(v<c-s||v>c+s)return null;}else{let a=(c-s-v)/d,b=(c+s-v)/d;if(a>b)[a,b]=[b,a];lo=Math.max(lo,a);hi=Math.min(hi,b);if(lo>hi)return null;}}return lo;}
export class Battle {
 constructor(tank=0,map=0,gear={}){this.map=MAPS[map];this.obstacles=makeObstacles(this.map.id);this.tanks=[];this.shots=[];this.events=[];this.time=0;this.result=null;this.kills=0;this.heavyUnlocked=false;this.charge=0;this.charging=false;this.damage=0;this.rng=735;for(let team=0;team<2;team++)for(let i=0;i<5;i++){let def=TANKS[team===0&&i===0?tank:(i+team*2)%6];let s=stats(def,team===0&&i===0?gear:{});this.tanks.push({id:team*5+i,team,def,s,x:(i-2)*18,z:team?124:-124,yaw:team?Math.PI:0,aim:team?Math.PI:0,pitch:0,hp:s.hp,energy:s.maxEnergy,reload:i*.22,speed:0,alive:true,avoid:0,stuck:0,phase:i*1.2});}this.player=this.tanks[0];}
 random(){this.rng=(this.rng*1664525+1013904223)>>>0;return this.rng/4294967296;}
 clearLine(a,b){return !this.obstacles.some(o=>segmentBox(a.x,a.z,b.x-a.x,b.z-a.z,o,0)!==null);}
 move(t,dx,dz){let ox=t.x,oz=t.z;const blocked=(x,z)=>Math.abs(x)>176||Math.abs(z)>176||this.obstacles.some(o=>Math.abs(x-o.x)<o.w/2+2.1&&Math.abs(z-o.z)<o.d/2+2.1)||this.tanks.some(v=>v!==t&&v.alive&&Math.hypot(v.x-x,v.z-z)<4.5);if(!blocked(t.x+dx,t.z))t.x+=dx;if(!blocked(t.x,t.z+dz))t.z+=dz;return Math.hypot(t.x-ox,t.z-oz);}
 damageBuilding(o,p){if(o?.type!=='building'||o.destroyed)return; o.hits=(o.hits||0)+1;o.maxHits ||= o.h>10?3:2;o.destroyed=o.hits>=o.maxHits;this.events.push({type:o.destroyed?'collapse':'crack',building:o.id,obstacle:{...o},x:p.x,y:p.y,z:p.z});if(o.destroyed)this.obstacles=this.obstacles.filter(v=>v!==o);}
 cancelCharge(){this.charge=0;this.charging=false;}
 playerFire(dt,input){if(!this.player.alive){this.cancelCharge();return;}if(!this.heavyUnlocked){if(input.fire||input.fireReleased)this.fire(this.player);return;}if(input.fire&&this.player.reload<=0){this.charging=true;this.charge=Math.min(1.2,this.charge+dt);}if(!input.fire&&(this.charging||input.fireReleased)){const heavy=this.charge>=1.2;this.cancelCharge();this.fire(this.player,heavy);}}
 fire(t,heavy=false){if(!t.alive||t.reload>0||this.result)return false;
 heavy=heavy&&t.id===0&&this.heavyUnlocked;t.reload=t.s.reload*(t.id===0?(heavy?1.5:1):1.65);const p=muzzle(t),c=Math.cos(t.pitch),v=t.s.muzzleSpeed;
 // Check the entire gun span, so a muzzle inside/beyond cover cannot shoot through it.
 const base={x:t.x,y:gunSpec(t.def.model,t.s.barrel).height,z:t.z};
 const delta={x:p.x-base.x,y:p.y-base.y,z:p.z-base.z};let obstruction=1,cover=null;
 for(const o of this.obstacles){const u=segmentAABB(base,delta,{x:o.x-o.w/2,y:0,z:o.z-o.d/2},{x:o.x+o.w/2,y:o.h??20,z:o.z+o.d/2});if(u!==null&&u<obstruction){obstruction=u;cover=o;}}
 if(obstruction<1){const p={x:base.x+delta.x*obstruction,y:base.y+delta.y*obstruction,z:base.z+delta.z*obstruction};this.events.push({type:'impact',...p,heavy});this.damageBuilding(cover,p);return true;}
 this.shots.push({...p,dx:Math.sin(t.aim)*c*v,dy:Math.sin(t.pitch)*v,dz:Math.cos(t.aim)*c*v,owner:t.id,team:t.team,heavy,damage:t.s.damage*(t.id===0?(heavy?2.5:1):.58),splash:t.s.splash,life:8,ammo:t.s.ammo});
 this.events.push({type:'fire',...p,owner:t.id,heavy});return true;}

 hit(v,d,owner){if(!v.alive)return;let damage=Math.min(v.hp,d);v.hp=Math.max(0,v.hp-d);if(owner===0)this.damage+=damage;this.events.push({type:'hit',x:v.x,z:v.z,damage:Math.round(d),target:v.id,owner});if(v.hp<=0){v.alive=false;v.speed=0;if(v.id===0)this.cancelCharge();if(owner===0){this.kills++;if(this.kills===2){this.heavyUnlocked=true;this.events.push({type:'skillUnlock'});}}this.events.push({type:'kill',x:v.x,z:v.z,target:v.id,owner,kills:owner===0?this.kills:0});}}
 update(dt,input={}){if(this.result)return;dt=Math.min(dt,.05);this.time+=dt;for(let t of this.tanks){if(!t.alive)continue;if(t.stun>0){t.stun=Math.max(0,t.stun-dt);t.speed=0;continue;}t.reload=Math.max(0,t.reload-dt);if(t.id===0){t.aim=input.aim??t.aim;t.pitch=clamp(input.pitch??t.pitch,MIN_PITCH,MAX_PITCH);let turn=(input.left?1:0)-(input.right?1:0);t.yaw+=turn*1.55*dt;let throttle=(input.forward?1:0)-(input.back?1:0);let boost=input.boost&&t.energy>0&&throttle>0;t.energy=clamp(t.energy+(boost?-30:18)*dt,0,t.s.maxEnergy);let grip=t.s.offroad?(1+this.map.grip)/2:this.map.grip;let desired=throttle*t.s.speed*grip*(boost?1.65:1)*(throttle<0?.6:1);t.speed+=(desired-t.speed)*Math.min(1,dt*4);this.move(t,Math.sin(t.yaw)*t.speed*dt,Math.cos(t.yaw)*t.speed*dt);this.playerFire(dt,input);
 }else{let enemies=this.tanks.filter(v=>v.team!==t.team&&v.alive);enemies.sort((a,b)=>Math.hypot(a.x-t.x,a.z-t.z)-Math.hypot(b.x-t.x,b.z-t.z));let target=enemies.find(v=>this.clearLine(t,v))||enemies[0];if(!target)continue;let dx=target.x-t.x,dz=target.z-t.z,dist=Math.hypot(dx,dz);let visible=this.clearLine(t,target);t.aim=Math.atan2(dx,dz);const gun=gunSpec(t.def.model,t.s.barrel);t.pitch=clamp(lowArcPitch(Math.max(1,dist-gun.fore-gun.length),1.65-gun.height,t.s.muzzleSpeed)??0,MIN_PITCH,MAX_PITCH);if(visible&&dist<135&&t.reload<=0){let aim=t.aim;t.aim+=(this.random()-.5)*.06;this.fire(t);t.aim=aim;}
 let desired=t.aim;if(t.avoid>0){t.avoid-=dt;desired=t.avoidYaw;}else if(dist<45&&visible)desired+=Math.PI/2*(t.id%2?1:-1);let da=Math.atan2(Math.sin(desired-t.yaw),Math.cos(desired-t.yaw));t.yaw+=clamp(da,-1.25*dt,1.25*dt);t.speed=t.s.speed*.65*this.map.grip*(dist<26&&visible?.4:1);let moved=this.move(t,Math.sin(t.yaw)*t.speed*dt,Math.cos(t.yaw)*t.speed*dt);if(moved<dt*.5){t.stuck+=dt;if(t.stuck>.3){t.avoidYaw=t.yaw+(t.id%2?1:-1)*(1.3+this.random());t.avoid=1.7;t.stuck=0;}}else t.stuck=0;}}
 for(const s of this.shots){if(s.life<=0)continue;
 // Integrate the parabola in short swept segments; vertical error <0.001 m at 120 Hz.
 let remaining=dt;while(remaining>1e-8&&s.life>0){const h=Math.min(remaining,1/120);remaining-=h;const next=shellPosition(s,h),d={x:next.x-s.x,y:next.y-s.y,z:next.z-s.z};let min=1,target=null,cover=null,impact=false;
 for(const o of this.obstacles){const u=segmentAABB(s,d,{x:o.x-o.w/2,y:0,z:o.z-o.d/2},{x:o.x+o.w/2,y:o.h??20,z:o.z+o.d/2});if(u!==null&&u<=min){min=u;impact=true;target=null;cover=o;}}
 for(const t of this.tanks){if(!t.alive||t.team===s.team)continue;const cy=Math.cos(t.yaw),sy=Math.sin(t.yaw),px=s.x-t.x,pz=s.z-t.z;const local={x:px*cy-pz*sy,y:s.y,z:px*sy+pz*cy},ld={x:d.x*cy-d.z*sy,y:d.y,z:d.x*sy+d.z*cy};
 const u=segmentAABB(local,ld,{x:-2.05,y:.1,z:-2.65},{x:2.05,y:2.85,z:2.65});if(u!==null&&u<min){min=u;target=t;cover=null;impact=true;}}
 if(next.y<=0&&s.y>=0){const u=s.y/(s.y-next.y);if(u<=min){min=u;target=null;cover=null;impact=true;}}
 s.x+=d.x*min;s.y+=d.y*min;s.z+=d.z*min;s.dy-=GRAVITY*h;s.life-=h;
 if(impact){s.life=0;this.events.push({type:'impact',x:s.x,y:Math.max(0,s.y),z:s.z,heavy:s.heavy});if(target){this.hit(target,s.damage,s.owner);if(s.heavy&&target.alive){target.stun=1;target.speed=0;this.events.push({type:'stun',target:target.id,x:target.x,z:target.z});}}if(cover)this.damageBuilding(cover,s);
 if(s.splash)for(const t of this.tanks)if(t!==target&&t.alive&&t.team!==s.team&&Math.hypot(t.x-s.x,t.z-s.z,1.5-s.y)<s.splash&&this.clearLine({x:s.x,z:s.z},t))this.hit(t,s.damage*.45,s.owner);}
 }}
 this.shots=this.shots.filter(s=>s.life>0);let allies=this.tanks.some(t=>t.team===0&&t.alive),enemies=this.tanks.some(t=>t.team===1&&t.alive);if(!enemies||!allies){this.result=!enemies?'victory':'defeat';this.reward=this.result==='victory'?500+this.kills*100:0;this.events.push({type:'end',result:this.result});}}
 drain(){return this.events.splice(0);}
}
