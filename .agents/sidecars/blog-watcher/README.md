# Antigravity Content Watcher & Auto-PR Sidecar

An automated Antigravity sidecar and agent that monitors official Flutter and Dart publications as well as the official Flutter YouTube channel for new content created by or featuring Andrew Brogdon.

When new content is detected:
1. Generates an editorial summary matching the literary tone of `redbrogdon.dev` using **Gemini 3.8** (`gemini-3.8-flash`).
2. Creates an isolated git branch (`bot/blog-<slug>` or `bot/media-<slug>`, max 25 chars).
3. Adds the entry to `public/blog/index.html` or `public/media/index.html` and `public/feed.xml`.
4. Updates `<lastmod>` in `public/sitemap.xml` where applicable.
5. Commits the changes conforming to the repository's commit workflow.
6. Pushes the branch and opens a GitHub Pull Request via `gh pr create`.

## Monitored Sources
- **Flutter Blog:** `https://blog.flutter.dev/feed.xml`
- **Dart Blog:** `https://dart.dev/blog/feed.xml`
- **Flutter YouTube Channel:** `https://www.youtube.com/@flutterdev/videos` (with fallback between YouTube Atom RSS and direct channel data parsing)

*(Medium feeds and other external sources are ignored per configuration).*

## Quick Usage

### 1. Dry Run (Test Detection & Summarization without Git/PR changes)
```bash
# Check all sources
python3 .agents/sidecars/blog-watcher/watch.py --dry-run

# Check only media (YouTube)
python3 .agents/sidecars/blog-watcher/watch.py --dry-run --type media

# Check only blog articles
python3 .agents/sidecars/blog-watcher/watch.py --dry-run --type blog
```

### 2. Single Run (Run once and exit)
```bash
python3 .agents/sidecars/blog-watcher/watch.py --once
```

### 3. Continuous Daemon (Default 6-hour polling)
```bash
python3 .agents/sidecars/blog-watcher/watch.py --interval 21600
```

## Antigravity Sidecar Registration
The sidecar is registered via `sidecar.json`:
```json
{
  "description": "Monitors blog.flutter.dev, dart.dev/blog, and the Flutter YouTube channel for new content by Andrew Brogdon and opens PRs via Gemini",
  "builtin": "schedule",
  "args": [
    "0 */6 * * *",
    "python3",
    "watch.py",
    "--once"
  ],
  "env": {
    "PATH": "/Library/Frameworks/Python.framework/Versions/3.14/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin",
    "GEMINI_MODEL": "gemini-3.8-flash"
  }
}
```
It runs periodically via Antigravity's scheduler without staying resident in memory, and is symlinked to `~/.gemini/config/sidecars/blog-watcher` for global discovery.

## Authentication & Environment Variables

The sidecar supports authenticating as a GitHub App (preferred) or via a personal access token.

- `GEMINI_MODEL`: Gemini model identifier (default: `gemini-3.8-flash`).
- `GEMINI_API_KEY`: API key for Google GenAI / Gemini API.
- `GITHUB_APP_ID`: GitHub App slug (e.g. `redbrogdon-antigravity`) or numerical App ID.
- `github.pem`: Private key file placed in `.agents/sidecars/blog-watcher/github.pem` (mode `600`, ignored by git).
- `GITHUB_TOKEN` / `GH_TOKEN`: Fallback GitHub personal access token if not using GitHub App.
