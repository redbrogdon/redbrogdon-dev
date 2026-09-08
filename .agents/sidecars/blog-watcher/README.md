# Antigravity Blog Watcher & Auto-PR Sidecar

An automated Antigravity sidecar and agent that monitors official Flutter and Dart publications for articles written by Andrew Brogdon.

When a new article is detected:
1. Generates an editorial summary matching the literary tone of `redbrogdon.dev` using **Gemini 3.8** (`gemini-3.8-flash`).
2. Creates an isolated git branch (`bot/blog-<slug>`, max 25 chars).
3. Adds the entry to `public/blog/index.html` and `public/feed.xml`.
4. Commits the changes conforming to the repository's commit workflow.
5. Pushes the branch and opens a GitHub Pull Request via `gh pr create`.

## Monitored Feeds
- **Flutter Blog:** `https://blog.flutter.dev/feed.xml`
- **Dart Blog:** `https://blog.dart.dev/feed.xml`

*(Medium feeds and other external sources are ignored per configuration).*

## Quick Usage

### 1. Dry Run (Test Detection & Summarization without Git/PR changes)
```bash
python3 .agents/sidecars/blog-watcher/watch.py --dry-run
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
  "description": "Monitors blog.flutter.dev and blog.dart.dev for new articles by Andrew Brogdon and opens PRs via Gemini 3.8",
  "command": "python3",
  "args": ["watch.py", "--interval", "21600"],
  "restart_policy": "always",
  "env": {
    "GEMINI_MODEL": "gemini-3.8-flash"
  }
}
```
It is also symlinked to `~/.gemini/config/sidecars/blog-watcher` for global Antigravity discovery.

## Authentication & Environment Variables

The sidecar supports authenticating as a GitHub App (preferred) or via a personal access token.

- `GEMINI_MODEL`: Gemini model identifier (default: `gemini-3.8-flash`).
- `GEMINI_API_KEY`: API key for Google GenAI / Gemini API.
- `GITHUB_APP_ID`: GitHub App slug (e.g. `redbrogdon-antigravity`) or numerical App ID.
- `github.pem`: Private key file placed in `.agents/sidecars/blog-watcher/github.pem` (mode `600`, ignored by git).
- `GITHUB_TOKEN` / `GH_TOKEN`: Fallback GitHub personal access token if not using GitHub App.
