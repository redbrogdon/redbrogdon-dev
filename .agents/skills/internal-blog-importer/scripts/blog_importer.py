import os
import re
import sys
import xml.etree.ElementTree as ET
import urllib.request
import json
import time
import argparse
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Standard headers to bypass crawler blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

# ---------------------------------------------------------
# Common Utilities
# ---------------------------------------------------------

def detect_language(code_content):
    code_content_strip = code_content.strip()
    if code_content_strip.startswith('<') and code_content_strip.endswith('>'):
        return 'xml'
    if code_content_strip.startswith('{') and code_content_strip.endswith('}'):
        if '"' in code_content_strip and ':' in code_content_strip:
            return 'json'
    yaml_keywords = ['dependencies:', 'dev_dependencies:', 'flutter:', 'sdk:', 'version:', 'name:', 'description:']
    if any(kw in code_content_strip for kw in yaml_keywords):
        return 'yaml'
    shell_commands = ['flutter create', 'flutter run', 'flutter pub', 'dart pub', 'git ', 'cd ', 'npm install', 'npx ']
    if any(code_content_strip.startswith(cmd) or f"$ {cmd}" in code_content_strip for cmd in shell_commands) or code_content_strip.startswith('$ '):
        return 'bash'
    dart_patterns = [
        r"import\s+'package:",
        r"import\s+'dart:",
        r"void\s+main\(\)",
        r"class\s+\w+",
        r"final\s+\w+",
        r"const\s+\w+",
        r"var\s+\w+",
        r"@override",
        r"Widget\s+build\(",
        r"BuildContext\s+",
        r"extends\s+",
        r"//",
        r"late\s+",
        r"async\s*",
        r"await\s+",
        r"Future<",
        r"Stream<",
        r"List<",
        r"Map<",
        r"String\s+",
        r"int\s+",
        r"double\s+",
        r"bool\s+",
    ]
    if any(re.search(pat, code_content) for pat in dart_patterns):
        return 'dart'
    programming_indicators = [';', '{', '}', '(', ')', '=']
    if sum(1 for char in programming_indicators if char in code_content_strip) >= 3:
        return 'dart'
    return ''

def slugify(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug.strip('-')

def fetch_url_with_retry(url, retries=3):
    delay = 1.0
    safe_url = urllib.parse.quote(url, safe=':/?&=%#+~-')
    for attempt in range(retries):
        try:
            req = urllib.request.Request(safe_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            if attempt == retries - 1:
                raise e
            print(f"  [Attempt {attempt+1}/{retries} failed. Retrying in {delay}s: {e}]", file=sys.stderr)
            time.sleep(delay)
            delay *= 2.0

# ---------------------------------------------------------
# Medium Blog Parser (Flutter)
# ---------------------------------------------------------

def apply_markups_utf16(text, markups):
    if not markups:
        return text
    utf16_bytes = text.encode('utf-16-le')
    code_units = [int.from_bytes(utf16_bytes[i:i+2], 'little') for i in range(0, len(utf16_bytes), 2)]
    
    actions = []
    for m in markups:
        m_type = m['type']
        start = m['start']
        end = m['end']
        href = m.get('href', '')
        
        def to_units(s):
            b = s.encode('utf-16-le')
            return [int.from_bytes(b[i:i+2], 'little') for i in range(0, len(b), 2)]
            
        if m_type == 1:
            actions.append((end, 1, to_units('**')))
            actions.append((start, 4, to_units('**')))
        elif m_type == 2:
            actions.append((end, 2, to_units('*')))
            actions.append((start, 3, to_units('*')))
        elif m_type == 3:
            actions.append((end, 0, to_units(f']({href})')))
            actions.append((start, 5, to_units('[')))
        elif m_type == 10:
            actions.append((end, 2, to_units('`')))
            actions.append((start, 3, to_units('`')))
            
    actions.sort(key=lambda x: (x[0], x[1]), reverse=True)
    for index, priority, units_to_insert in actions:
        idx = max(0, min(index, len(code_units)))
        code_units[idx:idx] = units_to_insert
    result_bytes = b''.join(u.to_bytes(2, 'little') for u in code_units)
    return result_bytes.decode('utf-16-le')

def resolve_media_resource(media_id):
    media_url = f"https://medium.com/media/{media_id}?format=json"
    try:
        content = fetch_url_with_retry(media_url, retries=2)
        json_str = content[content.find('{'):]
        data = json.loads(json_str)
        value = data['payload'].get('value', {})
        href = value.get('href')
        if href:
            return href
        iframe_src = value.get('iframeSrc')
        if iframe_src:
            return iframe_src
    except Exception as e:
        print(f"  Warning: Failed to resolve media resource {media_id}: {e}", file=sys.stderr)
    return None

def convert_medium_post(url):
    json_url = url + "?format=json"
    content = fetch_url_with_retry(json_url, retries=3)
    json_str = content[content.find('{'):]
    data = json.loads(json_str)
    
    post_val = data['payload']['value']
    title = post_val['title']
    pub_timestamp_ms = post_val['firstPublishedAt']
    pub_date = datetime.fromtimestamp(pub_timestamp_ms / 1000.0, timezone.utc)
    
    paragraphs = post_val['content']['bodyModel']['paragraphs']
    markdown_parts = []
    list_counter = 0
    
    for idx, p in enumerate(paragraphs):
        p_type = p['type']
        text = p.get('text', '')
        text = apply_markups_utf16(text, p.get('markups', []))
        prev_type = paragraphs[idx-1]['type'] if idx > 0 else None
        
        if p_type == 1:
            markdown_parts.append(f"\n\n{text}")
        elif p_type == 2:
            markdown_parts.append(f"\n\n# {text}")
        elif p_type == 3:
            if idx == 0:
                markdown_parts.append(f"\n\n# {text}")
            else:
                markdown_parts.append(f"\n\n## {text}")
        elif p_type == 13:
            markdown_parts.append(f"\n\n### {text}")
        elif p_type == 4:
            alt = p.get('metadata', {}).get('alt', '')
            caption = text
            parts = []
            if alt.strip():
                parts.append(alt.strip())
            if caption.strip():
                parts.append(f"Caption: {caption.strip()}")
            summary = " - ".join(parts)
            if not summary.strip():
                summary = "Unlabelled image"
            markdown_parts.append(f"\n\n*Image: {summary}*")
        elif p_type == 6:
            markdown_parts.append(f"\n\n> {text}")
        elif p_type == 7:
            markdown_parts.append(f"\n\n> *{text}*")
        elif p_type == 8:
            lang = detect_language(text)
            markdown_parts.append(f"\n\n```{lang}\n{text}\n```")
        elif p_type == 9:
            prefix = "\n" if prev_type == 9 else "\n\n"
            markdown_parts.append(f"{prefix}* {text}")
        elif p_type == 10:
            if prev_type == 10:
                list_counter += 1
            else:
                list_counter = 1
            prefix = "\n" if prev_type == 10 else "\n\n"
            markdown_parts.append(f"{prefix}{list_counter}. {text}")
        elif p_type == 11:
            media_id = p.get('iframe', {}).get('mediaResourceId')
            embed_url = None
            for m in p.get('markups', []):
                if m['type'] == 3:
                    embed_url = m.get('href')
                    break
            if not embed_url and 'thumbnailUrl' in p.get('iframe', {}):
                thumb = p['iframe']['thumbnailUrl']
                yt_match = re.search(r'vi%2F([^%]+)%2F', thumb)
                if yt_match:
                    embed_url = f"https://www.youtube.com/watch?v={yt_match.group(1)}"
            if not embed_url and media_id:
                embed_url = resolve_media_resource(media_id)
            if embed_url:
                markdown_parts.append(f"\n\n*Video: {embed_url}*")
            else:
                caption = text if text.strip() else "Video embed"
                markdown_parts.append(f"\n\n*Video: {caption}*")
        elif p_type == 14:
            markdown_parts.append(f"\n\n---")
            
    body_markdown = "".join(markdown_parts).strip()
    return title, pub_date, body_markdown

# ---------------------------------------------------------
# GitHub Blog Parser (Dart blog raw markdown)
# ---------------------------------------------------------

def clean_github_markdown(content):
    # 1. Parse frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    title = ""
    pub_date_str = ""
    
    if fm_match:
        fm_content = fm_match.group(1)
        title_match = re.search(r'^title:\s*"(.*?)"', fm_content, re.MULTILINE)
        if not title_match:
            title_match = re.search(r'^title:\s*(.*?)$', fm_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            
        date_match = re.search(r'^publishDate:\s*(.*?)$', fm_content, re.MULTILINE)
        if date_match:
            pub_date_str = date_match.group(1).strip()
            
        body = content[fm_match.end():].strip()
    else:
        body = content
        
    pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d") if pub_date_str else datetime.utcnow()
    
    # 2. Replace DashImage tags (or similar custom tags) with our inline image summary
    def replace_dash_image(match):
        tag_content = match.group(0)
        alt_match = re.search(r'alt="([^"]*)"', tag_content)
        alt = alt_match.group(1).strip() if alt_match else ""
        caption_match = re.search(r'caption="([^"]*)"', tag_content)
        caption = caption_match.group(1).strip() if caption_match else ""
        
        parts = []
        if alt:
            parts.append(alt)
        if caption:
            parts.append(f"Caption: {caption}")
        summary = " - ".join(parts)
        if not summary:
            summary = "Unlabelled image"
        return f"\n\n*Image: {summary}*\n\n"
        
    body = re.sub(r'<DashImage[^>]*>', replace_dash_image, body)
    
    def check_and_tag_codeblock(match):
        code_block = match.group(0)
        first_line = code_block.split('\n')[0]
        if len(first_line.strip()) == 3:
            code_content = "\n".join(code_block.split('\n')[1:-1])
            lang = detect_language(code_content)
            return f"```{lang}\n{code_content}\n```"
        return code_block
        
    body = re.sub(r'```.*?```', check_and_tag_codeblock, body, flags=re.DOTALL)
    body = re.sub(r'\n{3,}', '\n\n', body)
    
    return title, pub_date, body

def convert_dart_post(url):
    url_path = urlparse(url).path.strip('/')
    slug = url_path.split('/')[-1]
    
    github_url = f"https://raw.githubusercontent.com/dart-lang/site-www/main/src/content/blog/{slug}/index.md"
    print(f"Fetching from GitHub source: {github_url}")
    raw_md_content = fetch_url_with_retry(github_url, retries=3)
    return clean_github_markdown(raw_md_content)

def convert_go_blog_post(url):
    html_content = fetch_url_with_retry(url, retries=3)
    soup = BeautifulSoup(html_content, "html.parser")
    
    article = soup.find("div", class_="Article") or soup.find("main")
    if not article:
        raise ValueError("Could not find article content container")
        
    h1_tags = article.find_all("h1")
    if len(h1_tags) >= 2:
        title = h1_tags[1].text.strip()
    elif h1_tags:
        title = h1_tags[0].text.strip()
    else:
        title = "Untitled"
        
    pub_date = datetime.now(timezone.utc)
    author_p = article.find("p", class_="author")
    if author_p:
        author_text = author_p.text.strip()
        lines = [line.strip() for line in author_text.split("\n") if line.strip()]
        if lines:
            date_str = lines[-1]
            try:
                pub_date = datetime.strptime(date_str, "%d %B %Y").replace(tzinfo=timezone.utc)
            except Exception:
                try:
                    pub_date = datetime.strptime(date_str, "%B %d, %Y").replace(tzinfo=timezone.utc)
                except Exception:
                    pass

    markdown_div = article.find("div", class_="markdown")
    if not markdown_div:
        markdown_div = article
        
    md_lines = []
    for elem in markdown_div.children:
        if not elem.name:
            continue
        if elem.name in ['h1', 'h2', 'h3', 'h4']:
            level = int(elem.name[1])
            md_lines.append(f"\n{'#' * level} {elem.text.strip()}\n")
        elif elem.name == 'p':
            p_text = elem.decode_contents()
            p_text = re.sub(r'<a\s+href="([^"]+)">([^<]+)</a>', r'[\2](\1)', p_text)
            p_text = re.sub(r'<code[^>]*>([^<]+)</code>', r'`\1`', p_text)
            p_text = re.sub(r'<em>([^<]+)</em>', r'*\1*', p_text)
            p_text = re.sub(r'<strong>([^<]+)</strong>', r'**\1**', p_text)
            p_text = re.sub(r'<[^>]+>', '', p_text)
            md_lines.append(f"{p_text.strip()}\n")
        elif elem.name == 'pre':
            code_text = elem.text
            md_lines.append(f"```go\n{code_text.strip()}\n```\n")
        elif elem.name in ['ul', 'ol']:
            for li in elem.find_all('li', recursive=False):
                li_text = re.sub(r'<a\s+href="([^"]+)">([^<]+)</a>', r'[\2](\1)', li.decode_contents())
                li_text = re.sub(r'<code[^>]*>([^<]+)</code>', r'`\1`', li_text)
                li_text = re.sub(r'<[^>]+>', '', li_text)
                md_lines.append(f"* {li_text.strip()}")
            md_lines.append("")

    body = "\n".join(md_lines)
    return title, pub_date, body

# ---------------------------------------------------------
# Core Sync Logic
# ---------------------------------------------------------

def resolve_target_dir(url_or_domain, base_dir, custom_subfolder=None):
    if custom_subfolder:
        return os.path.join(base_dir, custom_subfolder)
        
    url_lower = url_or_domain.lower()
    if 'dart.dev' in url_lower:
        subfolder = 'dart'
    elif 'flutter.dev' in url_lower:
        subfolder = 'flutter'
    elif 'angular.dev' in url_lower:
        subfolder = 'angular'
    elif 'go.dev' in url_lower or 'golang.org' in url_lower:
        subfolder = 'go'
    else:
        parsed = urlparse(url_lower if url_lower.startswith('http') else f"https://{url_lower}")
        domain = parsed.netloc or parsed.path
        parts = domain.replace('.dev', '').replace('.com', '').replace('.org', '').replace('.io', '').split('.')
        filtered = [p for p in parts if p not in ('blog', 'www', 'medium', 'api', 'docs')]
        subfolder = filtered[0] if filtered else 'general'
        
    target_dir = os.path.join(base_dir, subfolder)
    return target_dir

def sync_post(url, base_dir, product=None):
    target_dir = resolve_target_dir(url, base_dir, custom_subfolder=product)
    os.makedirs(target_dir, exist_ok=True)
    
    if 'dart.dev' in url:
        title, pub_date, body = convert_dart_post(url)
    elif 'go.dev' in url or 'golang.org' in url:
        title, pub_date, body = convert_go_blog_post(url)
    else:
        title, pub_date, body = convert_medium_post(url)
        
    date_prefix = pub_date.strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_prefix}-{slug}.md"
    filepath = os.path.join(target_dir, filename)
    
    body = body.replace('&nbsp;', ' ')
    body = body.replace('&amp;', '&')
    body = body.replace('&lt;', '<')
    body = body.replace('&gt;', '>')
    body = body.replace('&quot;', '"')
    body = body.replace('&#39;', "'")
    body = body.replace('&#x27;', "'")
    body = body.replace(' ', ' ')
    body = body.replace('\xa0', ' ')
    
    full_markdown = f"""---
title: "{title}"
date: {pub_date.strftime("%Y-%m-%d")}
---

# {title}

{body}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_markdown)
    return filepath, filename, target_dir

def sync_all_flutter(domain, base_dir, product=None):
    target_dir = resolve_target_dir(domain, base_dir, custom_subfolder=product)
    os.makedirs(target_dir, exist_ok=True)
    
    sitemap_url = f"https://{domain}/sitemap/sitemap.xml"
    print(f"Fetching sitemap: {sitemap_url}")
    xml_data = fetch_url_with_retry(sitemap_url, retries=3)
    
    xml_start = xml_data.find('<?xml')
    if xml_start != -1:
        xml_data = xml_data[xml_start:]
    root = ET.fromstring(xml_data)
    
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = []
    for url_elem in root.findall('ns:url', ns):
        loc = url_elem.find('ns:loc', ns).text
        if loc == f"https://{domain}" or loc == f"https://{domain}/":
            continue
        if "/tagged/" in loc:
            continue
        if loc.endswith("/about"):
            continue
        urls.append(loc)
        
    return urls, target_dir

def sync_all_dart(domain, base_dir, product=None):
    target_dir = resolve_target_dir(domain, base_dir, custom_subfolder=product)
    os.makedirs(target_dir, exist_ok=True)
    
    feed_url = "https://dart.dev/blog/feed.xml"
    print(f"Fetching sitemap/feed: {feed_url}")
    xml_data = fetch_url_with_retry(feed_url, retries=3)
    
    xml_start = xml_data.find('<?xml')
    if xml_start != -1:
        xml_data = xml_data[xml_start:]
    root = ET.fromstring(xml_data)
    
    ns = {'ns': 'http://www.w3.org/2005/Atom'}
    urls = []
    for entry in root.findall('ns:entry', ns):
        link_elem = entry.find('ns:link', ns)
        if link_elem is not None:
            loc = link_elem.get('href')
            urls.append(loc)
            
    return urls, target_dir

def sync_all_go(domain, base_dir, product=None):
    target_dir = resolve_target_dir(domain, base_dir, custom_subfolder=product or 'go')
    os.makedirs(target_dir, exist_ok=True)
    
    all_url = f"https://{domain}/blog/all"
    print(f"Fetching Go blog index: {all_url}")
    html_data = fetch_url_with_retry(all_url, retries=3)
    
    matches = re.findall(r'href="(/blog/[^"]+)"', html_data)
    urls = [f"https://{domain}{m}" for m in set(matches) if m not in ("/blog/", "/blog/all", "/blog/index", "/blog/feed.atom", "/blog/feed.xml") and not m.startswith("/blog/tag")]
    urls.sort()
    return urls, target_dir

def sync_all(domain, base_dir, product=None):
    if 'dart.dev' in domain:
        urls, target_dir = sync_all_dart(domain, base_dir, product=product)
    elif 'go.dev' in domain or 'golang.org' in domain:
        urls, target_dir = sync_all_go(domain, base_dir, product=product)
    else:
        urls, target_dir = sync_all_flutter(domain, base_dir, product=product)
        
    print(f"Found {len(urls)} posts listed for {domain}.")
    
    existing_files = os.listdir(target_dir) if os.path.exists(target_dir) else []
    existing_slugs = set()
    for filename in existing_files:
        if filename.endswith(".md"):
            parts = filename.split('-', 3)
            if len(parts) >= 4:
                slug_part = parts[3][:-3]
                existing_slugs.add(slug_part)
                
    successes = []
    failures = []
    
    for i, url in enumerate(urls, 1):
        url_path = urlparse(url).path.strip('/')
        url_slug = url_path.split('/')[-1]
        
        if 'dart.dev' in domain:
            clean_slug = slugify(url_slug)
        else:
            slug_parts = url_slug.split('-')
            if len(slug_parts) > 1:
                clean_slug = slugify("-".join(slug_parts[:-1]))
            else:
                clean_slug = slugify(url_slug)
        
        if clean_slug in existing_slugs:
            continue
            
        print(f"[{i}/{len(urls)}] Syncing: {url} ...")
        try:
            filepath, filename, _ = sync_post(url, base_dir, product=product)
            print(f"  Saved: {filename}")
            successes.append((url, filename))
            time.sleep(0.15)
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
            failures.append((url, str(e)))
            
    return successes, failures, target_dir

def main():
    parser = argparse.ArgumentParser(description="Synchronize Medium-hosted (Flutter/Angular) or Jekyll/Jaspr-hosted (Dart) blogs to clean Markdown subfolders.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # sync-post
    post_parser = subparsers.add_parser("sync-post", help="Synchronize a single blog post URL.")
    post_parser.add_argument("--url", required=True, help="Full URL of the blog post.")
    post_parser.add_argument("--output-dir", default="content/published/blog_posts", help="Base output directory path.")
    post_parser.add_argument("--product", "--subfolder", dest="product", default=None, help="Explicit product subfolder name (e.g. angular, flutter, dart).")
    
    # sync-all
    all_parser = subparsers.add_parser("sync-all", help="Synchronize all missing posts from a blog's sitemap/feed.")
    all_parser.add_argument("--domain", required=True, help="The domain of the blog (e.g. blog.angular.dev, blog.flutter.dev, or dart.dev).")
    all_parser.add_argument("--output-dir", default="content/published/blog_posts", help="Base output directory path.")
    all_parser.add_argument("--product", "--subfolder", dest="product", default=None, help="Explicit product subfolder name (e.g. angular, flutter, dart).")

    args = parser.parse_args()
    
    if args.command == "sync-post":
        try:
            filepath, filename, target_dir = sync_post(args.url, args.output_dir, product=args.product)
            print(f"\nSuccess! Saved to {filepath} (Subfolder: {os.path.basename(target_dir)})")
        except Exception as e:
            print(f"\nError: Failed to sync post: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "sync-all":
        successes, failures, target_dir = sync_all(args.domain, args.output_dir, product=args.product)
        subfolder_name = os.path.basename(target_dir)
        
        print(f"\n=== Synchronization Summary for {subfolder_name} ===")
        print(f"Successfully Imported: {len(successes)} posts.")
        print(f"Failed to Import: {len(failures)} posts.")
        
        if failures:
            print("\nFailed Posts Log:")
            for url, err in failures:
                print(f"- URL: {url} | Error: {err}")
            sys.exit(1)

if __name__ == "__main__":
    main()
