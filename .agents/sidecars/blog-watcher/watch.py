#!/usr/bin/env python3
"""
Antigravity Blog Watcher & Auto-PR Agent

Monitors blog.flutter.dev and blog.dart.dev for new articles by Andrew Brogdon.
When a new article is discovered, uses Gemini 3.8 to generate an editorial summary,
updates public/blog/index.html and public/feed.xml, and opens a GitHub PR.
"""

import argparse
import datetime
import email.utils
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("blog-watcher")

FEEDS = [
    {
        "name": "Flutter Blog",
        "url": "https://blog.flutter.dev/feed.xml",
    },
    {
        "name": "Dart Blog",
        "url": "https://blog.dart.dev/feed.xml",
    },
]

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def load_env_file():
    """Load environment variables from .env if present in sidecar directory."""
    sidecar_dir = Path(__file__).resolve().parent
    for env_candidate in [sidecar_dir / ".env", Path.home() / ".gemini" / "config" / "sidecars" / "blog-watcher" / ".env"]:
        if env_candidate.exists():
            for line in env_candidate.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'\"")
            break

load_env_file()


def find_repo_root() -> Path:
    """Find the root directory of the redbrogdon-dev repository."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists() and (current / "public" / "blog" / "index.html").exists():
            return current
        current = current.parent
    # Fallback to current working directory
    return Path(os.getcwd())


def get_github_app_auth(repo_root: Path) -> tuple[str, str] | None:
    """
    Authenticate as a GitHub App using github.pem and GITHUB_APP_ID.
    Returns (installation_access_token, app_id_or_slug) or None if not configured.
    """
    pem_candidates = [
        repo_root / ".agents" / "sidecars" / "blog-watcher" / "github.pem",
        Path.home() / ".gemini" / "config" / "sidecars" / "blog-watcher" / "github.pem",
    ]
    pem_path = next((p for p in pem_candidates if p.exists()), None)
    if not pem_path:
        return None

    app_id = os.environ.get("GITHUB_APP_ID", "redbrogdon-antigravity").strip()
    if not app_id:
        return None

    try:
        import jwt
    except ImportError:
        logger.error("PyJWT is required for GitHub App authentication (pip install pyjwt cryptography).")
        return None

    # If app_id is non-numeric slug, query GitHub's public API to resolve to numeric App ID
    if not app_id.isdigit():
        try:
            req = urllib.request.Request(
                f"https://api.github.com/apps/{app_id}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "AntigravityBlogWatcher/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                app_data = json.loads(resp.read().decode("utf-8"))
                resolved_id = str(app_data["id"])
                logger.info(f"Resolved GitHub App '{app_id}' to numerical App ID {resolved_id}")
                app_id = resolved_id
        except Exception as e:
            logger.warning(f"Could not resolve GitHub App slug '{app_id}' via API: {e}")

    # Generate RS256 JWT
    try:
        private_key = pem_path.read_text(encoding="utf-8")
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": str(app_id),
        }
        jwt_token = jwt.encode(payload, private_key, algorithm="RS256")
    except Exception as e:
        logger.error(f"Failed to sign JWT with {pem_path.name}: {e}")
        return None

    # Find repository installation ID
    installation_id = os.environ.get("GITHUB_APP_INSTALLATION_ID")
    if not installation_id:
        try:
            inst_req = urllib.request.Request(
                "https://api.github.com/repos/redbrogdon/redbrogdon-dev/installation",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "User-Agent": "AntigravityBlogWatcher/1.0",
                },
            )
            with urllib.request.urlopen(inst_req, timeout=10) as resp:
                inst_data = json.loads(resp.read().decode("utf-8"))
                installation_id = str(inst_data["id"])
                logger.info(f"Discovered GitHub App installation ID: {installation_id}")
        except Exception as e:
            logger.error(f"Failed to find installation ID for redbrogdon/redbrogdon-dev: {e}")
            return None

    # Request an installation access token
    try:
        token_req = urllib.request.Request(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            data=b"{}",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "AntigravityBlogWatcher/1.0",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(token_req, timeout=10) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
            token = token_data.get("token")
            logger.info("Successfully generated GitHub App installation access token.")
            return token, app_id
    except Exception as e:
        logger.error(f"Failed to obtain installation access token from GitHub API: {e}")
        return None


def fetch_feed(url: str) -> str:
    """Fetch raw XML from an Atom/RSS feed URL, following redirects."""
    headers = {"User-Agent": "AntigravityBlogWatcher/1.0 (+https://redbrogdon.dev)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_feed_entries(raw_xml: str, feed_name: str) -> list[dict]:
    """Parse Atom entries and filter for articles authored by Andrew Brogdon."""
    root = ET.fromstring(raw_xml)
    entries = []

    # Check for Atom entries
    atom_entries = root.findall(".//atom:entry", ATOM_NS)
    if not atom_entries:
        atom_entries = root.findall(".//entry")

    for entry in atom_entries:
        # Check author
        author_elem = entry.find(".//atom:author/atom:name", ATOM_NS)
        if author_elem is None:
            author_elem = entry.find(".//author/name")
        author_name = author_elem.text.strip() if author_elem is not None and author_elem.text else ""

        # Filter strictly for Andrew Brogdon
        if "brogdon" not in author_name.lower():
            continue

        title_elem = entry.find("atom:title", ATOM_NS)
        if title_elem is None:
            title_elem = entry.find("title")
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"

        # Link
        link_elem = entry.find("atom:link[@rel='alternate']", ATOM_NS)
        if link_elem is None:
            link_elem = entry.find("atom:link", ATOM_NS)
        if link_elem is None:
            link_elem = entry.find("link")

        link = ""
        if link_elem is not None:
            link = link_elem.attrib.get("href") or link_elem.text or ""
        link = link.strip()

        # Published / Updated date
        pub_elem = entry.find("atom:published", ATOM_NS)
        if pub_elem is None:
            pub_elem = entry.find("atom:updated", ATOM_NS)
        if pub_elem is None:
            pub_elem = entry.find("published")
        if pub_elem is None:
            pub_elem = entry.find("updated")
        pub_date_str = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

        # Summary / Content
        content_elem = entry.find("atom:content", ATOM_NS)
        if content_elem is None:
            content_elem = entry.find("atom:summary", ATOM_NS)
        if content_elem is None:
            content_elem = entry.find("content")
        if content_elem is None:
            content_elem = entry.find("summary")
        content_text = content_elem.text.strip() if content_elem is not None and content_elem.text else ""
        # Clean basic HTML tags from summary
        cleaned_content = re.sub(r"<[^>]+>", " ", content_text)
        cleaned_content = re.sub(r"\s+", " ", cleaned_content).strip()

        entries.append({
            "title": title,
            "url": link,
            "author": author_name,
            "pub_date_str": pub_date_str,
            "summary": cleaned_content[:1500],
            "feed": feed_name,
        })

    return entries


def get_existing_slugs_and_urls(blog_html_path: Path) -> set[str]:
    """Extract known slugs and URLs from public/blog/index.html to avoid duplicate entries."""
    if not blog_html_path.exists():
        return set()

    content = blog_html_path.read_text(encoding="utf-8")
    existing = set()

    # Match all hrefs inside editorial-list
    hrefs = re.findall(r'href=["\'](https?://[^"\']+)["\']', content)
    for h in hrefs:
        existing.add(h)
        # Also extract slug component
        slug = h.rstrip("/").split("/")[-1].split("#")[0]
        if slug:
            existing.add(slug)

    # Match article titles
    titles = re.findall(r'class="entry-name">([^<]+)</a>', content)
    for t in titles:
        # Normalize title
        norm_t = re.sub(r"[^a-zA-Z0-9]+", "", t).lower()
        if norm_t:
            existing.add(norm_t)

    return existing


def is_new_article(article: dict, existing: set[str]) -> bool:
    """Check if an article is already recorded on redbrogdon.dev."""
    url = article["url"]
    slug = url.rstrip("/").split("/")[-1].split("#")[0]
    norm_title = re.sub(r"[^a-zA-Z0-9]+", "", article["title"]).lower()

    if url in existing or slug in existing or norm_title in existing:
        return False
    return True


def generate_branch_name(url: str, title: str) -> str:
    """Generate a git branch name guaranteed to be <= 25 characters total."""
    # Prefix is 9 characters
    prefix = "bot/blog-"
    # Extract slug from URL or title
    slug = url.rstrip("/").split("/")[-1]
    if not slug or len(slug) < 3:
        slug = title
    # Sanitize slug: alphanumeric only
    clean_slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower()
    # 25 max - 9 prefix = 16 chars max for slug
    truncated_slug = clean_slug[:16].rstrip("-")
    branch = f"{prefix}{truncated_slug}"
    assert len(branch) <= 25, f"Branch name {branch} exceeds 25 chars"
    return branch


def is_branch_or_pr_pending(repo_root: Path, branch: str) -> bool:
    """Check if a local branch or open GitHub PR already exists for this branch."""
    # 1. Check local git branches
    res = subprocess.run(
        ["git", "branch", "--list", branch],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if res.returncode == 0 and res.stdout.strip():
        return True

    # 2. Check open PRs via GitHub CLI
    try:
        if not os.environ.get("GH_TOKEN") and not os.environ.get("GITHUB_TOKEN"):
            app_auth = get_github_app_auth(repo_root)
            if app_auth:
                os.environ["GH_TOKEN"] = app_auth[0]
                os.environ["GITHUB_TOKEN"] = app_auth[0]

        pr_check = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "headRefName"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            env=os.environ,
        )
        if pr_check.returncode == 0 and pr_check.stdout.strip():
            prs = json.loads(pr_check.stdout)
            if any(p.get("headRefName") == branch for p in prs):
                return True
    except Exception:
        pass

    return False


def format_pub_date(date_str: str) -> tuple[str, str]:
    """Parse ISO date to (Month Year, RFC 822 format for RSS)."""
    try:
        # e.g., '2026-08-28T14:30:00Z' or '2026-08-28'
        clean_str = date_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean_str)
    except Exception:
        dt = datetime.datetime.now(datetime.timezone.utc)

    month_year = dt.strftime("%B %Y")
    rfc822_date = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return month_year, rfc822_date


def generate_blurb_with_gemini(article: dict, model_name: str = "gemini-3.8-flash") -> dict:
    """Use Gemini 3.8 to generate an editorial description matching the site tone."""
    try:
        from google import genai
        client = genai.Client()

        prompt = f"""You are an assistant for Andrew Brogdon's personal website (redbrogdon.dev).
The website has a refined, literary, monograph-style tone for technical essays and deep dives.
Here are existing blog entries for voice and structure reference:
- "How to tackle cold-start latency in generative UI apps. Explores pre-generating, streaming, and caching A2UI messages using the Commis kitchen assistant as a case study."
- "Creating Flutter frontends for Python-based ADK agents using a structured 5-step learning loop with Google Antigravity."
- "Key architectural changes to the genui package, showing how the A2UI protocol bridges autonomous AI agents with client-side Flutter widget catalogs."
- "Learn how client-side functions allow an agent to delegate local operations directly to Dart code running on a user's device."

Generate a 1-to-2 sentence editorial description for this newly published article:
Title: {article['title']}
URL: {article['url']}
Content Excerpt: {article['summary']}

Respond ONLY with valid JSON in this format:
{{
  "description": "1-2 concise, elegant sentences explaining the core insight of the article",
  "pr_summary": "A concise paragraph summarizing the new blog post for the GitHub Pull Request description."
}}
"""
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        text = response.text.strip()
        # Strip code fences if present
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Gemini API generation failed ({e}), falling back to excerpt.")
        summary = article.get("summary", "")
        first_period = summary.find(". ")
        fallback_desc = summary[: first_period + 1] if first_period > 20 else summary[:150]
        return {
            "description": fallback_desc,
            "pr_summary": f"Add new blog post: {article['title']}\n\nURL: {article['url']}",
        }


def update_blog_html(repo_root: Path, article: dict, description: str, month_year: str):
    """Insert the new blog post entry at the top of the list in public/blog/index.html."""
    blog_file = repo_root / "public" / "blog" / "index.html"
    content = blog_file.read_text(encoding="utf-8")

    # Format curly apostrophes
    display_title = article["title"].replace("'", "’")

    new_entry = f"""        <li>
          <div class="entry-line">
            <a href="{article['url']}" target="_blank" rel="noopener" class="entry-name">{display_title}</a>
            <span class="entry-meta">{month_year}</span>
          </div>
          <p class="entry-desc">
            {description}
          </p>
        </li>
"""
    # Insert right after <ul class="editorial-list">
    target = '<ul class="editorial-list">\n'
    if target in content:
        updated = content.replace(target, target + new_entry + "\n", 1)
        blog_file.write_text(updated, encoding="utf-8")
        logger.info("Updated public/blog/index.html")
    else:
        logger.error("Could not find <ul class=\"editorial-list\"> in public/blog/index.html")


def update_rss_feed(repo_root: Path, article: dict, description: str, rfc822_date: str):
    """Insert the new post into public/feed.xml."""
    feed_file = repo_root / "public" / "feed.xml"
    content = feed_file.read_text(encoding="utf-8")

    if article["url"] in content or article["title"] in content:
        logger.info("Article already present in public/feed.xml, skipping feed update.")
        return

    escaped_title = (
        article["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")
    )
    escaped_desc = (
        description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")
    )

    new_item = f"""  <item>
    <title>{escaped_title}</title>
    <link>{article['url']}</link>
    <guid>{article['url']}</guid>
    <pubDate>{rfc822_date}</pubDate>
    <description>{escaped_desc}</description>
  </item>
"""
    # Insert as the first item after channel header
    target = '<atom:link href="https://redbrogdon.dev/feed.xml" rel="self" type="application/rss+xml" />\n'
    if target in content:
        updated = content.replace(target, target + "\n" + new_item, 1)
        feed_file.write_text(updated, encoding="utf-8")
        logger.info("Updated public/feed.xml")
    else:
        logger.error("Could not find atom:link tag in public/feed.xml")


def run_git_cmd(cmd: list[str], cwd: Path, env: dict = None) -> subprocess.CompletedProcess:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True, env=full_env)


def create_pr_for_article(repo_root: Path, article: dict, blurb_data: dict, dry_run: bool = False):
    """Create a git branch, commit changes, and open a GitHub PR."""
    branch = generate_branch_name(article["url"], article["title"])
    title = article["title"]
    desc = blurb_data["description"]
    pr_body = blurb_data.get("pr_summary", f"Adds new blog post: {title}\n\n{desc}\n\nURL: {article['url']}")

    month_year, rfc822_date = format_pub_date(article["pub_date_str"])

    if dry_run:
        logger.info(f"[DRY-RUN] Would create branch: {branch} (Length: {len(branch)})")
        logger.info(f"[DRY-RUN] Editorial Blurb: {desc}")
        logger.info(f"[DRY-RUN] Month/Year: {month_year} | RFC 822: {rfc822_date}")
        logger.info(f"[DRY-RUN] Would execute: gh pr create --title \"Add blog post: {title}\" --head \"{branch}\"")
        return

    # Check for GitHub App credentials first, fall back to GITHUB_TOKEN / GH_TOKEN
    app_auth = get_github_app_auth(repo_root)
    git_commit_env = {}
    if app_auth:
        token, app_id = app_auth
        os.environ["GITHUB_TOKEN"] = token
        os.environ["GH_TOKEN"] = token
        bot_name = "redbrogdon-antigravity[bot]"
        bot_email = f"{app_id}+{bot_name}@users.noreply.github.com"
        git_commit_env = {
            "GIT_AUTHOR_NAME": bot_name,
            "GIT_AUTHOR_EMAIL": bot_email,
            "GIT_COMMITTER_NAME": bot_name,
            "GIT_COMMITTER_EMAIL": bot_email,
        }
        logger.info(f"Using GitHub App identity: {bot_name} <{bot_email}>")
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    # Check out new branch
    logger.info(f"Creating git branch: {branch}")
    run_git_cmd(["git", "checkout", "-b", branch], cwd=repo_root)

    try:
        update_blog_html(repo_root, article, desc, month_year)
        update_rss_feed(repo_root, article, desc, rfc822_date)

        # Stage and commit conforming to git-commit-workflow
        run_git_cmd(["git", "add", "public/blog/index.html", "public/feed.xml"], cwd=repo_root)
        commit_msg = f"Add {title[:35]} to blog and feed"
        run_git_cmd(["git", "commit", "-m", commit_msg], cwd=repo_root, env=git_commit_env)
        logger.info(f"Committed: {commit_msg}")

        # Push branch via HTTPS using the token
        if token:
            logger.info(f"Pushing branch {branch} to GitHub via authenticated HTTPS...")
            push_url = f"https://x-access-token:{token}@github.com/redbrogdon/redbrogdon-dev.git"
            run_git_cmd(["git", "push", "-u", push_url, branch], cwd=repo_root)
        else:
            logger.info(f"Pushing branch {branch} to origin...")
            run_git_cmd(["git", "push", "-u", "origin", branch], cwd=repo_root)

        # Open PR with GitHub CLI
        logger.info("Opening GitHub Pull Request...")
        pr_cmd = [
            "gh", "pr", "create",
            "--title", f"Add blog post: {title}",
            "--body", pr_body,
            "--head", branch,
        ]
        res = subprocess.run(pr_cmd, cwd=repo_root, capture_output=True, text=True, env=os.environ)
        if res.returncode == 0:
            logger.info(f"Pull Request opened successfully: {res.stdout.strip()}")
        else:
            logger.warning(f"gh pr create warning / exit: {res.stderr.strip()}")
    finally:
        # Return to main branch
        run_git_cmd(["git", "checkout", "main"], cwd=repo_root)


def run_cycle(repo_root: Path, model_name: str, dry_run: bool = False, slug_filter: str = None, limit: int = None):
    """Run one detection cycle across blog.flutter.dev and blog.dart.dev."""
    logger.info("Checking blog.flutter.dev and blog.dart.dev for new articles...")
    existing = get_existing_slugs_and_urls(repo_root / "public" / "blog" / "index.html")

    new_articles = []
    for feed_info in FEEDS:
        try:
            raw_xml = fetch_feed(feed_info["url"])
            articles = parse_feed_entries(raw_xml, feed_info["name"])
            logger.info(f"Found {len(articles)} article(s) by Andrew Brogdon in {feed_info['name']}.")
            for art in articles:
                if slug_filter and slug_filter.lower() not in art["url"].lower():
                    continue
                if is_new_article(art, existing):
                    logger.info(f"-> NEW ARTICLE DETECTED: '{art['title']}' ({art['url']})")
                    new_articles.append(art)
                else:
                    logger.debug(f"Already listed: '{art['title']}'")
        except Exception as e:
            logger.error(f"Error fetching/parsing {feed_info['name']}: {e}")

    if not new_articles:
        logger.info("All articles are up to date. No new posts found.")
        return

    if limit:
        new_articles = new_articles[:limit]

    logger.info(f"Processing {len(new_articles)} new article(s)...")
    for art in new_articles:
        branch = generate_branch_name(art["url"], art["title"])
        if is_branch_or_pr_pending(repo_root, branch):
            logger.info(f"Pending branch or PR already exists for '{art['title']}' ({branch}). Waiting for merge.")
            continue

        logger.info(f"Generating summary with Gemini ({model_name}) for '{art['title']}'...")
        blurb_data = generate_blurb_with_gemini(art, model_name=model_name)
        create_pr_for_article(repo_root, art, blurb_data, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(description="Antigravity Blog Watcher & Auto-PR Agent")
    parser.add_argument("--interval", type=int, default=21600, help="Check interval in seconds (default: 21600 / 6 hrs)")
    parser.add_argument("--once", action="store_true", help="Run once and exit immediately")
    parser.add_argument("--dry-run", action="store_true", help="Check and print actions without making git/PR changes")
    parser.add_argument("--slug", type=str, default=None, help="Process only a specific article matching this slug")
    parser.add_argument("--limit", type=int, default=None, help="Max new articles to process")
    parser.add_argument("--model", type=str, default=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"), help="Gemini model name")
    args = parser.parse_args()

    repo_root = find_repo_root()
    logger.info(f"Blog Watcher started for repo: {repo_root}")
    logger.info(f"Using model: {args.model} | Interval: {args.interval}s")

    if args.once or args.dry_run:
        run_cycle(repo_root, model_name=args.model, dry_run=args.dry_run, slug_filter=args.slug, limit=args.limit)
        return

    while True:
        try:
            run_cycle(repo_root, model_name=args.model, dry_run=False, slug_filter=args.slug, limit=args.limit)
        except Exception as e:
            logger.error(f"Unexpected error during cycle: {e}", exc_info=True)

        logger.info(f"Sleeping for {args.interval} seconds...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
