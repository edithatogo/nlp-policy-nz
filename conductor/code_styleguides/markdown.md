# Markdown Style Guide (nlp-policy-nz)

This document establishes the style standards for all markdown files, documentation, and report generation in the `nlp-policy-nz` project.

---

## 1. Document Structure & Headings

- **Single H1**: Each document must have exactly one H1 header (`# Title`) at the top.
- **Hierarchical Headings**: Headings must proceed in order (H1 -> H2 -> H3). Do not skip heading levels (e.g., do not jump from H1 directly to H3).
- **Capitalization**: Use Title Case or Sentence Case consistently. Prefer Sentence Case for general headers (e.g., `## Core features and architecture`).

---

## 2. Text Formatting

- **Bold & Italics**: Use `**bold**` for highlighting critical key terms and `*italics*` for code variables or foreign-language terms (such as Te Reo Māori concepts like *tikanga*).
- **Code Blocks**: Always specify the language name for syntax highlighting in fenced code blocks (e.g., ````markdown \n ```python \n ... \n ``` \n ````).
- **Lists**:
  - Prefer bulleted lists for unordered groups.
  - Use numbered lists for step-by-step instructions.

---

## 3. Link and Path Standards

- **Relative Paths**: Always use relative paths when linking to other files in the repository (e.g., `[Tech Stack](../tech-stack.md)`).
- **No Absolute Paths**: Do not hardcode absolute directories or URLs mapping to local developer filesystems.
