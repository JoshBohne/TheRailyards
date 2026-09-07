export type Point = readonly [number, number, number];
export type InstancePoint = readonly [number,number,number,number,number,number,number,number,number];
export interface InstanceGroup {name:string;prototype:string;points:InstancePoint[]}
export interface ReplayData {arrivalPath?:Point[];version:number;duration:number;sampleRate:number;contact:number;splash:number;waterCrossing:number;ballSamples:Point[];landing:Point;seatCount:number;instances:InstanceGroup[];waterDistanceFt:number;splashDistanceFt:number}
export interface Seat {id:number;tier:number;row:number;number:number;position:Point;rotation:number}
export const tierNames=['Lower bowl','Club','Middle','Upper deck','Outfield bleachers'] as const;
export function sampleBall(data:Pick<ReplayData,'duration'|'sampleRate'|'ballSamples'>,time:number):Point {
 const frame=Math.max(0,Math.min(data.ballSamples.length-1,Math.max(0,Math.min(data.duration,time))*data.sampleRate));
 const index=Math.floor(frame),u=frame-index,a=data.ballSamples[index],b=data.ballSamples[Math.min(index+1,data.ballSamples.length-1)];
 return [a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u,a[2]+(b[2]-a[2])*u];
}
export function buildSeats(points:readonly InstancePoint[],outfieldStart=Infinity):Seat[] {
 const levels=[...new Set(points.slice(0,outfieldStart).map(p=>p[2].toFixed(3)))].map(Number).sort((a,b)=>a-b);
 const outfieldLevels=[...new Set(points.slice(outfieldStart).map(p=>p[2].toFixed(3)))].map(Number).sort((a,b)=>a-b);
 const tierFor=(z:number)=>z<26?0:z<32?1:z<38?2:3;
 const rows=[...levels.map(z=>({z,tier:tierFor(z)})),...outfieldLevels.map(z=>({z,tier:4}))];const counts=new Map<string,number>();
 return points.map((p,id)=>{const tier=id>=outfieldStart?4:tierFor(p[2]);const row=rows.filter(r=>r.tier===tier).findIndex(r=>Math.abs(r.z-p[2])<.002)+1;
 const key=`${tier}:${row}`;const number=(counts.get(key)??0)+1;counts.set(key,number);
 return {id,tier,row,number,position:[p[0],p[2]+1.2,-p[1]],rotation:p[5]};});
}
export function nearestSeat(seats:readonly Seat[],position:Point,tier?:number):Seat {
 let best:Seat|undefined;let distance=Infinity;
 for(const seat of seats){if(tier!==undefined&&seat.tier!==tier)continue;const d=seat.position.reduce((sum,n,i)=>sum+(n-position[i])**2,0);if(d<distance){distance=d;best=seat;}}
 if(!best)throw new Error('No modeled seat matches this view');return best;
}
export function beatAt(data:Pick<ReplayData,'contact'|'waterCrossing'|'splash'>,time:number):string {
 if(time<data.contact-.12)return 'The pitch';if(time<data.contact+.35)return 'Contact';if(time<data.waterCrossing)return 'Over the ballpark';if(time<data.splash)return 'Across the river’s edge';return 'Into the river';
}

export function samplePath(points:readonly Point[],progress:number):Point {
 if(points.length<2)throw new Error('A camera path needs at least two points');
 const lengths=points.slice(1).map((p,i)=>Math.hypot(...p.map((v,k)=>v-points[i][k])));
 let remaining=Math.max(0,Math.min(1,progress))*lengths.reduce((a,b)=>a+b,0);
 for(let i=0;i<lengths.length;i++){
  if(remaining<=lengths[i]||i===lengths.length-1){const u=lengths[i]?remaining/lengths[i]:0;const a=points[i],b=points[i+1];return [a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u,a[2]+(b[2]-a[2])*u];}
  remaining-=lengths[i];
 }
 return points[points.length-1];
}
export function spatialChunks(points:readonly InstancePoint[],size:number):InstancePoint[][] {
 const cells=new Map<string,InstancePoint[]>();
 for(const point of points){const key=`${Math.floor(point[0]/size)}:${Math.floor(point[1]/size)}`;let cell=cells.get(key);if(!cell){cell=[];cells.set(key,cell);}cell.push(point);}
 return [...cells.values()];
}
