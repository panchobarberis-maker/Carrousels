#!/usr/bin/env python3
"""
Phase 2: clean ChatGPT markup inside Elementor text-editor widgets and set
their alignment to left. Backs up _elementor_data and content first.
Usage: python3 scripts/clean_elementor_posts.py POST_ID [POST_ID ...]
"""
import json, sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import post_to_wordpress as wp
from clean_post_html import clean, Unsafe

BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backups", "fase2-elementor")

def call(method, path, body=None):
    for attempt in range(5):
        try:
            return wp.request(method, path, data=json.dumps(body).encode() if body is not None else None,
                              headers={"Content-Type": "application/json"} if body is not None else None)
        except SystemExit as e:
            if any(c in str(e) for c in ("429", "502", "503", "504")):
                time.sleep(10 * (attempt + 1))
                continue
            raise
    raise SystemExit(f"gave up on {path}")

def process(pid):
    p = call("GET", f"/posts/{pid}?context=edit&_fields=id,slug,content,meta")
    raw = p["meta"].get("_elementor_data")
    if not raw:
        return "skip: no Elementor data"
    backup = os.path.join(BACKUP_DIR, f"post-{pid}.json")
    if not os.path.exists(backup):  # keep the original, never a re-cleaned copy
        with open(backup, "w") as f:
            json.dump({"id": pid, "slug": p["slug"], "content_raw": p["content"]["raw"], "_elementor_data": raw}, f)
    data = json.loads(raw)
    widgets = []
    def walk(nodes):
        for n in nodes:
            if n.get("widgetType") == "text-editor":
                widgets.append(n)
            walk(n.get("elements", []))
    walk(data)
    if not widgets:
        return "skip: no text-editor widget"
    try:
        cleaned = [clean(w.get("settings", {}).get("editor", "")) for w in widgets]
    except (Unsafe, ValueError) as e:
        return f"skip: {e}"
    for w, html in zip(widgets, cleaned):
        s = w.setdefault("settings", {})
        s["editor"] = html
        if s.get("align") == "justify":
            s["align"] = "left"
    content = "\n".join(w["settings"]["editor"] for w in widgets)
    call("POST", f"/posts/{pid}", {"content": content, "meta": {"_elementor_data": json.dumps(data)}})
    return f"ok ({len(raw)} -> {len(json.dumps(data))} bytes)"

if __name__ == "__main__":
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for pid in map(int, sys.argv[1:]):
        print(pid, process(pid))
