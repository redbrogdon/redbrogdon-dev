---
name: meta-refine-skill
description: Analyzes a recently completed content creation session, identifies friction or manual edits, and refines the associated skill instructions in-place (for local clones) or formats an issue report (for web users).
---

# Meta Refine Skill

This skill instructs the agent on how to analyze a completed content generation session, identify friction points or user corrections, and iteratively refine the associated skill's instructions (e.g. `SKILL.md`) or related files (e.g `references/*.md`).

---

## Workflow

When invoked (e.g. *"refine this skill"*, *"use meta-refine-skill"*, or *"improve the blog post skill based on our chat"*), execute the following steps in order:

### 1. Identify the Target Skill
Determine which skill was executed during the current or recent conversation (e.g. `content-create-blog-post`, `content-create-social-post`, `content-transform-video-to-blog`, etc.).

### 2. Analyze Session History
Inspect the conversation transcript and trajectory for:
* **User Corrections**: Moments where the user corrected tone, syntax, formatting, or structure.
* **Interview Friction**: Redundant, irrelevant, or awkwardly phrased clarifying questions.
* **Missing Guidance**: Product-specific nuances or guidelines that were missing and had to be supplied manually.
* **Output Delivery Preferences**: Unstated user preferences for formatting, delivery, or confirmation flow.

### 3. Solicit User Insights
Ask the user if they have any additional notes, memories of friction, or specific changes they'd like to see included.

### 4. Present Findings & Proposed Edits
Summarize the session findings and present the proposed Markdown diffs or instruction changes directly in chat. **DO NOT modify any files at this stage, even if file editing tools are available.**

### 5. Obtain User Alignment
Discuss the proposed edits with the user and iterate on the wording or rules until the user explicitly approves.

### 6. Deliver Changes Based on Environment Capabilities
Ask the user how they would like the approved changes to be delivered:

* **Local Workspace (Repo Clone with File System Access)**:
  * Offer to update the target skill file (`.agents/skills/<skill-name>/SKILL.md` or `references/product/<product>.md`) directly using code editing tools.
  * Offer to create a git commit, branch, or Pull Request to submit the improvement upstream.

* **Web Interface / Hosted Chat (No File System Access or External Repo)**:
  * Format a ready-to-submit GitHub Issue report containing the friction summary and exact Markdown snippet:
    ```markdown
    ### Proposed Skill Refinement: [Skill Name]

    **Friction Observed**:
    - [Summary of manual edit or friction point during session]

    **Proposed Update to `SKILL.md` / `references/product/[product].md`**:
    ```markdown
    [Exact Markdown diff or replacement snippet]
    ```
    ```
  * Direct the user to the issue tracker link to file the issue (e.g., `https://github.com/redbrogdon/first-draft/issues`).
