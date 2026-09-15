---
name: content-create-wotw-video
description: Drafts a short-form feature highlight or "Widget / Technique of the Week" (WOTW/TOTW) video script with metadata, outline, and 3-column script table.
---

# Content Create: Short Feature Video (WOTW / TOTW)

This skill instructs the agent on how to write short-form (~60-90 second) feature highlight scripts (such as *Widget of the Week* or *Technique of the Week*). It outlines the workflow, metadata structure, 3-column script table format, and product reference integration.

---

## 1. Workflow Instructions

Before writing any script content, you MUST complete the following steps:

1. **Analyze Context & Topic:** Review provided notes, code samples, or feature descriptions.
2. **Interview the User:** Conduct an interactive interview in the chat by asking the following mandatory questions:
   * **Target Product / Brand**: Which product or brand is this video for? (e.g. `Flutter`, `Dart`, `Firebase`, `Go`, or `General`).
   * **Output Destination & Delivery Preference**: How would you like the finished script delivered? (e.g. save to a local workspace file at `content/scripts/my-wotw-script.md`, display directly in chat as Markdown, export to a Google Doc, or open a GitHub PR).
   * **Feature Topic**: What specific widget, language feature, API, or technique is being highlighted?
   * **The "Hook" Pain Point**: What developer friction or problem does this feature solve?
   * **Presenter / Author Details**: Who is the author/presenter?
3. **Load Product Reference**:
   * Check if a product reference file exists in `references/product/{product}.md` (e.g. [`references/product/flutter.md`](references/product/flutter.md) or [`references/product/dart.md`](references/product/dart.md)).
   * If found, apply product series standards and visual notes conventions.
   * If not found, load [`references/product/default.md`](references/product/default.md).
4. **Wait for Answers:** Do not write the script until the user has responded to the interview questions.

---

## 2. Formatting Requirements

The script document must be formatted with the following structure:

### A. Metadata & Reviews Table
```markdown
**Metadata**

- **Status:** Draft
- **Video Title:** [Title]
- **Video Description / Caption:** [1-2 sentences]
- **Resource Links:** [URLs]
- **Author:** [Name]
- **Presenter:** [Name]
- **Date:** YYYY-MM-DD

**Reviews**

| Reviewer | Role | Status |
| -------- | ---- | ------ |
| [Name]   | DRE  | Not started |
```

### B. Content Outline
1. **Introduction (~10-15 seconds):** Hook the audience on the pain point and introduce the feature.
2. **Body (~1 minute):** Demonstrate syntax / API usage, key properties, and core benefits.
3. **Conclusion (~5-10 seconds):** CTA directing developers to documentation.

### C. 3-Column Script Table
```markdown
**Script Table**

| Script (Exact words which you will say) | Subtitle or text appearing on slide | Visual notes |
| --------------------------------------- | ----------------------------------- | ------------ |
| `<music>` | "How do I..." | Standard intro graphics with title card and animated logo. |
| [Dialogue line 1] | [Slide text or `code snippet`] | [Visual cue description] |
```

---

## 3. Output Destination & Delivery

Deliver the completed video script based on the user's expressed preference and available environment tools:
* **Local Workspace File**: If the user requested a local file and file creation tools are available, save the completed script to the specified file path and provide a clickable file link.
* **Direct Chat Output**: If the user requested chat delivery, or if local file writing tools are unavailable in the current environment, render the complete, high-fidelity script Markdown directly in the chat response.
* **External Integrations (Google Docs, GitHub PR, etc.)**: If the user requested an external destination and the environment supports corresponding integration tools, invoke them to create the document/PR; otherwise, render the script in chat and provide instructions or links for exporting.

### Continuous Skill Improvement Prompt
After delivering the script, include a brief closing note:
> *"💡 **Help Improve This Skill**: If you experienced any friction or had to make manual edits during this session, say **'use meta-refine-skill'** to automatically analyze our chat and update the skill instructions for future runs!"*