# 3. Self-Hosted Client-Side Prism.js Syntax Highlighting with Zero FOUC

Date: 2026-09-10
Status: Accepted

## Context
The technical deep dive essays on redbrogdon.dev include snippets in Python, JSON, and Bash. Displaying plain monochrome code blocks detracts from readability and editorial polish.

Two primary approaches were evaluated:
1. **Build-Time Pre-rendering (e.g. Pygments/Shiki)**: Renders syntax spans directly into the static HTML files.
2. **Client-Side Highlighting (e.g. Prism.js / Highlight.js)**: Runs in the browser against semantic `<code class="language-*\>`.

A primary constraint was avoiding Flash of Unstyled Code (FOUC), where code renders unhighlighted before jumping to colored text upon script load.

## Decision
We chose **client-side syntax highlighting via a self-hosted Prism.js bundle** engineered specifically for zero FOUC:

1. **Self-Hosted Lightweight Bundle**:
   - Packaged a minimal Prism.js bundle (`public/static/js/prism.min.js`) containing Prism core plus grammars for Python, JSON, Bash, and Markup (~7 KB gzipped).
   - Stored locally in `public/static/js/`—no third-party CDN dependencies.

2. **FOUC Elimination Mechanism**:
   - The script is referenced synchronously directly before `</body>` (`<script src="/static/js/prism.min.js"></script>`) without `async` or `defer`.
   - In browser rendering pipelines, synchronous parser-blocking scripts execute immediately as the parser reaches them, before the initial paint. Prism runs `Prism.highlightAll()` synchronously, tokenizing the DOM nodes into colored spans before the browser executes First Contentful Paint.
   - Syntax token CSS rules are embedded directly in `public/static/css/main.css` (loaded in `<head>`), ensuring token styles are compiled by the CSS engine before DOM parsing finishes.
   - Code container geometry, font metrics (`JetBrains Mono`), and backgrounds (`var(--code-bg)`) match before and after tokenization, guaranteeing zero layout reflow.

3. **Color Theme**:
   - Rather than vibrant neon IDE palettes, token colors were custom-styled in `main.css` to harmonize with the Monograph & Broadside palette across both light and dark modes (warm crimson/amber keywords, rust/coral functions, forest/sage strings, ochre/gold constants).

## Consequences
- **Positive**: Clean, human-readable HTML files; zero FOUC on initial render; seamless automatic dark/light mode switching; zero external CDN dependencies.
- **Negative**: Adds ~7 KB to the page payload for articles containing code blocks.
