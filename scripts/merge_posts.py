#!/usr/bin/env python3
"""
Consolidate cannibalizing posts into one winner WITHOUT redirects.

  python3 scripts/merge_posts.py WINNER_ID blog/<winner>.html "SEO title" "SEO description" "focus kw" LOSER_ID [LOSER_ID ...]
  add --dry-run to only print what would change.

1. Backs up the winner and every loser (full REST JSON + Rank Math meta) to backups/<date>-merge/.
2. Rewrites the winner with the merged GEO HTML (switches it off Elementor so the content field is used)
   and sets its Rank Math title/description/focus keyword.
3. Points each loser's Rank Math canonical at the winner (no redirects, per CLAUDE.md).
4. Lists other posts that still link to a loser so the links can be repointed to the winner.
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import post_to_wordpress as wp
from wp_publish import req, clear_cache, ROOT_API

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def backup(pid, folder):
    p = req("GET", f"/posts/{pid}?context=edit")
    with open(os.path.join(folder, f"post-{pid}.json"), "w") as f:
        json.dump(p, f)
    return p


def main(argv):
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    winner_id, html_file, seo_title, seo_desc, focus = int(argv[0]), argv[1], argv[2], argv[3], argv[4]
    losers = [int(x) for x in argv[5:]]
    assert len(seo_title) <= 62, f"SEO title too long ({len(seo_title)})"
    assert 140 <= len(seo_desc) <= 160, f"SEO description must be 140-160 chars ({len(seo_desc)})"
    folder = os.path.join(ROOT, "backups", f"{datetime.date.today()}-merge")
    os.makedirs(folder, exist_ok=True)

    w = backup(winner_id, folder)
    winner_url = w["link"]
    title, body, meta = wp.parse_post(html_file)
    print(f"WINNER {winner_id} {winner_url}\n  title: {title}")
    loser_urls = []
    for lid in losers:
        p = backup(lid, folder)
        loser_urls.append(p["link"])
        print(f"LOSER  {lid} {p['link']} -> canonical {winner_url}")
    if dry:
        return

    req("POST", f"/posts/{winner_id}", {"title": title, "content": body, "excerpt": meta.get("excerpt", ""),
                                        "meta": {"_elementor_edit_mode": ""}})
    req("POST", "/rankmath/v1/updateMeta", {"objectType": "post", "objectID": winner_id, "meta": {
        "rank_math_title": seo_title, "rank_math_description": seo_desc,
        "rank_math_focus_keyword": focus}}, api=ROOT_API)
    for lid in losers:
        req("POST", "/rankmath/v1/updateMeta", {"objectType": "post", "objectID": lid, "meta": {
            "rank_math_canonical_url": winner_url}}, api=ROOT_API)

    # Find posts that still link to a loser.
    for url in loser_urls:
        path = re.sub(r"^https?://[^/]+", "", url)
        hits = req("GET", f"/posts?search={path.strip('/')}&per_page=50&_fields=id,slug,content")
        refs = [h["slug"] for h in hits if path in h["content"]["rendered"] and h["id"] not in losers]
        print(f"  links to {path}: {refs or 'none'}")
    clear_cache()
    print("done; cache cleared")


if __name__ == "__main__":
    main(sys.argv[1:])
