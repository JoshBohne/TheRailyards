"""Offline hybrid-navigation regression tests with real browser scrolling.

Run: python -m pip install playwright
     python -m playwright install chromium
     python sites/tests/test_story_navigation.py

BROWSER=webkit also supported after `python -m playwright install webkit`.
LEAFLET_STUB=0 uses real vendored Leaflet for the same DOM tests. The default
adapter isolates navigation/layers from tiles; it does NOT test cartography.
There is no new production or build dependency.
"""
import functools
import http.server
import os
import re
from pathlib import Path
import shutil
import threading
import unittest
from playwright.sync_api import sync_playwright

PUBLIC = Path(__file__).resolve().parents[1] / 'public'
STUB = Path(__file__).with_name('leaflet-stub.js')
NAMES = ['intro','the78first','fire','amtrakYard','swap','stadium','explore']

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_): pass

class StoryNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(PUBLIC)))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.playwright=sync_playwright().start()
        name=os.environ.get('BROWSER','chromium')
        options={'headless':True}
        if name=='chromium' and shutil.which('chromium'): options['executable_path']=shutil.which('chromium')
        cls.browser=getattr(cls.playwright,name).launch(**options)
        cls.stub=os.environ.get('LEAFLET_STUB','1')!='0'
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.playwright.stop();cls.server.shutdown();cls.server.server_close()
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1280,'height':800})
        self.page=self.context.new_page();self.page.set_default_timeout(5000);self.errors=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.route('https://**',lambda route:route.abort())
        if self.stub:
            self.page.route('**/vendor/leaflet/leaflet.js',lambda route:route.fulfill(path=str(STUB),content_type='text/javascript'))
        else:
            def leaflet(route):
                source=(PUBLIC/'vendor/leaflet/leaflet.js').read_text()
                route.fulfill(body=source+'\nL.Map.addInitHook(function(){window.__map=this;});',content_type='text/javascript')
            self.page.route('**/vendor/leaflet/leaflet.js',leaflet)
        self.page.add_init_script("window.__scrollCalls=[];const scroll=window.scrollTo.bind(window);window.scrollTo=function(...args){window.__scrollCalls.push(args[0]);return scroll(...args)}")
    def tearDown(self):
        self.context.close();self.assertEqual(self.errors,[],'Uncaught browser errors')
    def load(self,query=''):
        if os.environ.get('OFFLINE_DOM') == '1':
            # No navigation/network required. Script and stylesheet bodies are
            # identical; the URL query and pageshow are simulated in this mode.
            if hasattr(self, '_offline_loaded'):
                size=self.page.viewport_size
                self.page.close()
                self.page=self.context.new_page()
                self.page.set_default_timeout(5000)
                self.page.set_viewport_size(size)
                self.page.on('pageerror',lambda e:self.errors.append(str(e)))
            self._offline_loaded=True
            html=(PUBLIC/'index.html').read_text()
            html=re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S|re.I)
            html=re.sub(r'<link\b[^>]*>', '', html, flags=re.I)
            self.page.set_content(html,wait_until='domcontentloaded')
            self.page.add_style_tag(content=(PUBLIC/'site.css').read_text())
            css=self.page.add_style_tag(content=(PUBLIC/'map-story.css').read_text())
            css.evaluate("e=>e.id='railyards-story-styles'")
            self.page.add_script_tag(content=STUB.read_text())
            self.page.add_script_tag(content=(PUBLIC/'map-data.js').read_text())
            self.page.evaluate("q=>{const Params=URLSearchParams;window.URLSearchParams=class extends Params{constructor(value){super(q||value)}};window.__scrollCalls=[];const scroll=window.scrollTo.bind(window);window.scrollTo=function(...args){window.__scrollCalls.push(args[0]);return scroll(...args)}}",query)
            self.page.add_script_tag(content=(PUBLIC/'map.js').read_text())
        else:
            self.page.goto(self.base+'/'+query)
        self.page.wait_for_selector('.story-hybrid[data-active-story]');self.page.wait_for_timeout(60)
    def active(self,name):
        self.page.wait_for_function("name=>document.querySelector('.story').dataset.activeStory===name&&document.querySelector('#railyards-map').dataset.storyView===name",arg=name,timeout=4000)
        self.assertEqual(self.page.locator('.story-step.is-active').count(),1)
    def jump(self,name):
        self.page.evaluate("""name=>{const p=document.querySelector('.story-map'),h=visualViewport?visualViewport.height:innerHeight,b=(parseFloat(getComputedStyle(p).top)||0)+p.getBoundingClientRect().height;const line=innerWidth<=900&&getComputedStyle(p).position==='sticky'?b+Math.min(64,(h-b)*.18):h*.35;const a=document.querySelector('[data-story="'+name+'"] [data-story-anchor]');window.scrollTo({top:scrollY+a.getBoundingClientRect().top-line+14,behavior:'auto'})}""",name)
        self.active(name)
    def next(self):self.page.locator('[data-story-next]').click()
    def test_01_readable_and_single_navigation(self):
        self.load();self.active('intro')
        self.assertEqual(self.page.locator('.story-step').count(),7)
        self.assertEqual(self.page.locator('.story-nav').count(),1)
        self.assertEqual(self.page.evaluate('getComputedStyle(document.documentElement).scrollSnapType'),'none')
        # Before Start, the chapters below the intro are blurred; the intro itself is readable.
        self.assertEqual(self.page.evaluate("getComputedStyle(document.querySelector(\".story-step[data-story='intro']\")).filter"),'none')
        self.assertTrue(self.page.evaluate("[...document.querySelectorAll('.story-step:not([data-story=intro])')].every(s=>getComputedStyle(s).filter!=='none')"))
        self.next();self.active('the78first');self.page.wait_for_timeout(600)
        self.assertTrue(self.page.evaluate("[...document.querySelectorAll('.story-step')].slice(0,2).every(s=>getComputedStyle(s).opacity==='1'&&getComputedStyle(s).filter==='none'&&getComputedStyle(s).transform==='none')"))
        self.assertTrue(self.page.evaluate("[...document.querySelectorAll('.story-step')].slice(2).every(s=>getComputedStyle(s).filter!=='none')"))
        self.jump('intro')
        self.assertTrue(self.page.evaluate('!__map.dragging.enabled()&&!__map.keyboard.enabled()&&!__map.scrollWheelZoom.enabled()'))
    def test_02_buttons_both_directions(self):
        self.load()
        for name in NAMES[1:]:
            self.next();self.active(name);self.page.wait_for_timeout(600)
        self.assertEqual(self.page.locator('[data-story-count]').inner_text(),'Explore')
        for name in reversed(NAMES[:-1]):
            self.page.locator('[data-story-prev]').click();self.active(name);self.page.wait_for_timeout(600)
    def test_03_fast_manual_scrolling(self):
        self.load()
        for name in ['stadium','fire','explore','amtrakYard','the78first','swap','intro']:self.jump(name)
        if self.stub:self.assertTrue(self.page.evaluate("__map.calls.filter(c=>c.method==='fitBounds'||c.method==='setView').every(c=>c.options.animate===false)"))
    def test_04_double_next_and_reverse(self):
        self.load()
        self.page.evaluate("document.querySelector('[data-story-next]').click();document.querySelector('[data-story-next]').click()")
        self.active('fire');self.page.wait_for_timeout(700)
        self.assertEqual(self.page.locator('[data-story-count]').inner_text(),'2 of 5')
        self.jump('intro')
        self.page.evaluate("document.querySelector('[data-story-next]').click();document.querySelector('[data-story-next]').click();document.querySelector('[data-story-prev]').click()")
        self.active('the78first');self.page.wait_for_timeout(700)
        self.assertEqual(self.page.locator('[data-story-count]').inner_text(),'1 of 5')
    def test_05_interruptions(self):
        for kind in ['wheel','touchstart','pointerdown','keydown']:
            self.load();self.next();self.page.wait_for_timeout(70)
            self.page.evaluate("""kind=>{const e=kind==='keydown'?new KeyboardEvent(kind,{key:'PageUp',bubbles:true}):kind==='wheel'?new WheelEvent(kind,{deltaY:-100,bubbles:true}):new Event(kind,{bubbles:true});document.body.dispatchEvent(e)}""",kind)
            # Allow an already submitted compositor frame to finish canceling.
            self.page.wait_for_timeout(80)
            stopped=self.page.evaluate('scrollY');self.page.wait_for_timeout(900)
            self.assertLessEqual(abs(stopped-self.page.evaluate('scrollY')),2,kind)
            self.jump('swap');self.page.wait_for_timeout(500);self.active('swap')
    def test_06_mobile_landing(self):
        for width,height in [(375,667),(390,844),(820,1180)]:
            self.page.set_viewport_size({'width':width,'height':height});self.load()
            self.next();self.active('the78first');self.page.wait_for_timeout(700)
            boxes=self.page.evaluate("""()=>{const m=document.querySelector('.story-map').getBoundingClientRect(),a=document.querySelector('.is-active [data-story-anchor]').getBoundingClientRect();return{mapHeight:m.height,anchorTop:a.top,mapBottom:m.bottom,overflow:document.documentElement.scrollWidth>innerWidth}}""")
            self.assertFalse(boxes['overflow']);self.assertGreater(boxes['anchorTop'],boxes['mapBottom'])
            self.assertLessEqual(boxes['mapHeight'],min(260,height*.3)+66)
            self.jump('explore');self.page.locator('[data-story-prev]').click();self.active('stadium')
    def test_07_explore_state(self):
        self.load();self.jump('explore')
        for name in ['parking','concept','renderings']:self.page.locator(f'[data-map-layer="{name}"]').click()
        self.page.locator('[data-map-basemap="satellite"]').click();self.page.evaluate("__map.panBy([80,40],{animate:false})")
        center=self.page.evaluate('JSON.stringify(__map.getCenter())')
        self.page.evaluate("window.scrollTo({top:scrollY+80,behavior:'auto'})");self.page.wait_for_timeout(150);self.active('explore')
        self.assertEqual(center,self.page.evaluate('JSON.stringify(__map.getCenter())'))
        self.jump('stadium')
        self.assertTrue(self.page.evaluate("[...document.querySelectorAll('[data-map-layer]')].every(b=>b.getAttribute('aria-pressed')==='false')"))
        if self.stub:self.assertTrue(self.page.evaluate('__groups.slice(5,9).every(g=>!__map.hasLayer(g))'))
    def test_08_resize_and_landscape(self):
        self.load();self.jump('amtrakYard')
        self.page.set_viewport_size({'width':390,'height':844});self.page.wait_for_timeout(200)
        self.jump('swap');self.next();self.active('stadium')
        self.page.set_viewport_size({'width':844,'height':390});self.page.wait_for_timeout(200)
        self.assertNotEqual(self.page.locator('.story-map').evaluate('e=>getComputedStyle(e).position'),'sticky')
        self.jump('fire');self.next();self.active('amtrakYard')
    def test_09_reduced_motion_keyboard(self):
        self.page.emulate_media(reduced_motion='reduce');self.load()
        self.page.locator('[data-story-next]').focus();self.page.keyboard.press('Enter');self.active('the78first')
        self.assertTrue(self.page.locator('[data-story-next]').evaluate('e=>e===document.activeElement'))
        self.page.keyboard.press('Space');self.active('fire')
        self.assertTrue(self.page.evaluate("__scrollCalls.every(c=>typeof c!=='object'||c.behavior!=='smooth')"))
    def test_10_deep_link_restore(self):
        self.load('?place=upCanalYard');self.active('explore');self.page.wait_for_timeout(150)
        center=self.page.evaluate('JSON.stringify(__map.getCenter())');self.assertIn('41.834',center)
        self.page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
        self.page.wait_for_timeout(150);self.active('explore');self.assertEqual(center,self.page.evaluate('JSON.stringify(__map.getCenter())'))
        self.page.locator('[data-story-prev]').click();self.active('stadium')
    def test_11_failed_image_geometry(self):
        self.load();self.jump('the78first');box=self.page.locator('[data-story="the78first"]').bounding_box()
        self.page.locator('[data-story="the78first"] img').evaluate("img=>{img.src='missing-image.jpg';img.dispatchEvent(new Event('error'))}")
        self.page.wait_for_timeout(150)
        self.assertAlmostEqual(box['height'],self.page.locator('[data-story="the78first"]').bounding_box()['height'],delta=1)

if __name__=='__main__':unittest.main(verbosity=2)
