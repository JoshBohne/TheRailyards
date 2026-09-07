import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sampleBall,buildSeats,nearestSeat,beatAt,type ReplayData} from './replay.ts';
const data=JSON.parse(readFileSync(new URL('../public/model/replay.json',import.meta.url),'utf8')) as ReplayData;
test('exported motion reaches home plate and the modeled river landing',()=>{
 assert.deepEqual(sampleBall(data,data.contact).map(n=>n===0?0:n),[0,13,0]);
 assert.deepEqual(sampleBall(data,data.duration),[142,0,-30]);
 assert.equal(beatAt(data,data.contact),'Contact');assert.equal(beatAt(data,data.splash+.1),'Into the river');
 const atWater=sampleBall(data,data.waterCrossing);assert.ok(Math.abs(atWater[0]-128)<.001);assert.ok(atWater[1]>0);
});
test('arbitrary seek order preserves the exact same world position',()=>{
 const expected=sampleBall(data,4.273);for(const t of [10.5,0,8.7,1.55,6.001])sampleBall(data,t);
 assert.deepEqual(sampleBall(data,4.273),expected);assert.deepEqual(sampleBall(data,-10),data.ballSamples[0]);
});
test('every bowl and outfield seat survives export with a stable unique ID',()=>{
 const bowl=data.instances.find(g=>g.name==='D2_Individual seats')!;const outfield=data.instances.find(g=>g.name==='D2_Outfield individual seats')!;
 const seats=buildSeats([...bowl.points,...outfield.points],bowl.points.length);
 assert.equal(seats.length,26950);assert.equal(seats.length,data.seatCount);assert.equal(new Set(seats.map(s=>s.id)).size,seats.length);
 assert.equal(seats.filter(s=>s.tier===4).length,1221);assert.ok(seats.every(s=>s.row>0&&s.number>0));
 const picked=nearestSeat(seats,seats[23001].position);assert.equal(picked.id,23001);
});
