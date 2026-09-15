---
name: internal-blog-importer
description: Synchronizes blog posts from blog.angular.dev, blog.flutter.dev, blog.dart.dev, or other Medium/RSS developer blogs into clean Markdown files with correct YYYY-MM-DD filenames, inline image descriptions, embed extraction, and code block language tagging.
---

# Internal Blog Importer Skill

The `internal-blog-importer` skill allows an agent to fetch and convert articles from Medium-hosted blogs (`blog.angular.dev`, `blog.flutter.dev`) or RSS feeds (`dart.dev`) into clean, production-grade markdown files. It automates sitemap scanning, content parsing (via Medium's `?format=json`), embed resolution, image description extraction, and language tagging.

---

## Directory Separation & Routing

The script automatically routes imported blog posts into product subfolders based on the URL/domain, or an explicit `--product` flag:
* `content/published/blog_posts/angular/` for articles from `blog.angular.dev`
* `content/published/blog_posts/flutter/` for articles from `blog.flutter.dev`
* `content/published/blog_posts/dart/` for articles from `blog.dart.dev`
* Custom product folders when passing `--product <name>`

---

## Quick Start

You can invoke the CLI script directly using python3:

```bash
# Sync a single post (automatically routed to angular/, dart/, or flutter/ subfolder)
python3 .agents/skills/internal-blog-importer/scripts/blog_importer.py sync-post --url "https://blog.angular.dev/announcing-angular-v19-e93175494297" --output-dir "content/published/blog_posts"

# Sync all missing posts from a sitemap (incremental sync)
python3 .agents/skills/internal-blog-importer/scripts/blog_importer.py sync-all --domain "blog.angular.dev" --output-dir "content/published/blog_posts"

# Explicit product override
python3 .agents/skills/internal-blog-importer/scripts/blog_importer.py sync-post --url "https://medium.com/my-blog/post-1" --product "myproduct" --output-dir "content/published/blog_posts"
```

---

## CLI Options

The skill runs `scripts/blog_importer.py`, which supports the following subcommands:

### `sync-post`
Fetches a single blog article URL, parses its content, formats it as Markdown, and saves it into the target product subfolder.
* `--url` (required): The full URL of the post.
* `--output-dir` (optional): Base output directory path (defaults to `content/published/blog_posts`).
* `--product` / `--subfolder` (optional): Explicit subfolder name (e.g. `angular`, `flutter`, `dart`).

### `sync-all`
Parses the blog sitemap/feed, checks the target subfolder for existing slugs, and downloads only new/missing articles.
* `--domain` (required): The domain of the blog (e.g. `blog.angular.dev`, `blog.flutter.dev`, or `dart.dev`).
* `--output-dir` (optional): Base output directory path (defaults to `content/published/blog_posts`).
* `--product` / `--subfolder` (optional): Explicit subfolder name override.

---

## Workflow

When the user asks to import or synchronize blog posts:

1. **Analyze Request**: Identify the target post URL or domain (such as `blog.angular.dev`).
2. **Execute the Script**: Run the appropriate command using the `run_command` tool.
3. **Inspect Results**: Check the console output and logs. List any failures clearly.
4. **Confirm Output**: Provide clickable file links to the newly created markdown files in the workspace.
