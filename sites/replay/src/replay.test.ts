import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sampleBall,samplePath,spatialChunks,buildSeats,nearestSeat,beatAt,type ReplayData} from './replay.ts';
const data=JSON.parse(readFileSync(new URL('../public/model/replay.json',import.meta.url),'utf8')) as ReplayData;
test('exported motion reaches home plate and the modeled river landing',()=>{
 assert.deepEqual(sampleBall(data,data.contact).map(n=>n===0?0:n),[0,13,0]);
 assert.deepEqual(sampleBall(data,data.duration),data.landing);
 assert.equal(data.landing[0],142);assert.equal(data.landing[1],0);assert.ok(data.landing[2]<0);
 assert.equal(beatAt(data,data.contact),'Contact');assert.equal(beatAt(data,data.splash+.1),'Into the river');
 const atWater=sampleBall(data,data.waterCrossing);assert.ok(Math.abs(atWater[0]-128)<.001);assert.ok(atWater[1]>0);
});
test('arbitrary seek order preserves the exact same world position',()=>{
 const expected=sampleBall(data,4.273);for(const t of [10.5,0,8.7,1.55,6.001])sampleBall(data,t);
 assert.deepEqual(sampleBall(data,4.273),expected);assert.deepEqual(sampleBall(data,-10),data.ballSamples[0]);
});
test('every bowl and outfield seat survives export with a stable unique ID',()=>{
 const bowl=data.instances.find(g=>g.name==='D2_Individual seats')!;const outfieldGroups=data.instances.filter(g=>g!==bowl&&g.name.toLowerCase().includes('individual seats'));
 const seats=buildSeats([...bowl.points,...outfieldGroups.flatMap(g=>g.points)],bowl.points.length);
 assert.ok(outfieldGroups.length>=1);assert.ok(seats.length>26000);assert.equal(seats.length,data.seatCount);assert.equal(new Set(seats.map(s=>s.id)).size,seats.length);
 assert.equal(seats.filter(s=>s.tier===4).length,outfieldGroups.reduce((n,g)=>n+g.points.length,0));assert.ok(seats.every(s=>s.row>0&&s.number>0));
 const picked=nearestSeat(seats,seats[23001].position);assert.equal(picked.id,23001);
});

test('arrival reaches its versioned entrance with a continuous sampled route',()=>{
 if(data.version<11)return;
 assert.ok(data.arrivalPath);assert.deepEqual(samplePath(data.arrivalPath,1),data.arrivalPath.at(-1));
 const end=samplePath(data.arrivalPath,1);assert.ok(end[2]>-145);assert.ok(data.version>=13?end[1]>15&&end[1]<16:end[1]>22&&end[1]<24);
 let previous=samplePath(data.arrivalPath,0);
 for(let i=1;i<=100;i++){const next=samplePath(data.arrivalPath,i/100);assert.ok(Math.hypot(...next.map((n,k)=>n-previous[k]))<2);previous=next;}
});
test('spatial culling retains every instance exactly once, including outside the bowl',()=>{
 for(const group of data.instances){const chunks=spatialChunks(group.points,35);assert.equal(chunks.flat().length,group.points.length);assert.equal(new Set(chunks.flat()).size,group.points.length);for(const chunk of chunks){for(const axis of [0,1] as const)assert.ok(Math.max(...chunk.map(p=>p[axis]))-Math.min(...chunk.map(p=>p[axis]))<=35);}}
});

test('sloping outfield returns retain their authored rows',()=>{
 if(data.version<13)return;
 for(const [name,maxRows] of [['LF',41],['RF',24]] as const){
  const group=data.instances.find(g=>g.name===`D2_${name} return individual seats`)!;
  assert.ok(group.points.length>1000);
  assert.ok(group.points.every(p=>Number.isFinite(p[9])));
  const seats=buildSeats(group.points,0);
  assert.ok(new Set(seats.map(s=>s.row)).size<=maxRows);
 }
});
