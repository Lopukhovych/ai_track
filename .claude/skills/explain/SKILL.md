---
name: explain
description: Explain code, a concept, or a file with visual diagrams and analogies. Use when the user asks "how does this work", "explain", or "walk me through".
argument-hint: "[file-or-concept]"
user-invocable: true
---

Explain `$ARGUMENTS` clearly using the following structure:

## 1. One-line summary
What this does in plain English (no jargon).

## 2. Analogy
Compare it to something from everyday life that the reader already understands.

## 3. Visual diagram
Draw an ASCII diagram showing the flow, structure, or data transformation:

```
Input → [Step A] → [Step B] → Output
              ↓
          [Side effect]
```

## 4. Step-by-step walkthrough
Go through the code/concept line by line (or concept by concept). For each non-obvious part, explain *why* it's done that way, not just *what* it does.

## 5. The one gotcha
What's the most common mistake or misconception people have with this? Give a concrete before/after example.

## 6. When to use it vs. alternatives
In 2-3 bullet points: what situation is this designed for, and what would you use instead in other situations?

---

If `$ARGUMENTS` is a file path, read it first. If it's a concept without a file, explain it in the context of the ai_track curriculum (weeks, use cases, practical examples from the labs).
