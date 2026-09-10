---
name: generate-blog-header
description: Generates minimalist, bold blog header PNG images locally for redbrogdon.dev posts using Garamond serif typography in dark and light schemes.
---

# Generate Blog Header

Generates minimalist, bold typography-only header images (PNG) locally for blog posts on `redbrogdon.dev`.

The images feature high-impact, dynamically scaled Garamond serif typography across two colorways that strictly adhere to the site's **Monograph & Broadside** design system:
* **Dark Scheme** (Default for social / Open Graph): `#151413` obsidian background with `#ede7dc` warm cream text.
* **Light Scheme**: `#fbf9f4` warm paper background with `#1c1917` deep charcoal text.

---

## When to Use This Skill

Activate this skill whenever:
* Creating a new blog post on `redbrogdon.dev` (e.g. following or during `content-create-blog-post`).
* Generating social preview cards (`og:image`, `twitter:image`) for existing or new articles.
* The user asks to create or refresh a blog header image.

---

## Workflow

### 1. Identify Title & Slug
* Determine the blog post title.
* Determine the slug (e.g., `client-side-functions` for *"Quick, reliable calculations with A2UI’s Client-Side Functions"*). If omitted, the tool automatically generates a URL-safe slug.

### 2. Run the Generator Script
Execute the Python script from the repository root:

```bash
python3 .agents/skills/generate-blog-header/scripts/generate_header.py \
  --title "Your Blog Post Title" \
  --slug "custom-slug"
```

#### Key Options:
* `--theme`: `both` (default, outputs dark and light versions), `dark`, or `light`.
* `--output-dir`: Output directory (default: `public/static/images/blog/`).
* `--no-social-default`: Omit copying the dark version to `<slug>.png` as the social fallback.
* `--width` / `--height`: Canvas dimensions (default: 1200 × 630).

### 3. Output Assets Produced
When run with default parameters, the tool creates three assets in `public/static/images/blog/`:
1. `<slug>-dark.png` — Dark scheme header.
2. `<slug>-light.png` — Light scheme header.
3. `<slug>.png` — The default social sharing image (a copy of the dark scheme image).

---

## 4. Embedding in Blog Posts

### In HTML `<head>` (Open Graph & Twitter Cards)
```html
<!-- Open Graph -->
<meta property="og:image" content="https://redbrogdon.dev/static/images/blog/<slug>.png">
<meta property="og:image:secure_url" content="https://redbrogdon.dev/static/images/blog/<slug>.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Exact Title of the Blog Post">

<!-- Twitter / X Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://redbrogdon.dev/static/images/blog/<slug>.png">
<meta name="twitter:image:alt" content="Exact Title of the Blog Post">
```

### In Blog Article Body (HTML Header)
To support both dark and light themes dynamically in the browser, use an HTML `<picture>` element:

```html
<header class="blog-header">
  <picture>
    <source srcset="/static/images/blog/<slug>-dark.png" media="(prefers-color-scheme: dark)">
    <img src="/static/images/blog/<slug>-light.png" alt="Exact Title of the Blog Post" class="blog-header-image" width="1200" height="630">
  </picture>
</header>
```

---

## Design System Reference

| Property | Dark Theme | Light Theme |
| :--- | :--- | :--- |
| **Background** | `#151413` | `#fbf9f4` |
| **Typography** | `#ede7dc` | `#1c1917` |
| **Font Family** | Georgia / EB Garamond | Georgia / EB Garamond |
| **Dimensions** | 1200 × 630 px | 1200 × 630 px |
| **Aspect Ratio** | 1.91 : 1 | 1.91 : 1 |
