from playwright.sync_api import sync_playwright
import re,json,os,subprocess,time
srv=subprocess.Popen(['python3','-m','http.server','8781'],cwd='SITE_DIR',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
B='http://localhost:8781/'
rep=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  # 1. static link + source checks
  for page in ['index.html','story.html']:
    pg=b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append('console '+m.type+': '+m.text) if m.type in('error',) else None)
    bad=[];pg.on('response',lambda r: bad.append(f'{r.status} {r.url}') if r.status>=400 else None)
    pg.goto(B+page);pg.wait_for_timeout(1500)
    res=pg.evaluate("""(()=>{const out={};const ids=new Set([...document.querySelectorAll('[id]')].map(e=>e.id));
      out.missingSrc=[...new Set([...document.querySelectorAll('[data-id]')].flatMap(b=>b.dataset.id.split(' ')).filter(i=>typeof SRC!=='undefined'&&!SRC[i]))];
      out.srcNoUrl=typeof SRC!=='undefined'?Object.keys(SRC).filter(k=>!SRC[k][3]).length:0;
      out.badLocal=[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)).filter(h=>h&&!ids.has(h));
      out.views=[...document.querySelectorAll('[data-go]')].map(b=>b.dataset.go).filter(v=>!document.getElementById('v-'+v));
      out.storyLinks=[...document.querySelectorAll('a[href^="story.html#"]')].map(a=>a.getAttribute('href').split('#')[1]);
      out.ext=[...document.querySelectorAll('a[href^="http"]')].map(a=>a.href);
      out.editorVisible=[...document.querySelectorAll('#editBtn,#notesBtn')].filter(e=>e.offsetParent!==null).map(e=>e.id);
      return out})()""")
    rep.append((page,res,errs,bad))
    if page=='story.html':
      storyids=set(pg.evaluate("[...document.querySelectorAll('[id]')].map(e=>e.id)"))
  # story links targets
  idx=[r for r in rep if r[0]=='index.html'][0][1]
  rep.append(('story link targets missing',[t for t in idx['storyLinks'] if t not in storyids],[],[]))
  # 2. every front-door view & mobile overflow
  for w,h in [(390,844),(1280,900)]:
    ctx=b.new_context(viewport={'width':w,'height':h},has_touch=(w<500),is_mobile=(w<500))
    pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for v in ['tour','home','two','charts','about']:
      pg.goto(B+'index.html#'+v);pg.wait_for_timeout(500)
      ov=pg.evaluate("document.documentElement.scrollWidth-innerWidth")
      if ov>1: rep.append((f'overflow {w}px index#{v}',ov,[],[]))
    pg.goto(B+'story.html');pg.wait_for_timeout(800)
    tot=pg.evaluate("document.documentElement.scrollHeight")
    for y in range(0,tot,700):
      pg.evaluate(f"scrollTo(0,{y})");pg.wait_for_timeout(60)
    ov=pg.evaluate("document.documentElement.scrollWidth-innerWidth")
    wide=pg.evaluate("[...document.querySelectorAll('main *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.closest('.tablewrap,.scroll,table,nav,.draftbar')).slice(0,8).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right))")
    rep.append((f'story {w}px horiz overflow',ov,wide,errs))
    ctx.close()
  # 3. touch scroll over charts on phone
  ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2)
  pg=ctx.new_page();pg.goto(B+'story.html');pg.wait_for_timeout(800)
  cdp=ctx.new_cdp_session(pg);out=[]
  for fid in ['f-nbr','f-rev','f-kids','f-bus9','f-staff','f-res','f-e19','f-cush']:
    pg.evaluate(f"document.getElementById('{fid}').scrollIntoView({{block:'center'}})");pg.wait_for_timeout(1200)
    box=pg.evaluate(f"(()=>{{const r=document.querySelector('#{fid} svg, #{fid} .cv').getBoundingClientRect();return [r.left+r.width/2,Math.max(Math.max(r.top,0)+40,Math.min(r.top+r.height/2,innerHeight-120))]}})()")
    y0=pg.evaluate('scrollY')
    cdp.send('Input.synthesizeScrollGesture',{'x':int(box[0]),'y':int(box[1]),'yDistance':-300,'speed':800,'gestureSourceType':'touch'})
    pg.wait_for_timeout(500)
    y1=pg.evaluate('scrollY');tip=pg.evaluate("!document.getElementById('tip').hidden")
    out.append(f'{fid}: scrolled {y1-y0}px, tooltip shown after swipe: {tip}')
  rep.append(('touch swipe over charts',out,[],[]))
  # tap shows tooltip
  pg.evaluate("document.getElementById('f-rev').scrollIntoView({block:'center'})");pg.wait_for_timeout(1200)
  hot=pg.evaluate("(()=>{const h=document.querySelector('#f-rev .hot');if(!h)return null;const r=h.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
  if hot: pg.touchscreen.tap(hot[0],hot[1]);pg.wait_for_timeout(300)
  rep.append(('tap on chart bar shows tooltip',pg.evaluate("!document.getElementById('tip').hidden") if hot else 'no .hot found',[],[]))
  # editor unlock
  pg.goto(B+'index.html#edit');pg.wait_for_timeout(500)
  ed=pg.evaluate("document.documentElement.classList.contains('editor')")
  pg.goto(B+'story.html');pg.wait_for_timeout(500)
  ed2=pg.evaluate("[...document.querySelectorAll('#editBtn,#notesBtn')].filter(e=>e.offsetParent!==null).length")
  pg.goto(B+'index.html#public');pg.wait_for_timeout(300)
  rep.append(('editor unlock via #edit (index class, story buttons visible)',[ed,ed2],[],[]))
  b.close()
finally:
  srv.terminate()
sizes={f:os.path.getsize('SITE_DIR/'+f) for f in ['index.html','story.html']}
img=sum(os.path.getsize('SITE_DIR/img/'+f) for f in os.listdir('SITE_DIR/img'))
rep.append(('sizes',sizes,f'img total {img//1024} KB',[]))
for r in rep: print(json.dumps(r,default=str)[:1500])
