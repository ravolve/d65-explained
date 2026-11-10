from playwright.sync_api import sync_playwright
from PIL import Image
import io,sys
ids=sys.argv[1:]
HIDE='.hint{display:none!important} figure.chart{border:0!important;border-radius:0!important} details.fold,.ed,.seg,.qs,.chart .note{display:none!important} .rv{opacity:1!important;transform:none!important} .draftbar,.site{display:none!important}'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    for w,suf in [(860,''),(390,'-m')]:
        pg=b.new_page(viewport={'width':w,'height':1200},device_scale_factor=2,color_scheme='light')
        pg.goto('file://SITE_DIR/story.html'); pg.wait_for_timeout(400); pg.add_style_tag(content=HIDE)
        for fid in ids:
            pg.evaluate(f"document.getElementById('{fid}').scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(2000)
            png=pg.locator('#'+fid).screenshot(animations='disabled')
            Image.open(io.BytesIO(png)).save(f'SITE_DIR/img/{fid}{suf}.webp','WEBP',quality=88,method=6)
    b.close()
