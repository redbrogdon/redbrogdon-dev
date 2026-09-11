---
name: generate-broadside-diagram
description: Generates clean, accessible SVG architecture and flow diagrams in dual light and dark schemes strictly conforming to the Monograph & Broadside design system.
---

# Generate Broadside Diagram

Generates clean, accessible vector diagrams (SVG) locally for articles and documentation on `redbrogdon.dev`.

The diagrams strictly adhere to the site's **Monograph & Broadside** design system across two colorways:
* **Light Scheme**: `#fbf9f4` warm paper canvas with `#f4f1ea` cards, muted slate accents, and `#991b1b` crimson terracotta highlights.
* **Dark Scheme**: `#151413` obsidian canvas with `#1e1b19` cards, charcoal accents, and `#d99b43` warm amber highlights.

Typography pairs `EB Garamond` for headings and numbers, `JetBrains Mono` for badges and code tokens, and system sans-serif for body descriptions.

---

## When to Use This Skill

Activate this skill whenever:
* Creating architecture diagrams, pipeline visualizations, sequence flows, or component diagrams for articles.
* Refreshing existing raster or off-brand diagrams on the site.
* The user asks for a diagram matching the site's editorial color scheme.

---

## Workflow

### 1. Run the Generator Script
Execute the script from the repository root:

```bash
python3 .agents/skills/generate-broadside-diagram/scripts/generate_diagram.py \
  --name "diagram-slug" \
  --output-dir "public/static/images/blog" \
  --theme both
```

#### Key Options:
* `--name`: Diagram slug / identifier (e.g. `sidecar-architecture`).
* `--theme`: `both` (default, outputs `<name>-light.svg` and `<name>-dark.svg`), `light`, or `dark`.
* `--output-dir`: Destination folder (default: `public/static/images/blog`).
* `--template`: Optional path to an SVG template containing `{{token}}` placeholders.

---

## Semantic Color Palette

| Token | Light Theme | Dark Theme | Purpose |
| :--- | :--- | :--- | :--- |
| `bg` | `#fbf9f4` | `#151413` | Canvas background |
| `box_det_bg` | `#f4f1ea` | `#1e1b19` | Deterministic / structural card background |
| `box_det_stroke` | `#d6d0c4` | `#36312a` | Deterministic border hairline |
| `pill_det_bg` | `#e8e3d8` | `#2a2520` | Deterministic badge fill |
| `pill_det_text` | `#44403c` | `#b8b0a2` | Deterministic badge label |
| `box_agent_bg` | `#fbf4f2` | `#1f1a14` | Agentic / synthesis card background |
| `box_agent_stroke` | `#991b1b` | `#d99b43` | Agentic border accent (Crimson / Amber) |
| `pill_agent_bg` | `#f5deda` | `#362916` | Agentic badge fill |
| `pill_agent_text` | `#991b1b` | `#d99b43` | Agentic badge label |
| `text_body` | `#292524` | `#dcd5c8` | Main descriptive prose |
| `arrow_line` | `#a8a29e` | `#575046` | Connector lines & arrowheads |
| `arrow_pill_bg` | `#f4f1ea` | `#1e1b19` | Connector label badge fill |

---

## Embedding Dual-Theme SVGs in Blog Articles

Always embed dual-theme SVGs using an HTML `<picture>` element inside `<figure>`. This allows the browser to seamlessly swap between light and dark variants based on the reader's `prefers-color-scheme`:

```html
<figure>
  <picture>
    <source srcset="/static/images/blog/<slug>-dark.svg" media="(prefers-color-scheme: dark)">
    <img src="/static/images/blog/<slug>-light.svg" alt="Accessible description of the diagram" width="720" height="460">
  </picture>
  <figcaption>Descriptive caption explaining the diagram flow</figcaption>
</figure>
```
