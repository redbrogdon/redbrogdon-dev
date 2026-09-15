---
name: content-transform-blog-to-video
description: Converts a markdown blog post into a structured video script with visual cues, abstract, and metadata, preserving the original narrative flow.
---

# Content Transform: Blog to Video Script

This skill instructs the agent on how to convert a standard markdown blog post into a professional video script asset. It outlines the universal workflow, production metadata standards, audio-visual pairing rules, and modular product guidance integration.

---

## 1. Workflow Instructions

Before writing any script content, you MUST complete the following steps:

1. **Read the Source:** Carefully read and analyze the provided markdown blog post.
2. **Interview the User:** Conduct an interactive interview in the chat by asking the following mandatory questions:
   * **Target Product / Brand**: Which product or brand is this video script for? (e.g. `Flutter`, `Dart`, `Firebase`, `Go`, or `General`).
   * **Output Destination & Delivery Preference**: How would you like the generated video script delivered? (e.g. save to a local workspace file at `content/scripts/my-video-script.md`, display directly in chat as Markdown, export to a Google Doc, or open a GitHub PR).
   * **Video Metadata**: What is the video title? Who are the author and presenter/talent?
   * **Target Audience**: Who is the target audience for this video?
   * **Desired Tone & Pacing**: (e.g. highly technical walkthrough, energetic quickstart, casual demo).
   * **Primary Call to Action (CTA)**: What action should viewers take in the outro?
3. **Load Product Reference**:
   * Check if a product-specific reference file exists in `references/product/{product}.md` (e.g. [`references/product/flutter.md`](references/product/flutter.md) or [`references/product/dart.md`](references/product/dart.md)).
   * Apply product-specific series standards, intro/outro graphics, and visual code cues.
   * If not found, load [`references/product/default.md`](references/product/default.md).
4. **Wait for Answers:** Do not proceed with script generation until the user has responded to the interview questions.

---

## 2. Formatting Requirements

The final script MUST adhere to the following structural format. **NEVER use markdown tables for the main script body.**

### Metadata & Header
The script must begin with a production metadata section, followed by YouTube metadata, an abstract, and an outline. 

```markdown
## Video script: [Title]

|                        |                              |
| :--------------------- | :--------------------------- |
| Author                 | [Name] ([LDAP/Handle])       |
| Title                  | [File Name/ID]               |
| Series (if applicable) | [Series Name]                |
| Product or Program     | [Product]                    |
| Talent                 | [Name] ([LDAP/Handle])       |

**YT Title**: [Draft Title]

**YT Thumbnail Text**: [Draft Text]

**YT Description**:<br>
[2-3 paragraphs summarizing the video and including necessary links/CTAs]

## Abstract
[1-2 sentences summarizing the technical scope of the video.]

## Outline
  * Intro
  * [Section 1 from Blog]
  * [Section 2 from Blog]
  * ...
  * Outro
```

### Script Body Structure
The main body of the script must use alternating `#### Script` and `#### Graphics` headers nested under the primary `###` section headings. 

**CRITICAL CHUNKING RULE**: Each `#### Graphics` section MUST contain **one and only one** graphic instruction (e.g. a single camera shot, a single code snippet state, a single JSON payload, or a UI recording). The preceding `#### Script` section MUST contain **only** the dialogue spoken while that specific graphic is on screen. **Do NOT combine multiple visual instructions or bullet lists into a single `#### Graphics` block.**

```markdown
## Script

### [Section Name]

#### Script
[Spoken dialogue for visual 1]

#### Graphics
[Graphic 1: e.g., "Presenter addresses camera"]

#### Script
[Spoken dialogue for visual 2]

#### Graphics
[Graphic 2: e.g., "Code editor showing initial class declaration"]
```

---

## 3. Content Adaptation Rules

* **Preserve Structure:** Maintain the structural section flow of the source blog post in the script `###` headings.
* **Conversational & First-Person Tone:** Translate written paragraphs into spoken, conversational first-person singular dialogue (`I`, `my`, `me`).
* **Offload to Visuals:** Move dense code blocks, long lists, and data payloads into `#### Graphics` blocks.
* **Granular 1:1 Audio-Visual Pairing:** Ensure every spoken `#### Script` section maps precisely to its corresponding `#### Graphics` visual cue.
* **Progressive Code Walkthroughs:** Step through code changes one piece at a time (shell $\rightarrow$ properties $\rightarrow$ logic implementation).
* **Strong Outro CTA:** Always include a spoken CTA in the final dialogue directing viewers to documentation or sample repos.

---

## 4. Output Destination & Delivery

Deliver the completed video script based on the user's expressed preference and available environment tools:
* **Local Workspace File**: If the user requested a local file and file creation tools are available, save the completed script to the specified file path and provide a clickable file link.
* **Direct Chat Output**: If the user requested chat delivery, or if local file writing tools are unavailable in the current environment, render the complete, high-fidelity script Markdown directly in the chat response.
* **External Integrations (Google Docs, GitHub PR, etc.)**: If the user requested an external destination and the environment supports corresponding integration tools, invoke them to create the document/PR; otherwise, render the script in chat and provide instructions or links for exporting.

### Continuous Skill Improvement Prompt
After delivering the script, include a brief closing note:
> *"💡 **Help Improve This Skill**: If you experienced any friction or had to make manual edits during this session, say **'use meta-refine-skill'** to automatically analyze our chat and update the skill instructions for future runs!"*
