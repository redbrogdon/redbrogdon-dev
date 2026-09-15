# Go Blog Post Reference & Guidance

This reference file contains product-specific guidelines, tone DNA, and specialized blueprints for articles intended for the official **Go Blog** (`go.dev/blog`).

---

## 1. Product Tone Persona ("The Pragmatic Language Architect")

* **Tone DNA**: Pragmatic, understated, clear, and engineering-focused.
  * Avoid marketing buzzwords, hype, or overly sensational language. Go's core value is **simplicity, readability, and software engineering trade-offs** (e.g. build speed vs execution performance, complexity vs readability, memory allocations).
  * Emphasize the **Go 1 Compatibility Promise**—new features must respect backward compatibility and code stability.
* **Style**: Concise, direct, and instructional. Use short, punchy paragraphs (1–3 sentences) and Socratic questions as headers (*"Why generics?"*, *"How does loop variable scoping work?"*).

---

## 2. Benchmark & Code Standards

* **Socratic Section Headers**: Use questions as headers for deep dives (`## Why Swiss Tables?`, `## When to use generics`).
* **Compilable Runnable Snippets**: Code blocks must be compilable, idiomatic Go examples (prefer including `package main` and `func main()` with standard `if err != nil` error handling).
* **Benchmark Metrics**: Include precise benchmark metrics when discussing performance or compiler optimizations (CPU time, allocations per op `allocs/op`).

---

## 3. Specialized Go Blueprints

### A. Major Language Releases
*(Extends Universal Blueprint 1)*
* Include subsections for Language Changes (e.g., loop variable scoping, range over integers), Tool Improvements (`go telemetry`, `govulncheck`, `go work`), Standard Library Additions (`log/slog`, `unique`, `synctest`), and Runtime/Compiler Performance (PGO, map implementations).

### B. Language Proposals & Design Rationales
*(Extends Universal Blueprint 2)*
* Structure around a core Socratic question (`## Why Generics?`), evaluate why previous workarounds (`interface{}`, reflection) fell short, provide compilable ````go```` snippets, detail usage trade-offs, and link to GitHub proposal discussions (`golang/go#...`).

### C. Runtime Mechanics, Concurrency & Memory
1. **Concept Introduction**: Distinguishing core concepts (concurrency vs parallelism, slices vs arrays, Swiss Tables vs legacy maps).
2. **Under-the-Hood Mechanics**: Memory layout, stack growth, channel scheduling, or lock-free data structures.
3. **Code & Benchmark Walkthrough**: Idiomatic concurrency patterns (`select`, channels, `sync.WaitGroup`, `testing/synctest`) with precise benchmark metrics (`allocs/op`).
4. **Common Pitfalls & Fixes**: Anti-patterns alongside corrected idiomatic Go code.

### D. Toolchain, Modules & Security Infrastructure
1. **Background & Security Context**: The problem space (supply chain attacks, vulnerability management, telemetry, module versioning).
2. **Tool Architecture & Usage**: How the tool operates (`govulncheck`, `go vet`, `gopls`) with CLI terminal snippets (`$ go vulncheck ./...`).
3. **Integration Guidelines**: CI/CD integration steps (GitHub Actions) and best practices.
