# 5. SEO Canonical Tagging, Schema.org Structured Data, and Global Analytics

Date: 2026-09-11
Status: Accepted

## Context
As `redbrogdon.dev` expanded with technical deep dives, literary poems, and media appearances, ensuring robust search engine discoverability and accurate analytics became critical. An SEO audit revealed four major gaps:
1. **Missing Canonical Tags**: None of the site's pages contained `<link rel="canonical">`, risking URL fragmentation and duplicate content penalties from crawler variations or UTM query parameters.
2. **Absence of Structured Data**: Search engines lacked explicit machine-readable metadata regarding the author, entity associations (`sameAs`), employer, and publication dates.
3. **Incomplete Article Open Graph Metadata**: Blog posts lacked explicit `article:published_time`, `article:modified_time`, and `article:author` tags.
4. **Patchy Analytics Coverage**: Google Analytics (`G-K7H22E9BGS`) was only installed on the homepage (`public/index.html`), leaving direct visits to blog posts, talks, and poems untracked.

## Decision
We implemented a standardized SEO, structured data, and analytics specification across the site:

1. **Mandatory Canonical URLs**:
   - Every index, article, and content page specifies `<link rel="canonical" href="https://redbrogdon.dev/...">` matching its canonical path.
   - The 404 error page explicitly omits a canonical link and includes `<meta name="robots" content="noindex, nofollow">`.

2. **Schema.org Structured Data (JSON-LD)**:
   - **Homepage (`/`)**: Defines a combined `WebSite` and `Person` schema declaring name, job title ("Staff Engineer"), organization ("Google"), image, and `sameAs` entity links to GitHub, Bluesky, LinkedIn, and X.
   - **Section Indexes (`/blog/`, `/media/`, `/poetry/`)**: Defines `CollectionPage` schema with author attribution.
   - **Articles (`/blog/*.html`)**: Defines `BlogPosting` schema with `headline`, `image`, `datePublished`, `dateModified`, `author`, `publisher`, and `mainEntityOfPage`.
   - **Poems (`/poetry/*.html`)**: Defines `CreativeWork` schema with title, author, and publication context.

3. **Article Open Graph Tags**:
   - Every published blog post specifies `article:published_time`, `article:modified_time`, and `article:author`.

4. **Universal Analytics Tracking**:
   - The Google Analytics tag (`G-K7H22E9BGS`) is included asynchronously in `<head>` across all 11 pages (including the 404 page to monitor broken inbound links).

## Consequences
- **Positive**: Eliminates indexing ambiguity across search engines; unlocks rich snippets and Google Knowledge Graph entity linking; provides complete traffic and referral visibility in GA4; reinforces AI search attribution.
- **Positive**: Low overhead—adds minimal bytes of inline JSON-LD without external blocking dependencies.
- **Negative**: Content additions require keeping canonical tags, Open Graph article dates, and sitemap `lastmod` synchronized.
