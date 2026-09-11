# System Architecture & Principles: redbrogdon.dev

This document defines the architectural standards, design specifications, and content workflows for **redbrogdon.dev**. All contributions, refactors, and automated agent workflows must conform to these principles.

---

## 1. Core Principles

1. **Static & Self-Contained (Zero External CDNs)**
   - The site is pure static HTML/CSS/JS deployed via Firebase Hosting.
   - All assets—including webfonts (EB Garamond, JetBrains Mono), icons (FontAwesome solid and brands), stylesheets, and scripts (Prism.js, Game of Life canvas)—must be self-hosted locally under `public/static/`.
   - Never link to external CDNs (e.g., cdnjs, unpkg, Google Fonts).

2. **Mandatory Content Synchronization**
   - Whenever any new content (blog post, poem, talk, podcast, or appearance) is added to the site:
     1. Create or update the content page or entry.
     2. Update the corresponding section index (`public/blog/index.html` or `public/media/index.html`).
     3. Prepend a new `<item>` entry to the RSS feed (`public/feed.xml`).
     4. Add or update the canonical `<url>` entry in the sitemap (`public/sitemap.xml`).
   - **Chronological Rule**: Both section indexes and the RSS feed must strictly maintain **descending chronological order** (newest content first).

3. **Layout Stability (Zero Jitter)**
   - Centered layouts (`margin: 0 auto`) shift horizontally when navigating between short pages without scrollbars (e.g., Home, Poetry) and long pages with scrollbars (e.g., Blog, Media).
   - `scrollbar-gutter: stable;` must be maintained on `html` in `public/static/css/main.css` to guarantee identical viewport metrics across every page.

---

## 2. Design System: Monograph & Broadside

The visual identity follows an editorial, literary broadside aesthetic with warm palettes, classical serifs, and clean monospaced accents.

### Typography
- **Headings & Body Prose**: `EB Garamond` (fallback: `Garamond, Georgia, serif`).
- **Code, Navigation, Labels, & Metadata**: `JetBrains Mono` (fallback: `ui-monospace, SFMono-Regular, Menlo, Monaco, monospace`).
- **Functional UI**: `Inter` (fallback: `system-ui, -apple-system, sans-serif`).

### Dual Color Palette
Colors dynamically adjust via standard CSS custom properties and `@media (prefers-color-scheme: dark)`:

| Token | Light Mode | Dark Mode | Description |
| :--- | :--- | :--- | :--- |
| `--bg` | `#fbf9f4` | `#151413` | Warm unbleached paper / Deep warm charcoal |
| `--text` | `#1c1917` | `#ede7dc` | High-contrast body text |
| `--muted` | `#78716c` | `#9d9588` | Secondary labels, dates, metadata |
| `--link` | `#991b1b` | `#d99b43` | Crimson terracotta / Warm amber |
| `--link-hover`| `#b91c1c` | `#e6af5c` | Slightly brighter interaction state |
| `--border` | `#e7e5e4` | `#312c26` | Hairline dividers and cards |
| `--surface` | `#f4f1ea` | `#1e1b19` | Elevated card surfaces |
| `--code-bg` | `#ece8df` | `#26231f` | Monospaced block background |

### Page Layout
- **Broadside Grid**: `.broadside-layout` uses `max-width: 1060px; margin: 0 auto; display: grid; grid-template-columns: 280px 1fr; gap: 4.5rem;`.
- **Sticky Sidebar (280px)**: Anchors headshot avatar, site title, navigation links, and social links. Responsive breakpoints collapse the sidebar to a stacked header on viewports below 840px.

### Navigation & Identity Links
The sidebar navigation and social links are uniform across all pages:
- **Navigation**: `Home` (`/`), `Blog` (`/blog/`), `Media` (`/media/`), `Poetry` (`/poetry/`), and `RSS` (`/feed.xml`). Active links carry `.active` with the `›` indicator.
- **Social Links**: GitHub, Bluesky, LinkedIn, X / Twitter.
- **CV Link**: Must use the document icon `<i class="fa-solid fa-file-lines"></i>` with label `"CV"`, linking to the official Google Drive document. Never use generic PDF paths or Google Drive brand icons.

---

## 3. Code Blocks & Syntax Highlighting

1. **Zero-FOUC Execution**
   - Syntax highlighting uses a self-hosted Prism.js bundle (`public/static/js/prism.min.js`) supporting Python, JSON, Bash, and Markup.
   - The script must be included synchronously directly before `</body>` without `async` or `defer`. This ensures that code tokenization occurs synchronously before the browser\'s First Contentful Paint, eliminating any flash of unstyled code.
2. **Integrated Token Styling**
   - Token styles are embedded in `public/static/css/main.css`, loaded in `<head>`.
   - Token colors strictly follow the Monograph & Broadside palette (crimson/amber keywords, rust/coral functions, forest/sage strings, ochre/gold numbers and booleans, muted slate comments).
3. **Markup Convention**:
   - Wrap snippets in `<pre><code class="language-{lang}">...</code></pre>`.
   - ASCII trees and unstructured logs omit the language class to render as clean, neutral monospace text.

---

## 4. Media & Social Assets

1. **Blog Header Images**
   - Generated via `.agents/skills/generate-blog-header/scripts/generate_header.py` at 1200×630 px PNG.
   - Output includes `-dark.png`, `-light.png`, and a default social card `.png`.
   - On article pages, headers are rendered via `<picture>` using **inverted contrast**:
     - Light mode page displays the **dark** image banner.
     - Dark mode page (`media="(prefers-color-scheme: dark)"`) displays the **light** image banner.
   - The display size on the page is capped to `max-width: 600px; height: auto;` to preserve broadside proportions and keep the banner compact.
   - The `<picture>` element is wrapped in `<h1 class="article-title-image">` with descriptive `alt` text to serve as the document title without duplicating text.
2. **Social Cards (Open Graph / Twitter)**
   - Every page must specify `og:image`, `og:image:width: 1200`, `og:image:height: 630`, and `twitter:card: summary_large_image`.
   - General site pages point to `/static/images/og-card.png`.
   - Blog posts point to their tailored 1200×630 header card.
3. **Diagrams & Visual Schematics**
   - Architecture, flow, and sequence diagrams must be created as vector SVGs adhering to the Monograph & Broadside design system using `.agents/skills/generate-broadside-diagram/scripts/generate_diagram.py`.
   - Dual variants must be generated: `<slug>-light.svg` (warm paper `#fbf9f4`, card `#f4f1ea`, terracotta `#991b1b` accents) and `<slug>-dark.svg` (obsidian `#151413`, card `#1e1b19`, warm amber `#d99b43` accents).
   - Embed within `<figure>` using `<picture>` for dynamic theme switching:
     ```html
     <figure>
       <picture>
         <source srcset="/static/images/blog/<slug>-dark.svg" media="(prefers-color-scheme: dark)">
         <img src="/static/images/blog/<slug>-light.svg" alt="..." width="720" height="460">
       </picture>
       <figcaption>...</figcaption>
     </figure>
     ```
4. **Embedded Screenshots & Raster Media**
   - Stored as PNG under `public/static/images/blog/`.
   - Bounded with `max-width: 100%; border-radius: 6px; border: 1px solid var(--border);` inside `<figure>` with `<figcaption>`.

---

## 5. Background Automation (Sidecars)

Background automation runs via Google Antigravity managed sidecars:
- Located under `.agents/sidecars/` (e.g. `blog-watcher`).
- **Architectural Division**:
  - **Deterministic Plumbing**: Python scripts handle feed fetching, diff checking, branch name validation, git commits, rotating logs (`watcher.log`), and GitHub App RS256 JWT minting.
  - **Agentic Synthesis**: Gemini (`gemini-3.8-flash`) synthesizes tailored, 1-2 sentence editorial summaries and pull request descriptions matching the site\'s voice.
- **Safety**: Sidecars must run on scheduled cron intervals (`0 */6 * * *`) via `"builtin": "schedule"` in `sidecar.json`, avoiding persistent daemon memory overhead.
