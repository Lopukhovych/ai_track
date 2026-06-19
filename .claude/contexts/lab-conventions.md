# Lab Exercise Conventions

Imported by CLAUDE.md. Defines the standard format for all lab notebooks.

## Notebook Structure (mandatory order)

1. **Title cell** — `# Week N: Title` + lab companion link + bullet list of "In this lab you will:"
2. **Setup cell** — imports, `load_dotenv()`, client init, `print("✓ Ready!")`
3. **Section cells** — `## 1. Topic Name` markdown + code implementing the concept
4. **Exercise cells** — `## N. Exercise: Name` + code with `# TODO` + `<details>` hint + `<details>` solution
5. **Summary cell** — `## Summary` with `✅` bullets of what was learned + "Next:" link

## Exercise Cell Format

````markdown
## 3. Exercise: Build a Semantic Search Engine

```python
# TODO: Implement semantic_search(query, documents, top_k=3)
# 1. Get embedding for the query
# 2. Get embeddings for all documents
# 3. Calculate cosine similarity for each doc
# 4. Return top_k results sorted by similarity
def semantic_search(query: str, documents: list, top_k: int = 3) -> list:
    pass
```

<details>
<summary>💡 <b>Hint</b> (click to expand)</summary>

Reuse `get_embedding()` from the setup cell.
Cosine similarity: `np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))`

</details>

<details>
<summary>✅ <b>Solution</b> (click to expand)</summary>

```python
def semantic_search(query, documents, top_k=3):
    query_emb = get_embedding(query)
    scored = [(doc, cosine_similarity(query_emb, get_embedding(doc))) for doc in documents]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]
```

</details>
````

## Rules for Claude when working on labs

- Never remove `<details>` blocks — they are the learning scaffold
- Never clear cell outputs — they show expected results
- When adding exercises, follow the exact format above
- Exercise difficulty should progress within each notebook (easy → medium → hard)
- All code in exercises must be runnable standalone (import what they need)
