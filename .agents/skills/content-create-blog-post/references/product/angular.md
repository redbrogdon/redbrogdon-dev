# Angular Blog Post Reference & Guidance

This reference file contains product-specific guidelines, tone DNA, and specialized blueprints for articles intended for the official **Angular Blog** (`blog.angular.dev`).

---

## 1. Product Tone Persona ("Framework Renaissance & Collective Stewardship")

* **Tone DNA**: Energetic, forward-thinking, transparent, and empirical ("The Angular Renaissance").
  * Combine excitement for modern web capabilities (Signals, Zone-less, Hydration, WebAssembly, GenAI) with engineering rigor and benchmark data (e.g. build speed multipliers, bundle size reductions).
  * Be transparent about trade-offs, developer friction, and early Developer Preview API design iterations.
* **Style**: Clear, developer-centric, and empathetic. Emphasize how new features reduce documentation lookups, eliminate boilerplate, and improve Core Web Vitals.

---

## 2. Interactive Media & Documentation Standards

* **Executive Summary Bullets**: Release posts must begin immediately under the title banner with a bold summary list of key features & performance gains (*"In vX.Y we’re happy to introduce: ... "*).
* **Interactive WebContainers & StackBlitz**: Include animated GIFs or embeds of interactive tutorials on `angular.dev` powered by WebContainers.

---

## 3. Specialized Angular Blueprints

### A. Major Version Releases
*(Extends Universal Blueprint 1)*
* Must begin with an executive summary bullet list under the title banner. Include dedicated subsections for Signals, Hydration, Control Flow, Deferrable Views (`@defer`), and `angular.dev` tooling.

### B. Architectural RFCs & Developer Preview Iterations
1. **The Motivation & Background**: Why is an existing pattern problematic or complex? What developer friction was observed in UX research studies?
2. **Design Principles & Trade-offs**: Core principles behind the proposed API (e.g., disappearing build-time syntax, type narrowing, explicit reactivity).
3. **Syntax Mechanics**: Clean, tagged TypeScript / Template code snippets demonstrating the proposed syntax.
4. **Community Feedback Callout**: Explicit call to action requesting feedback on GitHub RFC issues or survey forms.

### C. AI & Web Modernization
1. **Visionary Hook**: How AI agents, local models, or modern browser APIs are shifting web development.
2. **Architecture & Project Setup**: Integrating Angular with Firebase Genkit, Gemini SDK, Vitest, or WebXR.
3. **Code Walkthrough**: Component logic showing Signals (`signal()`, `computed()`, `httpResource()`) paired with reactive AI data flows.
4. **Security & Moderation**: Best practices for handling prompt security, API keys, and client-side safety.
