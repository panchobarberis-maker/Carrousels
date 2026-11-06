#!/usr/bin/env python3
"""
Repoint internal links from an old URL to a new one across all posts (no redirects involved).

  python3 scripts/repoint_links.py https://langefirm.com/old-slug/ https://langefirm.com/new-slug/

Updates Elementor posts (_elementor_data + content) and plain posts (content), backs each one up to
backups/<date>-repoint/, and also rewrites matching local blog/*.html files.
"""
import datetime, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from wp_publish import req, clear_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(old, new):
    old_path = old.split("langefirm.com", 1)[1]
    folder = os.path.join(ROOT, "backups", f"{datetime.date.today()}-repoint")
    os.makedirs(folder, exist_ok=True)
    hits = req("GET", f"/posts?search={old_path.strip('/')}&per_page=100&context=edit&_fields=id,slug,content,meta")
    for p in hits:
        raw = p["content"]["raw"]
        meta = p.get("meta") or {}
        el = meta.get("_elementor_data") or ""
        if old not in raw and old.replace("/", "\\/") not in el:
            continue
        with open(os.path.join(folder, f"post-{p['id']}.json"), "w") as f:
            json.dump(p, f)
        body = {"content": raw.replace(old, new)}
        if meta.get("_elementor_edit_mode") == "builder" and el:
            body["meta"] = {"_elementor_data": el.replace(old.replace("/", "\\/"), new.replace("/", "\\/")).replace(old, new)}
        req("POST", f"/posts/{p['id']}", body)
        print(f"updated {p['id']} {p['slug']}")
    for path in glob.glob(os.path.join(ROOT, "blog", "*.html")):
        text = open(path).read()
        if old in text:
            open(path, "w").write(text.replace(old, new))
            print(f"local file {os.path.basename(path)}")
    clear_cache()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
