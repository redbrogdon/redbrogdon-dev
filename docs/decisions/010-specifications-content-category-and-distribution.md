# 010: Specifications Content Category and Distribution

* **Date:** 2026-10-15
* **Status:** Accepted

---

## Context

`redbrogdon.dev` hosts technical essays, media appearances, and literary works. With the rise of autonomous AI coding agents (such as Google Antigravity, Cursor, Claude Code, and Gemini CLI), there is an emerging need for standardized, machine-consumable software specifications. 

The goal is to publish complete project specifications that any user can point their coding agent at, enabling the agent to autonomously implement a functional replica of the software project. Simultaneously, human visitors need a compelling landing page that demonstrates the author's reference implementation (via screenshots or video walkthroughs) and provides a ready-to-use prompt for their coding agent.

Because `redbrogdon.dev` is a pure static site hosted on Firebase Hosting without server-side runtimes, the spec distribution mechanism must:
1. Provide a predictable directory and file structure.
2. Enable direct HTTP fetching of raw Markdown files (`spec.md`) and sub-resources without CORS restrictions.
3. Preserve the site's Monograph & Broadside design system and anti-jitter layout rules.
4. Seamlessly integrate with site navigation, the RSS feed, and the XML sitemap.

---

## Decision

1. **Standardized Project Directory Structure**
   Each specification project is housed in its own directory under `public/specs/<slug>/`:
   ```text
   public/specs/<slug>/
     ├── index.html        # Human-readable landing page
     ├── spec.md           # Standardized "main" document for coding agents
     ├── domain/           # Domain-specific docs, data models, and schemas (optional)
     └── assets/           # UI screenshots, reference media, and sample assets
   ```
   - **`spec.md` as the Root Document:** The primary specification document is always named `spec.md`.
   - **Relative Links:** All domain sub-documents, schemas, and assets must be referenced from `spec.md` using relative paths (e.g., `./domain/schema.md`, `./assets/mockup.png`). Any agent starting at `spec.md` can traverse and discover the entire project graph.

2. **CORS and MIME Configuration in Firebase Hosting**
   To allow browser-based agent interfaces, webhooks, and local CLI tools to fetch raw Markdown directly without CORS errors, `firebase.json` is updated with dedicated headers for `**/*.md`:
   ```json
   {
     "source": "**/*.md",
     "headers": [
       {
         "key": "Content-Type",
         "value": "text/markdown; charset=utf-8"
       },
       {
         "key": "Access-Control-Allow-Origin",
         "value": "*"
       },
       {
         "key": "Cache-Control",
         "value": "public, max-age=3600, stale-while-revalidate=86400"
       }
     ]
   }
   ```

3. **Human-Readable Presentation Page Architecture**
   Individual spec pages (`public/specs/<slug>/index.html`) follow the Broadside layout (`.broadside-layout`, EB Garamond prose, JetBrains Mono accents, sticky sidebar) and include three standard sections:
   - **Executive Overview / Problem Statement:** Explaining what the project does, the architectural rationale, and user experience.
   - **Demo Media:** Screenshots or video walkthroughs (MP4/WebM or embedded player) showcasing the author's reference build, housed in `<figure class="spec-hero-media">` with `<figcaption>`.
   - **"Prompt Your Agent" Box:** A styled callout (`.agent-prompt-box`) containing copy-ready prompt instructions pointing the agent to the canonical `spec.md` URL.

4. **Site Navigation and Section Index**
   - **Sidebar Navigation:** A `Specs` link (`<a href="/specs/">Specs</a>`) is inserted between `Media` and `Poetry` across all site templates.
   - **Section Index (`/specs/`):** Located at `public/specs/index.html`, listing published specifications using the `.editorial-list` pattern in strict descending chronological order.

5. **Syndication, Structured Data, and SEO**
   - **RSS Feed (`public/feed.xml`):** The channel title is updated to `Andrew Brogdon · Blog, Media, and Specs`. Each new spec is prepended as an `<item>` with the title format `Spec: [Project Name]` and links to `https://redbrogdon.dev/specs/<slug>/`.
   - **Structured Data (JSON-LD):** 
     - `/specs/index.html` uses `CollectionPage` schema.
     - Individual spec landing pages (`/specs/<slug>/index.html`) use `TechArticle` schema.
   - **Sitemap (`public/sitemap.xml`):** Includes `/specs/` and all canonical spec URLs.

---

## Consequences

* **Positive:**
  - Standardized contract for agent ingestion: external agents only need the URL of `spec.md` to discover all project files via relative links.
  - Zero CORS friction when web-based agents or curl fetch Markdown files.
  - Consistent editorial presentation for human readers highlighting reference implementations and copy-paste agent prompts.
  - Full adherence to existing site principles: zero external CDNs, layout stability, RSS syndication, and clean SEO tagging.
* **Negative:**
  - Authors must maintain relative link integrity between `spec.md` and auxiliary sub-resources.
  - Adding a spec requires updating the specs section index, RSS feed, and sitemap in accordance with the mandatory content synchronization checklist.
