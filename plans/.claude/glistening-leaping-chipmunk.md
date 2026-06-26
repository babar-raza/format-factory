# Plan: Migrate External Plan Files to In-Repo plans/.claude/

## Context

Claude Code plan-mode creates plan files at `~/.claude/plans/<random-name>.md` (outside the repo).
These external files have been used as the ongoing task log and execution vehicle across multiple chat
sessions (e.g., `zany-riding-goblet.md` grew to 79KB across 6 revision cycles and was referenced by
multiple chats). This is problematic: files outside the repo are not version-controlled, accumulate
across sessions without clear ownership, and cause confusion when multiple chats reference the same
external file.

**Goal:** All ongoing sprint plan files live in `plans/.claude/` within the repo. Plan-mode seeds
the external file; execution migrates it to in-repo immediately at session start.

---

## Taskcards

### TC-001: Self-migrate this plan file into the repo
**Status:** `complete` *(audit 2026-06-26: plans/.claude/glistening-leaping-chipmunk.md in git ls-files; .gitkeep committed; active plan lock redirected)*

**File to copy:** `C:\Users\prora\.claude\plans\glistening-leaping-chipmunk.md`
**Destination:** `plans/.claude/glistening-leaping-chipmunk.md`

Steps:
1. Create `plans/.claude/` directory if it doesn't exist (a `.gitkeep` is fine)
2. Copy `C:\Users\prora\.claude\plans\glistening-leaping-chipmunk.md` → `plans/.claude/glistening-leaping-chipmunk.md`
3. Run `write_plan_lock.py --plan-path plans/.claude/glistening-leaping-chipmunk.md` to redirect the
   active lock to point at the in-repo copy
4. All subsequent edits to this plan go to `plans/.claude/glistening-leaping-chipmunk.md`

**Acceptance:** `plans/.claude/glistening-leaping-chipmunk.md` exists; active plan lock `plan_path`
field points to the in-repo path.

---

### TC-002: Update CLAUDE.md Step 0 — add plan migration sub-step
**Status:** `complete` *(audit 2026-06-26: CLAUDE.md lines 11-27 confirmed migration sub-step; committed to git HEAD 4f87a811 ancestry)*

**File:** `CLAUDE.md`

Add a new sub-step immediately after the existing "If a plan file is loaded:" detection block in
Step 0. Insert before "Execute the loaded plan exclusively":

```
**Step 0 — Plan Migration (external → in-repo):**
If the detected plan file path is outside the repository (i.e., contains `/.claude/plans/` or
`\.claude\plans\`), immediately migrate it into the repo:
1. Copy the external plan file to `plans/.claude/<filename>` (create the directory if needed)
2. Run: `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/<filename>`
   This redirects the active lock to the in-repo path.
3. All subsequent reads, writes, taskcard updates, and hardening go to `plans/.claude/<filename>`.
   The external file is the seed only — no further writes to it.
4. Continue execution using the in-repo path as the sole plan authority.
```

Also update the example in Step 0:
- Before: `python tools/supervisor/write_plan_lock.py --plan-path plans/polished-giggling-tome.md`
- Ensure the example path is consistent with `plans/.claude/` convention (it already uses an in-repo
  path, so just add a note that external paths must be migrated first)

**Acceptance:** CLAUDE.md Step 0 contains the migration sub-step. Reading CLAUDE.md, the migration
rule is unambiguous before "Execute the loaded plan exclusively."

---

### TC-003: Update MEMORY.md with the in-repo plan convention
**Status:** `complete` *(audit 2026-06-26: MEMORY.md line 3 has MANDATORY rule; grep confirms "plans/.claude" at line 3+)*

**File:** `C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md`

Add a new MANDATORY entry near the top (after existing MANDATORY entries):

```
## MANDATORY: Per-Chat Plan Files Live in plans/.claude/ (USER INSTRUCTION — always enforce)
When plan-mode creates a plan at `~/.claude/plans/<name>.md`:
1. At session start (Step 0), IMMEDIATELY copy it to `plans/.claude/<name>.md` in the repo
2. Run `write_plan_lock.py --plan-path plans/.claude/<name>` to redirect the lock
3. ALL taskcard updates, hardening, and audit writes go to the in-repo copy
4. The external `~/.claude/plans/` file is the seed only — never write to it again
5. This applies to this plan (glistening-leaping-chipmunk) and ALL future plan-mode plans
```

**Acceptance:** MEMORY.md contains the new MANDATORY rule, visible in the first 200 lines.

---

### TC-004: Add plans/.claude/ to .gitignore or confirm it is tracked
**Status:** `complete` *(audit 2026-06-26: .gitignore does NOT exclude plans/.claude/; git ls-files shows .gitkeep + 2 plan MDs tracked)*

**File:** `.gitignore` (read first)

Decision:
- If `plans/.claude/` should be version-controlled (preferred — makes plans visible in PRs and
  history), ensure it is NOT in `.gitignore`. Add a `.gitkeep` so the directory is committed.
- If the user wants `.claude/` subdirs ignored, add `plans/.claude/` to `.gitignore`.

Default: track in git (version control is the point). Verify `.gitignore` does not accidentally
exclude `plans/.claude/`.

**Acceptance:** `plans/.claude/` directory exists in the repo and is not excluded by `.gitignore`.

---

## Files Modified

| File | Change |
|------|--------|
| `plans/.claude/glistening-leaping-chipmunk.md` | Created (copy of external plan) |
| `plans/.claude/.gitkeep` | Created (ensures directory is tracked) |
| `CLAUDE.md` | Step 0 gains plan migration sub-step |
| `MEMORY.md` | New MANDATORY rule for in-repo plan convention |
| `.gitignore` | Verified/adjusted to not exclude `plans/.claude/` |

---

## Verification

1. `ls plans/.claude/` — shows `glistening-leaping-chipmunk.md` and `.gitkeep`
2. `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/glistening-leaping-chipmunk.md --status IN_PROGRESS` — exits 0
3. `python tools/supervisor/check_continuation.py` — returns CONTINUE (not POST_PLAN_TERMINAL or ACTIVE_PLAN_INCOMPLETE)
4. CLAUDE.md Step 0 grep: `grep -n "plans/.claude" CLAUDE.md` — shows migration sub-step
5. MEMORY.md grep: `grep -n "plans/.claude" memory/MEMORY.md` — shows MANDATORY rule
