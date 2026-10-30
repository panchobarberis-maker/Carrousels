import base64,sys
from playwright.sync_api import sync_playwright
bg=sys.argv[1]; out=sys.argv[2]; eyebrow,title,sub=sys.argv[3],sys.argv[4],sys.argv[5]
b64="data:image/png;base64,"+base64.b64encode(open(bg,'rb').read()).decode()
html=f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1536px;height:1024px;overflow:hidden;background:#111E33}}
.s{{position:relative;width:1536px;height:1024px;overflow:hidden;font-family:'DM Sans',sans-serif;color:#F0F4FF}}
.bg{{position:absolute;top:0;right:0;width:980px;height:1024px;background:url("{b64}") center 18%/cover}}
.ov{{position:absolute;inset:0;background:linear-gradient(90deg,#111E33 0%,#111E33 36%,rgba(17,30,51,.86) 50%,rgba(27,43,74,.35) 72%,rgba(17,30,51,.15) 100%)}}
.ov2{{position:absolute;inset:0;background:linear-gradient(0deg,rgba(17,30,51,.55) 0%,transparent 35%)}}
.logo{{position:absolute;top:70px;left:96px;display:flex;flex-direction:column;align-items:flex-start}}
.lt{{font-family:'Cormorant Garamond',serif;font-weight:700;font-size:30px;letter-spacing:9px;color:#9B6820;line-height:1}}
.lr{{width:200px;height:1px;background:linear-gradient(90deg,#C9A84C,transparent);margin:6px 0}}
.lb{{font-family:'Cormorant Garamond',serif;font-weight:700;font-size:30px;letter-spacing:12px;color:#C9A84C;line-height:1}}
.c{{position:absolute;left:96px;top:300px;width:760px}}
.eb{{font-size:20px;letter-spacing:6px;text-transform:uppercase;color:#C9A84C;margin-bottom:26px}}
h1{{font-family:'Cormorant Garamond',serif;font-weight:700;font-size:118px;line-height:.9;color:#F0F4FF;margin-bottom:34px}}
h1 em{{color:#E2C97E;font-style:italic}}
.rule{{width:84px;height:2px;background:#C9A84C;margin-bottom:30px}}
.sub{{font-size:34px;line-height:1.45;color:rgba(240,244,255,.9);font-weight:300;max-width:640px}}
.foot{{position:absolute;left:96px;bottom:70px;font-size:17px;letter-spacing:4px;text-transform:uppercase;color:rgba(220,228,255,.7)}}
</style></head><body><div class="s"><div class="bg"></div><div class="ov"></div><div class="ov2"></div>
<div class="logo"><span class="lt">THE LANGE</span><div class="lr"></div><span class="lb">FIRM</span></div>
<div class="c"><div class="eb">{eyebrow}</div><h1>{title}</h1><div class="rule"></div><p class="sub">{sub}</p></div>
<div class="foot">Houston Employment Law · langefirm.com</div>
</div></body></html>"""
SPKI="--ignore-certificate-errors-spki-list=PS48cX347wDVcRynzq+DFqswl2PLNE1sG6uQvxMCOS0="
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=next(x for x in ("/opt/pw-browsers/chromium-1243/chrome-linux64/chrome","/opt/pw-browsers/chromium-1194/chrome-linux/chrome") if __import__("os").path.exists(x)),args=[SPKI])
    pg=b.new_page(viewport={"width":1536,"height":1024})
    pg.set_content(html,wait_until="networkidle",timeout=60000)
    pg.wait_for_timeout(800)
    print('fonts ok:',pg.evaluate("document.fonts.check('700 40px \"Cormorant Garamond\"')"))
    pg.screenshot(path=out,type='jpeg',quality=88)
    b.close()
