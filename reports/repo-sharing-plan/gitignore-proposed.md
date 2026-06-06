# Proposed .gitignore Changes
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04

## Summary

Two types of changes are proposed:
1. **REMOVAL** (CRITICAL): Remove both `/reports` lines (173-174) — this is the highest-priority fix
2. **ADDITION** (LOW priority): Add a small set of patterns not yet covered

---

## Change 1 — REMOVAL of /reports (CRITICAL BUG FIX)

### Current state (lines 173-174 in .gitignore)

```
173: /reports
174: /reports
```

### Why this must be removed

The pattern `/reports` is anchored to the repository root and matches the entire `reports/`
directory. This means:
- Any NEW file added to `reports/` cannot be tracked without `git add -f` (force)
- `reports/repo-sharing-plan/` (this sprint's output) is blocked from being tracked
- Future sprint reports in `reports/supervisor/` cannot be added normally
- The bug was CONFIRMED by: `git check-ignore -v reports/repo-sharing-plan/` → `.gitignore:174:/reports`

### Why existing tracked files are unaffected

Once a file is tracked by git, `.gitignore` has no effect. The ~1867 tracked files
in `reports/r*/` and `reports/supervisor/` continue to show as Modified (M) correctly.
Only NEW additions to `reports/` are blocked.

### The fix

Remove BOTH `/reports` lines (173 and 174). They have no explanatory comment and were
accidentally appended at the end of the Ruflo config section (lines 163-174).

---

## Change 2 — ADDITIONS (low priority)

### Patterns already present (confirmed — no addition needed)

The following patterns were initially believed to be missing but are already in `.gitignore`:

| Pattern | Line | Section |
|---------|------|---------|
| `dist/` | 34 | Python |
| `build/` | 35 | Python |
| `.coverage` | 39 | Python |
| `.coverage.*` | 40 | Python |
| `coverage.xml` | 41 | Python |
| `*.snupkg` | 57 | .NET |
| `*.nupkg` | 56 | .NET |
| `*.log` | 92 | Editor/IDE |
| `*.tmp` | 93 | Editor/IDE |

### Genuine gaps (low priority — no leaks observed yet)

| Pattern | Priority | Reason |
|---------|----------|--------|
| `tmp/` | LOW | Temp scratch directories not covered by `.local/` |
| `temp/` | LOW | Temp scratch directories |
| `output*/` | LOW | Generated output directories (e.g., `output-20260604/`) |
| `.claude-flow/` | LOW | claude-flow runtime state directory (if created) |
| `.claude-flow-state/` | LOW | claude-flow state directory |

These are low priority because no such directories exist in the current repo and
all evidence/package artifacts are correctly in `.local/` (already gitignored).

---

## Proposed Patch (see gitignore-proposed.patch)

The patch file contains:
1. **Deletion** of lines 173-174 (`/reports` x2)
2. **Addition** of the low-priority patterns at the end of the file

The patch file is ready to apply with:
```bash
patch .gitignore < reports/repo-sharing-plan/gitignore-proposed.patch
```

Or manually:
1. Open `.gitignore`
2. Delete lines 173-174 (both `/reports`)
3. Append the new patterns block to the end

---

## Validation After Applying

```bash
# Verify reports/ is no longer ignored
git check-ignore -v reports/supervisor/
# Must return nothing (exit code 1)

git check-ignore -v reports/repo-sharing-plan/
# Must return nothing (exit code 1)

# Verify core product dirs are still not ignored
git check-ignore -v src/ tests/ docs/ tools/ memory/ plans/
# Must all return nothing

# Verify tmp/ is now ignored
git check-ignore -v tmp/
# Must return: .gitignore:<line>:tmp/    tmp/

# Verify .local/ still covered
git check-ignore -v .local/
# Must return: .gitignore:<line>:.local/    .local/
```
