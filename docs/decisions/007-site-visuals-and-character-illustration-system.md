# 007: Site Visuals, Character Illustration System & Unified Visual Asset Skill

* **Date:** 2026-09-24
* **Status:** Accepted

---

## Context

`redbrogdon.dev` previously utilized two separate, narrowly scoped skills for visual content:
1. `generate-blog-header`: Generated text-only, high-contrast serif typography headers (PNG) on solid backgrounds.
2. `generate-broadside-diagram`: Generated dual-theme vector SVGs for architecture and flow diagrams conforming to ADR-004.

While technically sound, this approach lacked an engaging, warm illustrative vocabulary for conveying complex software concepts (e.g., sidecar agents, generative UI, distributed tracing, release pipelines, and architectural refactoring). Furthermore, standard generative AI visuals frequently introduce undesirable characteristics ("AI slop"): glossy 3D CGI plastic surfaces, generic neon cyberpunk aesthetics, and impersonal "Corporate Memphis" flat human figures.

The site required a cohesive, editorial, and inclusive visual identity that harmonizes with the **Monograph & Broadside** design system, maintains zero external CDNs, respects dark/light contrast rules, and provides a playful, friendly recurring cast of characters.

---

## Decision

1. **Art Style: "Literary Interface Curations"**
   * Adopt a contemporary pochoir stencil and matte cut-paper collage aesthetic.
   * Render all scenes on warm unbleached parchment (`#fbf9f4`) with visible papercut edges, physical drop shadows providing tactile depth, and stippled gouache textures.
   * Restrict color schemes to the Monograph & Broadside palette: terracotta (`#991b1b`), warm charcoal (`#151413`), slate teal, amber gold (`#d99b43`), and warm cream ivory.
   * Enforce a wordless illustration canvas: zero rendered gibberish text or pseudo-typography.
   * Embed cultural inclusivity naturally by depicting everyday non-Western craft objects, foods, and textiles (e.g. brass tiffin carriers, cutting-chai glasses, samosas, woven kilim rugs).

2. **Canonical Character Trio (Bumpy, Spring, and Stacks)**
   Establish a permanent, shape-based character ensemble inspired by tactile children's book characters (*Mr. Men / Mr. Bump*):
   * **Bumpy (The Thinker & Observer):** Large bulbous pear/gumdrop shape in textured slate teal with small tactile surface bumps (no band-aids). Always wears round wire spectacles perched on his nose. Features cut-paper legs with bare feet (no shoes).
   * **Spring (The Catalyst & Action-Ready Energy):** Single contiguous vertical or arced column of terracotta paper coils (never separated into broken coils). Features a smooth domed head with friendly eyes and an open, cheerful smile. Zero metal embellishments. Cut-paper legs with bare feet.
   * **Stacks (The Curious Learner):** Exactly three smooth river pebbles stacked vertically with fixed semantic colors: **Blue** on top, **Yellow** in the middle, and **Red** on the bottom. **All three stones have their own distinct eyes and mouth.** Legs with bare feet extend *only* from the bottom red stone; arms extend *only* from the middle yellow stone.

3. **Unified Skill Architecture: `generate-site-visuals`**
   Create a single unified skill at `.agents/skills/generate-site-visuals/` encapsulating two distinct workflows:
   * **Workflow 1: Illustrative Images (The Trio Workflow)**:
     * **Interactive Sizing Mandate:** The workflow must **always interactively ask the user** for their preferred aspect ratio and dimensions (e.g., suggesting `16:9` / `1200×630` for headers, `3:2` for article figures, `1:1` for avatars) rather than silently defaulting.
     * **10-Variant Batch Mandate:** Never generate only a single image; always generate a batch of **10 diverse conceptual variants** for user review and selection before committing the final asset.
     * Injects the canonical model sheet (`resources/character-guide.md`) and anti-slop negative constraints.
     * Incorporates 7 canonical reference images under `resources/reference-images/` for direct model conditioning via `ImagePaths`.
     * Manages asset placement under `public/static/images/blog/` and handles HTML `<picture>` inverted-contrast embedding.
   * **Workflow 2: Vector Diagrams (Architecture & Flowcharts)**:
     * Generates accessible dual-theme SVGs (`-light.svg` and `-dark.svg`) conforming to ADR-004 semantic tokens.
     * Serves as the initial architectural foundation, with explicit plans to iterate on direct Mermaid-to-Broadside parsing and enhanced automated layout in upcoming sessions.

4. **Deprecation & Replacement**
   * Deprecate `.agents/skills/generate-blog-header` and `.agents/skills/generate-broadside-diagram` in favor of `.agents/skills/generate-site-visuals`.

---

## Consequences

### Positive
* **Unified Brand Identity:** Articles, social cards, and documentation share a distinct, recognizable, and welcoming visual language.
* **Slop-Free AI Execution:** Explicit negative constraints and tactile papercut framing eliminate uncanny CGI glossy textures and generic corporate tropes.
* **Layout & Theme Harmony:** Preserves the site's strict inverted-contrast `<picture>` rules, dark/light theme switching, and zero-CDN self-hosting architecture.
* **User Control:** The interactive sizing mandate prevents unwanted default aspect ratios.

### Negative / Trade-Offs
* **Diagram Iteration Needed:** While the illustrative workflow is fully formalized with character sheets and prompt templates, the diagram workflow remains at its initial baseline and will require a dedicated iteration cycle to automate direct Mermaid/markdown translation.
