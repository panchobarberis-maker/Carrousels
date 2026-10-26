#!/usr/bin/env python3
"""
Pre-publish cannibalization check. Compares one or more draft posts (blog/<slug>.html) against every
published post on langefirm.com plus the topic guides (/projects-post/) and practice pages, by title and
by body text (TF-IDF cosine similarity). Guides/practice pages are not in the REST API, so they are
fetched from the Rank Math sitemaps and cached for a day in ~/.cache/lf-guides.json.

Usage: python3 scripts/check_cannibalization.py blog/new-post.html [blog/other.html ...]
Exit code 1 if any draft is BLOCKED (too close to an existing post).

Thresholds (tuned on the 2026-10 audit, where real duplicates scored 0.55+ body or 0.6+ title):
  BLOCK  body >= 0.45  or title >= 0.55  -> improve/link the existing post instead of publishing (no redirects)
  REVIEW body >= 0.30  or title >= 0.40  -> publish only if the search intent is clearly different
"""
import html, json, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import post_to_wordpress as wp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BLOCK_BODY, BLOCK_TITLE, REVIEW_BODY, REVIEW_TITLE = 0.45, 0.55, 0.30, 0.40

def text_of(markup):
    markup = re.sub(r"<script.*?</script>", " ", markup, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", markup)))

def fetch_live():
    posts, page = [], 1
    while True:
        for attempt in range(5):
            try:
                r = wp.request("GET", f"/posts?status=publish&per_page=100&page={page}&_fields=id,slug,title,content")
                break
            except SystemExit as e:
                if "400" in str(e):
                    return posts
                time.sleep(10 * (attempt + 1))
        else:
            raise SystemExit("could not fetch posts")
        if not r:
            return posts
        posts += [{"slug": p["slug"], "t": html.unescape(p["title"]["rendered"]), "text": text_of(p["content"]["rendered"])} for p in r]
        if len(r) < 100:
            return posts
        page += 1

UA = "Mozilla/5.0 (compatible; LangeBlogBot/1.0)"
CACHE = os.path.expanduser("~/.cache/lf-guides.json")

def curl(url):
    return subprocess.run(["curl", "-s", "-A", UA, url], capture_output=True, text=True).stdout

def fetch_guides():
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 86400:
        return json.load(open(CACHE))
    from bs4 import BeautifulSoup
    pages = []
    for sm in ("projects-sitemap.xml", "practice-sitemap.xml"):
        for url in re.findall(r"<loc>([^<]+)</loc>", curl(f"https://langefirm.com/{sm}")):
            if url.rstrip("/").endswith(("projects-post", "practice-post")):
                continue
            soup = BeautifulSoup(curl(url), "html.parser")
            roots = [x for x in soup.select('[data-elementor-type="wp-page"],[data-elementor-type="wp-post"],[data-elementor-type="single-post"]')
                     if "elementor-218" not in x.get("class", [])]
            root = max(roots, key=lambda x: len(x.get_text()), default=soup.body)
            title = soup.title.get_text().split(" - ")[0] if soup.title else url
            slug = "/".join(url.rstrip("/").split("/")[-2:])
            pages.append({"slug": slug, "t": html.unescape(title), "text": re.sub(r"\s+", " ", root.get_text(" "))})
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(pages, open(CACHE, "w"))
    return pages

def main(paths):
    drafts = []
    for path in paths:
        title, body, _ = wp.parse_post(path)
        drafts.append({"slug": os.path.basename(path)[:-5], "t": title, "text": text_of(body)})
    live = [p for p in fetch_live() if p["slug"] not in {d["slug"] for d in drafts}] + fetch_guides()
    docs = live + drafts
    X = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2, max_df=0.5).fit_transform([d["t"] * 3 + " " + d["text"] for d in docs])
    T = TfidfVectorizer(stop_words="english").fit_transform([d["t"] for d in docs])
    S, ST = cosine_similarity(X), cosine_similarity(T)
    blocked = False
    for k, d in enumerate(drafts):
        i = len(live) + k
        top = sorted(range(len(live)), key=lambda j: -max(S[i, j], ST[i, j]))[:3]
        worst = max(max(S[i, j] for j in top), 0)
        status = "OK"
        for j in top:
            if S[i, j] >= BLOCK_BODY or ST[i, j] >= BLOCK_TITLE:
                status = "BLOCK"
            elif status == "OK" and (S[i, j] >= REVIEW_BODY or ST[i, j] >= REVIEW_TITLE):
                status = "REVIEW"
        blocked |= status == "BLOCK"
        print(f"{status:6} {d['slug']}")
        for j in top:
            print(f"       body {S[i, j]:.2f}  title {ST[i, j]:.2f}  /{live[j]['slug']}/  {live[j]['t'][:70]}")
    sys.exit(1 if blocked else 0)

if __name__ == "__main__":
    main(sys.argv[1:])
