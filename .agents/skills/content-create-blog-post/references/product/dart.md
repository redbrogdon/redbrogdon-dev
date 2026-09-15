# Dart Blog Post Reference & Guidance

This reference file contains product-specific guidelines, tone DNA, and specialized blueprints for articles intended for the official **Dart Blog** (`dart.dev/blog`).

---

## 1. Product Tone Persona ("Language Architect's Journal")

* **Tone DNA**: Precise, logical, design-document style, and technical. Focus on syntax design rationales, compiler edge-cases, type soundness, and benchmark metrics.
* **Style**: Clear engineering rigor. Explain the "why" behind syntax choices, language trade-offs, and compiler performance impacts.

---

## 2. Code & Interactive Playground Rules

* **Progressive Syntax Disclosure**: Introduce language syntax progressively (shell signature $\rightarrow$ field definitions $\rightarrow$ pattern matching / implementation logic).
* **Interactive DartPad Callouts**: Whenever practical, include callouts or links to interactive [DartPad](https://dartpad.dev) snippets so readers can execute the code live in their browser.

---

## 3. Specialized Dart Blueprints

### A. Language Features & Syntax Design
*(Extends Universal Blueprint 2)*
* Structure around core design choices (e.g. sound types, non-nullable by default, structural equality) and include interactive DartPad links.

### B. SDK & Platform Releases
*(Extends Universal Blueprint 1)*
* Include dedicated subsections for Language & Syntax updates, Tooling & Linter rules (`dart analyze`, `dart fix`), and Native Interop / Web Compilation (**FFI, WebAssembly / Wasm, C interop**).
