/** Capture the delivered cameras and check shared-clock UI behavior.
 * Start the site first. REPLAY_URL can target the dev server or a built site.
 * These captures do not measure real-device GPU or hosted-network performance.
 */
import {chromium} from 'playwright';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import assert from 'node:assert/strict';

const output=process.env.REPLAY_EVIDENCE_DIR??fileURLToPath(new URL('../../../work/replay-verification/',import.meta.url));
const base=process.env.REPLAY_URL??'http://127.0.0.1:8855/';
await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE});
const errors=[],results=[];
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
 const states=[['overview',0],['home',1.55],['upper',3],['left_center',6],['boat',8.7],['follow',5],['arrival',10.5],['riverwalk',0],['riverwalk',10.5],['seat',4,15000],['seat',4,26500]];
 for(const [view,time,seat] of states){
  const url=new URL(base);url.searchParams.set('capture',`${view}-${seat??time}`);url.hash=`view=${view}&t=${time}${seat===undefined?'':`&seat=${seat}`}`;
  // The query forces a full navigation: share links initialize on page load.
  await page.goto(url.href,{waitUntil:'networkidle'});
  await page.waitForFunction(({view,time})=>{const v=document.querySelector('#viewport');return v?.dataset.camera===view&&Math.abs(Number(v.dataset.time)-time)<.01&&Number(v.dataset.triangles)>0},{view,time},{timeout:60000});
  await page.screenshot({path:join(output,`${view}-${seat??time}.png`)});
  results.push({view,time,seat,...await page.locator('#viewport').evaluate(v=>({...v.dataset}))});
 }
 await page.getByRole('button',{name:'Above the diamond Upper deck'}).click();
 await page.getByRole('slider',{name:'Replay time'}).fill('3');
 await page.waitForFunction(()=>document.querySelector('#viewport').dataset.time==='3.000');
 const ball=await page.locator('#viewport').getAttribute('data-ball');
 await page.getByRole('button',{name:'On the river Boat level'}).click();
 await page.waitForFunction(()=>document.querySelector('#viewport').dataset.camera==='boat');
 assert.equal(await page.locator('#viewport').getAttribute('data-ball'),ball);
 await page.setViewportSize({width:390,height:844});
 await page.getByRole('button',{name:/The whole flight/}).click();
 await page.screenshot({path:join(output,'mobile-overview.png')});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.getByRole('button',{name:/Along the riverwalk/}).click();
 await page.screenshot({path:join(output,'mobile-riverwalk.png')});
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({states:results.length,errors,mobileWidth:390,output}));
}finally{
 await writeFile(join(output,'verification.json'),JSON.stringify({base,errors,results,mobileWidth:390,limitations:'Local browser correctness and screenshots; requires visual review and is not a real-device performance benchmark.'},null,2)+'\n');
 await browser.close();
}
