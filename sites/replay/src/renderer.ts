import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { sampleBall, samplePath, spatialChunks, type ReplayData, type Seat } from './replay';

export type CameraView='overview'|'home'|'upper'|'left_center'|'boat'|'follow'|'arrival'|'riverwalk'|'seat';
export const viewCopy:Record<Exclude<CameraView,'seat'>,{title:string;description:string}>={
 overview:{title:'The whole flight',description:'One hit. The ballpark, the skyline, and the river beyond.'},
 home:{title:'Behind the plate',description:'Watch contact, then follow the ball above right field.'},
 upper:{title:'Above the diamond',description:'A modeled upper-deck seat, with the city beyond the bowl.'},
 left_center:{title:'Left-center terrace',description:'The raised arrival park opens toward the field.'},
 boat:{title:'On the river',description:'The quay hides the field. Watch the ball emerge above it.'},
 follow:{title:'Follow the ball',description:'An impossible camera, for a perspective only a replay can give.'},
 riverwalk:{title:'Along the riverwalk',description:'Brick arches, café fronts and broad steps along the water.'},
 arrival:{title:'Off Roosevelt',description:'Approach through the raised park while the same play unfolds.'},
};
const up=new THREE.Vector3(0,1,0);
const vector=(p:readonly number[])=>new THREE.Vector3(p[0],p[1],p[2]);
const smooth=(u:number)=>{const t=THREE.MathUtils.clamp(u,0,1);return t*t*(3-2*t);};

export class ReplayRenderer {
 readonly renderer:THREE.WebGLRenderer;
 readonly scene=new THREE.Scene();
 readonly camera=new THREE.PerspectiveCamera(48,1,.08,18000);
 readonly controls:OrbitControls;
 readonly ball=new THREE.Mesh(new THREE.SphereGeometry(.11,14,8),new THREE.MeshBasicMaterial({color:0xfff1d5}));
 readonly crowd=new THREE.Group();
 readonly trail:THREE.Line;
 readonly rings:THREE.Mesh[]=[];
 readonly viewport:HTMLElement;
 readonly locator=document.createElement('div');
 view:CameraView='overview';
 seat:Seat|undefined;
 trackBall=true;
 showTrail=true;
 private mixer:THREE.AnimationMixer|undefined;
 private data:ReplayData;
 private gaze=new THREE.Vector2();
 private pointers=new Map<number,THREE.Vector2>();
 private pinchDistance=0;
 private lastTime=0;
 private frames=0;
 private fpsStart=performance.now();
 private markers:THREE.Mesh[]=[];
 private venue:THREE.Object3D|undefined;
 private instanceTransform=new THREE.Object3D();
 private baseMatrices=new Map<THREE.InstancedMesh,THREE.Matrix4[]>();
 private selectedHidden=new Map<THREE.InstancedMesh,number[]>();
 constructor(viewport:HTMLElement,data:ReplayData){
  this.data=data;this.viewport=viewport;
  this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance',logarithmicDepthBuffer:true});
  this.renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<800?1.25:1.5));
  this.renderer.setClearColor(0xb7cdd7);
  this.renderer.outputColorSpace=THREE.SRGBColorSpace;
  this.renderer.toneMapping=THREE.ACESFilmicToneMapping;
  this.renderer.toneMappingExposure=1.05;
  this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=THREE.PCFShadowMap;this.renderer.shadowMap.autoUpdate=false;
  viewport.append(this.renderer.domElement);this.locator.className='ball-locator';this.locator.setAttribute('aria-hidden','true');viewport.append(this.locator);
  this.scene.fog=new THREE.Fog(0xb7cdd7,2200,11000);
  const ambient=new THREE.HemisphereLight(0xe2efff,0x665b47,2.3);this.scene.add(ambient);
  const sun=new THREE.DirectionalLight(0xffedd0,3.1);sun.position.set(-150,320,140);sun.target.position.set(20,10,-45);sun.castShadow=true;
  sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-230;sun.shadow.camera.right=230;sun.shadow.camera.top=230;sun.shadow.camera.bottom=-230;
  sun.shadow.camera.near=1;sun.shadow.camera.far=800;sun.shadow.bias=-.0003;sun.shadow.normalBias=.12;this.scene.add(sun,sun.target);
  this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.enableDamping=false;this.controls.minDistance=10;this.controls.maxDistance=1200;this.controls.maxPolarAngle=Math.PI*.495;
  this.ball.renderOrder=1000;this.scene.add(this.ball,this.crowd);
  const points=data.ballSamples.slice(Math.ceil(data.contact*data.sampleRate),Math.floor(data.splash*data.sampleRate)+1).map(vector);
  const geometry=new THREE.BufferGeometry().setFromPoints(points);geometry.setDrawRange(0,0);
  this.trail=new THREE.Line(geometry,new THREE.LineBasicMaterial({color:0xffc367,transparent:true,opacity:.85}));this.trail.frustumCulled=false;this.scene.add(this.trail);
  for(let i=0;i<3;i++){const ring=new THREE.Mesh(new THREE.RingGeometry(.92,1,64),new THREE.MeshBasicMaterial({color:0xe5f4ec,transparent:true,opacity:.8,side:THREE.DoubleSide,depthWrite:false}));ring.rotation.x=-Math.PI/2;ring.position.copy(vector(data.landing));ring.position.y=.12+i*.01;this.scene.add(ring);this.rings.push(ring);}
  for(let i=0;i<24;i++){const drop=new THREE.Mesh(new THREE.SphereGeometry(.12,5,3),new THREE.MeshBasicMaterial({color:0xd8e9e7}));this.scene.add(drop);this.markers.push(drop);}
  new ResizeObserver(()=>this.resize()).observe(viewport);this.resize();this.setView('overview');this.bindLook();
 }
 async load(onProgress:(message:string,percent:number)=>void):Promise<void>{
  const draco=new DRACOLoader();draco.setDecoderPath(new URL('draco/',document.baseURI).href);draco.setWorkerLimit(2);
  const loader=new GLTFLoader();loader.setDRACOLoader(draco);
  onProgress('Loading the ballpark and skyline…',10);
  const venue=await loader.loadAsync(new URL('model/venue.glb',document.baseURI).href,event=>{if(event.total)onProgress('Loading the ballpark and skyline…',10+60*event.loaded/event.total);});
  this.venue=venue.scene;
  const prototypes=new Map<string,THREE.Object3D>();
  venue.scene.traverse(node=>{if(typeof node.userData.prototypeName==='string')prototypes.set(node.userData.prototypeName,node);});
  for(const p of prototypes.values())p.removeFromParent();
  venue.scene.traverse(node=>{if(node instanceof THREE.Mesh){node.castShadow=true;node.receiveShadow=true;}});
  this.scene.add(venue.scene);onProgress('Placing the modeled seats…',76);this.addInstances(prototypes);
  const actors=await loader.loadAsync(new URL('model/actors.glb',document.baseURI).href);
  this.scene.add(actors.scene);actors.scene.traverse(node=>{if(node instanceof THREE.Mesh){node.castShadow=false;node.receiveShadow=true;}});
  this.mixer=new THREE.AnimationMixer(actors.scene);
  for(const clip of actors.animations)this.mixer.clipAction(clip).play();
  if(!actors.animations.length)throw new Error('The authored player animation is missing');
  this.viewport.dataset.animationClips=String(actors.animations.length);
  this.viewport.dataset.seatCount=String(this.data.seatCount);
  this.renderer.shadowMap.needsUpdate=true;
  onProgress('Your view is ready.',100);this.render(0);draco.dispose();
 }
 private addInstances(prototypes:Map<string,THREE.Object3D>):void{
  const seatBase=new THREE.BoxGeometry(.43,.08,.40);seatBase.translate(0,.43,0);
  const seatBack=new THREE.BoxGeometry(.44,.44,.07);seatBack.translate(0,.69,-.18);
  const seatGeometry=mergeGeometries([seatBase,seatBack]);
  if(!seatGeometry)throw new Error('Could not construct the browser seat prototype');
  const bodyGeometry=new THREE.IcosahedronGeometry(1,0);bodyGeometry.scale(.20,.29,.14);bodyGeometry.translate(0,.79,0);
  const headGeometry=new THREE.IcosahedronGeometry(.11,0);headGeometry.translate(0,1.16,0);
  const standingBody=bodyGeometry.clone();standingBody.translate(0,.44,0);
  const standingHead=headGeometry.clone();standingHead.translate(0,.45,0);
  const leftLeg=new THREE.CylinderGeometry(.065,.055,.98,6);leftLeg.translate(-.10,.50,0);
  const rightLeg=new THREE.CylinderGeometry(.065,.055,.98,6);rightLeg.translate(.10,.50,0);
  const legs=mergeGeometries([leftLeg,rightLeg]);if(!legs)throw new Error('Could not construct visitor legs');
  const crowdColors=[0x172129,0xc8c8bd,0x586363,0x253342,0x2b5572,0x864137];
  for(const source of this.data.instances){
   for(const points of spatialChunks(source.points,source.prototype.toLowerCase().includes('tree')?80:35)){
   const group={...source,points};
   const isSeat=group.name.toLowerCase().includes('individual seats'),isFan=group.name.toLowerCase().includes('spectators'),isTree=group.prototype.toLowerCase().includes('tree');
   if(isTree){
    const prototype=prototypes.get(group.prototype);if(!prototype)continue;
    prototype.updateMatrixWorld(true);
    prototype.traverse(node=>{if(!(node instanceof THREE.Mesh))return;
     const mesh=new THREE.InstancedMesh(node.geometry,node.material,group.points.length);
     for(let i=0;i<group.points.length;i++){const p=group.points[i];this.instanceTransform.position.set(p[0],p[2],-p[1]);this.instanceTransform.rotation.set(0,p[5],0);this.instanceTransform.scale.set(p[6],p[8],p[7]);this.instanceTransform.updateMatrix();mesh.setMatrixAt(i,this.instanceTransform.matrix.clone().multiply(node.matrixWorld));}
     mesh.computeBoundingSphere();mesh.receiveShadow=true;this.scene.add(mesh);
    });continue;
   }
   const geometries=isSeat?[seatGeometry]:isFan?[bodyGeometry,headGeometry]:[standingBody,standingHead,legs];
   for(let part=0;part<geometries.length;part++){
    const color=isSeat?0x263d38:part===1?0xb38d72:part===2?0x25313b:crowdColors[Number(group.name.match(/\d$/)?.[0]??3)%crowdColors.length];
    const mesh=new THREE.InstancedMesh(geometries[part],new THREE.MeshLambertMaterial({color}),group.points.length);mesh.name=group.name+(part?' heads':'');
    const matrices:THREE.Matrix4[]=[];
    group.points.forEach((p,i)=>{this.instanceTransform.position.set(p[0],p[2],-p[1]);this.instanceTransform.rotation.set(0,p[5],0);this.instanceTransform.scale.set(p[6],p[8],p[7]);this.instanceTransform.updateMatrix();mesh.setMatrixAt(i,this.instanceTransform.matrix);if(!isSeat)matrices.push(this.instanceTransform.matrix.clone());});
    mesh.receiveShadow=true;mesh.computeBoundingSphere();
    if(isSeat)this.scene.add(mesh);else this.crowd.add(mesh);
    if(!isSeat)this.baseMatrices.set(mesh,matrices);
   }
   }
  }
 }
 private resize():void{const width=this.viewport.clientWidth,height=this.viewport.clientHeight;this.renderer.setSize(width,height,false);this.camera.aspect=width/height;this.camera.updateProjectionMatrix();}
 setView(view:CameraView,seat?:Seat):void{
  this.view=view;this.seat=seat;this.gaze.set(0,0);this.camera.fov=view==='overview'?48:57;this.camera.updateProjectionMatrix();this.controls.enabled=view==='overview';
  if(view==='overview'){this.camera.position.set(232,170,140);this.controls.target.set(48,24,-43);this.controls.update();}
  this.hideForegroundPeople(seat);
 }
 private hideForegroundPeople(seat:Seat|undefined):void{
  for(const [mesh,indices] of this.selectedHidden){const matrices=this.baseMatrices.get(mesh)!;for(const i of indices)mesh.setMatrixAt(i,matrices[i]);mesh.instanceMatrix.needsUpdate=true;}
  this.selectedHidden.clear();
  const path=this.view==='arrival'?this.data.arrivalPath:this.view==='riverwalk'?[[121,5.95,-205],[121,5.95,-270]]:undefined;
  if(!seat&&!path)return;
  const p=new THREE.Vector3();
  for(const [mesh,matrices] of this.baseMatrices){
   const hidden:number[]=[];
   for(let i=0;i<matrices.length;i++){
    p.setFromMatrixPosition(matrices[i]);
    let close=!!seat&&Math.hypot(p.x-seat.position[0],p.z-seat.position[2])<.5&&Math.abs(p.y-(seat.position[1]-1.2))<.1;
    if(path)for(let k=1;k<path.length&&!close;k++){
     const a=path[k-1],b=path[k];const dx=b[0]-a[0],dz=b[2]-a[2];const u=THREE.MathUtils.clamp(((p.x-a[0])*dx+(p.z-a[2])*dz)/(dx*dx+dz*dz),0,1);
     close=Math.hypot(p.x-a[0]-dx*u,p.z-a[2]-dz*u)<8&&Math.abs(p.y-(a[1]+(b[1]-a[1])*u-1.7))<3;
    }
    if(close){mesh.setMatrixAt(i,matrices[i].clone().scale(new THREE.Vector3(0,0,0)));hidden.push(i);}
   }
   if(hidden.length){this.selectedHidden.set(mesh,hidden);mesh.instanceMatrix.needsUpdate=true;}
  }
 }
 private bindLook():void{
  const canvas=this.renderer.domElement;
  canvas.addEventListener('pointerdown',e=>{if(this.view==='overview')return;canvas.setPointerCapture(e.pointerId);this.pointers.set(e.pointerId,new THREE.Vector2(e.clientX,e.clientY));this.pinchDistance=0;});
  canvas.addEventListener('pointermove',e=>{const previous=this.pointers.get(e.pointerId);if(!previous||this.view==='overview')return;
   const current=new THREE.Vector2(e.clientX,e.clientY);
   if(this.pointers.size===1){this.gaze.x-=(current.x-previous.x)*.004;this.gaze.y+=(current.y-previous.y)*.003;this.gaze.y=THREE.MathUtils.clamp(this.gaze.y,-1.2,1.2);}
   this.pointers.set(e.pointerId,current);
   if(this.pointers.size===2){const [a,b]=[...this.pointers.values()];const distance=a.distanceTo(b);if(this.pinchDistance)this.camera.fov=THREE.MathUtils.clamp(this.camera.fov*this.pinchDistance/distance,25,90);this.pinchDistance=distance;this.camera.updateProjectionMatrix();}
  });
  const release=(e:PointerEvent)=>{this.pointers.delete(e.pointerId);this.pinchDistance=0;};canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
  canvas.addEventListener('wheel',e=>{if(this.view==='overview')return;e.preventDefault();this.camera.fov=THREE.MathUtils.clamp(this.camera.fov+e.deltaY*.035,25,90);this.camera.updateProjectionMatrix();},{passive:false});
 }
 render(time:number):void{
  const ballPosition=vector(sampleBall(this.data,time));this.ball.position.copy(ballPosition);
  this.ball.visible=time<this.data.splash;
  this.trail.visible=this.showTrail;this.trail.geometry.setDrawRange(0,time<this.data.contact?0:Math.min(this.trail.geometry.attributes.position.count,Math.floor((time-this.data.contact)*this.data.sampleRate)+1));
  const splashAge=time-this.data.splash;
  this.rings.forEach((ring,i)=>{const age=splashAge-i*.13;ring.visible=age>=0&&age<2;ring.scale.setScalar(1+Math.max(0,age)*4);(ring.material as THREE.MeshBasicMaterial).opacity=Math.max(0,.85-age*.4);});
  this.markers.forEach((drop,i)=>{const age=splashAge;drop.visible=age>=0&&age<.8;if(drop.visible){const angle=i*2.39996,velocity=1.8+(i%4)*.4;drop.position.set(this.data.landing[0]+Math.cos(angle)*age*velocity,Math.max(.05,age*4-age*age*6),this.data.landing[2]+Math.sin(angle)*age*velocity);}});
  this.mixer?.setTime(Math.min(time,this.data.duration-.001));
  if(this.view!=='overview'){
   let aim=this.trackBall?ballPosition.clone():new THREE.Vector3(15,15,-22);
   if((this.view==='seat'||this.view==='home'||this.view==='upper')&&this.seat)this.camera.position.copy(vector(this.seat.position));
   if(this.view==='left_center')this.camera.position.set(53,23.42,-135);
   if(this.view==='boat'){this.camera.position.set(181,2.6+.06*Math.sin(time*.7),-8-time*1.2);if(!this.trackBall)aim.set(60,24,-24);}
   if(this.view==='arrival'){
    if(this.data.arrivalPath)this.camera.position.copy(vector(samplePath(this.data.arrivalPath,smooth(time/this.data.duration))));
    else{const y=294-67*smooth(time/this.data.duration);this.camera.position.set(50,14.1+.045*(300-y)+1.7,-y);}
    aim.set(45,18,-105);
   }
   if(this.view==='riverwalk'){const y=205+65*smooth(time/this.data.duration);this.camera.position.set(121,5.95,-y);aim.set(92,10,-y-12);}
   if(this.view==='follow'){
    if(time<this.data.contact){this.camera.position.set(-9,17,12);aim.set(0,13,0);}
    else{this.camera.position.copy(ballPosition).add(new THREE.Vector3(-15,5,7));this.camera.position.y=Math.max(12,this.camera.position.y);aim.copy(ballPosition).add(new THREE.Vector3(6,-1,-1));}
   }
   if(this.trackBall&&['seat','home','upper','left_center'].includes(this.view)){
    const weight=.48*smooth((time-this.data.contact)/.7);aim.lerp(new THREE.Vector3(30,15,-30),weight);
    const horizontal=Math.hypot(aim.x-this.camera.position.x,aim.z-this.camera.position.z);aim.y=Math.min(aim.y,this.camera.position.y+Math.tan(25*Math.PI/180)*horizontal);
   }
   const direction=aim.sub(this.camera.position).normalize();direction.applyAxisAngle(up,this.gaze.x);const right=new THREE.Vector3().crossVectors(direction,up).normalize();direction.applyAxisAngle(right,this.gaze.y);this.camera.lookAt(this.camera.position.clone().add(direction));
  }
  const markerScale=THREE.MathUtils.clamp(this.camera.position.distanceTo(ballPosition)*.026,1,14);this.ball.scale.setScalar(markerScale);
  this.renderer.render(this.scene,this.camera);this.lastTime=time;

  this.frames++;const elapsed=performance.now()-this.fpsStart;if(elapsed>1500){this.viewport.dataset.fps=(1000*this.frames/elapsed).toFixed(1);this.frames=0;this.fpsStart=performance.now();}
  this.viewport.dataset.fov=this.camera.fov.toFixed(1);this.viewport.dataset.time=time.toFixed(3);this.viewport.dataset.ball=ballPosition.toArray().map(n=>n.toFixed(3)).join(',');this.viewport.dataset.camera=this.view;this.viewport.dataset.cameraPosition=this.camera.position.toArray().map(n=>n.toFixed(3)).join(',');const projected=ballPosition.clone().project(this.camera);this.locator.hidden=!this.showTrail||time>=this.data.splash||projected.z>1||Math.abs(projected.x)>1||Math.abs(projected.y)>1;this.locator.style.left=`${(projected.x+1)*this.viewport.clientWidth/2}px`;this.locator.style.top=`${(1-projected.y)*this.viewport.clientHeight/2}px`;this.viewport.dataset.triangles=String(this.renderer.info.render.triangles);
 }
 get time():number{return this.lastTime;}
 get triangleCount():number{return this.renderer.info.render.triangles;}
 get loaded():boolean{return this.venue!==undefined;}
}
