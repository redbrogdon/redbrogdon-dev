# 2. Deterministic and Agentic Sidecar Architecture

Date: 2026-09-08
Status: Accepted

## Context
Maintaining an up-to-date personal bibliography across distributed publications (e.g. `blog.flutter.dev`, `dart.dev/blog`, YouTube channels, podcasts) is tedious and easily forgotten. 

While autonomous AI agents can monitor sources and open pull requests, fully unconstrained agents struggle with deterministic reliability: they hallucinate URLs, invent inconsistent git branch names, mishandle edge cases in XML parsing, and waste API tokens on redundant runs.

## Decision
We implemented a background watcher as an **Antigravity Sidecar** (`.agents/sidecars/blog-watcher/`) based on a strict architectural division of labor:

1. **Deterministic Plumbing (Python)**:
   - Feeds are pulled directly via Atom/RSS XML and parsed deterministically.
   - Articles are cross-referenced against existing slugs in `public/blog/index.html` and active GitHub PRs (`gh pr list --state open`). If a PR is open or merged, the process exits cleanly.
   - Authentication is performed as an official GitHub App (`redbrogdon-antigravity[bot]`) via RS256 JWT signing, obtaining short-lived installation access tokens.
   - Git operations, strict branch naming constraints (`bot/blog-<slug>`), and atomic commits are managed strictly through deterministic code.
   - A local rotating log file (`watcher.log`) records every execution cycle.

2. **Agentic Synthesis (Google GenAI / Gemini 3.8 Flash)**:
   - When an unaddressed article is verified, the full content is passed to Gemini with strict site voice constraints and structured JSON output.
   - The model is responsible solely for synthesizing:
     - A 1-2 sentence editorial blurb for `public/blog/index.html`.
     - An informative, structured GitHub PR description.

3. **Lifecycle & Scheduling**:
   - The sidecar runs every six hours via Antigravity's built-in scheduler (`"builtin": "schedule"`, `"args": ["0 */6 * * *", "python3", "watch.py", "--once"]`). It performs its check and exits immediately, avoiding idle memory consumption.

## Consequences
- **Positive**: 100% deterministic reliability for plumbing, security credentials, and git hygiene; high-quality, creative editorial blurbs matching the site tone; pull requests arrive carrying verified GitHub App bot badges.
- **Negative**: Requires maintaining both the Python sidecar script and a registered GitHub App with private key secrets.
