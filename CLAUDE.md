# The Lange Firm – blog & SEO working rules

Site: https://langefirm.com (WordPress + Elementor, Rank Math, WP Engine/Cloudflare).
Firm focus: **employment law in Houston** (probate and estate planning are secondary).
Credentials: environment API credential for langefirm.com (Basic auth, injected by the proxy).

## Publishing a new blog post
- Write the post as HTML in `blog/<slug>.html` using the `.lf-post` components (styles live in
  `blog/lf-blog.css`, published site-wide as Elementor Custom Code snippet #4340).
- GEO format, always: `.lf-answer` short answer at the top, numbered sections, an FAQ section with
  inline `FAQPage` JSON-LD, cited official sources (DOL, EEOC, TWC, OSHA, statutes) and a CTA.
- CTA says **"Request a Paid Consultation"** (consultations are paid, never "free") + 713-357-6994.
- Author is **Evan Lange (user 6)**; category Employment Law (35); short slug; Rank Math title ≤ 62
  chars and description 140–160 chars.
- Featured image: `scripts/make_featured_image.py` (carousel style, 1536×1024, an Evan photo not
  used before) with descriptive alt text.
- Verify every fact against a primary source before publishing; flag anything unverified.
- After publishing: clear the WP Engine cache, verify title/canonical/schema/H1 live, commit files.

## Internal linking (always, both directions)
- **Outbound:** every new post links to 4–8 related existing pages: the topic guide
  (`/projects-post/...`), related blog posts, and one service page (`/home-one/wrongful-termination/`,
  `/home-one/harassment-at-work/`, `/home-one/workplace-discrimination/`, `/home-one/eeoc-claim/`).
  Use descriptive anchor text and final URLs (no redirects).
- **Inbound:** after publishing, add a "Related:" link to the new post from 2–3 existing posts on the
  same topic (`scripts/add_related_link.py`). New posts must never be orphans.
- Prioritize inbound links from posts with real traffic once Search Console data is available.
- Do not create a new post on a topic that already has a page; update/link the existing one instead
  (see the cannibalization audit).
- **Before publishing, always run `python3 scripts/check_cannibalization.py blog/<slug>.html`.**
  BLOCK = do not publish (improve the existing post and 301 the weaker URL instead); REVIEW = publish
  only if the search intent is clearly different, and cross-link the two posts.

## Editing existing posts
- Posts are Elementor text-editor widgets: edit `_elementor_data` and keep `content` in sync.
- Back up before any change (`backups/`), test on 1–2 posts, then batch.
- Elementor element cache: changes show after **Elementor → Tools → Clear Files & Data** (ask the user).
