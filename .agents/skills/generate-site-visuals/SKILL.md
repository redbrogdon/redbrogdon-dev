---
name: generate-site-visuals
description: Generates visual assets for redbrogdon.dev, supporting illustrative cut-paper character scenes (starring Bumpy, Spring, and Stacks) and dual-theme accessible SVG vector diagrams.
---

# Generate Site Visuals

Generates cohesive, accessible visual assets for `redbrogdon.dev` that conform to the **Monograph & Broadside** design system.

This skill encompasses two specialized workflows:
1. **Illustrative Image Workflow:** Creates warm, handcrafted cut-paper collage illustrations featuring the site's canonical shape-based character trio (**Bumpy**, **Spring**, and **Stacks**) for blog headers, editorial articles, social preview cards, and video thumbnails.
2. **Vector Diagram Workflow:** Generates dual-theme (`-light.svg` and `-dark.svg`), accessible vector diagrams based on text descriptions, markdown tables, or Mermaid syntax. *(Note: This workflow is an initial foundation and will be iterated on further in upcoming sessions).*

---

## When to Use This Skill

Activate this skill whenever:
* Creating a new blog post header or editorial hero image (e.g., during `content-create-blog-post`).
* Generating social preview cards (`og:image`, `twitter:image`) for new or refreshed content.
* Illustrating technical concepts (architecture, generative UI, debugging, release pipelines, pair programming) with character-driven visual storytelling.
* Creating or updating system architecture, flowcharts, or sequence diagrams for articles.

---

## Workflow 1: Illustrative Images (The Trio Workflow)

### Step 1: Context & Concept Analysis
* Read the source text (blog post draft, video transcript, or user prompt).
* Identify the core metaphor or concept to depict (e.g., sidecars/automata, error recovery, refactoring, pipeline delivery, or studio craft).
* Determine which characters to spotlight:
  * By default, feature all three characters (**Bumpy**, **Spring**, and **Stacks**) to reinforce their collaborative trio dynamic.
  * Individual characters or duos may also be spotlighted when specifically suited to the article's narrative.

### Step 2: Interactive Sizing & Aspect Ratio Inquiry (MANDATORY)
> [!IMPORTANT]
> **Never silently default to a particular image size or aspect ratio.** Always ask the user for their preferred dimensions before generating, offering helpful suggestions:
> * **`16:9` Widescreen (Suggested for Blog Headers):** Standard for article headers (`1200×630` px equivalent), social cards, and YouTube presentations.
> * **`3:2` Landscape:** Classic editorial format for wide inline article figures.
> * **`1:1` Square:** Compact card format for avatars, section dividers, or social threads.
> * **Custom dimensions:** As requested by the user.

### Step 3: Canonical Character Rules
Consult [`resources/character-guide.md`](resources/character-guide.md) for complete specifications:
* **Bumpy (The Thinker & Observer):** Large bulbous pear/gumdrop shape in textured slate teal. Small tactile bumps across his surface (zero band-aids). **Always wears round wire reading spectacles** perched on his nose. Cut-paper legs and bare feet. Studious, observant, and cautious.
* **Spring (The Catalyst & Energy):** **Single contiguous column of spiral coils** in terracotta paper (never separated into multiple coils). **Smooth domed head** atop the coil with eyes and a cheerful open smile. **Zero metal embellishments**. Cut-paper legs and bare feet. Leaping, action-ready, and optimistic.
* **Stacks (The Curious Learner):** Exactly **three smooth river stones stacked vertically**: **Blue** on top, **Yellow** in the middle, **Red** on the bottom. **All three stones have their own distinct pair of eyes and mouth.** Legs with bare feet extend **only from the bottom red stone**; arms extend **only from the middle yellow stone**.
* **Bare Feet Rule:** All characters have cut-paper legs and **bare feet** (do not include shoes unless specifically relevant to the image topic).

### Step 4: Art Style Prompt Construction ("Literary Interface Curations")
Every illustrative generation prompt must include the canonical style block:
```text
Contemporary pochoir stencil and matte cut-paper collage illustration on warm unbleached paper (#fbf9f4). Visible paper cut edges, delicate physical drop shadows, stippled gouache textures, Monograph and Broadside color palette (terracotta, warm charcoal, slate teal, amber gold). Clean, welcoming editorial composition, completely wordless, zero text, zero 3D plastic gloss, zero corporate blobs.
```

### Step 5: Conditioning on Canonical Reference Images
The skill includes 7 canonical reference images in [`resources/reference-images/`](resources/reference-images/):
1. `01-automata-inspection.jpg` (Spring's single continuous coil, bare feet, Bumpy's observant look)
2. `02-dynamic-ui-assembly.jpg` (Stacks' limb separation, UI cards)
3. `03-release-pipeline.jpg` (Delivery pipeline, workshop atmosphere)
4. `04-drafting-table.jpg` (Oversized drafting tools, technical drawing)
5. `05-tiffin-tea-break.jpg` (Cultural inclusivity, brass tiffin, chai, kilim rug)
6. `06-tangled-spool.jpg` (Playful slapstick, Spring's domed head, laughter)
7. `07-late-night-pop-up-book.jpg` (Cozy lighting, sleeping Stacks)

> [!TIP]
> When calling `generate_image`, pass 1 to 3 relevant reference image paths in `ImagePaths` (e.g. `[".agents/skills/generate-site-visuals/resources/reference-images/01-automata-inspection.jpg", ".agents/skills/generate-site-visuals/resources/reference-images/02-dynamic-ui-assembly.jpg"]`). This visually grounds the model in the exact character shapes and paper textures.

### Step 6: Batch Generation of 10 Diverse Variants (MANDATORY)
> [!IMPORTANT]
> **Never generate only a single image.** Always generate **10 distinct variants** for any editorial illustration or blog header request.
> * **Diverse Conceptual Staging:** Vary the actions, metaphorical props, scene composition, perspective, and character dynamics across all 10 candidates. Explore different narrative moments (e.g., active problem-solving, quiet study, workshop assembly, celebration, humorous mishaps).
> * **Strict Character Consistency:** All 10 variants must strictly adhere to the character specifications (Bumpy's spectacles, bumps, and thoughtful demeanor; Spring's single continuous coil and cheerful dome; Stacks' 3 stones, 3 faces, and strict limb rules; bare feet for all).
> * **Reference Image Conditioning:** Pass 1 to 3 relevant canonical reference images from `resources/reference-images/` in `ImagePaths` for every generation to anchor the visual style.
> * **Naming Convention:** Save the candidates with descriptive, structured filenames: `<slug>_v01_<concept>`, `<slug>_v02_<concept>`, ... `<slug>_v10_<concept>`.

### Step 7: Interactive User Review & Selection
* Present all 10 generated candidate variations clearly to the user with a title and brief 1-sentence description of the concept for each option.
* Prompt the user to select their favorite variant (e.g., *"Here are 10 conceptual variations for this piece. Which one do you prefer, or would you like any targeted adjustments to your favorite?"*).
* **Execution Gate:** Always wait for the user's explicit choice before committing the final asset into the website content tree or generating inverted contrast pairs.

### Step 8: Final Asset Preparation & Inverted Contrast Embedding
* Once the user selects their favorite variant:
  * Save the chosen asset to `public/static/images/blog/<slug>-light.png`.
  * If dark/light inverted contrast pairing is needed, generate the dark-background variant (`<slug>-dark.png` on obsidian `#151413`).
  * Embed in HTML `<header class="blog-header">` using an HTML `<picture>` element:
    * Light mode page displays `-dark.png`.
    * Dark mode page (`media="(prefers-color-scheme: dark)"`) displays `-light.png`.
    * Cap display width with `.blog-header-image` (`max-width: 600px; height: auto;`).
    * Wrap inside `<h1 class="article-title-image">` with descriptive `alt` text.

### Step 9: Cultural Inclusivity
* When depicting communal breaks, shared meals, or craft workspaces, naturally include everyday non-Western craft objects, foods, and textiles (e.g., brass tiffin carriers, cutting-chai glasses, samosas, woven kilim rugs).

---

## Workflow 2: Vector Diagrams (Modern Swiss Monograph)

Conforming to **ADR-008**, all technical schematics, DAG pipelines, network topologies, taxonomies, data flows, and comparative matrices use the **Modern Swiss Monograph** design system.

### Visual Anatomy & Design Principles
1. **Geometry & Borders:** Crisp rectilinear geometry with subtle corner radii (`rx="2"` or `rx="3"`). Hairline border strokes (`stroke-width="1"` or `1.2"`). Zero heavy drop shadows.
2. **Typographic Hierarchy:**
   * **Diagram Title:** `EB Garamond`, font-size 22–24px, font-weight 600, primary text color.
   * **Subtitle:** System sans-serif, font-size 13–14px, muted text color.
   * **Top Divider:** 1px horizontal hairline rule across the diagram header (`stroke="{t['border']}"`).
   * **Node Header:** System sans-serif, font-size 13–14px, font-weight 700, primary text.
   * **Stage / Status Badges:** `JetBrains Mono`, font-size 10–11px, font-weight 700, uppercase with letter-spacing.
   * **Code / Attribute Lists:** `JetBrains Mono`, font-size 10.5–11px, muted text or accent highlight.
3. **Status Indicators & Beacons:**
   * Node cards feature a distinct circular beacon (`<circle cx="..." cy="..." r="4" fill="..." />`) placed alongside an uppercase category badge (e.g. `STAGE 01`, `GLOBAL EDGE CDN`, `PRIMARY (FAST)`).
4. **Connectors & Flow:**
   * Clean hairline paths (`stroke-width: 1.2px` to `1.5px`) with standard triangular directional markers (`arrow-{theme}`, `arrow-red-{theme}`, `arrow-teal-{theme}`).
5. **Metric / Status Footers:**
   * Where applicable, conclude diagrams with a full-width bottom status bar displaying operational metrics, cache statistics, or execution summaries in `JetBrains Mono` 11px.
6. **Multi-Line Text Rule (Mandatory):**
   * SVG `<text>` elements do not auto-wrap. Multi-line descriptions must always be authored across stacked `<text>` lines with coordinated vertical increments (`y="55"`, `y="75"`, `y="95"`) to prevent card boundary overflows.

### Semantic Color Tokens (ADR-008 Dual-Theme)
| Token | Light Theme (`#fbf9f4`) | Dark Theme (`#151413`) | Semantic Usage |
|---|---|---|---|
| `bg` | `#fbf9f4` | `#151413` | Canvas background |
| `surface` | `#f4f1ea` | `#1e1b19` | Standard structural node card fill |
| `surface_alt` | `#f7f5ef` | `#2a2621` | Secondary nested container fill |
| `border` | `#d6d0c4` | `#36312a` | Container border and divider hairline |
| `border_subtle`| `#e8e4da` | `#2b2722` | Internal card dividers and grid lines |
| `text_primary` | `#1c1917` | `#ede7dc` | Titles, node headers, key metrics |
| `text_muted` | `#78716c` | `#9d9588` | Subtitles, descriptions, secondary metadata |
| `accent_red` | `#991b1b` (bg: `#fbf4f2`) | `#e05345` (bg: `#2a1b18`) | Active stage, critical path, deploy |
| `accent_teal` | `#2d6a78` (bg: `#f0f6f7`) | `#5fa3b2` (bg: `#182427`) | Fast edge, caching, completed stage |
| `accent_gold` | `#b45309` (bg: `#fdf7ec`) | `#d99b43` (bg: `#292116`) | Secondary flow, warning, pending stage |

### SVG Generation Tooling
Execute the dual-theme SVG compiler:
```bash
python3 .agents/skills/generate-site-visuals/scripts/generate_diagram.py \
  --name "pipeline-architecture" \
  --output-dir "public/static/images/blog" \
  --theme both
```

### Embedding in Content
Embed diagrams using `<figure>` and `<picture>` for dynamic theme adaptation:
```html
<figure>
  <picture>
    <source srcset="/static/images/blog/<slug>-dark.svg" media="(prefers-color-scheme: dark)">
    <img src="/static/images/blog/<slug>-light.svg" alt="Detailed description of the diagram flow" width="720" height="460">
  </picture>
  <figcaption>Descriptive caption explaining the diagram architecture</figcaption>
</figure>
```

---

## Deprecation & Replacement Note
This skill supersedes and replaces:
* `.agents/skills/generate-blog-header` (typography-only banner generator).
* `.agents/skills/generate-broadside-diagram` (standalone diagram script).
