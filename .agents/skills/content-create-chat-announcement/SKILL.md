---
name: content-create-chat-announcement
description: Generates concise, copy-ready internal chat announcements (for Google Chat, Slack, Discord) to amplify newly published content (blog posts, videos, talks, social threads) across team channels.
---

# Content Create: Chat Announcement

This skill guides the agent in producing short, high-impact internal chat announcements (optimized for Google Chat, Slack, and Discord). These messages are designed for sharing within team channels to inform coworkers about new content and encourage peer amplification across social platforms.

---

## 1. Message Structure & Anatomy

Every announcement must strictly follow this spaced, 3-part layout:

```text
[Thematic Emoji] [Announcement Header: What went live & where]

[One-sentence value description: What it covers & why readers care]

[Platform Icon] [Platform Name]: [URL]
[Platform Icon] [Platform Name]: [URL]
...
```

### Section Breakdown:

1. **Header: The Hook / Announcement**
   - Starts with a single, highly relevant, creative emoji (e.g. 🛵 for sidecars, 🛸 for Antigravity, 🎥 for video releases, 🚀 for launches).
   - Announces the content format, title/topic, and that it is live.
   - Example: `🛵 New blog post and social thread on Antigravity background sidecars are live`
   - **Line Break**: Always followed by a blank line.

2. **Body: The Value Proposition**
   - Exactly **one clear, punchy sentence**.
   - Explains the core problem solved, the technical insight, or the key takeaway for practitioners.
   - Avoid generic summaries; highlight concrete details (e.g. tools used, architecture patterns, or workflow benefits).
   - Example: `Explores practical developer automation: pairing deterministic Python with Gemini 3.8 and GitHub Apps to quietly automate repo maintenance without brittle OS daemons.`
   - **Line Break**: Always followed by a blank line before the links.

3. **Links: Platform Amplification Links**
   - Clean, scannable list pairing an emoji icon with the platform name and direct public URL.
   - Use standard platform pairings:
     - 💼 **LinkedIn / LinkedIn Post**: `<URL>`
     - 🐦 **X Thread / X**: `<URL>`
     - 🦋 **Bluesky**: `<URL>`
     - 📝 **Blog Post**: `<URL>`
     - 🎥 **YouTube / Video**: `<URL>`
     - 🎙️ **Podcast / Talk**: `<URL>`
     - 🐙 **GitHub / Repo**: `<URL>`

---

## 2. Voice & Tone Guidelines

- **Peer-to-Peer & Natural**: Sound like an engineer sharing something cool with teammates over chat.
- **Concise & Scannable**: Coworkers scan chat in seconds. Do not write paragraphs or multi-sentence teasers.
- **🚫 Strict Banned Vocabulary (AI Slop)**: Never use *delve, elevate, robust, harness, supercharge, game changer, streamline, testament, tapestry, vibrant, seamlessly*.
- **🚫 No Throat Clearing**: Never start with *"Excited to announce"*, *"I'm thrilled to share"*, or *"Hey everyone, check this out"*. Get straight to the subject.

---

## 3. Workflow

1. **Gather Content & Links**:
   - Identify the source material (blog post, video, talk) and all corresponding live URLs (social posts, blog, video links).
   - If URLs have not yet been generated or published, check with the user or draft with placeholders.
2. **Draft the Summary**:
   - Synthesize the core value of the content into a single sentence.
3. **Select the Leading Emoji**:
   - Pick a clever, topic-specific emoji. If there are multiple good options (e.g. literal vs. thematic), present 2–3 recommendations for the user to choose from.
4. **Deliver in a Code Block**:
   - Always wrap the output in a fenced Markdown code block so the user can copy the exact text with one click and paste it into their chat client.

---

## 4. Example Output

```markdown
🛵 New blog post and social thread on Antigravity background sidecars are live

Explores practical developer automation: pairing deterministic Python with Gemini 3.8 and GitHub Apps to quietly automate repo maintenance without brittle OS daemons.

💼 LinkedIn: https://www.linkedin.com/feed/update/urn:li:share:7505294421135867904
🐦 X Thread: https://x.com/redbrogdon/status/2099528716254867830
🦋 Bluesky: https://bsky.app/profile/redbrogdon.dev/post/3mvii6arnbv2r
📝 Blog Post: https://redbrogdon.dev/blog/enabling-my-vanity-with-antigravity-sidecars.html
```
