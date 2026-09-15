---
name: content-transform-video-to-blog
description: Converts a video script or transcript and graphic cues into a structured, engaging markdown blog post.
---

# Content Transform: Video to Blog Post

This skill instructs the agent on how to convert a video script or transcript (including slide cues, visual descriptions, and live-coding moments) into a high-quality markdown blog post. It outlines the universal workflow, spoken-to-written conversion rules, and modular product guidance integration.

---

## 1. Workflow Instructions

Before writing any blog content, you MUST complete the following steps:

1. **Read the Source:** Carefully read and analyze the provided video transcript, script, and visual descriptions.
2. **Interview the User:** Conduct an interactive interview in the chat by asking the following mandatory questions:
   * **Target Product / Brand**: Which product or brand is this blog post for? (e.g. `Flutter`, `Dart`, `Firebase`, `Go`, or `General`).
   * **Output Destination & Delivery Preference**: How would you like the finished blog post delivered? (e.g. save to a local workspace file at `content/drafts/my-blog-post.md`, display directly in chat as Markdown, export to a Google Doc, or open a GitHub PR).
   * **Target Audience**: Who is the intended audience (e.g. beginner developers, experienced engineers, tech leads)?
   * **Key Takeaways & Focus**: What primary themes should be emphasized?
   * **Desired Tone & Style**: (e.g. technical tutorial, thought leadership, casual walkthrough).
   * **SEO Keywords & Frontmatter Requirements**: Are there specific target keywords or frontmatter keys needed?
3. **Load Product Reference**:
   * Check if a product reference file exists in `references/product/{product}.md` (e.g. [`references/product/flutter.md`](references/product/flutter.md) or [`references/product/dart.md`](references/product/dart.md)).
   * If found, apply product-specific CMS formats and frontmatter rules.
   * If not found, load [`references/product/default.md`](references/product/default.md).
4. **Wait for Answers:** Do not proceed with blog post generation until the user has responded to the interview questions.

---

## 2. Formatting Requirements

### Frontmatter Metadata
Every blog post must begin with standard YAML frontmatter:

```yaml
---
title: "[Compelling, SEO-Optimized Title]"
date: YYYY-MM-DD
author: "[Author Name]"
excerpt: "[1-2 sentence hook summarizing the value of the post]"
tags:
  - tag1
  - tag2
---
```

### Blog Post Structure
* **Educational Introduction (Hook):** Never copy spoken greeting dialogue (e.g., *"Hey everybody! I'm..."*). Write an introductory section defining core concepts and setting up what the reader will learn.
* **Body Sections:** Use clear hierarchical markdown headers (`##`, `###`).
* **Unified & Annotated Code Blocks:** Consolidate step-by-step video code fragments into single, comprehensive, copy-pasteable blocks with inline comments.
* **Callouts & Alerts:** Use standard markdown blockquotes or GitHub-style alerts (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`) to highlight key takeaways or warnings.
* **Visual Elements & Slide Graphics**: Translate slide illustrations or UI demos into descriptive text, tables, or Mermaid diagrams.
* **Summary & Call to Action (CTA):** End with a `## Summary` header wrapping up takeaways, and direct readers to next steps (documentation, codelabs, repos).

---

## 3. Content Adaptation Rules

* **Preserve Structural Flow:** Maintain the structural flow of the source video script while converting spoken intros and outros into written opening sections and summaries.
* **Polished Written Style:** Remove video-specific filler (e.g. "like and subscribe", "comment below", "link in description", "as you can see on screen").
* **Active URL Resolution:** Replace spoken references to tools, codelabs, or docs with valid inline hyperlinks.
* **Reconstruct Screen Visuals:** Convert spoken references to visual cues ("if we look over here...") into descriptive text (e.g., "Click the **Add Item** (`+`) button to create a record").

---

## 4. Output Destination & Delivery

Deliver the completed blog post based on the user's expressed preference and available environment tools:
* **Local Workspace File**: If the user requested a local file and file creation tools are available, save the completed draft to the specified file path and provide a clickable file link.
* **Direct Chat Output**: If the user requested chat delivery, or if local file writing tools are unavailable in the current environment, render the complete, high-fidelity Markdown directly in the chat response.
* **External Integrations (Google Docs, GitHub PR, etc.)**: If the user requested an external destination and the environment supports corresponding integration tools, invoke them to create the document/PR; otherwise, render the draft in chat and provide instructions or links for exporting.

### Continuous Skill Improvement Prompt
After delivering the blog post, include a brief closing note:
> *"💡 **Help Improve This Skill**: If you experienced any friction or had to make manual edits during this session, say **'use meta-refine-skill'** to automatically analyze our chat and update the skill instructions for future runs!"*
