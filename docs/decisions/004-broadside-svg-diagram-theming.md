# 4. Monograph & Broadside SVG Diagram Theming

Date: 2026-09-10
Status: Accepted

## Context
Technical essays on `redbrogdon.dev` frequently include architecture flowcharts, pipeline visualizations, and system diagrams. Historically, diagrams were generated as ad-hoc raster PNGs or standalone SVGs using generic off-the-shelf software colors (vibrant blues, purples, and high-saturation cold grays) that clashed sharply with the site's warm editorial Monograph & Broadside aesthetic.

Additionally, static raster images do not respond to system color scheme shifts (`prefers-color-scheme: dark`), leading to glaring contrast mismatches when dark mode is enabled.

## Decision
We adopted a unified vector diagram workflow centered on **self-hosted, dual-theme SVG generation** paired with responsive HTML `<picture>` elements:

1. **Local Diagram Generation Skill (`generate-broadside-diagram`)**:
   - Created `.agents/skills/generate-broadside-diagram/` equipped with `generate_diagram.py`.
   - The generator produces two synchronized vector assets for every diagram: `<slug>-light.svg` and `<slug>-dark.svg`.
   - Diagrams adhere strictly to the Monograph & Broadside palette:
     - **Deterministic / Structural blocks**: Warm paper card surfaces (`#f4f1ea` light / `#1e1b19` dark) with muted hairline borders (`#d6d0c4` light / `#36312a` dark).
     - **Agentic / Interactive blocks**: Highlighted with the site's primary accent colors: terracotta crimson (`#991b1b`) in light mode and warm amber (`#d99b43`) in dark mode.
     - **Typography**: `EB Garamond` for step numbers and italic section subtitles, `JetBrains Mono` for badge tags and code symbols, and clean sans-serif for descriptive prose.

2. **Responsive `<picture>` Embedding**:
   - Diagram images in HTML articles are embedded via `<picture>` inside `<figure>`:
     ```html
     <figure>
       <picture>
         <source srcset="/static/images/blog/<slug>-dark.svg" media="(prefers-color-scheme: dark)">
         <img src="/static/images/blog/<slug>-light.svg" alt="..." width="720" height="460">
       </picture>
       <figcaption>...</figcaption>
     </figure>
     ```
   - This provides instantaneous vector switching when the user toggles light/dark mode with crisp rendering across all screen pixel densities.

## Consequences
- **Positive**: Complete visual consistency with the site's editorial broadside typography and palette; crisp resolution-independent rendering on high-DPI displays; native light/dark theme adaptation without client-side JavaScript.
- **Positive**: Reproducible generation workflow via automated skill scripts in `.agents/skills/`.
- **Negative**: Requires maintaining two SVG variants per diagram.
