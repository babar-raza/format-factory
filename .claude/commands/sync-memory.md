# /sync-memory

Compare `/memory` files against `plans/master-plan.md` and current repo state.
Detect contradictions and produce `reports/supervisor/memory-sync-report.md`.

**Memory is context. `plans/master-plan.md` is authority.**

## What This Command Does

1. **Enumerate memory files**: Read all files in `memory/` directory
2. **Extract key claims**: Phase status, phase 0 acceptance, allowed/forbidden actions,
   decision register state, gap register state, run history
3. **Compare against master-plan**: For each key claim, find the corresponding section
   in `plans/master-plan.md` and verify agreement
4. **Detect contradictions**: Log any divergences with: file, memory claim, master-plan fact, severity
5. **Secrets check**: Confirm no secrets, raw prompts/responses, or copyrighted excerpts
   appear in `/memory` files
6. **Produce report**: Write `reports/supervisor/memory-sync-report.md` with:
   - Comparison date
   - Files compared
   - Contradictions list (or "No contradictions detected")
   - Secrets check result
   - Recommended resolution for each contradiction

## Output

- `reports/supervisor/memory-sync-report.md` — Full sync report
- Log: "Memory sync complete: N files compared, M contradictions found"

## Constraints

- **Never modify** any repo file based on memory content alone
- **Never treat** memory as more authoritative than `plans/master-plan.md`
- **Never add** secrets, raw LLM prompts/responses, or copyrighted spec text to memory
- If contradictions found: log as gap entries in `plans/master-plan.md` Section 27

## Procedure

```
1. Read AGENTS.md Section U (Memory Usage and Maintenance)
2. Read memory/00-index.md for the memory structure
3. Read each memory/*.md file; note key claims about phase, decisions, gaps
4. Read plans/master-plan.md current state
5. Compare claims: for each memory claim, find master-plan ground truth
6. For contradictions: record [file, claim, master-plan-fact, severity: low/medium/high]
7. Run secrets check: grep for patterns matching passwords, API keys, PROF_*_KEY, raw spec quotes
8. Write reports/supervisor/memory-sync-report.md
9. If contradictions with severity >= medium: add gap entry to plans/master-plan.md
```

## Usage

```
/sync-memory
```

No arguments. Always compares full memory against current master-plan.

## Authority

Memory (`memory/*.md`) is **advisory context** preserved from prior conversation history.
It helps agents understand project evolution but has NO authority over:
- `plans/master-plan.md` (project authority)
- `registry/format-registry.yaml` (format authority)
- `AGENTS.md` (governance authority)
- `CLAUDE.md` (session instruction authority)

When memory contradicts any authority document, the authority document wins.

---
*TC-0008 | Phase 1+ | Created 2026-06-18*
