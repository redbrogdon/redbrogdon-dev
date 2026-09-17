# 6. Multi-Source Media and Video Watcher Sidecar

Date: 2026-09-14
Status: Accepted

## Context
Following the implementation of the blog post watcher sidecar ([ADR 002](002-deterministic-and-agentic-sidecar-architecture.md)), keeping the media bibliography on `redbrogdon.dev/media/` updated with technical talks, conference appearances, and video guides on the official Flutter YouTube channel remained a manual chore.

Monitoring YouTube presents distinct challenges compared to traditional blogs:
1. **Feed Unreliability**: YouTube's official Atom RSS endpoints (`https://www.youtube.com/feeds/videos.xml?channel_id=...`) experience frequent, intermittent platform-side 404/500 outages.
2. **Attribution Complexity**: The official Flutter channel features numerous rotating hosts, guests, and DevRel engineers. Candidate videos must be reliably filtered to detect Andrew Brogdon's actual appearances rather than other team members' presentations or tangential bibliography citations.
3. **Monograph Presentation**: YouTube video titles often contain clickbait, episode tags, or guest prefixes (e.g. `The future of designing & building Flutter design libraries with Widgetbook | Lucas Josefiak`) that clash with the site's classical monograph style (`The Future of Flutter Design Libraries with Widgetbook`).

## Decision
We extended the Antigravity background sidecar (`.agents/sidecars/blog-watcher/watch.py`) to support multi-source monitoring across both written blogs and YouTube video media:

1. **Resilient Dual-Mode Video Scraping**:
   - The sidecar attempts the YouTube Atom feed (`feeds/videos.xml?channel_id=UCwXdFgeE9KYzlDdR7TG9cMw`) first.
   - If the XML feed fails or returns an HTTP error, it transparently falls back to parsing `ytInitialData` from `https://www.youtube.com/@flutterdev/videos`, ensuring continuous discovery even during YouTube feed outages.

2. **Deterministic Video Filtering & Deduplication**:
   - Known video IDs, full URLs, and normalized titles are extracted from `public/media/index.html`. Already listed videos are skipped immediately with zero downstream network overhead.
   - Candidate videos have their watch page fetched to inspect detailed metadata and full descriptions.
   - Videos are evaluated for Andrew Brogdon's presence via speaker credits (`Speaker: Andrew Brogdon`), host introductions (`Andrew from the Flutter team catches up with...`), and DevRel markers, cleanly rejecting videos presented exclusively by other team members.
   - Unmerged PR protection: The sidecar verifies open GitHub PRs via `gh pr list` matching branch names, item URLs, and video IDs. This prevents redundant PR generation when unmerged pull requests are pending across poll intervals.

3. **Agentic Editorial Synthesis (Gemini 3.8 Flash)**:
   - When reachable, Gemini evaluates candidate videos to confirm Andrew's active role, transforms raw titles into clean monograph headlines, and crafts a 1–2 sentence editorial summary following the site's third-person present participle convention (`Interviewing...`, `Exploring...`, `Announcing...`).
   - If Gemini is unreachable or restricted, a deterministic fallback cleans titles and extracts descriptions.

4. **Multi-File Site Synchronization**:
   - New videos are inserted at the top of `<ul class="editorial-list">` in `public/media/index.html` with `<i class="fa-solid fa-video media-type-icon"></i>`.
   - New items are prepended to `public/feed.xml`.
   - The `<lastmod>` date for `https://redbrogdon.dev/media/` in `public/sitemap.xml` is refreshed.
   - Git branches strictly follow `bot/media-<slug>` (max 25 chars, where slug is deterministically derived from the canonical video ID or URL slug, identical to blog watcher's URL slug convention) and commits follow the repository standard (`Add <title[:35]> to media and feed`).

## Consequences
- **Positive**: Automated discovery of new YouTube video appearances without manual entry; resilient against YouTube RSS server flakiness; high-fidelity monograph titles and summaries; full adherence to site architectural principles.
- **Negative**: Requires maintaining YouTube HTML parsing heuristics if YouTube's frontend layout changes dramatically.
