#!/usr/bin/env python3
"""
Add a "Related:" link to an existing Elementor blog post (inbound internal linking).
Appends one paragraph to the post's last text-editor widget, keeps `content` in sync and
backs up the original first. Skips posts that already link to the target URL.

Usage: python3 scripts/add_related_link.py SOURCE_SLUG TARGET_URL "Anchor text"
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import post_to_wordpress as wp

BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backups", "related-links")

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

def add_related(slug, url, anchor):
    found = call("GET", f"/posts?slug={slug}&context=edit&_fields=id,slug,content,meta")
    if not found:
        return f"{slug}: not found"
    p = found[0]
    raw = p["meta"].get("_elementor_data")
    if not raw:
        return f"{slug}: no Elementor data"
    if url in raw:
        return f"{slug}: already links to {url}"
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup = os.path.join(BACKUP_DIR, f"post-{p['id']}.json")
    if not os.path.exists(backup):
        with open(backup, "w") as f:
            json.dump({"id": p["id"], "slug": slug, "content_raw": p["content"]["raw"], "_elementor_data": raw}, f)
    data = json.loads(raw)
    widgets = []
    def walk(nodes):
        for n in nodes:
            if n.get("widgetType") == "text-editor":
                widgets.append(n)
            walk(n.get("elements", []))
    walk(data)
    if not widgets:
        return f"{slug}: no text-editor widget"
    para = f'<p><strong>Related:</strong> <a href="{url}">{anchor}</a></p>'
    widgets[-1]["settings"]["editor"] = widgets[-1]["settings"].get("editor", "").rstrip() + para
    content = "\n".join(w["settings"]["editor"] for w in widgets)
    call("POST", f"/posts/{p['id']}", {"content": content, "meta": {"_elementor_data": json.dumps(data)}})
    return f"{slug}: added link to {url}"

if __name__ == "__main__":
    print(add_related(sys.argv[1], sys.argv[2], sys.argv[3]))
