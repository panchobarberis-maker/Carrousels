#!/usr/bin/env python3
"""
Lange Firm "scenario" carousel (same look as EVAN LANGE/fired-overtime): 5 slides, 1080x1350 JPG.

Usage: python3 scripts/generate_scenario_carousel.py content.json "EVAN LANGE/<slug>"

content.json:
{
  "cover":     {"title": "...", "subtitle": "...", "photo": "file.png"},
  "situation": {"label": "THE SITUATION", "text": "...", "note": "...", "photo": "file.png"},
  "point":     {"label": "THE LAW", "title": "...", "note": "...", "photo": "file.png"},
  "evidence":  {"label": "...", "title": "...", "note": "...", "photo": "file.png"},
  "cta":       {"label": "WE CAN HELP", "title": "...", "note": "...", "button": "...", "photo": "file.png"}
}
Photos are paths relative to the repo root (the Evan photos). Optional "crop_bottom" (0-1) per slide
trims the bottom of a photo, e.g. to hide a desk nameplate.
"""
import base64, html, io, json, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CHROME = next((p for p in ("/opt/pw-browsers/chromium-1243/chrome-linux64/chrome",
                           "/opt/pw-browsers/chromium-1194/chrome-linux/chrome") if os.path.exists(p)), None)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden;background:#111E33;color:#F0F4FF;font-family:'DM Sans',sans-serif}
.s{width:1080px;height:1350px;position:relative;overflow:hidden}
.bg{position:absolute;inset:0;background-size:cover;background-position:center 20%}
.ov{position:absolute;inset:0}
.logo{position:absolute;top:64px;left:72px;z-index:5;font-family:'Cormorant Garamond',serif;font-weight:700;
  font-size:26px;letter-spacing:6px;color:#C9A84C;text-shadow:0 2px 10px rgba(0,0,0,.6)}
.logo b{color:#C08A3A;font-weight:700}
.num{position:absolute;top:64px;right:72px;z-index:5;font-family:'DM Sans';font-size:20px;letter-spacing:3px;color:rgba(240,244,255,.55)}
.label{font-family:'Cormorant Garamond',serif;font-weight:700;font-size:24px;letter-spacing:7px;color:#C9A84C;text-transform:uppercase}
.rule{width:64px;height:2px;background:#C9A84C;margin:22px 0 34px}
.c{position:absolute;z-index:4}
h1{font-family:'Cormorant Garamond',serif;font-weight:700;font-size:112px;line-height:.98;color:#fff}
h2{font-family:'Cormorant Garamond',serif;font-weight:700;font-size:68px;line-height:1.08;color:#fff}
.it{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:400;font-size:58px;line-height:1.25;color:#fff}
.sub{font-size:31px;line-height:1.45;color:rgba(230,236,255,.88);font-weight:300}
.note{font-size:27px;line-height:1.5;color:rgba(230,236,255,.80);font-weight:300;margin-top:34px}
.btn{display:inline-block;margin-top:44px;border:2px solid #C9A84C;color:#E2C97E;padding:20px 38px;
  font-size:24px;letter-spacing:4px;font-weight:500}
.foot{position:absolute;bottom:56px;left:72px;z-index:5;font-size:19px;letter-spacing:4px;color:rgba(240,244,255,.55)}
.arrow{position:absolute;bottom:50px;right:72px;z-index:5;color:#C9A84C;font-size:34px}
"""
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,700;1,400'
         '&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">')

def photo(path, crop_bottom=0):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    if crop_bottom:
        im = im.crop((0, 0, im.width, int(im.height * (1 - crop_bottom))))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

e = html.escape

def chrome(n, total, body, bg, overlay, last=False):
    return f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{CSS}</style></head><body><div class="s">
<div class="bg" style="background-image:url('{bg}')"></div><div class="ov" style="background:{overlay}"></div>
<div class="ov" style="background:linear-gradient(180deg,rgba(17,30,51,.92) 0,rgba(17,30,51,.55) 150px,rgba(17,30,51,0) 300px)"></div>
<div class="logo"><b>THE LANGE</b> FIRM</div><div class="num">{n:02d} / {total:02d}</div>
{body}
<div class="foot">HOUSTON EMPLOYMENT LAW</div>{'' if last else '<div class="arrow">&rarr;</div>'}
</div></body></html>"""

def build(c):
    total = 5
    s = []
    v = c["cover"]
    s.append(chrome(1, total, f"""<div class="c" style="left:72px;right:120px;bottom:170px">
<h1>{e(v['title'])}</h1><div class="rule"></div><div class="sub">{e(v['subtitle'])}</div></div>""",
        photo(v["photo"], v.get("crop_bottom", 0)),
        "linear-gradient(180deg,rgba(17,30,51,.25) 0%,rgba(17,30,51,.35) 35%,rgba(17,30,51,.93) 68%,#111E33 100%)"))
    v = c["situation"]
    s.append(chrome(2, total, f"""<div class="c" style="left:90px;right:90px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center">
<div class="label">{e(v['label'])}</div><div class="rule"></div><div class="it">{e(v['text'])}</div><div class="note">{e(v['note'])}</div></div>""",
        photo(v["photo"], v.get("crop_bottom", 0)), "rgba(17,30,51,.86)"))
    v = c["point"]
    s.append(chrome(3, total, f"""<div class="c" style="left:72px;right:90px;bottom:150px">
<div class="label">{e(v['label'])}</div><div class="rule"></div><h2>{e(v['title'])}</h2><div class="note">{e(v['note'])}</div></div>""",
        photo(v["photo"], v.get("crop_bottom", 0)),
        "linear-gradient(180deg,rgba(17,30,51,.10) 0%,rgba(17,30,51,.25) 38%,rgba(17,30,51,.94) 62%,#111E33 100%)"))
    v = c["evidence"]
    s.append(chrome(4, total, f"""<div class="c" style="left:90px;right:90px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center">
<div class="label">{e(v['label'])}</div><div class="rule"></div><h2 style="font-size:76px">{e(v['title'])}</h2><div class="note">{e(v['note'])}</div></div>""",
        photo(v["photo"], v.get("crop_bottom", 0)), "rgba(17,30,51,.86)"))
    v = c["cta"]
    s.append(chrome(5, total, f"""<div class="c" style="left:72px;right:90px;bottom:150px">
<div class="label">{e(v['label'])}</div><div class="rule"></div><h2>{e(v['title'])}</h2><div class="note">{e(v['note'])}</div>
<div class="btn">{e(v['button'])}</div></div>""",
        photo(v["photo"], v.get("crop_bottom", 0)),
        "linear-gradient(180deg,rgba(17,30,51,.10) 0%,rgba(17,30,51,.30) 36%,rgba(17,30,51,.94) 60%,#111E33 100%)", last=True))
    return s

def main(cfile, outdir):
    c = json.load(open(cfile))
    out = os.path.join(ROOT, outdir); os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, doc in enumerate(build(c), 1):
            pg.set_content(doc, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            png = pg.screenshot(type="png")
            Image.open(io.BytesIO(png)).convert("RGB").save(os.path.join(out, f"slide{i}.jpg"), "JPEG", quality=92)
            print("saved", os.path.join(outdir, f"slide{i}.jpg"))
        b.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
