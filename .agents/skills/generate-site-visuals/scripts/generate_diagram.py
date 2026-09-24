#!/usr/bin/env python3
"""
generate_diagram.py

Generates accessible, dual-theme vector diagrams in the canonical
Modern Swiss Monograph design system (ADR-008) for redbrogdon.dev.
"""

import argparse
import html
import sys
from pathlib import Path

# ==============================================================================
# MODERN SWISS MONOGRAPH COLOR TOKENS (ADR-008)
# ==============================================================================

THEMES = {
    "light": {
        "name": "light",
        "bg": "#fbf9f4",
        "surface": "#f4f1ea",
        "surface_card": "#ffffff",
        "surface_alt": "#f7f5ef",
        "border": "#d6d0c4",
        "border_subtle": "#e8e4da",
        "text_primary": "#1c1917",
        "text_muted": "#78716c",
        "text_inv": "#fbf9f4",
        "accent_red": "#991b1b",
        "accent_red_bg": "#fbf4f2",
        "accent_gold": "#b45309",
        "accent_gold_bright": "#d99b43",
        "accent_gold_bg": "#fdf7ec",
        "accent_teal": "#2d6a78",
        "accent_teal_bg": "#f0f6f7",
        "pill_bg": "#e8e3d8",
        "pill_text": "#44403c",
        "code_bg": "#ece8df",
        "arrow": "#78716c",
        "grid_dot": "#e2ded4",
        "grid_line": "#efece4",
    },
    "dark": {
        "name": "dark",
        "bg": "#151413",
        "surface": "#1e1b19",
        "surface_card": "#24201c",
        "surface_alt": "#2a2621",
        "border": "#36312a",
        "border_subtle": "#2b2722",
        "text_primary": "#ede7dc",
        "text_muted": "#9d9588",
        "text_inv": "#151413",
        "accent_red": "#e05345",
        "accent_red_bg": "#2a1b18",
        "accent_gold": "#d99b43",
        "accent_gold_bright": "#f3b965",
        "accent_gold_bg": "#292116",
        "accent_teal": "#5fa3b2",
        "accent_teal_bg": "#182427",
        "pill_bg": "#2a2520",
        "pill_text": "#b8b0a2",
        "code_bg": "#26231f",
        "arrow": "#9d9588",
        "grid_dot": "#27231e",
        "grid_line": "#1f1c19",
    }
}

FONTS = {
    "serif": "'EB Garamond', Garamond, Georgia, serif",
    "mono": "'JetBrains Mono', Menlo, Monaco, 'Courier New', monospace",
    "sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
}

def common_defs(t):
    return f"""
    <defs>
      <marker id="arrow-{t['name']}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{t['arrow']}" />
      </marker>
      <marker id="arrow-red-{t['name']}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{t['accent_red']}" />
      </marker>
      <marker id="arrow-teal-{t['name']}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{t['accent_teal']}" />
      </marker>
      <marker id="arrow-gold-{t['name']}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{t['accent_gold']}" />
      </marker>
    </defs>
    """

def sanitize_text(s: str) -> str:
    if not s:
        return ""
    return html.escape(html.unescape(s))

# ==============================================================================
# CANONICAL MODERN SWISS MONOGRAPH DIAGRAM BUILDERS
# ==============================================================================

def build_pipeline(t, title="Site Deployment DAG Pipeline", subtitle="Automated Verification, Prerendering &amp; Zero-CDN Edge Distribution"):
    """DAG Pipeline: Linear or branching execution stages."""
    title = sanitize_text(title)
    subtitle = sanitize_text(subtitle)
    arrow = f"url(#arrow-{t['name']})"
    arrow_red = f"url(#arrow-red-{t['name']})"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 380" width="100%" height="100%">
  {common_defs(t)}
  <rect width="820" height="380" fill="{t['bg']}" />

  <text x="36" y="44" font-family="{FONTS['serif']}" font-size="24" font-weight="600" fill="{t['text_primary']}">{title}</text>
  <text x="36" y="68" font-family="{FONTS['sans']}" font-size="13" fill="{t['text_muted']}">{subtitle}</text>
  <line x1="36" y1="84" x2="784" y2="84" stroke="{t['border']}" stroke-width="1" />

  <!-- Node 1 -->
  <g transform="translate(36, 130)">
    <rect width="150" height="120" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1" />
    <circle cx="20" cy="20" r="4" fill="{t['accent_teal']}" />
    <text x="32" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_teal']}">STAGE 01</text>
    <text x="16" y="55" font-family="{FONTS['sans']}" font-size="14" font-weight="700" fill="{t['text_primary']}">Lint &amp; Rules</text>
    <text x="16" y="80" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">markdownlint</text>
    <text x="16" y="96" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">GEMINI.md check</text>
  </g>

  <!-- Node 2 -->
  <g transform="translate(230, 130)">
    <rect width="150" height="120" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1" />
    <circle cx="20" cy="20" r="4" fill="{t['accent_teal']}" />
    <text x="32" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_teal']}">STAGE 02</text>
    <text x="16" y="55" font-family="{FONTS['sans']}" font-size="14" font-weight="700" fill="{t['text_primary']}">Sync Validation</text>
    <text x="16" y="80" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">RSS &amp; Sitemap</text>
    <text x="16" y="96" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">Descending sort</text>
  </g>

  <!-- Node 3 -->
  <g transform="translate(424, 130)">
    <rect width="160" height="120" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1" />
    <circle cx="20" cy="20" r="4" fill="{t['accent_gold']}" />
    <text x="32" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_gold']}">STAGE 03</text>
    <text x="16" y="55" font-family="{FONTS['sans']}" font-size="14" font-weight="700" fill="{t['text_primary']}">Asset Check</text>
    <text x="16" y="80" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">Prism zero-FOUC</text>
    <text x="16" y="96" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">Local webfonts</text>
  </g>

  <!-- Node 4 -->
  <g transform="translate(628, 130)">
    <rect width="156" height="120" rx="2" fill="{t['accent_red_bg']}" stroke="{t['accent_red']}" stroke-width="1.5" />
    <circle cx="20" cy="20" r="4" fill="{t['accent_red']}" />
    <text x="32" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_red']}">STAGE 04</text>
    <text x="16" y="55" font-family="{FONTS['sans']}" font-size="14" font-weight="700" fill="{t['text_primary']}">Edge Deploy</text>
    <text x="16" y="80" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">Firebase Hosting</text>
    <text x="16" y="96" font-family="{FONTS['mono']}" font-size="11" fill="{t['accent_red']}">Atomic Cutover</text>
  </g>

  <!-- Connectors -->
  <line x1="186" y1="190" x2="228" y2="190" stroke="{t['text_primary']}" stroke-width="1.5" marker-end="{arrow}" />
  <line x1="380" y1="190" x2="422" y2="190" stroke="{t['text_primary']}" stroke-width="1.5" marker-end="{arrow}" />
  <line x1="584" y1="190" x2="626" y2="190" stroke="{t['accent_red']}" stroke-width="1.5" marker-end="{arrow_red}" />

  <!-- Bottom Metric Bar -->
  <rect x="36" y="290" width="748" height="40" rx="2" fill="{t['surface_alt']}" />
  <text x="50" y="315" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">TOTAL BUILD DURATION: 18.4s · STATUS: SUCCESSFUL · CACHE HIT: 94.2%</text>
</svg>"""

def build_topology(t, title="Infrastructure &amp; Edge Topology", subtitle="Global Edge Points of Presence &amp; Static Content Invalidation"):
    """Topology: Layered multi-tier architecture."""
    title = sanitize_text(title)
    subtitle = sanitize_text(subtitle)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 400" width="100%" height="100%">
  {common_defs(t)}
  <rect width="820" height="400" fill="{t['bg']}" />

  <text x="36" y="44" font-family="{FONTS['serif']}" font-size="24" font-weight="600" fill="{t['text_primary']}">{title}</text>
  <text x="36" y="68" font-family="{FONTS['sans']}" font-size="13" fill="{t['text_muted']}">{subtitle}</text>
  <line x1="36" y1="84" x2="784" y2="84" stroke="{t['border']}" stroke-width="1" />

  <!-- Layer: Client Viewports -->
  <g transform="translate(36, 120)">
    <rect width="170" height="180" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['text_muted']}">CLIENT LAYER</text>
    <text x="16" y="55" font-family="{FONTS['sans']}" font-size="13" font-weight="600" fill="{t['text_primary']}">Desktop Web</text>
    <text x="16" y="75" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">EB Garamond / Mono</text>
    <line x1="16" y1="95" x2="154" y2="95" stroke="{t['border']}" stroke-width="0.8" />
    <text x="16" y="125" font-family="{FONTS['sans']}" font-size="13" font-weight="600" fill="{t['text_primary']}">Mobile Safari / Chrome</text>
    <text x="16" y="145" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">prefers-color-scheme</text>
  </g>

  <!-- Layer: Edge CDN -->
  <g transform="translate(250, 120)">
    <rect width="280" height="180" rx="2" fill="{t['accent_teal_bg']}" stroke="{t['accent_teal']}" stroke-width="1.2" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_teal']}">GLOBAL EDGE CDN</text>
    <text x="16" y="55" font-family="{FONTS['sans']}" font-size="14" font-weight="600" fill="{t['text_primary']}">Firebase Global Anycast</text>
    <text x="16" y="80" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">TTL: max-age=3600</text>
    <text x="16" y="100" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">Brotli + Gzip Compression</text>
    <text x="16" y="120" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">Zero External DNS Lookups</text>
    <rect x="16" y="140" width="248" height="24" rx="2" fill="{t['bg']}" />
    <text x="140" y="156" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['accent_teal']}" font-weight="700" text-anchor="middle">SSL: Auto-Renewing Let's Encrypt</text>
  </g>

  <!-- Layer: Origin Storage -->
  <g transform="translate(574, 120)">
    <rect width="210" height="180" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['text_muted']}">ORIGIN STORE</text>
    <text x="16" y="55" font-family="{FONTS['sans']}" font-size="14" font-weight="600" fill="{t['text_primary']}">Google Cloud Storage</text>
    <text x="16" y="80" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">/public/blog/*.html</text>
    <text x="16" y="100" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">/public/static/css/*</text>
    <text x="16" y="120" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">/public/static/js/*</text>
    <text x="16" y="140" font-family="{FONTS['mono']}" font-size="11" fill="{t['text_muted']}">/public/static/webfonts/*</text>
  </g>

  <!-- Connecting Lines -->
  <line x1="206" y1="210" x2="250" y2="210" stroke="{t['text_primary']}" stroke-width="1.5" />
  <line x1="530" y1="210" x2="574" y2="210" stroke="{t['text_primary']}" stroke-width="1.5" />
</svg>"""

def build_sidecar(t, title="Deterministic &amp; Agentic Sidecar Architecture", subtitle="ADR-002 · Multi-Source Feed Ingestion with LLM Synthesis"):
    """Sidecar: Two-stage hybrid pipeline."""
    title = sanitize_text(title)
    subtitle = sanitize_text(subtitle)
    arrow = f"url(#arrow-{t['name']})"
    arrow_red = f"url(#arrow-red-{t['name']})"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 420" width="100%" height="100%">
  {common_defs(t)}
  <rect width="820" height="420" fill="{t['bg']}" />

  <text x="36" y="44" font-family="{FONTS['serif']}" font-size="24" font-weight="600" fill="{t['text_primary']}">{title}</text>
  <text x="36" y="68" font-family="{FONTS['sans']}" font-size="13" fill="{t['text_muted']}">{subtitle}</text>
  <line x1="36" y1="84" x2="784" y2="84" stroke="{t['border']}" stroke-width="1" />

  <!-- Stage 1: Deterministic Engine -->
  <g transform="translate(36, 120)">
    <rect width="748" height="105" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.2" />
    <circle cx="20" cy="22" r="4" fill="{t['accent_teal']}" />
    <text x="32" y="26" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_teal']}">DETERMINISTIC ENGINE · PYTHON RUNTIME</text>
    
    <text x="20" y="55" font-family="{FONTS['sans']}" font-size="13" font-weight="600" fill="{t['text_primary']}">1. Scrape &amp; Deduplicate</text>
    <text x="20" y="75" font-family="{FONTS['sans']}" font-size="11.5" fill="{t['text_muted']}">Periodic cron polling of Atom/RSS feeds and YouTube HTML. Verifies author attribution.</text>
    <text x="20" y="92" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['text_muted']}">blog.flutter.dev · dart.dev/blog · youtube.com/@flutterdev</text>
  </g>

  <!-- Transition Arrow -->
  <line x1="410" y1="225" x2="410" y2="260" stroke="{t['accent_red']}" stroke-width="1.5" marker-end="{arrow_red}" />
  <rect x="330" y="235" width="160" height="20" rx="2" fill="{t['accent_red_bg']}" stroke="{t['accent_red']}" stroke-width="0.8" />
  <text x="410" y="249" font-family="{FONTS['mono']}" font-size="9.5" font-weight="700" fill="{t['accent_red']}" text-anchor="middle">NEW MEDIA DETECTED</text>

  <!-- Stage 2: Agentic Synthesis -->
  <g transform="translate(36, 265)">
    <rect width="748" height="115" rx="2" fill="{t['accent_red_bg']}" stroke="{t['accent_red']}" stroke-width="1.5" />
    <circle cx="20" cy="22" r="4" fill="{t['accent_red']}" />
    <text x="32" y="26" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_red']}">AGENTIC SYNTHESIS · GEMINI 3.8 FLASH</text>
    
    <text x="20" y="55" font-family="{FONTS['sans']}" font-size="13" font-weight="700" fill="{t['text_primary']}">2. Synthesize &amp; Commit</text>
    <text x="20" y="75" font-family="{FONTS['sans']}" font-size="11.5" fill="{t['text_primary']}">Generates 1–2 sentence editorial summary in the Monograph voice, mints RS256 JWT, and creates PR.</text>
    <text x="20" y="96" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['accent_red']}">public/media/index.html · public/feed.xml · public/sitemap.xml</text>
  </g>
</svg>"""

def build_dataflow(t, title="Sidecar Video Ingestion Data Flow", subtitle="Dual-Mode Fetching: Atom XML with Fallback to ytInitialData JSON Parsing"):
    """Data Flow: Branching acquisition with convergence to LLM synthesis."""
    title = sanitize_text(title)
    subtitle = sanitize_text(subtitle)
    arrow = f"url(#arrow-{t['name']})"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 400" width="100%" height="100%">
  {common_defs(t)}
  <rect width="820" height="400" fill="{t['bg']}" />

  <text x="36" y="44" font-family="{FONTS['serif']}" font-size="24" font-weight="600" fill="{t['text_primary']}">{title}</text>
  <text x="36" y="68" font-family="{FONTS['sans']}" font-size="13" fill="{t['text_muted']}">{subtitle}</text>
  <line x1="36" y1="84" x2="784" y2="84" stroke="{t['border']}" stroke-width="1" />

  <!-- Input Source -->
  <g transform="translate(36, 130)">
    <rect width="160" height="90" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['accent_red']}">YOUTUBE CHANNEL</text>
    <text x="16" y="50" font-family="{FONTS['sans']}" font-size="13" font-weight="600" fill="{t['text_primary']}">@flutterdev</text>
    <text x="16" y="70" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['text_muted']}">Atom Feed / HTML</text>
  </g>

  <!-- Dual Branch -->
  <path d="M 196 160 L 260 135" stroke="{t['text_primary']}" stroke-width="1.2" marker-end="{arrow}" />
  <path d="M 196 185 L 260 215" stroke="{t['text_primary']}" stroke-width="1.2" marker-end="{arrow}" />

  <!-- Primary Path -->
  <g transform="translate(265, 105)">
    <rect width="180" height="60" rx="2" fill="{t['surface_alt']}" stroke="{t['border']}" stroke-width="1" />
    <text x="14" y="22" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['accent_teal']}">PRIMARY (FAST)</text>
    <text x="14" y="42" font-family="{FONTS['sans']}" font-size="12" font-weight="600" fill="{t['text_primary']}">Atom XML Feed Parser</text>
  </g>

  <!-- Fallback Path -->
  <g transform="translate(265, 185)">
    <rect width="180" height="60" rx="2" fill="{t['surface_alt']}" stroke="{t['border']}" stroke-width="1" />
    <text x="14" y="22" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['accent_gold']}">FALLBACK (ROBUST)</text>
    <text x="14" y="42" font-family="{FONTS['sans']}" font-size="12" font-weight="600" fill="{t['text_primary']}">ytInitialData Scraper</text>
  </g>

  <!-- Converge to Filter -->
  <path d="M 445 135 L 495 160" stroke="{t['text_primary']}" stroke-width="1.2" marker-end="{arrow}" />
  <path d="M 445 215 L 495 185" stroke="{t['text_primary']}" stroke-width="1.2" marker-end="{arrow}" />

  <!-- Synthesis Engine -->
  <g transform="translate(500, 130)">
    <rect width="140" height="90" rx="2" fill="{t['accent_red_bg']}" stroke="{t['accent_red']}" stroke-width="1.5" />
    <text x="14" y="24" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['accent_red']}">LLM SYNTHESIS</text>
    <text x="14" y="50" font-family="{FONTS['sans']}" font-size="12" font-weight="600" fill="{t['text_primary']}">Title &amp; Summary</text>
    <text x="14" y="70" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['text_muted']}">gemini-flash</text>
  </g>

  <path d="M 640 175 L 680 175" stroke="{t['text_primary']}" stroke-width="1.5" marker-end="{arrow}" />

  <!-- Output Files -->
  <g transform="translate(685, 120)">
    <rect width="100" height="110" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1" />
    <text x="12" y="24" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['text_muted']}">EMIT</text>
    <text x="12" y="50" font-family="{FONTS['mono']}" font-size="10" fill="{t['text_primary']}">media.html</text>
    <text x="12" y="70" font-family="{FONTS['mono']}" font-size="10" fill="{t['text_primary']}">feed.xml</text>
    <text x="12" y="90" font-family="{FONTS['mono']}" font-size="10" fill="{t['text_primary']}">sitemap</text>
  </g>
</svg>"""

def build_taxonomy(t, title="Antigravity Customization Taxonomy", subtitle="Precedence &amp; Resolution Order for Workspace Agent Directives"):
    """Taxonomy: Strict hierarchical precedence layout."""
    title = sanitize_text(title)
    subtitle = sanitize_text(subtitle)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 400" width="100%" height="100%">
  {common_defs(t)}
  <rect width="820" height="400" fill="{t['bg']}" />

  <text x="36" y="44" font-family="{FONTS['serif']}" font-size="24" font-weight="600" fill="{t['text_primary']}">{title}</text>
  <text x="36" y="68" font-family="{FONTS['sans']}" font-size="13" fill="{t['text_muted']}">{subtitle}</text>
  <line x1="36" y1="84" x2="784" y2="84" stroke="{t['border']}" stroke-width="1" />

  <!-- Root -->
  <g transform="translate(36, 120)">
    <rect width="210" height="60" rx="2" fill="{t['accent_red_bg']}" stroke="{t['accent_red']}" stroke-width="1.5" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['accent_red']}">HIGHEST PRECEDENCE</text>
    <text x="16" y="45" font-family="{FONTS['sans']}" font-size="13" font-weight="700" fill="{t['text_primary']}">User Explicit Prompts</text>
  </g>

  <!-- Level 2: Workspace Rules -->
  <g transform="translate(286, 120)">
    <rect width="230" height="60" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.2" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['accent_gold']}">PRECEDENCE LEVEL 2</text>
    <text x="16" y="45" font-family="{FONTS['sans']}" font-size="13" font-weight="600" fill="{t['text_primary']}">Workspace Rules (GEMINI.md)</text>
  </g>

  <!-- Level 3: Specialized Skills -->
  <g transform="translate(556, 120)">
    <rect width="228" height="60" rx="2" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.2" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['accent_teal']}">PRECEDENCE LEVEL 3</text>
    <text x="16" y="45" font-family="{FONTS['sans']}" font-size="13" font-weight="600" fill="{t['text_primary']}">Skills (.agents/skills/*)</text>
  </g>

  <!-- Child Leaves under Skills -->
  <g transform="translate(556, 210)">
    <rect width="228" height="150" rx="2" fill="{t['surface_alt']}" stroke="{t['border_subtle']}" />
    <text x="16" y="24" font-family="{FONTS['mono']}" font-size="11" font-weight="700" fill="{t['text_primary']}">REGISTERED SKILLS</text>
    <text x="16" y="50" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['accent_red']}">• generate-site-visuals</text>
    <text x="16" y="70" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['text_muted']}">• content-create-blog-post</text>
    <text x="16" y="90" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['text_muted']}">• content-create-social-post</text>
    <text x="16" y="110" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['text_muted']}">• internal-blog-importer</text>
    <text x="16" y="130" font-family="{FONTS['mono']}" font-size="10.5" fill="{t['text_muted']}">• meta-refine-skill</text>
  </g>

  <!-- Connectors -->
  <line x1="246" y1="150" x2="286" y2="150" stroke="{t['border']}" stroke-width="1.5" />
  <line x1="516" y1="150" x2="556" y2="150" stroke="{t['border']}" stroke-width="1.5" />
  <line x1="670" y1="180" x2="670" y2="210" stroke="{t['border']}" stroke-width="1.5" />
</svg>"""

def build_triad(t, title="The Triad of Modern Agentic Engineering", subtitle="Convergence of Deterministic Architecture, LLM Synthesis, and Editorial Craft"):
    """Triad: Intersecting domain Venn diagram."""
    title = sanitize_text(title)
    subtitle = sanitize_text(subtitle)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 420" width="100%" height="100%">
  {common_defs(t)}
  <rect width="820" height="420" fill="{t['bg']}" />

  <text x="36" y="44" font-family="{FONTS['serif']}" font-size="24" font-weight="600" fill="{t['text_primary']}">{title}</text>
  <text x="36" y="68" font-family="{FONTS['sans']}" font-size="13" fill="{t['text_muted']}">{subtitle}</text>
  <line x1="36" y1="84" x2="784" y2="84" stroke="{t['border']}" stroke-width="1" />

  <!-- Venn Circles -->
  <circle cx="340" cy="220" r="120" fill="{t['accent_red_bg']}" stroke="{t['accent_red']}" stroke-width="1.8" opacity="0.85" />
  <circle cx="480" cy="220" r="120" fill="{t['accent_teal_bg']}" stroke="{t['accent_teal']}" stroke-width="1.8" opacity="0.85" />
  <circle cx="410" cy="300" r="120" fill="{t['accent_gold_bg']}" stroke="{t['accent_gold']}" stroke-width="1.8" opacity="0.85" />

  <!-- Labels -->
  <text x="270" y="180" font-family="{FONTS['serif']}" font-size="16" font-weight="700" fill="{t['accent_red']}">Deterministic</text>
  <text x="270" y="198" font-family="{FONTS['sans']}" font-size="11" fill="{t['text_muted']}">Plumbing &amp; Sandboxes</text>

  <text x="540" y="180" font-family="{FONTS['serif']}" font-size="16" font-weight="700" fill="{t['accent_teal']}">Generative</text>
  <text x="540" y="198" font-family="{FONTS['sans']}" font-size="11" fill="{t['text_muted']}">LLMs &amp; Tool Calling</text>

  <text x="410" y="380" font-family="{FONTS['serif']}" font-size="16" font-weight="700" fill="{t['accent_gold']}" text-anchor="middle">Editorial Craft</text>
  <text x="410" y="398" font-family="{FONTS['sans']}" font-size="11" fill="{t['text_muted']}" text-anchor="middle">Design Systems &amp; Writing</text>

  <!-- Center Intersection -->
  <circle cx="410" cy="245" r="32" fill="{t['bg']}" stroke="{t['text_primary']}" stroke-width="1.5" />
  <text x="410" y="243" font-family="{FONTS['mono']}" font-size="10" font-weight="700" fill="{t['text_primary']}" text-anchor="middle">redbrogdon</text>
  <text x="410" y="257" font-family="{FONTS['mono']}" font-size="9" fill="{t['text_muted']}" text-anchor="middle">.dev</text>
</svg>"""

BUILDERS = {
    "pipeline": build_pipeline,
    "topology": build_topology,
    "sidecar": build_sidecar,
    "dataflow": build_dataflow,
    "taxonomy": build_taxonomy,
    "triad": build_triad,
}

# ==============================================================================
# CLI DISPATCHER
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Modern Swiss Monograph dual-theme diagrams for redbrogdon.dev."
    )
    parser.add_argument(
        "--type",
        choices=list(BUILDERS.keys()),
        default="pipeline",
        help="Canonical diagram structural type (default: pipeline)"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="diagram",
        help="Slug prefix for generated files (default: diagram)"
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Optional custom diagram title"
    )
    parser.add_argument(
        "--subtitle",
        type=str,
        default=None,
        help="Optional custom diagram subtitle"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("public/static/images/blog"),
        help="Directory to write output SVGs (default: public/static/images/blog)"
    )
    parser.add_argument(
        "--theme",
        choices=["light", "dark", "both"],
        default="both",
        help="Themes to generate: light, dark, or both (default: both)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available diagram builders and exit"
    )

    args = parser.parse_args()

    if args.list:
        print("Available Modern Swiss Monograph diagram types:")
        for k in sorted(BUILDERS.keys()):
            print(f"  - {k}")
        sys.exit(0)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    builder = BUILDERS[args.type]

    themes_to_run = ["light", "dark"] if args.theme == "both" else [args.theme]

    for th_name in themes_to_run:
        theme = THEMES[th_name]
        kwargs = {}
        if args.title:
            kwargs["title"] = html.escape(html.unescape(args.title))
        if args.subtitle:
            kwargs["subtitle"] = html.escape(html.unescape(args.subtitle))

        svg_content = builder(theme, **kwargs)
        out_path = args.output_dir / f"{args.name}-{th_name}.svg"
        out_path.write_text(svg_content.strip() + "\n", encoding="utf-8")
        print(f"Generated: {out_path}")

if __name__ == "__main__":
    main()
