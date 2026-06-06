# Final Single-Go Prompt: .gitignore Fix + Remote Refresh
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04
# Task: TC-SHARE-010

## Purpose

This file contains a ready-to-send prompt that, when given to Claude Code in a new session
with explicit push authorization, will execute the complete remote refresh in a single run.

Copy the block between the START and END markers and paste it as a session prompt.

---

## Prerequisites Before Sending This Prompt

- [ ] User has explicitly authorized: commit + push to `origin main`
- [ ] This file (`final-single-go-gitignore-remote-refresh-prompt.md`) has been reviewed
- [ ] `reports/repo-sharing-plan/remote-refresh-execution-plan.md` has been reviewed
- [ ] `reports/repo-sharing-plan/gitignore-proposed.patch` has been reviewed
- [ ] No other work is in progress on the `main` branch

---

## PROMPT START
---

You are authorized to execute the format-factory remote refresh. This is a single-session
execution with full commit and push authorization.

**Authorization:** `authorized_to_push: true`

**Remote:** `https://github.com/babar-raza/format-factory.git`
**Branch:** `main`

**What to do — execute in order, stopping on any hard-stop failure:**

### Step 1: Confirm baseline
```bash
git branch --show-current   # must be: main
git remote -v               # must show: babar-raza/format-factory.git
git log --oneline -3        # review recent commits
```

### Step 2: Fix .gitignore (CRITICAL)
- Open `.gitignore`
- Delete BOTH lines 173 and 174 (both contain exactly `/reports`)
- Append to the end of `.gitignore`:
  ```
  # Temporary scratch directories
  tmp/
  temp/
  output*/

  # External orchestration tool runtime state
  .claude-flow/
  .claude-flow-state/
  ```
- Validate: `git check-ignore -v reports/supervisor/` must return nothing
- Validate: `git check-ignore -v src/ tests/ docs/ tools/ memory/` must all return nothing

### Step 3: Sanitize product-gap-selection.md
- Edit `reports/supervisor/product-gap-selection.md` line 1
- Replace any occurrence of `C:/Users/prora/OneDrive/Documents/GitHub/format-factory/` with `./`
- Verify: `grep -i "prora" reports/supervisor/product-gap-selection.md` must return empty

### Step 4: Stage all changes
```bash
git add .gitignore
git add reports/supervisor/product-gap-selection.md
git add src/net/fods/FodsDocument.cs
git add src/net/fodt/FodtDocument.cs
git add src/net/netpbm/Model/NetpbmImage.cs
git add src/python/sylk/sylk_parser.py
git add tests/net/fods/ tests/net/fodt/ tests/net/netpbm/
git add tests/python/ tests/supervisor/
git add examples/ docs/governance/ docs/prompt-templates/
git add tools/supervisor/
git add .supervisor/ .claude/commands/
git add memory/ plans/ state/
git add product-capability-matrix/
git add reports/supervisor/ reports/repo-sharing-plan/
git add reports/r90/product-code-change-ledger.json
```

### Step 5: Security check — HARD STOP if any return output
```bash
git diff --cached | grep -i "prora"
git diff --cached | grep -i "api_key\|password\|token\|secret"
git diff --cached --name-only | grep "^\.env"
git diff --cached --name-only | grep "^\.local/"
```

### Step 6: Commit
```bash
git commit -m "$(cat <<'EOF'
feat(r94-r113): tests, examples, docs, supervisor tools, .gitignore repair

- Fix .gitignore: remove accidental /reports bug (lines 173-174); add tmp/temp patterns
- 276 new .NET and Python tests (FODS, FODT, Netpbm, PPM, PBM, PGM, SYLK, DIF, ZST)
- 17 new usage examples (Python + .NET)
- 42 new docs (governance, prompt-templates)
- 32 new supervisor tools and validators
- 6 new .claude/commands
- FODS/FODT/Netpbm .NET source updates (R94-R113)
- SYLK Python parser update
- Capability matrix and supervisor reports updated (R94-R113)
- Sanitize product-gap-selection.md (remove local path)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

### Step 7: Verify commit
```bash
git status      # must be: nothing to commit
git log --oneline -3
git diff --cached   # must be empty
```

### Step 8: Push
```bash
git push origin main
```

### Step 9: Confirm remote
```bash
git status   # must be: up to date with origin/main
git log --oneline -3
```

**Hard stops:**
- ANY security check output in Step 5 → STOP, do not commit, report finding
- `git check-ignore -v src/` returns anything → STOP, .gitignore patch broke something
- Pre-commit hook failure → STOP, investigate, do NOT use --no-verify

---
## PROMPT END

---

## Notes for Executor

- This prompt assumes the planning outputs in `reports/repo-sharing-plan/` already exist
- The `reports/repo-sharing-plan/` directory will be staged in Step 4 — it contains
  the complete planning artifacts from this sprint
- After the push, `git status` should show no modified/untracked files
- Total expected tracked files after refresh: ~4136 (was 3761 + ~375 new)
