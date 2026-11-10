# D65 Explained

A neutral, sourced, plain-language guide to Evanston/Skokie School District 65.

- **Public site:** https://www.d65explained.com (Vercel, deployed from this repo's `main` branch)
- **Old preview link:** https://claude.ai/artifact/7EQwGhQKexjgxwEoq6Zbkv (claude.ai artifact; secondary, not the address to share)
- **Owner:** Andy. Corrections: andy@paperprismstudio.com (as listed on the site)

This repository is the source of truth for the site. `site/` holds exactly what is published. Vercel serves `site/` (see `vercel.json`), and every push to `main` goes live within about a minute.

## Layout

| Path | What it is |
|---|---|
| `site/index.html` | Main page: tour, Two minutes, charts gallery, About |
| `site/story.html` | The full story, live charts and the source list (`SRC` table) |
| `site/img/` | Still pictures of the 20 gallery charts (`f-*.webp` desktop, `f-*-m.webp` phone) |
| `site/og.png` | Link-preview image (1200×630) |
| `site/robots.txt`, `site/sitemap.xml` | Search-engine files |
| `site/404.html` | Page-not-found screen |
| `vercel.json` | Tells Vercel to serve `site/` as is (no build) |
| `tools/capture-charts.py` | Re-takes chart pictures from `story.html` (Playwright + Chrome) |
| `tools/function-test.py` | Checks links, sources, overflow, tooltips and script errors |

## How to make an edit (for Claude, in any session)

1. Clone this repo and edit `site/`. Use exact-match string replacements, and check each one matches only once.
2. If a chart's title, labels or data changed, re-take that chart's pictures:
   `python3 tools/capture-charts.py f-tax f-cush` (set `SITE_DIR` in the script to the `site/` path first). Then update that chart's sizes in `const DIM={...}` in `index.html`. If the chart also appears in the tour, update the hard-coded `width`/`height` on its `<picture>`.
3. Run `tools/function-test.py` (set `SITE_DIR` first). Expect no script errors, no missing sources, and no horizontal overflow at 390 and 1280 px.
4. Commit and push to `main`. Vercel deploys it to d65explained.com within about a minute. Then open https://www.d65explained.com to confirm it.
5. Optional: also update the old claude.ai artifact (slug `3276407a-84ea-4dc4-bbdb-d5dc5fc54d0b`, `publish_files` with `shared_live: "public"` and `artifact_title: "D65 Explained"`). It isn't the shared address.

Get Andy's OK on any wording change; his explicit instructions count as approval.

## House rules for the text

- Neutral, calm and plainspoken. No opinions, proposals, jokes or sarcasm.
- Avoid AI-speak patterns, especially "It isn't X, it's Y."
- Say "families facing school closures." Don't use "north side."
- "special education" never takes a hyphen.
- Every fact carries a source tag. Label estimates "District estimate" or "Our calculation."
- Treat residents' analyses as theirs. Don't repeat personal allegations about named staff.

## Things that will go stale

- If you add a page, add it to `site/sitemap.xml` and give it the same preview tags as `index.html`.
- "What's next" (main page and story section 9), and the Nov. 9 news box at the end of the story, say a vote is expected **Nov. 16, 2026**. Update them after that meeting.

## Editing tools

The in-page editor was turned off at launch (Nov. 10, 2026). Edits go through Claude and this repo.

Connected to Vercel on Nov. 10, 2026.
