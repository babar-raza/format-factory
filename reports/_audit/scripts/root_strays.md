# Root Strays Audit — format-factory

Audit date: 2026-06-23

Lists all script-like files found at repo root or outside canonical script folders
(`tools/`, `scripts/`, `.github/workflows/`, `prototypes/`, `packaging/`, `drivers/`).

---

## Repo Root

**No stray scripts found at repo root.** Zero `.py`, `.sh`, `.ps1`, `.cmd`, `.bat` files.
No `Makefile`, `Taskfile`, `justfile`, or `invoke` configuration detected.

---

## Stray Scripts Outside Canonical Folders

| Path | Why It Is a Script | Evidence of Usage | Proposed Destination | Notes |
|------|-------------------|-------------------|---------------------|-------|
| `examples/dogfood_csv_export.py` | Executable Python (`python examples/dogfood_csv_export.py` in docstring) | Docstring says "Runnable"; part of dogfood proof workflow | **KEEP IN PLACE** — `examples/` is a legitimate location for usage examples | Not a stray; correctly placed |
| `reports/repo-sharing-plan/untrack-commands-plan.sh` | Has `#!/bin/bash` shebang | NOT EXECUTED: Line 43-45 has `echo` + `exit 0`; describes planned git operations as comments only | **archive or delete** — it's a plan document disguised as a shell script | No operational effect; misleading `.sh` extension. Could be `.md` instead. |

---

## .local/ One-Off Scripts (47 files — gitignored, NOT committed)

All 47 `.local/*.py` files are one-off development/debugging scripts. They are:
- Gitignored (not committed to the repository)
- Historical (all have completed their purpose)
- Not referenced by any active workflow

**Classification:**
- 10 `create_*_metadata.py` — Sprint metadata generators (historical)
- 8 `fix_*` — Ledger/evidence repair scripts (historical)
- 7 `tmp_*` — Temporary data scripts (historical)
- 8 `gen_*` / `build_*` — Artifact generators (historical)
- 5 `r51-*` / `*_workflow_test.py` — Smoke tests (historical)
- 5 `verify_*` / `run_*` / `add_*` — Miscellaneous one-offs (historical)
- 4 other — Remaining one-offs

**Proposed action:** No action needed — these are gitignored and do not appear in the committed repo. They are development debris that could be bulk-deleted if disk space matters.

---

## Build Artifact Contamination (NOT scripts — build debris)

Nested `build/lib/` directories were found containing Python files that are NOT scripts
but are build artifacts from `python -m build` or `pip install -e`:

```
build/lib/python/fods/build/lib/fods/build/lib/fods/build/lib/fods/build/lib/fods/exceptions.py
build/lib/python/fodt/build/lib/fodt/build/lib/fodt/exceptions.py
src/python/fods/build/lib/fods/build/lib/fods/build/lib/fods/build/lib/fods/exceptions.py
src/python/fodt/build/lib/fodt/exceptions.py
```

**These are NOT stray scripts** — they are deeply nested `build/` artifacts from repeated
editable installs. They are gitignored. They indicate that `build/` cleanup (`rm -rf build/`)
has not been run recently.

**Proposed action:** Run `rm -rf build/` and `rm -rf src/python/*/build/` to clean up
nested build artifacts. Add explicit `build/` entries to `.gitignore` if not already present.

---

## Summary

| Category | Count | Action |
|----------|-------|--------|
| Repo root strays | 0 | None needed |
| Stray scripts outside canonical folders | 1 | `untrack-commands-plan.sh` — rename to `.md` or archive |
| Legitimate non-canonical scripts | 1 | `examples/dogfood_csv_export.py` — keep in place |
| .local/ one-offs (gitignored) | 47 | Optional bulk cleanup |
| Build artifact contamination | ~15 nested files | Clean up `build/` directories |
