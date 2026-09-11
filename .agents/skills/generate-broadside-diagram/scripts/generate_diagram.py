#!/usr/bin/env python3
"""
generate_diagram.py

Generates diagrams as SVGs in light and dark color schemes matching
the Monograph & Broadside design system for redbrogdon.dev.

Supports generating the built-in sidecar architecture diagram or
compiling themed SVGs from semantic SVG templates.
"""

import argparse
import os
import sys
from pathlib import Path


# Monograph & Broadside color palette tokens for diagram generation
THEMES = {
    "light": {
        "bg": "#fbf9f4",
        "box_det_bg": "#f4f1ea",
        "box_det_stroke": "#d6d0c4",
        "box_agent_bg": "#fbf4f2",
        "box_agent_stroke": "#991b1b",
        "pill_det_bg": "#e8e3d8",
        "pill_det_text": "#44403c",
        "pill_agent_bg": "#f5deda",
        "pill_agent_text": "#991b1b",
        "sub_title": "#78716c",
        "sub_title_agent": "#8a4f47",
        "num_det": "#1c1917",
        "num_agent": "#991b1b",
        "text_body": "#292524",
        "text_code": "#44403c",
        "code_bg": "#ece8df",
        "arrow_line": "#a8a29e",
        "arrow_pill_bg": "#f4f1ea",
        "arrow_pill_stroke": "#d6d0c4",
        "arrow_pill_text": "#57534e",
    },
    "dark": {
        "bg": "#151413",
        "box_det_bg": "#1e1b19",
        "box_det_stroke": "#36312a",
        "box_agent_bg": "#1f1a14",
        "box_agent_stroke": "#d99b43",
        "pill_det_bg": "#2a2520",
        "pill_det_text": "#b8b0a2",
        "pill_agent_bg": "#362916",
        "pill_agent_text": "#d99b43",
        "sub_title": "#9d9588",
        "sub_title_agent": "#bda27e",
        "num_det": "#ede7dc",
        "num_agent": "#d99b43",
        "text_body": "#dcd5c8",
        "text_code": "#ede7dc",
        "code_bg": "#26231f",
        "arrow_line": "#575046",
        "arrow_pill_bg": "#1e1b19",
        "arrow_pill_stroke": "#36312a",
        "arrow_pill_text": "#b8b0a2",
    },
}

FONTS = {
    "serif": '"EB Garamond", Garamond, Georgia, serif',
    "mono": '"JetBrains Mono", Menlo, Monaco, "Courier New", monospace',
    "sans": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
}


def build_sidecar_architecture_svg(theme_name: str) -> str:
    """Renders the Sidecar Pipeline architecture diagram in the chosen theme."""
    t = THEMES[theme_name]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 460" width="100%" height="100%">
  <defs>
    <style>
      .bg {{ fill: {t["bg"]}; }}
      .box-det {{ fill: {t["box_det_bg"]}; stroke: {t["box_det_stroke"]}; stroke-width: 1.5; rx: 6; }}
      .box-agent {{ fill: {t["box_agent_bg"]}; stroke: {t["box_agent_stroke"]}; stroke-width: 1.5; rx: 6; }}
      .pill-det {{ fill: {t["pill_det_bg"]}; rx: 3; }}
      .pill-agent {{ fill: {t["pill_agent_bg"]}; rx: 3; }}
      .pill-text-det {{ fill: {t["pill_det_text"]}; font-family: {FONTS["mono"]}; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; }}
      .pill-text-agent {{ fill: {t["pill_agent_text"]}; font-family: {FONTS["mono"]}; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; }}
      .sub-title {{ fill: {t["sub_title"]}; font-family: {FONTS["serif"]}; font-size: 14.5px; font-style: italic; }}
      .sub-title-agent {{ fill: {t["sub_title_agent"]}; font-family: {FONTS["serif"]}; font-size: 14.5px; font-style: italic; }}
      .num-det {{ fill: {t["num_det"]}; font-family: {FONTS["serif"]}; font-size: 15px; font-weight: 600; }}
      .num-agent {{ fill: {t["num_agent"]}; font-family: {FONTS["serif"]}; font-size: 15px; font-weight: 600; }}
      .text-body {{ fill: {t["text_body"]}; font-family: {FONTS["sans"]}; font-size: 13px; }}
      .text-code {{ fill: {t["text_code"]}; font-family: {FONTS["mono"]}; font-size: 11.5px; }}
      .arrow-line {{ stroke: {t["arrow_line"]}; stroke-width: 1.5; stroke-linecap: round; }}
      .arrow-head {{ fill: {t["arrow_line"]}; }}
      .arrow-pill-bg {{ fill: {t["arrow_pill_bg"]}; stroke: {t["arrow_pill_stroke"]}; stroke-width: 1; rx: 12; }}
      .arrow-pill-text {{ fill: {t["arrow_pill_text"]}; font-family: {FONTS["sans"]}; font-size: 11.5px; font-weight: 500; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="720" height="460" class="bg" />

  <!-- Step 1: Deterministic -->
  <g transform="translate(60, 20)">
    <rect width="600" height="110" class="box-det" />
    <rect x="20" y="14" width="112" height="20" class="pill-det" />
    <text x="76" y="28" text-anchor="middle" class="pill-text-det">DETERMINISTIC</text>
    <text x="144" y="29" class="sub-title">Periodic scan &amp; deduplication</text>

    <text x="25" y="56" class="num-det">1.</text>
    <text x="44" y="56" class="text-body">Fetch Atom/RSS feeds (<tspan class="text-code">blog.flutter.dev</tspan> &amp; <tspan class="text-code">dart.dev/blog</tspan>)</text>

    <text x="25" y="76" class="num-det">2.</text>
    <text x="44" y="76" class="text-body">Filter for entries authored by Andrew Brogdon</text>

    <text x="25" y="96" class="num-det">3.</text>
    <text x="44" y="96" class="text-body">Deduplicate against <tspan class="text-code">public/blog/index.html</tspan> &amp; open GitHub PRs</text>
  </g>

  <!-- Arrow 1 -->
  <g transform="translate(360, 130)">
    <line x1="0" y1="0" x2="0" y2="12" class="arrow-line" />
    <rect x="-110" y="12" width="220" height="24" class="arrow-pill-bg" />
    <text x="0" y="28" text-anchor="middle" class="arrow-pill-text">New unindexed article discovered</text>
    <line x1="0" y1="36" x2="0" y2="48" class="arrow-line" />
    <polygon points="-5,44 5,44 0,51" class="arrow-head" />
  </g>

  <!-- Step 2: Agentic -->
  <g transform="translate(60, 185)">
    <rect width="600" height="92" class="box-agent" />
    <rect x="20" y="14" width="75" height="20" class="pill-agent" />
    <text x="57.5" y="28" text-anchor="middle" class="pill-text-agent">AGENTIC</text>
    <text x="107" y="29" class="sub-title-agent">Google GenAI / Gemini API</text>

    <text x="25" y="56" class="num-agent">4.</text>
    <text x="44" y="56" class="text-body">Analyze article content and extract core themes</text>

    <text x="25" y="76" class="num-agent">5.</text>
    <text x="44" y="76" class="text-body">Synthesize tailored editorial blurb &amp; PR summary matching site tone</text>
  </g>

  <!-- Arrow 2 -->
  <g transform="translate(360, 277)">
    <line x1="0" y1="0" x2="0" y2="12" class="arrow-line" />
    <rect x="-95" y="12" width="190" height="24" class="arrow-pill-bg" />
    <text x="0" y="28" text-anchor="middle" class="arrow-pill-text">Editorial blurb &amp; PR body</text>
    <line x1="0" y1="36" x2="0" y2="48" class="arrow-line" />
    <polygon points="-5,44 5,44 0,51" class="arrow-head" />
  </g>

  <!-- Step 3: Deterministic -->
  <g transform="translate(60, 332)">
    <rect width="600" height="110" class="box-det" />
    <rect x="20" y="14" width="112" height="20" class="pill-det" />
    <text x="76" y="28" text-anchor="middle" class="pill-text-det">DETERMINISTIC</text>
    <text x="144" y="29" class="sub-title">Git &amp; GitHub App automation</text>

    <text x="25" y="56" class="num-det">6.</text>
    <text x="44" y="56" class="text-body">Inject new entry into HTML &amp; RSS templates</text>

    <text x="25" y="76" class="num-det">7.</text>
    <text x="44" y="76" class="text-body">Mint GitHub App installation token (<tspan class="text-code">RS256 JWT</tspan>)</text>

    <text x="25" y="96" class="num-det">8.</text>
    <text x="44" y="96" class="text-body">Checkout branch (&lt;= 25 chars), commit under bot identity, &amp; open PR</text>
  </g>
</svg>
"""


def apply_theme_to_template(template_str: str, theme_name: str) -> str:
    """Substitutes {{token_name}} placeholders with theme values."""
    t = THEMES[theme_name]
    output = template_str
    for key, val in t.items():
        output = output.replace(f"{{{{{key}}}}}", val)
    for f_key, f_val in FONTS.items():
        output = output.replace(f"{{{{font_{f_key}}}}}", f_val)
    return output


def generate_diagram(
    name: str,
    output_dir: Path,
    theme: str = "both",
    template_path: str = None,
) -> list[Path]:
    """Generates light and/or dark SVGs for the given diagram name."""
    output_dir.mkdir(parents=True, exist_ok=True)
    themes_to_render = ["light", "dark"] if theme == "both" else [theme]
    created = []

    for th in themes_to_render:
        if template_path:
            with open(template_path, "r", encoding="utf-8") as f:
                content = apply_theme_to_template(f.read(), th)
        elif name == "sidecar-architecture":
            content = build_sidecar_architecture_svg(th)
        else:
            raise ValueError(f"Unknown diagram '{name}'. Provide --template for custom diagrams.")

        out_file = output_dir / f"{name}-{th}.svg"
        out_file.write_text(content, encoding="utf-8")
        print(f"Generated: {out_file}")
        created.append(out_file)

    return created


def main():
    parser = argparse.ArgumentParser(
        description="Generate light and dark SVGs matching the Monograph & Broadside design system."
    )
    parser.add_argument(
        "--name",
        default="sidecar-architecture",
        help="Diagram identifier / slug (default: sidecar-architecture)",
    )
    parser.add_argument(
        "--output-dir",
        default="public/static/images/blog",
        help="Output directory (default: public/static/images/blog)",
    )
    parser.add_argument(
        "--theme",
        choices=["both", "light", "dark"],
        default="both",
        help="Which theme variant(s) to generate (default: both)",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Optional path to a custom SVG template with {{token}} placeholders",
    )

    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    generate_diagram(args.name, out_dir, args.theme, args.template)


if __name__ == "__main__":
    main()
