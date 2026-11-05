#!/usr/bin/env python3
"""Remove a stale year (e.g. 2025) from evergreen post titles. Slugs are never changed.
Usage: python3 scripts/strip_year_titles.py titles.json [--apply] [--only ID,ID]"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from wp_publish import req

KEEP = {4096, 4094, 3794}  # news/time-bound titles where the year is the topic

def strip(t, y="2025"):
    s = t
    m = re.search(rf"\((?:Guía\s+)?{y}[^)]*Texas[^)]*\)\s*$", s)
    if m and "Texas" not in s[:m.start()]:
        return s[:m.start()].rstrip() + " (Texas Guide)"
    s = re.sub(rf"\s*\((?:Guía\s+)?{y}(?:[^)]*)\)\s*:", ":", s)          # "(2025): ..." -> ":"
    s = re.sub(rf"\s*\((?:Guía\s+)?{y}(?:[^)]*)\)", "", s)                # "(2025 Guide ...)" -> ""
    s = re.sub(rf":\s*{y}\s+Guide\s+", ": Guide ", s)                    # ": 2025 Guide to ..." -> ": Guide to ..."
    s = re.sub(rf",?\s*A Complete Guide for {y}", ": A Complete Guide", s).replace(":: ", ": ")
    s = re.sub(rf"\.\s*{y}\s+Guide$", "", s)                              # ". 2025 Guide"
    s = re.sub(rf"\s+in\s+{y}(?=[?:]|$)", "", s)                          # "... in 2025" / "in 2025?"
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s

if __name__ == "__main__":
    items = json.load(open(sys.argv[1]))
    apply = "--apply" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    for p in ([] if "--h1" in sys.argv else items):
        if p["id"] in KEEP or (only and p["id"] not in only):
            continue
        old = p["title"]["raw"]; new = strip(old)
        if new == old or "2025" in new:
            print("SKIP", p["id"], old); continue
        print(p["id"], "|", old, "\n   ->", new)
        if apply:
            req("POST", f"/posts/{p['id']}", {"title": new})

def fix_h1(pid, backup_dir="backups/2026-11-05-titles"):
    """Strip the year from the in-content <h1> inside the Elementor text-editor widgets, keep content in sync."""
    import html as _html
    p = req("GET", f"/posts/{pid}?context=edit&_fields=id,slug,content,meta")
    raw = p["meta"].get("_elementor_data")
    if not raw:
        return "no elementor data"
    os.makedirs(backup_dir, exist_ok=True)
    bk = os.path.join(backup_dir, f"post-{pid}.json")
    if not os.path.exists(bk):
        json.dump({"id": pid, "slug": p["slug"], "content_raw": p["content"]["raw"], "_elementor_data": raw}, open(bk, "w"))
    data = json.loads(raw); widgets = []
    def walk(nodes):
        for n in nodes:
            if n.get("widgetType") == "text-editor":
                widgets.append(n)
            walk(n.get("elements", []))
    walk(data)
    changed = 0
    for w in widgets:
        ed = w["settings"].get("editor", "")
        def rep(m):
            nonlocal changed
            inner = m.group(2)
            if "2025" not in inner:
                return m.group(0)
            new = strip(_html.unescape(inner))
            if "2025" in new or new == _html.unescape(inner):
                return m.group(0)
            changed += 1
            return f"{m.group(1)}{_html.escape(new, quote=False)}{m.group(3)}"
        w["settings"]["editor"] = re.sub(r"(<h1[^>]*>)(.*?)(</h1>)", rep, ed, flags=re.S)
    if not changed:
        return "no h1 with year"
    content = "\n".join(w["settings"]["editor"] for w in widgets)
    req("POST", f"/posts/{pid}", {"content": content, "meta": {"_elementor_data": json.dumps(data)}})
    return f"h1 updated ({changed})"

if __name__ == "__main__" and "--h1" in sys.argv:
    for p in json.load(open(sys.argv[1])):
        if p["id"] in KEEP or (only and p["id"] not in only):
            continue
        print(p["id"], fix_h1(p["id"]))
