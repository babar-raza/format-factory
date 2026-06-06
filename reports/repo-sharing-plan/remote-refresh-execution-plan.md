# Remote Refresh Execution Plan
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04
# Task: TC-SHARE-007

## HARD STOPS — Never Proceed Without

- [ ] Explicit user authorization: `authorized_to_push: true`
- [ ] `git check-ignore -v src/` returns nothing (core dirs not accidentally ignored)
- [ ] `git diff --cached | grep -i "prora"` returns nothing
- [ ] `git diff --cached | grep -i "api_key\|password\|token\|secret"` returns nothing

---

## Phase 1 — Baseline Confirmation

```bash
# 1.1 Confirm branch and remote
git branch --show-current
# Expected: main

git remote -v
# Expected: origin  https://github.com/babar-raza/format-factory.git (fetch/push)

# 1.2 Review current state
git status --short | head -30
# Review for unexpected changes

# 1.3 Check latest commit
git log --oneline -3
# Expected: 3a86a05 feat(r93): ...
```

---

## Phase 2 — Fix .gitignore (CRITICAL — must be first)

```bash
# 2.1 Open .gitignore and delete lines 173 and 174 (both contain /reports)
# Method A: Manual edit in text editor
#   - Open .gitignore
#   - Go to lines 173-174
#   - Delete both /reports lines
#   - Save

# Method B: Using sed (verify line numbers first)
grep -n "/reports" .gitignore
# Expected output: 173:/reports and 174:/reports

# Delete lines 173 and 174
sed -i '173,174d' .gitignore

# 2.2 Optionally add proposed new patterns (low priority)
cat >> .gitignore << 'EOF'

# Temporary scratch directories
tmp/
temp/
output*/

# External orchestration tool runtime state
.claude-flow/
.claude-flow-state/
EOF

# 2.3 Validate the fix
git check-ignore -v reports/supervisor/
# Must return nothing (exit code 1)

git check-ignore -v reports/repo-sharing-plan/
# Must return nothing (exit code 1)

git check-ignore -v src/ tests/ docs/ tools/ memory/
# Must all return nothing

git check-ignore -v .local/
# Must return: .gitignore:<line>:.local/    .local/

# 2.4 Stage .gitignore
git add .gitignore
```

---

## Phase 3 — Sanitize Sensitive Content

```bash
# 3.1 Fix absolute path in product-gap-selection.md
head -3 reports/supervisor/product-gap-selection.md
# Look for C:/Users/prora/... on line 1

# Replace the absolute path
sed -i 's|C:/Users/prora/OneDrive/Documents/GitHub/format-factory/|./|g' \
  reports/supervisor/product-gap-selection.md

# 3.2 Verify sanitization
head -3 reports/supervisor/product-gap-selection.md | grep -i "prora"
# Must return empty

# 3.3 Stage the sanitized file
git add reports/supervisor/product-gap-selection.md
```

---

## Phase 4 — Stage All Legitimate Changes

```bash
# 4.1 Stage product source changes
git add src/net/fods/FodsDocument.cs
git add src/net/fodt/FodtDocument.cs
git add src/net/netpbm/Model/NetpbmImage.cs
git add src/python/sylk/sylk_parser.py

# 4.2 Stage new tests (all untracked tests are safe)
git add tests/net/fods/
git add tests/net/fodt/
git add tests/net/netpbm/
git add tests/python/

# Wait for tests/supervisor/ — review first
git add tests/supervisor/

# 4.3 Stage new examples
git add examples/

# 4.4 Stage new docs
git add docs/governance/
git add docs/prompt-templates/

# 4.5 Stage supervisor tools + config
git add tools/supervisor/
git add .supervisor/

# 4.6 Stage Claude commands
git add .claude/commands/

# 4.7 Stage memory + plans + state
git add memory/
git add plans/
git add state/

# 4.8 Stage supervisor reports (now accessible after .gitignore fix)
git add reports/supervisor/
git add reports/repo-sharing-plan/

# 4.9 Stage capability matrix updates
git add product-capability-matrix/

# 4.10 Stage sprint ledger update
git add reports/r90/product-code-change-ledger.json
```

---

## Phase 5 — Final Validation Before Commit

```bash
# 5.1 Review what will be committed
git status --short
git diff --cached --stat

# 5.2 Security check — MUST return empty
git diff --cached | grep -i "prora"
git diff --cached | grep -i "api_key\|password\|token\|secret"
git diff --cached --name-only | grep "^\.env"
git diff --cached --name-only | grep "^\.local/"

# If any of the above return results — STOP and investigate

# 5.3 Spot-check key files
git diff --cached src/net/fods/FodsDocument.cs | head -50
git diff --cached reports/supervisor/session-resume.md | head -20
```

---

## Phase 6 — Create Commit

**Requires explicit user authorization. Do NOT auto-execute.**

```bash
# Proposed commit message:
git commit -m "$(cat <<'EOF'
feat(r94-r113): add tests, examples, docs, supervisor tools, capability updates

- 276 new .NET and Python tests (FODS, FODT, Netpbm, PPM, PBM, PGM, SYLK, DIF, ZST)
- 17 new examples (Python + .NET)
- 42 new docs (governance, prompt-templates)
- 32 new supervisor tools and validators
- 6 new .claude/commands
- .gitignore: remove accidental /reports bug (lines 173-174); add tmp/temp/output*/
- FODS/FODT/Netpbm .NET source updates from R94-R113 sprints
- SYLK Python parser update
- Capability matrix and supervisor reports updated

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase 7 — Push to Remote

**Requires SEPARATE explicit user authorization. Hard stop here.**

```bash
# 7.1 Final state check
git status
git log --oneline -3

# 7.2 Push (ONLY with explicit authorization)
git push origin main

# 7.3 Verify
git status
# Expected: nothing to commit, working tree clean
```

---

## Rollback Procedures

| Step | Rollback Command |
|------|-----------------|
| .gitignore changes | `git checkout .gitignore` |
| product-gap-selection.md sanitize | `git checkout reports/supervisor/product-gap-selection.md` |
| Staged but not committed | `git reset HEAD` (unstage all) |
| Committed but not pushed | `git reset --soft HEAD~1` |
| Pushed (emergency) | Contact Babar Raza — force push requires authorization |

---

## Expected Final State

After successful execution:
- `git status` → `nothing to commit, working tree clean`
- `git log --oneline -1` → new commit with feat(r94-r113) message
- Remote at `https://github.com/babar-raza/format-factory.git` is up to date
- Total tracked files increases from 3761 to ~4136 (+ 375 previously untracked)
- `.gitignore` no longer blocks `reports/` directory
