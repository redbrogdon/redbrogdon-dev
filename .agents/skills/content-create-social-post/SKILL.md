---
name: content-create-social-post
description: Generates high-engagement social copy variations for technical audiences on X (Twitter) and/or LinkedIn based supplied resources and an interview with the user.
---

# Content Create: Social Post

This skill instructs the agent on how to write high-engagement social media posts (targeting **X / Twitter** and **LinkedIn**). It outlines the universal platform specs, copy options formatting, and modular product guidance integration.

## Best practices

### Avoid creating "AI slop"

When drafting the post, strictly adhere to these writing standards:

#### 1. Inject Authentic Warmth & Signature Phrasing:
- **Use the User's Signature Words**: Pepper in the user's favorite phrasing and colloquialisms defined in their style guide.
- **Write Peer-to-Peer**: Sound like a practitioner talking in a team chat, over a coffee, or pairing on a terminal.
- **Embrace Vulnerability & Self-Effacement**: Acknowledge when you struggled, did multiple drafts, or reverted to simple tools.
- **Use Natural Rhythm**: Use contractions (*didn't, wasn't, I've*), conversational sentence fragments, and relatable transitions.

#### 2. 🚫 Strict Banned Vocabulary (AI-isms):
Never use: *delve, tapestry, beacon, testament, robust, elevate, supercharge, harness, seamlessly, ever-evolving, vibrant, pioneering, game changer, streamline, furthermore, moreover, multifaceted, transformative, paramount, unravel, meticulous*.

#### 3. 🚫 Strict Banned Openers & Throat-Clearing:
Never start with:
- *"Here's the thing,"*
- *"In today's fast-paced tech world,"*
- *"It's important to remember that,"*
- *"Let's dive in,"*
- *"Have you ever wondered..."*
- *"At its core..."*

#### 4. 🚫 Strict Banned Corporate Dribble & Anti-Tone:
Never use abstract corporate buzzwords like *"leveraging synergies"*, *"driving cross-functional alignment"*, *"maximizing operational bandwidth"*, or *"streamlining workflow velocity"*. Never sound like a sanitized corporate press release or a fake-profound thought leader.

### Consider the user's preferences when delivering the social copy

When you deliver the completed social copy, do so in a manner that aligns with the user's expressed preference and available environment tools. Here are some options:

* **Direct Chat Output**: If the user requested chat delivery, or if local file writing tools are unavailable in the current environment, render the copy directly in the chat response.
* **Local Workspace File**: If the user requested a local file and file creation tools are available, save the completed document to the specified file path and provide a clickable file link.
* **External Integrations (Google Docs, GitHub PR, etc.)**: If the user requested an external destination and the environment supports corresponding integration tools, invoke them to create the document/PR; otherwise, render the copy in chat and provide instructions or links for exporting.

### Representing shortlinks

Always output external URLs using the placeholder: `[g.dev link placeholder: <URL>]`.

---

## Workflow

You must use this workflow to generate social copy for the user. Perform each step in order.

### 1. Gather metadata

Analyze the user's initial prompt and any provided URLs to auto-extract as much metadata as possible before asking clarifying questions:

* **Target Product / Brand**: Auto-detect from prompt or URL domain/path if present (e.g. `flutter.dev` $\rightarrow$ `Flutter`, `firebase.google.com` $\rightarrow$ `Firebase`). Otherwise, ask the user.
* **Existing resources**: Infer from links supplied in the prompt. If no links were provided, ask if reference docs or URL targets exist.
* **Target platforms**: Confirm target platforms (e.g. `X`, `LinkedIn`, `Bluesky`). Look for platform-specific reference files in `references` matching the selected platform(s) and read them.
* **Output Destination & Delivery Preference**: Confirm whether output should be delivered in chat or saved to a workspace file.
* **Visual Asset**: Confirm media type (*Image*, *Video / Short*, *Link Preview*, or *None / text-only*).

> **Verification Rule**: Explicitly state all auto-extracted metadata to the user when responding (e.g., *"Based on the link, I've set the target brand to **Flutter** and the resource to [URL]. Let me know if that's incorrect."*) so they can quickly verify or correct it, while prompting for any remaining unstated preferences.

### 2. Analyze resources and product references
If the user provided links to resources, read those resources.

Check if a product reference file exists in `references/product/{product}.md` (e.g. [`references/product/flutter.md`](references/product/flutter.md) or [`references/product/dart.md`](references/product/dart.md)). If not found, load [`references/product/default.md`](references/product/default.md). In either case, use the conventions you find when drafting copy.

### 3. Brainstorm

Check to see whether the user already has a topic, structure, and framework for the content they'd like to generate. If not, use the following workflow to brainstorm with the user:

#### Step 3a: Ground the brainstorm

Ask the user to describe the topic for the content they're interesting in creating. Invite them to reply with unstructured thoughts, ideas, links, and anything else they can think of. If they provide links to resources, read them. If you feel additional research is appropriate, ask permission to do so, and (if given permission) perform that research.

#### Step 3b: Active listening

Briefly restate what you've heard and learned to make sure that you and the user are aligned on what they told you and what you found out for yourself (if anything).

#### Step 3c: Structured topic discovery & "Grill Me" mode

Next, work to narrow down the topic of the post based on the user's goals. Never ask open-ended questions like *"What do you want to write about?"*. Instead, use **structured anchors** or enter **"Grill Me" Mode**:

Structure anchors:
1. 🚀 **The Micro-Win / What Worked**: A small victory, feature shipped, or workflow discovery.
2. 💥 **The Mistake / What Went Wrong**: A tricky bug, failed assumption, or hard lesson.
3. 📖 **The Learning / What You Read**: An article, doc, or paper that sparked an insight or disagreement.
4. 🔥 **The Contrarian Take / Myth Busting**: Industry advice you disagree with or find flawed.
5. 🔍 **The Behind-the-Scenes**: A reality of how your work actually gets done vs. how outsiders perceive it.

If the user asks to be grilled or is unsure which topic to use, ask 3–4 opinionated, situational questions:
* **The "Roll Your Eyes" Take**: *"What is something people in your industry keep claiming on social media that doesn't match your actual day-to-day experience?"*
* **The 3-Hour Rabbit Hole**: *"What was the most frustrating bug, test failure, or roadblock you hit recently where the fix was either surprisingly simple or taught you something subtle?"*
* **The Workflow Hack**: *"Have you wired up a custom script, shortcut, or automation recently that quietly saves you hours of time?"*
* **The Practitioner Dilemma**: *"What is a debate or realization you had with your team recently about how tools are actually used vs. how companies market them?"*

#### Step 3d: Deep-Dive Interview (Extracting the Gold)

Once the user selects a topic, ask **2–3 focused follow-up questions** to extract the core contrast and insights. Ask them to first choose which structure the post should take. 

* **Before vs. After (The Contrast)**: What did your situation look like before (e.g. pain, time wasted, manual drag), and what does it look like now?
* **The "Secret Sauce" / The Why**: Why did previous attempts or off-the-shelf tools fail, and what was the key realization or breakthrough that made this work?
* **The Unvarnished Truth (Realism over Hype)**: What's one limitation, trade-off, or setup detail that people need to know so this doesn't sound like magic hype?
* **The Core Takeaway**: If the reader takes away one actionable rule from this, what should it be?

#### Step 3e: Framework Selection & Mapping

Match the extracted topic and structure to one of the proven high-engagement frameworks:

| Framework | Best For | Core Formula |
| :--- | :--- | :--- |
| **Personal Proof Story** | Shipped projects, performance wins, workflow hacks | *"I used to struggle with X. Now I do Y. Here is the breakdown."* |
| **The Anti-SaaS / Custom Tool Breakthrough** | Custom scripts, agent setups, personal systems | *"Why off-the-shelf tools failed $\rightarrow$ The lightweight custom fix $\rightarrow$ The mindset shift."* |
| **Tactical Value Drop** | How-to guides, code snippets, tool recommendations | *"Here is the common problem. Here is the exact fix/setup."* |
| **Curiosity + Contrast (Contrarian)** | Unpopular opinions, myth busting, counterintuitive findings | *"You expect A... but here is why B actually works."* |
| **The Mistake Breakdown** | Post-mortems, painful bugs, lessons learned | *"The mistake I made cost X. Here is how to prevent it."* |
| **The Curated List / Toolkit** | Resource roundups, cheat sheets, rules | *"N rules/tools that simplified [outcome]. Learned over [timeframe]."* |

### 4. Generate draft copy

Use all that you have learned to generate 5 social copy options for the user to review. Format each of the options in this manner:

```
### Option [number]: [Short Title / Theme of variation]

**[name of platform]**:
[Draft text for that platform]

**[name of platform]**:
[Draft text for that platform]

...

---
```

Ask the user for feedback and which of the five options they'd like to move forward with. Work with them to iterate on the draft. When the user indicates they're satisfied, deliver the final version to them.

### 5. Final Notes
After delivering the copy, tell the user these two things:

```
⚠️ **Draft Notice**: This is an AI-generated draft to help structure your ideas. Before publishing, **read it aloud and edit it in your own words**. Replace any phrasing that doesn't sound like you, verify all technical details, and make sure it represents your authentic experience.

💡 **Help Improve This Skill**: If you experienced any friction or had to make manual edits during this session, say **'use meta-refine-skill'** to automatically analyze our chat and update the skill instructions for future runs!
```
