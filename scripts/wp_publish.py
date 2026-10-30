#!/usr/bin/env python3
"""
Helpers to publish a GEO blog post to langefirm.com and keep it safe from duplicates.

  from wp_publish import req, publish, clear_cache
  req(method, path, body=None, api=None)   # JSON request with retries on 429/502/503/504
  publish(html_file, slug, seo_title, seo_desc, focus_kw, image_path, alt_text) -> (id, link, status, media_id)

Re-running publish() reuses an existing post with the same slug and an existing media item with the
same file name, so a retry never creates duplicates. Author 6 (Evan Lange), category 35.
"""
import datetime, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import post_to_wordpress as wp

ROOT_API = wp.WP_URL + "/wp-json"

def req(method, path, body=None, api=None):
    base = api or wp.API
    for attempt in range(6):
        saved = wp.API
        try:
            wp.API = base
            return wp.request(method, path, data=json.dumps(body).encode() if body is not None else None,
                              headers={"Content-Type": "application/json"} if body is not None else None)
        except SystemExit as e:
            if any(c in str(e) for c in ("429", "502", "503", "504")) and attempt < 5:
                time.sleep(10 * (attempt + 1))
                continue
            raise
        finally:
            wp.API = saved

def clear_cache():
    return req("POST", "/wpe/cache-plugin/v1/clear_all_caches", {}, api=ROOT_API)

def publish(html_file, slug, seo_title, seo_desc, focus_kw, image_path, alt_text):
    title, body, meta = wp.parse_post(html_file)
    found = req("GET", f"/posts?context=edit&status=draft,publish&slug={slug}&_fields=id")
    if found:
        pid = found[0]["id"]
    else:
        payload = {"title": title, "content": body, "status": "draft", "author": 6, "slug": slug,
                   "excerpt": meta.get("excerpt", ""), "categories": [35]}
        try:
            pid = req("POST", "/posts", payload)["id"]
        except SystemExit:
            time.sleep(15)
            again = req("GET", f"/posts?context=edit&status=draft&slug={slug}&_fields=id")
            if not again:
                raise
            pid = again[0]["id"]
    req("POST", "/rankmath/v1/updateMeta", {"objectType": "post", "objectID": pid, "meta": {
        "rank_math_title": seo_title, "rank_math_description": seo_desc, "rank_math_focus_keyword": focus_kw}}, api=ROOT_API)
    name = os.path.basename(image_path).rsplit(".", 1)[0]
    media = req("GET", f"/media?search={name}&_fields=id")
    mid = media[0]["id"] if media else None
    for _ in range(4):
        if mid:
            break
        try:
            mid = wp.upload_image(image_path)
        except SystemExit:
            time.sleep(15)
            media = req("GET", f"/media?search={name}&_fields=id")
            mid = media[0]["id"] if media else None
    req("POST", f"/media/{mid}", {"alt_text": alt_text})
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    r = req("POST", f"/posts/{pid}", {"featured_media": mid, "status": "publish", "date_gmt": now})
    return pid, r["link"], r["status"], mid
