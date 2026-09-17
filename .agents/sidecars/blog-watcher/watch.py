#!/usr/bin/env python3
"""
Antigravity Content Watcher & Auto-PR Agent

Monitors blog.flutter.dev and dart.dev/blog for new articles by Andrew Brogdon,
and monitors the Flutter YouTube channel for new videos featuring Andrew Brogdon.
When new content is discovered, uses Gemini 3.8 to generate an editorial summary,
updates public/blog/index.html or public/media/index.html and public/feed.xml,
and opens a GitHub PR.
"""

import argparse
import datetime
import email.utils
import html as html_lib
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Setup logging
log_format = "[%(asctime)s] [%(levelname)s] %(message)s"
log_datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=log_format, datefmt=log_datefmt)
logger = logging.getLogger("blog-watcher")

# Persistent file log in the sidecar directory (ignored by git via *.log)
log_file = Path(__file__).resolve().parent / "watcher.log"
file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
file_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
logger.addHandler(file_handler)

BLOG_FEEDS = [
    {
        "name": "Flutter Blog",
        "url": "https://blog.flutter.dev/feed.xml",
    },
    {
        "name": "Dart Blog",
        "url": "https://dart.dev/blog/feed.xml",
    },
]

FLUTTER_YOUTUBE_CHANNEL_ID = "UCwXdFgeE9KYzlDdR7TG9cMw"
FLUTTER_YOUTUBE_RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={FLUTTER_YOUTUBE_CHANNEL_ID}"
FLUTTER_YOUTUBE_VIDEOS_URL = "https://www.youtube.com/@flutterdev/videos"

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


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

    app_id = (
        os.environ.get("GITHUB_APP_CLIENT_ID")
        or os.environ.get("GITHUB_APP_ID")
        or "Iv23liEePSBPOLuM9xpZ"
    ).strip()
    if not app_id:
        return None

    try:
        import jwt
    except ImportError:
        logger.error("PyJWT is required for GitHub App authentication (pip install pyjwt cryptography).")
        return None

    # Generate RS256 JWT using Client ID or App ID as issuer (iss)
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

    # Retrieve numerical App ID if not already known (for commit bot email)
    numeric_id = os.environ.get("GITHUB_APP_ID", "")
    if not numeric_id.isdigit():
        try:
            meta_req = urllib.request.Request(
                "https://api.github.com/app",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "User-Agent": "AntigravityContentWatcher/1.0",
                },
            )
            with urllib.request.urlopen(meta_req, timeout=10) as resp:
                meta_data = json.loads(resp.read().decode("utf-8"))
                numeric_id = str(meta_data.get("id", "4867627"))
        except Exception:
            numeric_id = "4867627"

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
                    "User-Agent": "AntigravityContentWatcher/1.0",
                },
            )
            with urllib.request.urlopen(inst_req, timeout=10) as resp:
                inst_data = json.loads(resp.read().decode("utf-8"))
                installation_id = str(inst_data["id"])
                logger.info(f"Discovered GitHub App installation ID: {installation_id}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                logger.error(
                    "GitHub App is not yet installed on repository 'redbrogdon/redbrogdon-dev'. "
                    "Please visit https://github.com/settings/apps/redbrogdon-antigravity/installations "
                    "and install the app on this repository."
                )
            else:
                logger.error(f"Failed to find installation ID for redbrogdon/redbrogdon-dev: {e}")
            return None
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
                "User-Agent": "AntigravityContentWatcher/1.0",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(token_req, timeout=10) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
            token = token_data.get("token")
            logger.info("Successfully generated GitHub App installation access token.")
            return token, numeric_id
    except Exception as e:
        logger.error(f"Failed to obtain installation access token from GitHub API: {e}")
        return None


def fetch_feed(url: str) -> str:
    """Fetch raw XML from an Atom/RSS feed URL, following redirects."""
    headers = {"User-Agent": "AntigravityContentWatcher/1.0 (+https://redbrogdon.dev)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


# -----------------------------------------------------------------------------
# Blog Monitoring & Processing
# -----------------------------------------------------------------------------

def parse_feed_entries(raw_xml: str, feed_name: str) -> list[dict]:
    """Parse Atom entries and filter for articles authored by Andrew Brogdon."""
    root = ET.fromstring(raw_xml)
    entries = []

    atom_entries = root.findall(".//atom:entry", ATOM_NS)
    if not atom_entries:
        atom_entries = root.findall(".//entry")

    for entry in atom_entries:
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

        link_elem = entry.find("atom:link[@rel='alternate']", ATOM_NS)
        if link_elem is None:
            link_elem = entry.find("atom:link", ATOM_NS)
        if link_elem is None:
            link_elem = entry.find("link")

        link = ""
        if link_elem is not None:
            link = link_elem.attrib.get("href") or link_elem.text or ""
        link = link.strip()

        pub_elem = entry.find("atom:published", ATOM_NS)
        if pub_elem is None:
            pub_elem = entry.find("atom:updated", ATOM_NS)
        if pub_elem is None:
            pub_elem = entry.find("published")
        if pub_elem is None:
            pub_elem = entry.find("updated")
        pub_date_str = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

        content_elem = entry.find("atom:content", ATOM_NS)
        if content_elem is None:
            content_elem = entry.find("atom:summary", ATOM_NS)
        if content_elem is None:
            content_elem = entry.find("content")
        if content_elem is None:
            content_elem = entry.find("summary")
        content_text = content_elem.text.strip() if content_elem is not None and content_elem.text else ""
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

    hrefs = re.findall(r'href=["\'](https?://[^"\']+)["\']', content)
    for h in hrefs:
        existing.add(h)
        slug = h.rstrip("/").split("/")[-1].split("#")[0]
        if slug:
            existing.add(slug)

    titles = re.findall(r'class="entry-name">([^<]+)</a>', content)
    for t in titles:
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
    prefix = "bot/blog-"
    slug = url.rstrip("/").split("/")[-1]
    if not slug or len(slug) < 3:
        slug = title
    clean_slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower()
    truncated_slug = clean_slug[:16].rstrip("-")
    branch = f"{prefix}{truncated_slug}"
    assert len(branch) <= 25, f"Branch name {branch} exceeds 25 chars"
    return branch


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
    target = '<ul class="editorial-list">\n'
    if target in content:
        updated = content.replace(target, target + new_entry + "\n", 1)
        blog_file.write_text(updated, encoding="utf-8")
        logger.info("Updated public/blog/index.html")
    else:
        logger.error('Could not find <ul class="editorial-list"> in public/blog/index.html')


def create_pr_for_article(repo_root: Path, article: dict, blurb_data: dict, dry_run: bool = False):
    """Create a git branch, commit changes, and open a GitHub PR."""
    branch = generate_branch_name(article["url"], article["title"])
    title = article["title"]
    desc = blurb_data["description"]
    pr_body = blurb_data.get("pr_summary", f"Adds new blog post: {title}\n\n{desc}")
    if article.get("url") and article["url"] not in pr_body:
        pr_body = f"{pr_body.strip()}\n\nURL: {article['url']}"

    month_year, rfc822_date = format_pub_date(article["pub_date_str"])

    if dry_run:
        logger.info(f"[DRY-RUN] Would create branch: {branch} (Length: {len(branch)})")
        logger.info(f"[DRY-RUN] Editorial Blurb: {desc}")
        logger.info(f"[DRY-RUN] Month/Year: {month_year} | RFC 822: {rfc822_date}")
        logger.info(f"[DRY-RUN] Would execute: gh pr create --title \"Add blog post: {title}\" --head \"{branch}\"")
        return

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

    logger.info(f"Creating git branch: {branch}")
    run_git_cmd(["git", "checkout", "-B", branch], cwd=repo_root)

    try:
        update_blog_html(repo_root, article, desc, month_year)
        update_rss_feed(repo_root, article, desc, rfc822_date)

        run_git_cmd(["git", "add", "public/blog/index.html", "public/feed.xml"], cwd=repo_root)
        commit_msg = f"Add {title[:35]} to blog and feed"
        run_git_cmd(["git", "commit", "-m", commit_msg], cwd=repo_root, env=git_commit_env)
        logger.info(f"Committed: {commit_msg}")

        if token:
            logger.info(f"Pushing branch {branch} to GitHub via authenticated HTTPS...")
            push_url = f"https://x-access-token:{token}@github.com/redbrogdon/redbrogdon-dev.git"
            run_git_cmd(["git", "push", "-u", push_url, branch], cwd=repo_root)
        else:
            logger.info(f"Pushing branch {branch} to origin...")
            run_git_cmd(["git", "push", "-u", "origin", branch], cwd=repo_root)

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
        run_git_cmd(["git", "checkout", "main"], cwd=repo_root)


# -----------------------------------------------------------------------------
# YouTube Media Monitoring & Processing
# -----------------------------------------------------------------------------

def fetch_youtube_channel_videos() -> list[dict]:
    """
    Fetch the latest videos from the Flutter YouTube channel.
    Attempts the Atom RSS feed first, falling back to parsing ytInitialData from @flutterdev/videos.
    """
    # 1. Try Atom RSS
    try:
        raw_xml = fetch_feed(FLUTTER_YOUTUBE_RSS_URL)
        root = ET.fromstring(raw_xml)
        entries = []
        atom_entries = root.findall(".//atom:entry", ATOM_NS)
        if not atom_entries:
            atom_entries = root.findall(".//entry")
        for entry in atom_entries:
            id_elem = entry.find(".//yt:videoId", ATOM_NS)
            if id_elem is None:
                id_elem = entry.find(".//{http://www.youtube.com/xml/schemas/2015}videoId")
            vid_id = id_elem.text.strip() if id_elem is not None and id_elem.text else ""

            title_elem = entry.find("atom:title", ATOM_NS)
            if title_elem is None:
                title_elem = entry.find("title")
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

            link_elem = entry.find("atom:link[@rel='alternate']", ATOM_NS)
            if link_elem is None:
                link_elem = entry.find("link")
            url = link_elem.attrib.get("href", "") if link_elem is not None else f"https://www.youtube.com/watch?v={vid_id}"

            pub_elem = entry.find("atom:published", ATOM_NS)
            if pub_elem is None:
                pub_elem = entry.find("published")
            pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

            if vid_id:
                entries.append({
                    "id": vid_id,
                    "title": html_lib.unescape(title),
                    "url": url,
                    "pub_date_str": pub_date,
                })
        if entries:
            logger.info(f"Fetched {len(entries)} video(s) via YouTube Atom feed.")
            return entries
    except Exception as e:
        logger.warning(f"YouTube Atom feed fetch failed ({e}), falling back to @flutterdev/videos HTML scraper.")

    # 2. Fallback to @flutterdev/videos
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        req = urllib.request.Request(FLUTTER_YOUTUBE_VIDEOS_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_content = resp.read().decode("utf-8", errors="replace")

        match = re.search(r"var ytInitialData\s*=\s*({.*?});</script>", html_content)
        if not match:
            logger.error("Could not find ytInitialData in @flutterdev/videos")
            return []

        data = json.loads(match.group(1))

        def find_key(obj, key):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == key:
                        yield v
                    yield from find_key(v, key)
            elif isinstance(obj, list):
                for item in obj:
                    yield from find_key(item, key)

        entries = []
        for item in find_key(data, "lockupViewModel"):
            vid_id = item.get("contentId")
            title = item.get("metadata", {}).get("lockupMetadataViewModel", {}).get("title", {}).get("content", "")
            if vid_id and title:
                entries.append({
                    "id": vid_id,
                    "title": html_lib.unescape(title),
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                    "pub_date_str": "",
                })
        logger.info(f"Fetched {len(entries)} video(s) via @flutterdev/videos scraper.")
        return entries
    except Exception as e:
        logger.error(f"Error scraping @flutterdev/videos: {e}")
        return []


def get_existing_media_ids_and_urls(media_html_path: Path) -> set[str]:
    """Extract known video IDs, URLs, and normalized titles from public/media/index.html."""
    if not media_html_path.exists():
        return set()

    content = media_html_path.read_text(encoding="utf-8")
    existing = set()

    # Match all YouTube video IDs
    vid_ids = re.findall(r"youtube\.com/watch\?v=([a-zA-Z0-9_-]+)", content)
    for vid in vid_ids:
        existing.add(vid)
        existing.add(f"https://www.youtube.com/watch?v={vid}")

    short_ids = re.findall(r"youtu\.be/([a-zA-Z0-9_-]+)", content)
    for vid in short_ids:
        existing.add(vid)
        existing.add(f"https://youtu.be/{vid}")

    # Match titles in entry-name
    titles = re.findall(r'class="entry-name">([^<]+)</a>', content)
    for t in titles:
        norm_t = re.sub(r"[^a-zA-Z0-9]+", "", t).lower()
        if norm_t:
            existing.add(norm_t)

    return existing


def is_new_video(video: dict, existing: set[str]) -> bool:
    """Check if a YouTube video is already recorded on redbrogdon.dev/media/."""
    vid_id = video.get("id", "")
    url = video.get("url", "")
    norm_title = re.sub(r"[^a-zA-Z0-9]+", "", video.get("title", "")).lower()

    if vid_id in existing or url in existing or norm_title in existing:
        return False
    return True


def fetch_video_details(video_id: str) -> dict:
    """Fetch video watch page to retrieve description, exact publication date, and speaker details."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_content = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.error(f"Error fetching watch page for {video_id}: {e}")
        return {"id": video_id, "url": url, "title": "", "description": "", "pub_date_str": "", "raw_html": ""}

    title_match = re.search(r'<meta name="title" content="([^"]+)"', html_content)
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html_content)
    date_match = re.search(r'<meta itemprop="datePublished" content="([^"]+)"', html_content)

    title = html_lib.unescape(title_match.group(1)) if title_match else ""
    desc = html_lib.unescape(desc_match.group(1)) if desc_match else ""
    date_str = date_match.group(1) if date_match else ""

    # Extract full description from ytInitialData if present
    data_match = re.search(r"var ytInitialData\s*=\s*({.*?});</script>", html_content)
    full_desc = desc
    if data_match:
        try:
            yt_data = json.loads(data_match.group(1))

            def find_description(obj):
                if isinstance(obj, dict):
                    if "attributedDescriptionBodyText" in obj and "content" in obj["attributedDescriptionBodyText"]:
                        return obj["attributedDescriptionBodyText"]["content"]
                    if "description" in obj and isinstance(obj["description"], dict) and "simpleText" in obj["description"]:
                        return obj["description"]["simpleText"]
                    for v in obj.values():
                        res = find_description(v)
                        if res:
                            return res
                elif isinstance(obj, list):
                    for item in obj:
                        res = find_description(item)
                        if res:
                            return res
                return None

            extracted = find_description(yt_data)
            if extracted and len(extracted) > len(full_desc):
                full_desc = extracted
        except Exception:
            pass

    return {
        "id": video_id,
        "url": url,
        "title": title,
        "description": full_desc,
        "pub_date_str": date_str,
        "raw_html": html_content,
    }


def is_video_featuring_andrew(video: dict, full_html: str) -> bool:
    """Determine if a video features Andrew Brogdon based on description, metadata, and speaker tags."""
    title = video.get("title", "")
    desc = video.get("description", "")
    combined_text = (title + " " + desc + " " + full_html).lower()

    # Direct name match
    if "brogdon" in combined_text:
        return True

    # Check for "Andrew" in combination with DevRel / Flutter hosting markers
    desc_lower = desc.lower()
    title_lower = title.lower()
    devrel_indicators = [
        "flutter team",
        "catches up",
        "interview",
        "explains",
        "demonstrates",
        "presents",
        "speaker",
        "host",
        "devrel",
        "developer relations",
    ]

    if "andrew from the flutter team" in desc_lower or "speaker: andrew" in desc_lower or "with andrew" in desc_lower:
        return True

    if re.search(r"\bandrew\b", desc_lower) and any(ind in desc_lower for ind in devrel_indicators):
        return True

    if re.search(r"\bandrew\b", title_lower):
        return True

    return False


def clean_video_title(raw_title: str) -> str:
    """Deterministically clean up YouTube video title (stripping channel suffixes, guest tags, clickbait)."""
    title = html_lib.unescape(raw_title).strip()
    if " | " in title:
        title = title.split(" | ")[0].strip()
    title = re.sub(r"^(?:Why you should be\s+|How to\s+)?", "", title, flags=re.IGNORECASE)
    title = re.sub(r"'s\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$", "", title)
    return title.strip()


def generate_video_blurb_with_gemini(video: dict, model_name: str = "gemini-3.8-flash") -> dict:
    """Use Gemini to confirm Andrew's presence, refine the title, and generate an editorial description."""
    try:
        from google import genai
        client = genai.Client()

        prompt = f"""You are an editorial assistant for Andrew Brogdon's personal website (redbrogdon.dev).
The website has a refined, literary, monograph-style tone for technical essays, talks, and media presentations.

Here are existing video entries on the media page for title and tone reference:
- Title: "The Future of Flutter Design Libraries with Widgetbook"
  Description: "Interviewing Lucas Josefiak, co-founder and CEO of Widgetbook, live at Fluttercon USA on Widgetbook 4, AI coding agents using design systems, and self-healing UI feedback loops."
- Title: "Building with Full-stack Dart with Serverpod"
  Description: "Catching up with Serverpod founder Viktor Lidholt at Fluttercon USA to discuss full-stack hot reload, built-in MCP servers for AI coding agents, and Dart on the backend."
- Title: "A2UI 0.9.0 and GenUI"
  Description: "Exploring the latest updates to the A2UI protocol and Flutter's genui package, covering architectural shifts and the new prompt-first approach."
- Title: "Flutter + A2UI = GenUI"
  Description: "Introducing A2UI, an open protocol for Generative UI that enables autonomous AI agents to dynamically negotiate and render Flutter interfaces."
- Title: "Introducing the Full-stack developer guide (Flutter, Firebase, Angular)"
  Description: "Announcing a joint guide from the Flutter, Firebase, and Angular teams demonstrating how to architect and build full-stack, multiplatform apps."

Analyze the following newly published video from the Flutter YouTube channel:
Raw Title: {video['title']}
URL: {video['url']}
Description / Transcript Excerpt:
{video['description'][:2000]}

Instructions:
1. Confirm if Andrew Brogdon (also known as Andrew from the Flutter team) is a speaker, presenter, host, or interviewer in this video.
2. If NOT featuring Andrew, set "features_andrew": false.
3. If YES, set "features_andrew": true and generate:
   - "title": A clean, concise title matching the monograph style (strip YouTube clickbait, guest pipes like '| Name', and channel tags).
   - "description": A 1-to-2 sentence editorial description matching the site's voice and third-person present participle convention ("Interviewing...", "Exploring...", "Catching up with...").
   - "pr_summary": A concise paragraph summarizing the video for the GitHub Pull Request description.

Respond ONLY with valid JSON in this format:
{{
  "features_andrew": true,
  "title": "Cleaned Monograph Title",
  "description": "1-2 concise, elegant sentences explaining the core presentation or conversation",
  "pr_summary": "A concise paragraph summarizing the new video for the GitHub Pull Request description."
}}
"""
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        return data
    except Exception as e:
        logger.warning(f"Gemini API video generation failed ({e}), falling back to deterministic excerpt.")
        cleaned_title = clean_video_title(video["title"])
        desc = video.get("description", "")
        clean_desc = re.sub(r"https?://\S+", "", desc)
        clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
        first_period = clean_desc.find(". ")
        fallback_desc = clean_desc[: first_period + 1] if first_period > 20 else clean_desc[:160]
        return {
            "features_andrew": True,
            "title": cleaned_title,
            "description": fallback_desc,
            "pr_summary": f"Add new video: {cleaned_title}\n\nURL: {video['url']}",
        }


def generate_media_branch_name(url: str, title: str = "") -> str:
    """Generate a git branch name guaranteed to be <= 25 characters total."""
    prefix = "bot/media-"
    # Extract YouTube video ID or URL slug if present (e.g. watch?v=8OUcGUiKj8M or youtu.be/8OUcGUiKj8M)
    vid_match = re.search(r"(?:v=|youtu\.be/|/embed/|/v/)([a-zA-Z0-9_-]{6,})", url)
    if vid_match:
        slug = vid_match.group(1).lower()
    else:
        slug = url.rstrip("/").split("/")[-1].split("?")[0]
        if not slug or len(slug) < 3:
            slug = title

    clean_slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower()
    # 25 max - 10 prefix = 15 chars max for slug
    truncated_slug = clean_slug[:15].rstrip("-")
    branch = f"{prefix}{truncated_slug}"
    assert len(branch) <= 25, f"Branch name {branch} exceeds 25 chars"
    return branch


def update_media_html(repo_root: Path, video: dict, title: str, description: str, month_year: str):
    """Insert the new video entry at the top of the list in public/media/index.html."""
    media_file = repo_root / "public" / "media" / "index.html"
    content = media_file.read_text(encoding="utf-8")

    display_title = title.replace("'", "’")

    new_entry = f"""        <li>
          <div class="entry-line">
            <div class="entry-title">
              <i class="fa-solid fa-video media-type-icon" aria-hidden="true"></i>
              <a href="{video['url']}" target="_blank" rel="noopener" class="entry-name">{display_title}</a>
            </div>
            <span class="entry-meta">{month_year}</span>
          </div>
          <p class="entry-desc">
            {description}
          </p>
        </li>
"""
    target = '<ul class="editorial-list">\n'
    if target in content:
        updated = content.replace(target, target + new_entry + "\n", 1)
        media_file.write_text(updated, encoding="utf-8")
        logger.info("Updated public/media/index.html")
    else:
        logger.error('Could not find <ul class="editorial-list"> in public/media/index.html')


def update_sitemap_media_lastmod(repo_root: Path):
    """Update <lastmod> for https://redbrogdon.dev/media/ in public/sitemap.xml."""
    sitemap_file = repo_root / "public" / "sitemap.xml"
    if not sitemap_file.exists():
        return
    content = sitemap_file.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    pattern = r"(<loc>https://redbrogdon\.dev/media/</loc>\s*<lastmod>)[^<]+(</lastmod>)"
    if re.search(pattern, content):
        updated = re.sub(pattern, rf"\g<1>{today}\g<2>", content)
        sitemap_file.write_text(updated, encoding="utf-8")
        logger.info(f"Updated public/sitemap.xml /media/ lastmod to {today}")


def create_pr_for_video(repo_root: Path, video: dict, blurb_data: dict, dry_run: bool = False):
    """Create a git branch, commit changes, and open a GitHub PR for a new video."""
    title = blurb_data.get("title") or video.get("title") or "Untitled Video"
    clean_fallback = clean_video_title(video.get("title", ""))
    branch = generate_media_branch_name(video["url"], clean_fallback)
    desc = blurb_data["description"]
    pr_body = blurb_data.get("pr_summary", f"Adds new video: {title}\n\n{desc}")
    if video.get("url") and video["url"] not in pr_body:
        pr_body = f"{pr_body.strip()}\n\nURL: {video['url']}"

    month_year, rfc822_date = format_pub_date(video.get("pub_date_str", ""))

    if dry_run:
        logger.info(f"[DRY-RUN] Would create branch: {branch} (Length: {len(branch)})")
        logger.info(f"[DRY-RUN] Clean Title: {title}")
        logger.info(f"[DRY-RUN] Editorial Blurb: {desc}")
        logger.info(f"[DRY-RUN] Month/Year: {month_year} | RFC 822: {rfc822_date}")
        logger.info(f"[DRY-RUN] Would execute: gh pr create --title \"Add video: {title}\" --head \"{branch}\"")
        return

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

    logger.info(f"Creating git branch: {branch}")
    run_git_cmd(["git", "checkout", "-B", branch], cwd=repo_root)

    try:
        update_media_html(repo_root, video, title, desc, month_year)
        update_rss_feed(repo_root, {"title": title, "url": video["url"]}, desc, rfc822_date)
        update_sitemap_media_lastmod(repo_root)

        run_git_cmd(["git", "add", "public/media/index.html", "public/feed.xml", "public/sitemap.xml"], cwd=repo_root)
        commit_msg = f"Add {title[:35]} to media and feed"
        run_git_cmd(["git", "commit", "-m", commit_msg], cwd=repo_root, env=git_commit_env)
        logger.info(f"Committed: {commit_msg}")

        if token:
            logger.info(f"Pushing branch {branch} to GitHub via authenticated HTTPS...")
            push_url = f"https://x-access-token:{token}@github.com/redbrogdon/redbrogdon-dev.git"
            run_git_cmd(["git", "push", "-u", push_url, branch], cwd=repo_root)
        else:
            logger.info(f"Pushing branch {branch} to origin...")
            run_git_cmd(["git", "push", "-u", "origin", branch], cwd=repo_root)

        logger.info("Opening GitHub Pull Request...")
        pr_cmd = [
            "gh", "pr", "create",
            "--title", f"Add video: {title}",
            "--body", pr_body,
            "--head", branch,
        ]
        res = subprocess.run(pr_cmd, cwd=repo_root, capture_output=True, text=True, env=os.environ)
        if res.returncode == 0:
            logger.info(f"Pull Request opened successfully: {res.stdout.strip()}")
        else:
            logger.warning(f"gh pr create warning / exit: {res.stderr.strip()}")
    finally:
        run_git_cmd(["git", "checkout", "main"], cwd=repo_root)


# -----------------------------------------------------------------------------
# Common Helpers
# -----------------------------------------------------------------------------

def format_pub_date(date_str: str) -> tuple[str, str]:
    """Parse ISO date to (Month Year, RFC 822 format for RSS)."""
    try:
        clean_str = date_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean_str)
    except Exception:
        dt = datetime.datetime.now(datetime.timezone.utc)

    month_year = dt.strftime("%B %Y")
    rfc822_date = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return month_year, rfc822_date


def update_rss_feed(repo_root: Path, item: dict, description: str, rfc822_date: str):
    """Insert the new item into public/feed.xml."""
    feed_file = repo_root / "public" / "feed.xml"
    content = feed_file.read_text(encoding="utf-8")

    if item["url"] in content or item["title"] in content:
        logger.info("Item already present in public/feed.xml, skipping feed update.")
        return

    escaped_title = (
        item["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")
    )
    escaped_desc = (
        description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")
    )

    new_item = f"""  <item>
    <title>{escaped_title}</title>
    <link>{item['url']}</link>
    <guid>{item['url']}</guid>
    <pubDate>{rfc822_date}</pubDate>
    <description>{escaped_desc}</description>
  </item>
"""
    target = '<atom:link href="https://redbrogdon.dev/feed.xml" rel="self" type="application/rss+xml" />\n'
    if target in content:
        updated = content.replace(target, target + "\n" + new_item, 1)
        feed_file.write_text(updated, encoding="utf-8")
        logger.info("Updated public/feed.xml")
    else:
        logger.error("Could not find atom:link tag in public/feed.xml")


def is_branch_or_pr_pending(repo_root: Path, branch: str, item_url: str = None, item_id: str = None) -> bool:
    """Check if an open GitHub PR already exists for this branch, item URL, or ID."""
    try:
        if not os.environ.get("GH_TOKEN") and not os.environ.get("GITHUB_TOKEN"):
            app_auth = get_github_app_auth(repo_root)
            if app_auth:
                os.environ["GH_TOKEN"] = app_auth[0]
                os.environ["GITHUB_TOKEN"] = app_auth[0]

        pr_check = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "headRefName,title,body"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            env=os.environ,
        )
        if pr_check.returncode == 0 and pr_check.stdout.strip():
            prs = json.loads(pr_check.stdout)
            for p in prs:
                head_ref = p.get("headRefName", "")
                if head_ref == branch:
                    return True
                body = p.get("body", "")
                title = p.get("title", "")
                if item_url and (item_url in body or item_url in title):
                    return True
                if item_id and (item_id in body or item_id in title or item_id.lower() in head_ref.lower()):
                    return True
        elif pr_check.returncode != 0:
            # Fallback when gh CLI or GitHub API is offline: check local git branches
            local_check = subprocess.run(
                ["git", "branch", "--list", branch],
                cwd=repo_root,
                capture_output=True,
                text=True,
            )
            if local_check.returncode == 0 and branch in local_check.stdout:
                logger.info(f"Local branch {branch} found (fallback PR check).")
                return True
    except Exception as e:
        logger.debug(f"Error checking open PRs: {e}")

    return False


def run_git_cmd(cmd: list[str], cwd: Path, env: dict = None) -> subprocess.CompletedProcess:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True, env=full_env)


# -----------------------------------------------------------------------------
# Cycles & CLI
# -----------------------------------------------------------------------------

def run_blog_cycle(repo_root: Path, model_name: str, dry_run: bool = False, slug_filter: str = None, limit: int = None):
    """Run detection cycle across monitored blog publications."""
    logger.info("Checking blog.flutter.dev and dart.dev/blog for new articles...")
    existing = get_existing_slugs_and_urls(repo_root / "public" / "blog" / "index.html")

    new_articles = []
    for feed_info in BLOG_FEEDS:
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
        if is_branch_or_pr_pending(repo_root, branch, item_url=art["url"]):
            logger.info(f"Pending branch or PR already exists for '{art['title']}' ({branch}). Waiting for merge.")
            continue

        logger.info(f"Generating summary with Gemini ({model_name}) for '{art['title']}'...")
        blurb_data = generate_blurb_with_gemini(art, model_name=model_name)
        create_pr_for_article(repo_root, art, blurb_data, dry_run=dry_run)


def run_media_cycle(repo_root: Path, model_name: str, dry_run: bool = False, slug_filter: str = None, limit: int = None):
    """Check Flutter YouTube channel for new videos featuring Andrew Brogdon."""
    logger.info("Checking Flutter YouTube channel for new videos...")
    existing = get_existing_media_ids_and_urls(repo_root / "public" / "media" / "index.html")

    channel_videos = fetch_youtube_channel_videos()
    logger.info(f"Found {len(channel_videos)} recent video(s) on Flutter channel.")

    new_videos = []
    for vid in channel_videos:
        if slug_filter and slug_filter.lower() not in vid["url"].lower() and slug_filter.lower() not in vid["title"].lower():
            continue
        if is_new_video(vid, existing):
            new_videos.append(vid)
        else:
            logger.debug(f"Already listed in media: '{vid['title']}' ({vid['id']})")

    if not new_videos:
        logger.info("All media is up to date. No new videos found.")
        return

    logger.info(f"Evaluating {len(new_videos)} candidate video(s) for Andrew Brogdon appearances...")
    candidates_to_process = []
    for vid in new_videos:
        details = fetch_video_details(vid["id"])
        vid.update(details)
        if is_video_featuring_andrew(vid, details.get("raw_html", "")):
            logger.info(f"-> NEW ANDREW VIDEO DETECTED: '{vid['title']}' ({vid['url']})")
            candidates_to_process.append(vid)
        else:
            logger.debug(f"Video does not feature Andrew Brogdon: '{vid['title']}'")

    if not candidates_to_process:
        logger.info("No new videos featuring Andrew Brogdon found.")
        return

    if limit:
        candidates_to_process = candidates_to_process[:limit]

    logger.info(f"Processing {len(candidates_to_process)} verified new video(s)...")
    for vid in candidates_to_process:
        clean_title = clean_video_title(vid["title"])
        branch = generate_media_branch_name(vid["url"], clean_title)
        if is_branch_or_pr_pending(repo_root, branch, item_url=vid["url"], item_id=vid.get("id")):
            logger.info(f"Pending branch or PR already exists for '{clean_title}' ({branch}). Waiting for merge.")
            continue

        logger.info(f"Generating summary with Gemini ({model_name}) for '{clean_title}'...")
        blurb_data = generate_video_blurb_with_gemini(vid, model_name=model_name)
        if not blurb_data.get("features_andrew", True):
            logger.info(f"Gemini determined video does not feature Andrew Brogdon. Skipping '{clean_title}'.")
            continue

        create_pr_for_video(repo_root, vid, blurb_data, dry_run=dry_run)


def run_cycle(
    repo_root: Path,
    model_name: str,
    dry_run: bool = False,
    slug_filter: str = None,
    limit: int = None,
    content_type: str = "all",
):
    """Run detection cycle across monitored blogs and Flutter YouTube channel."""
    if content_type in ("all", "blog"):
        run_blog_cycle(repo_root, model_name=model_name, dry_run=dry_run, slug_filter=slug_filter, limit=limit)

    if content_type in ("all", "media"):
        run_media_cycle(repo_root, model_name=model_name, dry_run=dry_run, slug_filter=slug_filter, limit=limit)


def main():
    parser = argparse.ArgumentParser(description="Antigravity Content Watcher & Auto-PR Agent")
    parser.add_argument("--interval", type=int, default=21600, help="Check interval in seconds (default: 21600 / 6 hrs)")
    parser.add_argument("--once", action="store_true", help="Run once and exit immediately")
    parser.add_argument("--dry-run", action="store_true", help="Check and print actions without making git/PR changes")
    parser.add_argument("--type", choices=["all", "blog", "media"], default="all", help="Content type to check (default: all)")
    parser.add_argument("--slug", type=str, default=None, help="Process only an item matching this slug, title, or URL")
    parser.add_argument("--video-id", type=str, default=None, help="Process only a specific YouTube video ID")
    parser.add_argument("--limit", type=int, default=None, help="Max new items to process")
    parser.add_argument("--model", type=str, default=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"), help="Gemini model name")
    args = parser.parse_args()

    repo_root = find_repo_root()
    logger.info(f"Content Watcher started for repo: {repo_root}")
    logger.info(f"Type: {args.type} | Model: {args.model} | Interval: {args.interval}s")

    slug = args.video_id if args.video_id else args.slug
    ctype = "media" if args.video_id else args.type

    if args.once or args.dry_run:
        run_cycle(repo_root, model_name=args.model, dry_run=args.dry_run, slug_filter=slug, limit=args.limit, content_type=ctype)
        return

    while True:
        try:
            run_cycle(repo_root, model_name=args.model, dry_run=False, slug_filter=slug, limit=args.limit, content_type=ctype)
        except Exception as e:
            logger.error(f"Unexpected error during cycle: {e}", exc_info=True)

        logger.info(f"Sleeping for {args.interval} seconds...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
