# Default Developer Blog Post Reference & Guidance

This reference file contains general guidelines, voice/tone standards, and blueprints for technical developer blog posts across Google and open-source projects.

---

## 1. General Voice & Tone

* **Perspective**:
  * For official team announcements and major product releases, use first-person plural (`we`, `our`, `us`).
  * For technical tutorials, deep dives, and opinionated walkthroughs, use first-person singular (`I`, `my`, `me`).
* **Tone**: Clear, helpful, developer-centric, and authoritative without being overly formal. Write as an experienced engineer sharing practical insights.
* **Vendor Neutrality**: When explaining architectural patterns or concepts, keep explanations vendor-neutral (e.g. use generic terms like "object storage", "pub/sub queues", or "relational databases") unless specific third-party tools are core to the tutorial.

---

## 2. General Content Pacing & Structure

* **Problem-First Hook**: Always explain the problem area or developer friction before presenting the solution.
* **Content Alternation**: Maintain readability by avoiding long blocks of prose. Intersperse prose every 3-4 paragraphs with code snippets, tables, bulleted lists, or diagrams.
* **Progressive Code Breakdown**: Break down code walkthroughs into logical steps rather than dumping monolithic files.

---

## 3. Universal Blueprints

### A. Technical Deep Dive
1. **The Challenge**: A complex engineering problem or performance bottleneck.
2. **Under-the-Hood Mechanics**: Conceptual overview of why the problem occurs and how the subsystem works.
3. **The Solution**: Walkthrough of the fix, diagnostic steps, or optimized code.
4. **Before & After**: Code or benchmark comparison demonstrating the improvement.
5. **CTA**: Relevant links to documentation, sample repos, or issues.

### B. Product / Feature Announcement
1. **Introduction**: What is being launched and why it matters.
2. **Key Capabilities**: Core features and developer benefits.
3. **Code Walkthrough / Quickstart**: Quick code snippet showing how to get started.
4. **CTA**: Getting started link, repository, or documentation page.
