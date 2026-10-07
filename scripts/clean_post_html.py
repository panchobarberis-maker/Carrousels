#!/usr/bin/env python3
"""
Clean HTML pasted from ChatGPT into Elementor text-editor widgets.

- Unwraps the chat UI wrappers (div/section/span) and drops their attributes
  (data-start, data-message-*, data-testid, class, dir, tabindex...).
- Keeps one H1: later H1s become H2 and the levels under them shift down one.
- The visible text must stay identical; clean() raises if it changes.
"""
import re
from bs4 import BeautifulSoup, NavigableString, Comment

KEEP_ATTRS = {"a": {"href", "target", "rel", "title"}, "img": {"src", "alt", "width", "height", "title"},
              "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan", "scope"}, "ol": {"start", "type"}}
UNWRAP = {"div", "section", "span", "article", "main", "font"}
# Markup the cleaner must not touch (embedded forms, scripts, iframes)
UNSAFE = {"form", "input", "textarea", "select", "button", "script", "iframe", "embed", "object"}
BOLD = re.compile(r"font-weight\s*:\s*(bold|[6-9]00)", re.I)

class Unsafe(Exception):
    pass

def visible_text(html):
    s = BeautifulSoup(html, "html.parser")
    return re.sub(r"\s+", " ", s.get_text(" ")).strip()

def _shift_headings(soup):
    hs = soup.find_all(re.compile(r"^h[1-6]$"))
    first_h1 = next((h for h in hs if h.name == "h1"), None)
    if not first_h1 or sum(h.name == "h1" for h in hs) < 2:
        return
    after = False
    for h in hs:
        if h is first_h1:
            after = True
            continue
        if after:
            h.name = f"h{min(int(h.name[1]) + 1, 6)}"

def clean(html):
    soup = BeautifulSoup(html, "html.parser")
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    if soup.find(list(UNSAFE)):
        raise Unsafe("contains form/script/iframe markup")
    for tag in soup.find_all(True):
        if tag.name in ("span", "font") and BOLD.search(tag.get("style", "")):
            tag.name, tag.attrs = "strong", {}
            continue
        if tag.name in UNWRAP:
            tag.unwrap()
            continue
        allowed = KEEP_ATTRS.get(tag.name, set())
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
    # drop empty paragraphs left behind by the wrappers
    for p in soup.find_all("p"):
        if not p.get_text(strip=True) and not p.find(["img", "br", "a"]):
            p.decompose()
    _shift_headings(soup)
    out = str(soup)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    if visible_text(out) != visible_text(html):
        raise ValueError("visible text changed")
    return out
