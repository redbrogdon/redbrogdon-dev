#!/usr/bin/env python3
"""
generate_header.py

Generates minimalist, bold blog header images (PNG) locally for redbrogdon.dev.
Uses dynamic typography scaling in Garamond/Georgia serif, matching the site's
Monograph & Broadside design system in dark and light palettes.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


# Site Monograph & Broadside color palette
THEMES = {
    "dark": {
        "bg": "#151413",
        "text": "#ede7dc",
    },
    "light": {
        "bg": "#fbf9f4",
        "text": "#1c1917",
    },
}


def slugify(text: str) -> str:
    """Convert a title to a clean URL/filename slug."""
    text = text.lower().strip()
    # Replace smart quotes/apostrophes
    text = re.sub(r"[’‘'\"“”]", "", text)
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Strip leading/trailing hyphens
    return text.strip("-")


def detect_best_font(preferred_font: str = "EB Garamond") -> str:
    """
    Selects the best available serif font for macOS sips rasterization.
    Defaults to Georgia if EB Garamond is not registered in system fonts.
    """
    candidates = [f.strip() for f in preferred_font.split(",") if f.strip() and f.strip() != "serif"]
    if not candidates:
        return "Georgia"

    for cand in candidates:
        if cand in ["Georgia", "Palatino", "Iowan Old Style", "Baskerville"]:
            return cand

    return "Georgia"


def layout_title(
    title: str,
    max_w: int = 1030,
    max_h: int = 510,
    font_name: str = "Georgia",
):
    """
    Dynamically finds the optimal font size and line wrapping so that
    the title fills the canvas with bold, authoritative typography while
    avoiding awkward line breaks.
    """
    words = title.split()
    if not words:
        words = ["Untitled"]
    longest_word_len = max(len(w) for w in words)

    # Search from 140px down to 50px for the largest font size that fits comfortably
    best_layout = None

    for font_size in range(140, 48, -2):
        char_w = font_size * 0.54
        line_h = font_size * 1.15

        # Check if the longest word fits within max width
        if longest_word_len * char_w > max_w:
            continue

        wrap_cols = int(max_w / char_w)
        lines = textwrap.wrap(
            title,
            width=wrap_cols,
            break_long_words=False,
            break_on_hyphens=False,
        )

        # Verify no line exceeds max_w
        if any(len(line) * char_w > max_w for line in lines):
            continue

        # Cap maximum lines to 4 to preserve bold editorial impact
        if len(lines) > 4:
            continue

        total_h = (len(lines) - 1) * line_h + font_size
        if total_h <= max_h:
            best_layout = (font_size, lines, line_h, total_h)
            break

    if not best_layout:
        font_size = 48
        line_h = font_size * 1.15
        lines = textwrap.wrap(title, width=36, break_long_words=False, break_on_hyphens=False)
        total_h = (len(lines) - 1) * line_h + font_size
        best_layout = (font_size, lines, line_h, total_h)

    return best_layout


def render_svg(
    title: str,
    theme: str,
    width: int = 1200,
    height: int = 630,
    margin_x: int = 85,
    font_name: str = "Georgia",
) -> str:
    """Generates the SVG markup for the header image."""
    colors = THEMES.get(theme, THEMES["dark"])
    bg_color = colors["bg"]
    text_color = colors["text"]

    max_w = width - (2 * margin_x)
    max_h = height - 120

    font_size, lines, line_h, total_h = layout_title(
        title, max_w=max_w, max_h=max_h, font_name=font_name
    )

    # Vertical centering with optical baseline adjustment
    start_y = (height - total_h) // 2 + font_size - (font_size * 0.12)
    start_x = margin_x

    text_nodes = []
    for i, line in enumerate(lines):
        y = start_y + (i * line_h)
        # XML entity escaping
        escaped_line = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        text_nodes.append(
            f'  <text x="{start_x}" y="{y:.1f}" '
            f'font-family="{font_name}" font-size="{font_size}" font-weight="bold" '
            f'fill="{text_color}">{escaped_line}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="{bg_color}"/>
{''.join(text_nodes)}
</svg>"""
    return svg


def svg_to_png(svg_content: str, output_png_path: Path):
    """Converts SVG content to PNG using macOS built-in sips tool."""
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_svg:
        tmp_svg_path = Path(tmp_svg.name)
        tmp_svg.write(svg_content.encode("utf-8"))

    try:
        output_png_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["sips", "-s", "format", "png", str(tmp_svg_path), "--out", str(output_png_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"sips conversion failed: {result.stderr}")
    finally:
        if tmp_svg_path.exists():
            tmp_svg_path.unlink()


def generate_headers(
    title: str,
    slug: str = None,
    theme: str = "both",
    output_dir: str = "public/static/images/blog",
    width: int = 1200,
    height: int = 630,
    font_name: str = "Georgia",
    social_default: bool = True,
):
    """Generates PNG header images for a blog post."""
    if not slug:
        slug = slugify(title)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    themes_to_generate = ["dark", "light"] if theme == "both" else [theme]
    generated_files = []

    for t in themes_to_generate:
        svg_content = render_svg(
            title=title,
            theme=t,
            width=width,
            height=height,
            font_name=font_name,
        )
        file_name = f"{slug}-{t}.png"
        target_file = out_path / file_name
        svg_to_png(svg_content, target_file)
        generated_files.append(target_file)
        print(f"✓ Generated [{t}]: {target_file}")

    # Create social default (<slug>.png) from dark theme if requested
    if social_default and "dark" in themes_to_generate:
        social_target = out_path / f"{slug}.png"
        dark_file = out_path / f"{slug}-dark.png"
        if dark_file.exists():
            import shutil
            shutil.copyfile(dark_file, social_target)
            generated_files.append(social_target)
            print(f"✓ Generated [social default]: {social_target}")

    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description="Generate minimalist, bold blog header images (PNG) for redbrogdon.dev."
    )
    parser.add_argument(
        "title",
        nargs="?",
        help="Blog post title (e.g. 'Quick, reliable calculations with A2UI').",
    )
    parser.add_argument(
        "--title",
        dest="flag_title",
        help="Blog post title as a named flag.",
    )
    parser.add_argument(
        "--slug",
        help="Custom URL/filename slug. Defaults to slugified title.",
    )
    parser.add_argument(
        "--theme",
        choices=["dark", "light", "both"],
        default="both",
        help="Color scheme to generate (default: both).",
    )
    parser.add_argument(
        "--output-dir",
        default="public/static/images/blog",
        help="Output directory (default: public/static/images/blog).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1200,
        help="Image width in pixels (default: 1200).",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=630,
        help="Image height in pixels (default: 630).",
    )
    parser.add_argument(
        "--font",
        default="Georgia",
        help="Font family name (default: Georgia).",
    )
    parser.add_argument(
        "--no-social-default",
        action="store_false",
        dest="social_default",
        help="Disable copying the dark version to <slug>.png for social.",
    )

    args = parser.parse_args()
    title = args.title or args.flag_title

    if not title:
        parser.error("A blog post title is required (either as an argument or via --title).")

    font = detect_best_font(args.font)

    generate_headers(
        title=title,
        slug=args.slug,
        theme=args.theme,
        output_dir=args.output_dir,
        width=args.width,
        height=args.height,
        font_name=font,
        social_default=args.social_default,
    )


if __name__ == "__main__":
    main()
