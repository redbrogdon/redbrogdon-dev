# 008: Modern Swiss Monograph Vector Diagram System

* **Date:** 2026-09-24
* **Status:** Accepted

---

## Context

Following the adoption of the character illustration system for editorial visuals in [ADR-007](007-site-visuals-and-character-illustration-system.md), `redbrogdon.dev` required a standardized, production-ready vector diagram style for technical architecture, flowcharts, pipelines, and schema visualizations.

Previously, diagrams were generated ad-hoc under [ADR-004](004-broadside-svg-diagram-theming.md) using custom SVG templates that lacked a single unifying aesthetic. To identify the ideal design language for technical schematics, a 20-diagram exploration suite was authored across four distinct visual paradigms:
1. *Broadside Letterpress & Blueprint* (technical drawing grid, classical serif titles, labeled bounding boxes)
2. *Cut-Paper Layers & Card Depth* (tactile shadows, overlapping rounded cards, gouache accents)
3. *Modern Swiss Monograph* (high-contrast rectilinear grid, hairlines, uppercase status badges with indicator dots, bold typography hierarchy)
4. *Terminal ASCII-Craft* (monospaced ASCII trees, command prompts, faux terminal chrome)

Upon comparative review across flowcharts, sequence diagrams, architectures, class models, roadmaps, DAGs, topologies, and matrices, **Style 3: Modern Swiss Monograph** was selected as the site's canonical diagram style.

---

## Decision

1. **Adopt Modern Swiss Monograph as Canonical Diagram Style**
   All architectural, pipeline, topology, taxonomy, data flow, and comparative diagrams across `redbrogdon.dev` must strictly follow the Modern Swiss Monograph aesthetic.

2. **Visual Anatomy & Layout Rules**
   * **Geometry:** Crisp rectilinear containers with subtle corner radii (`rx="2"` or `rx="3"`), avoiding large bubbly radii or heavy drop shadows.
   * **Typographic Hierarchy:**
     * **Diagram Titles:** `EB Garamond`, font-size 22–24px, font-weight 600, primary text color.
     * **Subtitles:** System sans-serif, font-size 13–14px, muted text color.
     * **Top Divider Rule:** 1px solid stroke separating the header from the canvas.
     * **Node Headers:** System sans-serif, font-size 13–14px, font-weight 600–700, primary text.
     * **Pills & Badges:** `JetBrains Mono`, font-size 10–11px, font-weight 700, uppercase letter-spacing.
     * **Attribute Lists & Code:** `JetBrains Mono`, font-size 10.5–11px, muted or accent color.
   * **Status Indicators & Beacons:**
     * Node cards feature a distinct circular beacon (`<circle cx="..." cy="..." r="4" fill="..." />`) positioned alongside an uppercase category badge (e.g. `STAGE 01`, `GLOBAL EDGE CDN`, `PRIMARY (FAST)`).
   * **Connectors & Flow:**
     * Clean hairline stroke connectors (`stroke-width: 1.2px` to `1.5px`) with standard triangular directional markers (`arrow-{theme}`, `arrow-red-{theme}`, `arrow-teal-{theme}`).
   * **Metric & Status Footers:**
     * Where applicable, diagrams conclude with a full-width bottom status bar displaying operational metrics, cache statistics, or execution summaries in `JetBrains Mono` 11px.
   * **Text-Wrapping Enforcement:**
     * Because SVG `<text>` elements do not auto-wrap, multi-line prose or list items must always be authored as discrete stacked lines with explicit vertical coordinate offsets (`y="..."` or `dy="..."`) to prevent bounding box overflows.

3. **Semantic Color Tokens (Dual-Theme Compliance)**
   Every diagram must be rendered in both light (`-light.svg`) and dark (`-dark.svg`) variants conforming to the site palette:

   | Element / Token | Light Theme (`#fbf9f4`) | Dark Theme (`#151413`) |
   |---|---|---|
   | Canvas Background | `#fbf9f4` | `#151413` |
   | Standard Node Fill | `#f4f1ea` | `#1e1b19` |
   | Secondary Node Fill | `#f7f5ef` | `#2a2621` |
   | Border / Hairline | `#d6d0c4` | `#36312a` |
   | Subtle Divider | `#e8e4da` | `#2b2722` |
   | Primary Text | `#1c1917` | `#ede7dc` |
   | Muted Text | `#78716c` | `#9d9588` |
   | Accent Red (Active / Critical) | `#991b1b` (fill: `#fbf4f2`) | `#e05345` (fill: `#2a1b18`) |
   | Accent Teal (Fast / Edge / OK) | `#2d6a78` (fill: `#f0f6f7`) | `#5fa3b2` (fill: `#182427`) |
   | Accent Gold (Pending / Warning) | `#b45309` (fill: `#fdf7ec`) | `#d99b43` (fill: `#292116`) |

4. **Integration & Tooling**
   * The `generate-site-visuals` skill and its companion script `generate_diagram.py` are updated to serve as the reference compiler for Modern Swiss Monograph diagrams.
   * Articles embed diagrams via `<figure>` and `<picture>` with `(prefers-color-scheme: dark)` media queries for zero-runtime client-side theme switching.

---

## Consequences

### Positive
* **Editorial Consistency:** Technical schematics match the literary, structured aesthetic of the Monograph & Broadside design system without looking like generic third-party SaaS charts.
* **Information Density:** Rectilinear nodes with hairline borders and monospaced meta-badges provide exceptional information density while remaining clean and readable.
* **Zero CDNs & Accessibility:** Fully self-hosted vector SVGs, high-contrast semantic color pairings, scalable across all viewport sizes, and resilient to dark/light OS switching.
* **Prevented Layout Regressions:** Codified multi-line SVG wrapping rules eliminate card boundary overflows.

### Negative / Trade-Offs
* Handcrafted SVG nodes require explicit coordinate management compared to unstyled auto-generated Markdown/Mermaid outputs.
