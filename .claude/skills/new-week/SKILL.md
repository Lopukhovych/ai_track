---
name: new-week
description: Scaffold a new curriculum week — creates agenda markdown and lab notebook following course conventions. Use when adding a new week to the curriculum.
argument-hint: "<week-number> <topic-name>"
disable-model-invocation: true
allowed-tools: Read, Write, Bash(ls *), Bash(cp *)
---

Scaffold a new curriculum week for the ai_track course.

**Arguments:** `$ARGUMENTS` should be `<week-number> <topic-name>`
- Example: `/new-week 05 vector-databases`
- Week number: $ARGUMENTS[0]
- Topic name: $ARGUMENTS[1]

## Steps

1. Verify week number is not already taken:
   ```bash
   ls agenda/week_$ARGUMENTS[0]*.md labs/week_$ARGUMENTS[0]*.ipynb 2>/dev/null
   ```

2. Read an existing week for reference format:
   - Read `agenda/week_01.md` for agenda structure
   - Read the summary cell of `labs/week_03_embeddings.ipynb` for notebook structure

3. Create `agenda/week_$ARGUMENTS[0]_$ARGUMENTS[1].md`:
   - Follow the exact structure of existing agenda files
   - Sections: Overview, Learning Objectives, Model Options table, 4-5 content parts, Lab Preview, Further Reading
   - Duration: 6-8 hours
   - Connect to previous and next week

4. Create `labs/week_$ARGUMENTS[0]_$ARGUMENTS[1].ipynb`:
   - Valid Jupyter notebook JSON (nbformat 4, nbformat_minor 5)
   - Setup cell with load_dotenv, client init, print("✓ Ready!")
   - 3-5 concept sections with working code examples
   - 2-3 exercises with `# TODO`, `<details>` hint, `<details>` solution
   - Summary cell with ✅ bullets and Next: link

5. Report what was created with file sizes.

**Important:** Follow `.claude/contexts/lab-conventions.md` for exact notebook format.
