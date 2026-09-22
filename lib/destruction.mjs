import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

// Partition the shipped Blender geometry, preserving its UVs and original silhouette.
// Terrain stays baked; movable building fragments use live lighting only.
export function partitionBuildings(environment, obstacles) {
  const buildings = new Map(obstacles.filter(o=>o.type==='building').map(o=>[o.id,{o,pieces:[],cracks:new THREE.Group(),hits:0}]));
  const candidates=[...buildings.values()];
  environment.updateMatrixWorld(true);
  const meshes=[];environment.traverse(o=>{if(o.isMesh)meshes.push(o)});
  for(const mesh of meshes){
    const source=(mesh.geometry.index?mesh.geometry.toNonIndexed():mesh.geometry.clone()).applyMatrix4(mesh.matrixWorld);
    const p=source.attributes.position, buckets=new Map();
    for(let i=0;i<p.count;i+=3){
      const x=(p.getX(i)+p.getX(i+1)+p.getX(i+2))/3,y=(p.getY(i)+p.getY(i+1)+p.getY(i+2))/3,z=(p.getZ(i)+p.getZ(i+1)+p.getZ(i+2))/3;
      const b=y>.12?candidates.find(({o})=>Math.abs(x-o.x)<o.w/2+.65&&Math.abs(z-o.z)<o.d/2+.65&&y<o.h+3):null;
      const cell=b?`${b.o.id}:${x>b.o.x?1:0}:${z>b.o.z?1:0}:${Math.min(2,Math.floor(y/(b.o.h+3)*3))}`:'static';
      if(!buckets.has(cell))buckets.set(cell,{indices:[],b});buckets.get(cell).indices.push(i,i+1,i+2);
    }
    for(const [key,{indices,b}] of buckets){
      const geometry=new THREE.BufferGeometry();
      for(const [name,attr] of Object.entries(source.attributes)){
        const values=new attr.array.constructor(indices.length*attr.itemSize);
        indices.forEach((idx,j)=>{for(let k=0;k<attr.itemSize;k++)values[j*attr.itemSize+k]=attr.array[idx*attr.itemSize+k]});
        geometry.setAttribute(name,new THREE.BufferAttribute(values,attr.itemSize,attr.normalized));
      }
      const material=mesh.material.clone();
      // Texture ownership is separate because the static source will be disposed.
      for(const [name,value] of Object.entries(material))if(value?.isTexture)material[name]=value.clone();
      if(b){material.lightMap?.dispose();material.lightMap=null;material.onBeforeCompile=()=>{};material.customProgramCacheKey=()=> 'dynamic-building';material.side=THREE.DoubleSide;}
      const part=new THREE.Mesh(geometry,material);part.castShadow=true;part.receiveShadow=true;
      if(b){geometry.computeBoundingBox();const center=geometry.boundingBox.getCenter(new THREE.Vector3());geometry.translate(-center.x,-center.y,-center.z);part.position.copy(center);part.layers.enable(1);b.pieces.push(part);}
      environment.add(part);
    }
    source.dispose();mesh.removeFromParent();mesh.geometry.dispose();for(const v of Object.values(mesh.material))if(v?.isTexture)v.dispose();mesh.material.dispose();
  }
  for(const b of buildings.values()){
    environment.add(b.cracks);
    // Intact buildings need one draw, not a draw for every future fragment.
    if(b.pieces.length){const geos=b.pieces.map(m=>{m.updateMatrix();m.visible=false;return m.geometry.clone().applyMatrix4(m.matrix)});const geo=mergeGeometries(geos);geos.forEach(g=>g.dispose());if(geo){b.intact=new THREE.Mesh(geo,b.pieces[0].material);b.intact.castShadow=true;b.intact.receiveShadow=true;b.intact.layers.enable(1);environment.add(b.intact);}else b.pieces.forEach(m=>m.visible=true);}
  }
  return buildings;
}

export class BuildingDestruction {
  constructor(buildings,world){this.buildings=buildings;this.world=world;this.clouds=[];}
  hit(e){const b=this.buildings.get(e.building);if(!b||b.collapsed)return;
    b.hits=e.obstacle.hits;
    if(e.type==='collapse'){
      b.collapsed=true;b.time=0;b.cracks.visible=false;if(b.intact){b.intact.removeFromParent();b.intact.geometry.dispose();b.intact=null;}
      for(const m of b.pieces){m.visible=true;m.userData.velocity=new THREE.Vector3((m.position.x-b.o.x)*.65,1+Math.random()*3,(m.position.z-b.o.z)*.65);m.userData.spin=new THREE.Vector3(Math.random()-.5,Math.random()-.5,Math.random()-.5);}
      this.dust(b.o.x,.6,b.o.z,Math.max(b.o.w,b.o.d)*.45,22);
    }else{
      this.crack(b,e);this.dust(e.x,e.y,e.z,1.3,5);
    }
  }
  crack(b,e){
    const {o}=b;const material=new THREE.MeshBasicMaterial({color:0x171512,side:THREE.DoubleSide});
    // Branching, widening fissures on the original outer wall surfaces.
    for(const axis of ['x','z'])for(const sign of [-1,1])for(let branch=0;branch<2;branch++){
      const vertices=[],height=Math.min(o.h,3+b.hits*5),steps=10;
      for(let i=0;i<steps;i++){
        const point=j=>{const y=.15+j/steps*height;const lateral=Math.sin(j*2.4+branch)*.24+(branch?j*.08:-j*.08);return axis==='x'?new THREE.Vector3(o.x+sign*(o.w/2+.018),y,o.z+lateral):new THREE.Vector3(o.x+lateral,y,o.z+sign*(o.d/2+.018));};
        const a=point(i),c=point(i+1),offset=axis==='x'?new THREE.Vector3(0,0,.035*b.hits):new THREE.Vector3(.035*b.hits,0,0);
        for(const v of [a.clone().sub(offset),a.clone().add(offset),c.clone().add(offset),a.clone().sub(offset),c.clone().add(offset),c.clone().sub(offset)])vertices.push(v.x,v.y,v.z);
      }
      const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));b.cracks.add(new THREE.Mesh(geo,material));
    }
  }
  dust(x,y,z,size,count){
    // Bounded transparent dust, lit by the current map's live lights.
    while(this.clouds.length+count>100){const old=this.clouds.shift();old.mesh.removeFromParent();old.mesh.geometry.dispose();old.mesh.material.dispose();}
    for(let i=0;i<count;i++){
      const m=new THREE.Mesh(new THREE.IcosahedronGeometry(1,1),new THREE.MeshStandardMaterial({color:0x968b79,transparent:true,opacity:.32,depthWrite:false,roughness:1}));
      m.layers.enable(1);m.position.set(x+(Math.random()-.5)*size,y+Math.random()*size*.3,z+(Math.random()-.5)*size);m.scale.setScalar(size*(.22+Math.random()*.2));this.world.add(m);
      this.clouds.push({mesh:m,life:3,max:3,v:new THREE.Vector3((Math.random()-.5)*size,1+Math.random()*2,(Math.random()-.5)*size)});
    }
  }
  update(dt){
    for(const b of this.buildings.values())if(b.collapsed&&!b.settled){
      b.time+=dt;
      for(const m of b.pieces){const v=m.userData.velocity;v.y-=17*dt;m.position.addScaledVector(v,dt);m.rotation.x+=m.userData.spin.x*dt;m.rotation.z+=m.userData.spin.z*dt;
        // Flatten into a shallow rubble bed; the cleared footprint is driveable.
        const flatten=THREE.MathUtils.smoothstep(b.time,1,2.8);m.scale.y=1-flatten*.96;
        const floor=.08+(m.geometry.boundingBox.max.y-m.geometry.boundingBox.min.y)*m.scale.y*.5;
        if(m.position.y<floor){m.position.y=floor;v.y=Math.abs(v.y)*.12;v.x*=Math.exp(-dt*8);v.z*=Math.exp(-dt*8);m.rotation.x*=Math.exp(-dt*8);m.rotation.z*=Math.exp(-dt*8);}
      }
      if(b.time>3.5){b.settled=true;
        // Collapse settled geometry to one draw per original material.
        const groups=new Map();for(const m of b.pieces){m.updateMatrix();const key=m.material.map?.image; if(!groups.has(key))groups.set(key,[]);groups.get(key).push(m);}
        for(const pieces of groups.values()){
          const geos=pieces.map(m=>m.geometry.clone().applyMatrix4(m.matrix));const geo=mergeGeometries(geos);geos.forEach(g=>g.dispose());if(!geo)continue;
          const rubble=new THREE.Mesh(geo,pieces[0].material);rubble.receiveShadow=true;rubble.castShadow=true;rubble.layers.enable(1);pieces[0].parent.add(rubble);
          for(const m of pieces){m.removeFromParent();m.geometry.dispose();if(m.material!==rubble.material){for(const v of Object.values(m.material))if(v?.isTexture)v.dispose();m.material.dispose();}}
        }b.pieces=[];
      }
    }
    for(const c of this.clouds){c.life-=dt;c.mesh.position.addScaledVector(c.v,dt);c.mesh.scale.multiplyScalar(1+dt*.5);c.mesh.material.opacity=.32*Math.max(0,c.life/c.max);if(c.life<=0){c.mesh.removeFromParent();c.mesh.geometry.dispose();c.mesh.material.dispose();}}
    this.clouds=this.clouds.filter(c=>c.life>0);
  }
}
