#!/usr/bin/env python3
"""
Lange Firm WordPress Blog Poster
Usage: python3 scripts/post_to_wordpress.py <post_file> [--image <path>] [--status draft|publish]
       python3 scripts/post_to_wordpress.py --check

post_file: Markdown (.md) or HTML (.html). The first "# Heading" line is used as the title.
Optional front matter lines at the top of the file (before the title):
  excerpt: Short summary
  categories: 5, 12        # category IDs (GET /wp-json/wp/v2/categories)

Credentials (never commit them), either:
  - an environment API credential for langefirm.com (Basic auth), which the
    proxy injects into every request, or
  - WP_USER + WP_APP_PASSWORD environment variables (Application Password
    from Users -> Profile).
  WP_URL           Site URL (default https://langefirm.com)
"""

import sys, os, json, base64, argparse, mimetypes, urllib.request, urllib.error
from pathlib import Path

WP_URL = os.environ.get("WP_URL", "https://langefirm.com").rstrip("/")
API = f"{WP_URL}/wp-json/wp/v2"

def auth_header():
    user, pwd = os.environ.get("WP_USER"), os.environ.get("WP_APP_PASSWORD")
    if not user or not pwd:
        return {}  # rely on the environment credential injected by the proxy
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def request(method, path, data=None, headers=None):
    req = urllib.request.Request(f"{API}{path}", data=data, method=method,
                                 headers={**auth_header(), **(headers or {})})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"WordPress API error {e.code}: {e.read().decode()[:500]}")

def to_html(text, is_markdown):
    if not is_markdown:
        return text
    try:
        import markdown
        return markdown.markdown(text, extensions=["extra"])
    except ImportError:
        sys.exit("Install the markdown package (pip install markdown) or pass an .html file.")

def parse_post(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    meta, title = {}, None
    while lines and not lines[0].startswith("# "):
        line = lines.pop(0)
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    if lines:
        title = lines.pop(0)[2:].strip()
    if not title:
        sys.exit("Post file needs a '# Title' line.")
    body = to_html("\n".join(lines).strip(), path.endswith(".md"))
    return title, body, meta

def upload_image(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    media = request("POST", "/media", data=Path(path).read_bytes(), headers={
        "Content-Disposition": f'attachment; filename="{Path(path).name}"',
        "Content-Type": mime,
    })
    print(f"Uploaded image: {media['source_url']}")
    return media["id"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post_file", nargs="?")
    ap.add_argument("--image")
    ap.add_argument("--status", default="draft", choices=["draft", "publish", "pending"])
    ap.add_argument("--check", action="store_true", help="Only verify credentials")
    args = ap.parse_args()

    if args.check:
        me = request("GET", "/users/me?context=edit")
        print(f"Connected to {WP_URL} as {me['name']} (roles: {', '.join(me.get('roles', []))})")
        return
    if not args.post_file:
        ap.error("post_file is required")

    title, body, meta = parse_post(args.post_file)
    payload = {"title": title, "content": body, "status": args.status}
    if meta.get("excerpt"):
        payload["excerpt"] = meta["excerpt"]
    if meta.get("categories"):
        payload["categories"] = [int(c) for c in meta["categories"].split(",") if c.strip()]
    if args.image:
        payload["featured_media"] = upload_image(args.image)

    post = request("POST", "/posts", data=json.dumps(payload).encode(),
                   headers={"Content-Type": "application/json"})
    print(f"Created {post['status']} post #{post['id']}: {post['link']}")
    print(f"Edit: {WP_URL}/wp-admin/post.php?post={post['id']}&action=edit")

if __name__ == "__main__":
    main()
