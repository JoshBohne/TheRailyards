import './style.css';
import { ReplayRenderer,viewCopy,type CameraView } from './renderer';
import { beatAt,buildSeats,nearestSeat,tierNames,type ReplayData,type Seat } from './replay';

function element<T extends HTMLElement>(selector:string):T {
 const found=document.querySelector<T>(selector);if(!found)throw new Error(`Missing replay control: ${selector}`);return found;
}
const viewport=element('#viewport');const play=element<HTMLButtonElement>('#play');
const timeline=element<HTMLInputElement>('#timeline');const clock=element('#clock');const beat=element('#beat');
const tierControl=element<HTMLSelectElement>('#tier');const rowControl=element<HTMLSelectElement>('#row');const seatControl=element<HTMLSelectElement>('#seat');
const map=element<HTMLCanvasElement>('#seat-map');const loading=element('#loading');
let renderer:ReplayRenderer;let data:ReplayData;let seats:Seat[]=[];let selected:Seat|undefined;
let time=0;let playing=false;let dirty=true;let previous=0;let lastRender=0;let toastTimer:ReturnType<typeof setTimeout>|undefined;

function toast(text:string):void{element('#toast').textContent=text;if(toastTimer)clearTimeout(toastTimer);toastTimer=setTimeout(()=>element('#toast').textContent='',3500);}
function updateControls():void{
 timeline.value=String(time);clock.textContent=`${time.toFixed(1)} / ${data.duration.toFixed(1)} s`;beat.textContent=beatAt(data,time);
 play.textContent=playing?'Pause':time>=data.duration?'Replay':'Play';play.setAttribute('aria-pressed',String(playing));
}
function seek(next:number):void{time=Math.max(0,Math.min(data.duration,next));dirty=true;updateControls();}
function togglePlay():void{if(!renderer)return;if(time>=data.duration)time=0;playing=!playing;previous=performance.now();dirty=true;updateControls();}
function option(value:number,label:string):HTMLOptionElement{const o=document.createElement('option');o.value=String(value);o.textContent=label;return o;}
function updateSeatControls(seat:Seat):void{
 tierControl.value=String(seat.tier);
 const rows=[...new Set(seats.filter(s=>s.tier===seat.tier).map(s=>s.row))];rowControl.replaceChildren(...rows.map(row=>option(row,String(row))));rowControl.value=String(seat.row);
 const rowSeats=seats.filter(s=>s.tier===seat.tier&&s.row===seat.row);seatControl.replaceChildren(...rowSeats.map(s=>option(s.id,String(s.number))));seatControl.value=String(seat.id);
 drawMap();
}
function selectView(view:CameraView,seat?:Seat):void{
 if(!renderer)return;
 if(view==='home')seat=nearestSeat(seats.filter(s=>s.row===1),[-11,15.2,5],0);
 if(view==='upper')seat=nearestSeat(seats,[-35,43,35],3);
 selected=seat??selected;renderer.setView(view,seat);dirty=true;
 for(const button of document.querySelectorAll<HTMLButtonElement>('[data-camera]'))button.setAttribute('aria-pressed',String(button.dataset.camera===view));
 const title=view==='seat'&&seat?`${tierNames[seat.tier]} · Row ${seat.row} · Seat ${seat.number}`:viewCopy[view as Exclude<CameraView,'seat'>].title;
 element('#camera-label').textContent=title;
 element('#camera-description').textContent=view==='seat'?'An actual modeled seat. Drag to look around; the view may be obstructed.':viewCopy[view].description;
 if(seat)updateSeatControls(seat);
}
function chooseSeat(seat:Seat):void{selectView('seat',seat);}

// The seat map projects every actual model seat. There is no invented capacity grid.
const mapBounds={minX:-85,maxX:90,minZ:-145,maxZ:120};
function project(seat:Pick<Seat,'position'>):[number,number]{return[(seat.position[0]-mapBounds.minX)/(mapBounds.maxX-mapBounds.minX)*map.width,(seat.position[2]-mapBounds.minZ)/(mapBounds.maxZ-mapBounds.minZ)*map.height];}
function drawMap():void{
 const c=map.getContext('2d');if(!c)return;c.clearRect(0,0,map.width,map.height);
 const tier=Number(tierControl.value);
 for(const seat of seats){const [x,y]=project(seat);c.fillStyle=seat.tier===tier?'#adc4c7':'#3c505a';c.fillRect(x,y,seat.tier===tier?1.7:1,seat.tier===tier?1.7:1);}
 const home=project({position:[0,0,0]});c.fillStyle='#81926e';c.beginPath();c.moveTo(home[0],home[1]);c.lineTo(home[0]+62,home[1]);c.lineTo(home[0]+62,home[1]-43);c.lineTo(home[0],home[1]-43);c.closePath();c.fill();
 c.fillStyle='#d7e1e4';c.font='12px Arial';c.fillText('FIELD',home[0]+12,home[1]-16);c.fillStyle='#5f8999';c.fillRect(map.width-19,0,19,map.height);c.save();c.translate(map.width-5,map.height/2+35);c.rotate(-Math.PI/2);c.fillStyle='#d4e2e7';c.fillText('CHICAGO RIVER',0,0);c.restore();
 if(selected){const[x,y]=project(selected);c.strokeStyle='#ffc875';c.lineWidth=3;c.beginPath();c.arc(x,y,6,0,Math.PI*2);c.stroke();}
}
map.addEventListener('click',event=>{const rect=map.getBoundingClientRect();const x=(event.clientX-rect.left)/rect.width*map.width,y=(event.clientY-rect.top)/rect.height*map.height;let best:Seat|undefined;let distance=Infinity;for(const seat of seats){if(seat.tier!==Number(tierControl.value))continue;const [sx,sy]=project(seat);const d=(sx-x)**2+(sy-y)**2;if(d<distance){distance=d;best=seat;}}if(best)chooseSeat(best);});
tierControl.addEventListener('change',()=>{const seat=seats.find(s=>s.tier===Number(tierControl.value));if(seat)chooseSeat(seat);});
rowControl.addEventListener('change',()=>{const seat=seats.find(s=>s.tier===Number(tierControl.value)&&s.row===Number(rowControl.value));if(seat)chooseSeat(seat);});
seatControl.addEventListener('change',()=>{const seat=seats[Number(seatControl.value)];if(seat)chooseSeat(seat);});
for(const button of document.querySelectorAll<HTMLButtonElement>('[data-camera]'))button.addEventListener('click',()=>selectView(button.dataset.camera as CameraView));
function setPickerMode(mode:'seat'|'view'):void{
 const pickSeat=mode==='seat';
 element('#choose-seat').setAttribute('aria-pressed',String(pickSeat));
 element('#choose-view').setAttribute('aria-pressed',String(!pickSeat));
 element('#seat-picker').hidden=!pickSeat;element('#camera-presets').hidden=pickSeat;
 if(pickSeat&&seats.length){chooseSeat(selected??nearestSeat(seats,[-12,19,12],0));drawMap();}
}
element('#choose-seat').addEventListener('click',()=>setPickerMode('seat'));
element('#choose-view').addEventListener('click',()=>setPickerMode('view'));

play.addEventListener('click',togglePlay);
timeline.addEventListener('input',()=>{if(!data)return;playing=false;seek(Number(timeline.value));});
element<HTMLInputElement>('#track-ball').addEventListener('change',event=>{if(renderer){renderer.trackBall=(event.currentTarget as HTMLInputElement).checked;dirty=true;}});
element<HTMLInputElement>('#show-trail').addEventListener('change',event=>{if(renderer){renderer.showTrail=(event.currentTarget as HTMLInputElement).checked;dirty=true;}});
element<HTMLInputElement>('#crowd').addEventListener('change',event=>{if(renderer){renderer.crowd.visible=(event.currentTarget as HTMLInputElement).checked;dirty=true;}});
viewport.addEventListener('pointermove',()=>dirty=true);viewport.addEventListener('wheel',()=>dirty=true);window.addEventListener('resize',()=>dirty=true);
element('#fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await element('#experience').requestFullscreen();}catch{toast('Fullscreen is unavailable in this browser.');}});
window.addEventListener('keydown',event=>{const target=event.target;if(target instanceof HTMLElement&&['INPUT','SELECT','BUTTON','A','TEXTAREA'].includes(target.tagName)||!data)return;
 if(event.code==='Space'){event.preventDefault();togglePlay();}else if(event.key==='ArrowRight'){event.preventDefault();playing=false;seek(time+.1);}else if(event.key==='ArrowLeft'){event.preventDefault();playing=false;seek(time-.1);}else if(event.key.toLowerCase()==='r'){playing=false;seek(0);}
});
document.addEventListener('visibilitychange',()=>{previous=performance.now();dirty=true;});
function frame(now:number):void{
 requestAnimationFrame(frame);const elapsed=Math.min(.1,(now-previous)/1000);previous=now;if(document.hidden)return;
 if(playing){time+=elapsed;if(time>=data.duration){time=data.duration;playing=false;}dirty=true;updateControls();}
 const budget=innerWidth<800?1000/30:1000/60;if(dirty&&now-lastRender>=budget){renderer.render(time);lastRender=now;dirty=false;}
}
async function start():Promise<void>{
 try{
  const response=await fetch(new URL('model/replay.json',document.baseURI));if(!response.ok)throw new Error(`Replay data failed (${response.status})`);
  data=await response.json() as ReplayData;
  if(![10,11,12].includes(data.version)||!Array.isArray(data.ballSamples)||data.ballSamples.length<2||!Number.isFinite(data.duration)||data.duration<=0)throw new Error('Replay data is incomplete');
  const bowl=data.instances.find(g=>g.name==='D2_Individual seats');if(!bowl)throw new Error('The seat geometry is missing');
  const outfieldGroups=data.instances.filter(g=>g!==bowl&&g.name.toLowerCase().includes('individual seats'));
  seats=buildSeats([...bowl.points,...outfieldGroups.flatMap(g=>g.points)],bowl.points.length);
  if(seats.length!==data.seatCount)throw new Error('Seat export count does not match the replay');
  renderer=new ReplayRenderer(viewport,data);renderer.controls.addEventListener('change',()=>dirty=true);
  await renderer.load((text,percent)=>{element('#loading-status').textContent=text;element<HTMLProgressElement>('#load-progress').value=percent;});
  element('#water-distance').textContent=String(data.waterDistanceFt);element('#splash-distance').textContent=String(data.splashDistanceFt);timeline.max=String(data.duration);play.disabled=false;loading.hidden=true;
  selected=nearestSeat(seats,[-12,19,12],0);updateSeatControls(selected);
  const hash=new URLSearchParams(location.hash.slice(1));const desired=hash.get('view');const seatId=Number(hash.get('seat'));
  if(desired==='seat'&&Number.isInteger(seatId)&&seats[seatId]){selectView('seat',seats[seatId]);setPickerMode('seat');}else if(desired&&desired in viewCopy)selectView(desired as CameraView);else selectView('overview');
  const initial=Number(hash.get('t'));seek(Number.isFinite(initial)?initial:0);

  viewport.dataset.ready='true';previous=performance.now();requestAnimationFrame(frame);
 }catch(error:unknown){console.error(error);element('#loading-status').textContent='The interactive scene could not load. You can still watch all four rendered films.';element<HTMLProgressElement>('#load-progress').hidden=true;viewport.dataset.error=error instanceof Error?error.message:'Unknown loading error';}
}
void start();
