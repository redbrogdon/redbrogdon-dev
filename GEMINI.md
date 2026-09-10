# Workspace Guidelines & Rules for redbrogdon.dev

These rules apply to all AI assistants and coding agents working within this workspace.

---

## 1. Documentation & Architecture Mandates

1. **Read Architectural Documentation**:
   - Before designing new features, refactoring components, modifying layouts, or adding content, consult [`docs/architecture.md`](docs/architecture.md) and the relevant records in [`docs/decisions/`](docs/decisions/).
2. **Keep `docs/architecture.md` Up to Date**:
   - Whenever a change alters, extends, or introduces architectural patterns, design rules, or content workflows, update [`docs/architecture.md`](docs/architecture.md) in the same session.
3. **Record Architectural Decisions (ADRs)**:
   - When making non-trivial technical, architectural, or design system decisions (e.g. adopting new libraries, restructuring automation, altering responsive layouts, changing hosting configurations), create a new Architecture Decision Record in [`docs/decisions/`](docs/decisions/).
   - Follow the sequential naming convention: `docs/decisions/NNN-<short-slug>.md` (e.g. `004-*.md`).
   - Use the standard ADR format:
     - `Title`, `Date`, `Status` (Accepted / Deprecated / Superseded)
     - `## Context`: The problem, forces, and constraints.
     - `## Decision`: The specific technical choice and implementation approach.
     - `## Consequences`: Positive and negative trade-offs.

---

## 2. Core Site Principles & Checklist

### Content Synchronization (Mandatory Checklist)
Whenever new content (a blog post, poem, video, talk, or podcast appearance) is created or published:
- [ ] Add the content file (for internal posts/poems).
- [ ] Update the relevant section index ([`public/blog/index.html`](public/blog/index.html) or [`public/media/index.html`](public/media/index.html)).
- [ ] Prepend a new `<item>` entry to the RSS feed ([`public/feed.xml`](public/feed.xml)).
- [ ] Add the canonical `<url>` to the sitemap ([`public/sitemap.xml`](public/sitemap.xml)).
- [ ] **Chronological Rule**: Both section indexes and the RSS feed must strictly be sorted in **descending chronological order** (newest first).

### Self-Hosting & Zero CDNs
- All assets—fonts, icons, styles, and scripts—must be stored locally under `public/static/`. Never link to external CDNs (Google Fonts, cdnjs, etc.).

### Layout Stability (Anti-Jitter)
- Do not remove `scrollbar-gutter: stable;` from the `html` element in `public/static/css/main.css`. It is required to prevent layout shifts between short pages (Home, Poetry) and long pages (Blog, Media).

### Syntax Highlighting (Zero FOUC)
- Use the self-hosted Prism.js bundle ([`public/static/js/prism.min.js`](public/static/js/prism.min.js)).
- Include the script tag **synchronously** immediately before `</body>` (no `async` or `defer`) so that DOM tokenization completes prior to First Contentful Paint.
- Token styles must live in `public/static/css/main.css` and use the Monograph & Broadside palette.
- Tag snippets with `<pre><code class="language-{python|json|bash}">...</code></pre>`. Plain text and directory trees omit language classes.

### Blog Headers & Social Cards
- Blog header cards must be generated via `.agents/skills/generate-blog-header/` at 1200×630 PNG.
- On article pages, use `<picture>` with **inverted contrast**:
  - Light mode displays `-dark.png`.
  - Dark mode (`prefers-color-scheme: dark`) displays `-light.png`.
- Cap header display size with `.blog-header-image` (`max-width: 600px; height: auto;`).
- Wrap the `<picture>` in `<h1 class="article-title-image">` with descriptive `alt` text. Do not add a redundant text `<h1>`.
- Ensure Open Graph and Twitter Card tags specify `summary_large_image` pointing to the 1200×630 PNG.

### Identity & Navigation
- The CV link in the sidebar must use `<i class="fa-solid fa-file-lines"></i>` with title and label `"CV"`, linking to the official Google Drive document.
