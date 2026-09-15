---
name: content-create-blog-post
description: Drafts a new high-fidelity technical blog post based on notes, conversation context, and an interactive user interview, leveraging product-specific style guides and blueprints.
---

# Content Create: Technical Blog Post

This skill instructs the agent on how to write professional, high-fidelity technical blog posts. It outlines the universal workflow, progressive code pacing, formatting standards, and modular product guidance integration.

---

## 1. Workflow & Interactive Interview

Before drafting any blog post content, you MUST complete the following steps:

1. **Analyze Context & Notes:** Review provided notes, outlines, drafts, or conversation history. Ask the user for all the context and resources they can provide. Make sure they've indicated there are no more available resources they can provide before proceeding.
2. **Interview the User:** Conduct an interactive interview in the chat by asking the following mandatory clarifying questions:
   * **Target Product / Brand**: Which product or brand is this blog post for? (e.g. `Angular`, `Flutter`, `Dart`, `Firebase`, `Go`, or `General`).
   * **Output Destination & Delivery Preference**: How would you like the generated blog post delivered? (e.g. save to a local workspace file at `content/drafts/my-post.md`, display directly in chat as Markdown, export to a Google Doc, or open a GitHub Pull Request).
   * **Category**: What core category does this post fall under? (e.g. *Product / SDK Release*, *Technical Deep Dive*, *Architecture & Tutorials*, *Case Studies*).
   * **The "Why" (Pain Point)**: What specific developer problem, friction, or limitation does this post address? Why is this feature or topic important?
   * **Technical Details & Code Snippets**: What specific APIs, commands, or packages must be featured? Do you have raw code, or should I draft realistic production-grade snippets?
   * **Call to Action (CTA)**: What primary action should the reader take (e.g. visit documentation, try a package/tool, check out a GitHub repo)?
   * **Target Publication Date**: What is the target date for the YAML frontmatter?
3. **Load Product Reference**:
   * Check if a product-specific reference file exists in `references/product/{product}.md` (e.g. [`references/product/go.md`](references/product/go.md), [`references/product/angular.md`](references/product/angular.md), [`references/product/flutter.md`](references/product/flutter.md), or [`references/product/dart.md`](references/product/dart.md)).
   * If a product-specific file exists, read and adhere strictly to its tone persona, community requirements, and category blueprints.
   * If no product-specific file exists for the chosen product, load [`references/product/default.md`](references/product/default.md) and offer to help document a new product reference file for future use.
4. **Wait for Answers:** Do not write or outline the blog post until the user has responded to the interview questions.

---

## 2. Universal Style & Structure Guidelines

Once the interview is complete and product guidance is loaded:

### A. General Voice & Tone Rules
* **Dual Perspective Standard**:
  * **Announcements & Version Releases**: Write strictly from the perspective of the product team using first-person plural (`we`, `our`, `us`).
  * **Deep Dives, Tutorials & Showcases**: Write from a developer perspective using first-person singular (`I`, `my`, `me`).
* **Active & Conversational**: Pair-programming tone. Ground explanations in real software engineering realities, avoiding empty marketing jargon.

### B. Universal Structural Principles
* **The "Why" Before the "How"**: Always establish the developer friction, limitation, or problem before introducing the new solution, API, or syntax primitive.
* **Content Rhythm & 3-4 Paragraph Rule**: Never write long walls of unbroken prose. Interleave text every 3 to 4 paragraphs with a code snippet, visual/image placeholder, comparison block, or benchmark table.
* **Progressive Disclosure**: When introducing code, break complex structures down into progressive steps (signature $\rightarrow$ properties $\rightarrow$ implementation logic) rather than dropping monolithic blocks.
* **Side-by-Side Comparisons**: When showcasing refactored or new syntax, format code using explicit comparative headers:
  * `**The old way:**` followed by the legacy code block.
  * `**The new way:**` followed by the new concise code block.
* **Community Gratitude Outro**: Every major announcement, release post, community survey, or RFC update must include an explicit section acknowledging community contributors, issue reporters, or survey participants, closing with an explicit thank-you.
* **Call to Action (CTA) Footer**: Every blog post must conclude with a CTA section providing clear next steps (links to documentation, installation guides, migration tools, GitHub repos, or interactive playgrounds).

---

## 3. Universal Master Blueprints

### Blueprint 1: SDK / Major Product Release Announcement
1. **Title / Headline**: "What’s new in [Product] X.Y" or "Introducing [Product] vX" or "[Product] X.Y is released!"
2. **Introduction / Executive Summary**: Energetic hook summarizing major themes, performance benchmarks, or headline features.
3. **Core Feature Walkthroughs**: Subsections for key framework, language, or engine features.
4. **Tooling & Developer Experience**: Updates to CLI tools, IDE extensions, DevTools, or analysis servers.
5. **Community Gratitude**: Dedicated section thanking contributors, issue reporters, and ecosystem maintainers.
6. **CTA Footer**: Links to official documentation, migration schematics, and installation guides.

### Blueprint 2: Technical Deep Dive & Feature Design
1. **The Problem / Motivation**: Stating the specific developer friction, limitation, or performance bottleneck.
2. **The Architectural Solution**: Explaining the design principles, trade-offs, and under-the-hood mechanics.
3. **Syntax & Code Walkthrough**: Compilable, tagged code snippets demonstrating the new primitive or pattern.
4. **Before / After Comparison**: Comparative code block showing legacy verbose patterns vs new concise primitives.
5. **CTA Footer**: Links to tutorials, sample repositories, or interactive playgrounds (e.g. StackBlitz, DartPad, Go Playground).

---

## 4. Formatting & Syntax Standards

* **YAML Frontmatter**: Every blog post must begin with valid YAML frontmatter:
  ```yaml
  ---
  title: "Exact Title of the Blog Post"
  date: YYYY-MM-DD
  ---
  ```
* **Annotated Code Blocks**: Annotate code snippets with single-line comments (`//` or `#`) explaining key APIs.
* **Boilerplate Minimization**: Focus code blocks strictly on the essential logic being demonstrated.
* **Language Tagging**: Always tag code blocks with appropriate language identifiers (e.g. `dart`, `go`, `ts`, `yaml`, `bash`, `python`, `json`).

---

## 5. Output Destination & Delivery

Deliver the completed content based on the user's expressed preference and available environment tools:
* **Local Workspace File**: If the user requested a local file and file creation tools are available, save the completed document to the specified file path and provide a clickable file link.
* **Direct Chat Output**: If the user requested chat delivery, or if local file writing tools are unavailable in the current environment, render the complete, high-fidelity Markdown directly in the chat response.
* **External Integrations (Google Docs, GitHub PR, etc.)**: If the user requested an external destination and the environment supports corresponding integration tools, invoke them to create the document/PR; otherwise, render the Markdown in chat and provide instructions or links for exporting.

### Continuous Skill Improvement Prompt
After delivering the content, include a brief closing note:
> *"💡 **Help Improve This Skill**: If you experienced any friction or had to make manual edits during this session, say **'use meta-refine-skill'** to automatically analyze our chat and update the skill instructions for future runs!"*
