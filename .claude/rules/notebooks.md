---
paths:
  - "labs/**/*.ipynb"
---

# Lab Notebook Rules

## Cell structure
- Run cells top-to-bottom — later cells import objects from earlier ones
- Each notebook must have a setup cell at the top that loads `.env` and imports
- `# TODO` comments go inside code cells, never in markdown cells

## Content integrity
- Never remove or reorganize `<details>` hint/solution blocks — they are intentional
- Never clear saved outputs before committing — outputs show the expected results
- If a cell produces an error in a clean run, fix the cell before committing

## Environment loading
- All notebooks load `.env` from the repo root (parent of `labs/`):
  ```python
  import os
  from dotenv import load_dotenv
  load_dotenv(os.path.join(os.path.dirname(os.getcwd()), ".env"))
  ```
- Default model throughout the course: `gpt-4o-mini` unless the exercise specifies otherwise

## API calls
- Use `client = OpenAI()` — the key comes from the environment, not hardcoded
- Add `print("✓ Ready!")` at the end of setup cells to confirm successful init

## Formatting
- Markdown cells: use H2 (`##`) for sections, H3 (`###`) for sub-sections
- Code cells: keep under 50 lines — split long logic into multiple cells
- Always include a "Summary" markdown cell at the end of each notebook
