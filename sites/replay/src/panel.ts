export function setupPanel(panel:HTMLElement,container:HTMLElement):void {
 const collapse=panel.querySelector<HTMLButtonElement>('#collapse-panel')!;
 const content=panel.querySelector<HTMLElement>('#view-options')!;
 const handle=panel.querySelector<HTMLButtonElement>('#resize-panel')!;
 let drag:{x:number;y:number;width:number;height:number;top:number}|undefined;
 let expandedHeight='';
 function resize(width:number,height:number,top?:number):void {
  const area=container.getBoundingClientRect();
  const bounds=panel.getBoundingClientRect();
  const left=bounds.left-area.left;
  const availableWidth=area.width-left-8;
  panel.style.width=`${Math.max(Math.min(280,availableWidth),Math.min(width,availableWidth))}px`;
  const availableHeight=area.height-(top??56)-8;
  panel.style.height=`${Math.max(Math.min(200,availableHeight),Math.min(height,availableHeight))}px`;
  if(top!==undefined){panel.style.top=`${top}px`;panel.style.bottom='auto';}
 }
 function reset():void {
  panel.style.width='';panel.style.height='';panel.style.top='';panel.style.bottom='';
 }
 collapse.addEventListener('click',()=>{
  const open=collapse.getAttribute('aria-expanded')==='true';
  if(open){expandedHeight=panel.style.height;panel.style.height='';}
  else panel.style.height=expandedHeight;
  content.hidden=open;handle.hidden=open;panel.classList.toggle('collapsed',open);
  collapse.setAttribute('aria-expanded',String(!open));
  collapse.setAttribute('aria-label',open?'Expand view picker':'Collapse view picker');
 });
 handle.addEventListener('pointerdown',event=>{
  if(event.button!==0)return;
  const bounds=panel.getBoundingClientRect();
  drag={x:event.clientX,y:event.clientY,width:bounds.width,height:bounds.height,top:bounds.top-container.getBoundingClientRect().top};
  handle.setPointerCapture(event.pointerId);event.preventDefault();
 });
 handle.addEventListener('pointermove',event=>{
  if(drag)resize(drag.width+event.clientX-drag.x,drag.height+event.clientY-drag.y,drag.top);
 });
 handle.addEventListener('lostpointercapture',()=>{drag=undefined;});
 handle.addEventListener('pointerup',event=>{if(handle.hasPointerCapture(event.pointerId))handle.releasePointerCapture(event.pointerId);});
 handle.addEventListener('keydown',event=>{
  if(event.key==='Home'){event.preventDefault();reset();return;}
  const step=event.shiftKey?40:16;
  const change:Record<string,[number,number]>={ArrowLeft:[-step,0],ArrowRight:[step,0],ArrowUp:[0,-step],ArrowDown:[0,step]};
  const delta=change[event.key];if(!delta)return;
  event.preventDefault();const bounds=panel.getBoundingClientRect();
  panel.style.top='';panel.style.bottom='';resize(bounds.width+delta[0],bounds.height+delta[1]);
 });
 window.addEventListener('resize',()=>{reset();expandedHeight='';});
}
