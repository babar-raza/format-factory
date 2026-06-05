# Healing Plan: Repo-Sharing Plan Review Package Wiring
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Created: 2026-06-04

## Context

The FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001 sprint produced all
22 planning artifacts, but the sprint evidence declaration was missing the `run_id` field
required by `build_declaration_review_package.py`. As a result:

1. The review package ZIP was placed at `.local/supervisor/reviews/unknown/` instead of
   `.local/supervisor/reviews/repo-sharing-plan/`.
2. `validation-results.md` row 20 shows PENDING for `review-package-proof.md` even
   though that file was subsequently created.

## Gap Table

| Gap ID | Description | Taskcard |
|--------|-------------|----------|
| GAP-SR-01 | `run_id` field missing from evidence-declaration.yaml → ZIP in `reviews/unknown/` | SR-01 |
| GAP-SR-02 | `validation-results.md` row 20 shows PENDING after review-package-proof.md was created | SR-02 |

---

## Taskcard SR-01: Add run_id + Rebuild Review Package

**Status:** Done
**Gap linkage:** GAP-SR-01
**Role:** Senior engineer — drop-in fix, production-ready

### Scope
- **Fix:** Add `run_id: repo-sharing-plan` to `.local/evidences/repo-sharing-plan/evidence-declaration.yaml`
- **Allowed paths:**
  - `.local/evidences/repo-sharing-plan/evidence-declaration.yaml`
  - `.local/supervisor/reviews/repo-sharing-plan/` (new ZIP output)
  - `reports/repo-sharing-plan/review-package-proof.md`
- **Forbidden paths:** No product source changes; no .gitignore changes; no commits

### Acceptance Checks
- [ ] `evidence-declaration.yaml` contains `run_id: repo-sharing-plan`
- [ ] `build_declaration_review_package.py` exits with code 0 or 2 (not 9)
- [ ] ZIP is at `.local/supervisor/reviews/repo-sharing-plan/declaration-review-package.zip`
- [ ] ZIP is NOT at `.local/supervisor/reviews/unknown/declaration-review-package.zip` (old one can remain)
- [ ] `review-package-proof.md` updated with correct path and new SHA-256
- [ ] Absolute path reported in `review-package-proof.md` matches `C:\Users\prora\...\reviews\repo-sharing-plan\...`

### Deliverables
- Updated `evidence-declaration.yaml` (run_id field added)
- New ZIP at `reviews/repo-sharing-plan/`
- Updated `review-package-proof.md` (correct path + SHA)

### Hard Rules
- Do NOT modify any product source files
- Do NOT commit
- Do NOT push
- Do NOT delete `.local/supervisor/reviews/unknown/` — leave it

### Review Dimensions — What 5/5 Means
- **Correctness:** ZIP is at expected path; `run_id` matches directory name
- **Wiring:** `build_declaration_review_package.py` reads `run_id` correctly
- **Observability:** `review-package-proof.md` has correct absolute path and SHA

### Now (Runbook)
```bash
# 1. Add run_id to declaration
# Edit .local/evidences/repo-sharing-plan/evidence-declaration.yaml
# Add line: run_id: "repo-sharing-plan"

# 2. Rebuild
cd <repo_root>
.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/repo-sharing-plan/evidence-declaration.yaml

# 3. Verify ZIP location
ls .local/supervisor/reviews/repo-sharing-plan/
# Must show: declaration-review-package.zip

# 4. Read new SHA from output or compute
# 5. Update review-package-proof.md with new path + SHA
```

---

## Taskcard SR-02: Update validation-results.md Row 20

**Status:** Done
**Gap linkage:** GAP-SR-02
**Role:** Senior engineer — drop-in fix, production-ready

### Scope
- **Fix:** Edit `reports/repo-sharing-plan/validation-results.md` to mark row 20
  (`review-package-proof.md`) as PASS
- **Also fix:** Update file counts from 19/22 to 22/22 and update PENDING count
- **Allowed paths:** `reports/repo-sharing-plan/validation-results.md` only
- **Forbidden paths:** No other files

### Acceptance Checks
- [ ] Row 20 in validation-results.md shows `review-package-proof.md | EXISTS | EXISTS | PASS`
- [ ] Rows 21-22 also correctly show PASS for evidence-declaration.yaml and evidence-manifest.yaml
- [ ] File count shows `22/22` not `19/22`
- [ ] PENDING count shows `0` not `3`
- [ ] No other rows changed

### Deliverables
- Updated `validation-results.md` with correct PASS status for all 22 files

### Hard Rules
- Do NOT modify any other section of the file
- Do NOT change the verdict

### Now (Runbook)
```bash
# Edit reports/repo-sharing-plan/validation-results.md
# Change row 20: PENDING → PASS
# Change rows 21-22: PENDING → PASS
# Update "Files written: 19/22" → "22/22"
# Update "Pending: 3" → "Pending: 0"
```
