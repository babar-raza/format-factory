# Plan: Consolidate GitLab Credentials to `gitlab_token`

## Context

The user wants all GitLab authentication consolidated to a single machine-level
system environment variable `gitlab_token` (all lowercase), with a permanent rule
prohibiting any other variable name.

---

## Assessment scope

- **System:** GitLab push authentication — the credential variable naming, the push
  command template, the execution path, and the enforcement mechanisms.
- **Intended outcome:** One canonical variable, one push command format, zero ambiguity,
  no drift across sessions or plan files.
- **Evidence inspected:** CLAUDE.md, AGENTS.md, python-library-extraction-standard.md,
  5 plan files in `plans/.claude/`, 1 report, `.claude/settings.json`, `gate.py` hook,
  `sprint_executor.py`, `autonomous_cycle.py`, `autonomous_loop_runner.py`,
  `autonomous_host_runner.py`, `generate_next_worker_prompt.py`, `.gitlab-ci.yml`,
  `validate_handover.py`, `validate_committed_checkpoint.py`.
- **Missing evidence:** Whether the user has already set `gitlab_token` as a Windows
  system variable. Whether the current PAT is valid (it was expired/invalid during
  the crystalline-sauteeing-cupcake session — see Symptoms §2).

---

## Current-state reconstruction

### Actual execution path (no wrapper exists)

Every GitLab push is a **raw Bash tool call** — the agent reads the command template
from CLAUDE.md line 487 or AGENTS.md line 1238, pastes it into a `Bash()` call, and
the shell expands the credential variables. There is:

- **No Python wrapper** that executes `git push`
- **No askpass implementation** — described in plan docs, tried once, failed (token was
  invalid, not the mechanism itself), never built
- **No credential helper** — GCM is explicitly avoided via inline URL
- **No pre-push validation** — nothing checks if vars are set before the push attempt
- **No settings.json entry** for `git push` — it's neither allowed nor denied, falls to
  user-prompt default

### Safety rails (preserved, not touched)

Multiple supervisor modules treat `git push` as a hard-stop keyword to prevent
automated pushes: `autonomous_loop_runner.py` (line 45 `_FORBIDDEN_TASK_LABELS`,
line 57 `_HARD_STOP_PATTERNS`), `autonomous_host_runner.py` (line 54
`HARD_STOP_KEYWORDS`), `autonomy_route_decider.py` (line 84), `continuation_state.py`
(line 48), `generate_next_worker_prompt.py` (line 868). None of these reference
credential variable names — they match on "git push" as a string. **Unaffected by
this migration.**

### Components NOT involved (confirmed false positives)

| File | Why excluded |
|------|-------------|
| `governance_validators_ext.py` | `_gl_path` = gap-ledger file path |
| `autonomous_cycle.py` (23 hits) | `_gl_path`, `_gl_path_0c` = gap-ledger |
| `test_gap_closure_engine.py` (41 hits) | gap-ledger test fixtures |
| `.gitlab-ci.yml` | Uses `$CI_*` built-in vars, not user credentials |
| `validate_handover.py` | Read-only git ops, never pushes |
| External GitLab refs (gnome.org, gitlab.com) | Different instances entirely |

---

## Symptoms

1. **Six different variable names** for the same credential across the codebase:
   `gl_pat`, `gl_username`, `gl_password`, `gl_token`, `gitlab_pat`, `GITLAB_TOKEN`.
2. **Documented push failure** in `crystalline-sauteeing-cupcake.md` lines 2608-2623:
   `gl_pat` was invalid/expired, 4 auth methods tried, all failed, 52 commits sat
   locally unpushed. Classified as `EXTERNAL_BLOCKER: git_push_credentials_unavailable`.
3. **Push command requires two variables** (`gl_username` + `gl_pat`) where GitLab's
   `oauth2` pseudo-username needs only one.
4. **No pre-push validation** — agent discovers credential failure only after the push
   attempt, with a generic git error ("HTTP Basic: Access denied").

---

## Root causes

### RC-1: No canonical variable declaration (confidence: HIGH)

**Evidence:** Six names exist because each plan file independently chose one. CLAUDE.md
uses `gl_pat`/`gl_username`. The extraction standard uses `gl_token`. The CI audit plan
uses `gitlab_pat`. No document declares which is authoritative.

**First failing boundary:** The moment a second plan file chose a different name than
CLAUDE.md without updating CLAUDE.md.

**Why existing controls missed it:** No governance validator scans for credential
variable names. The push command is prose in markdown, not executable code — no linter
catches naming drift in documentation.

### RC-2: Two-variable push command (confidence: HIGH)

**Evidence:** CLAUDE.md line 487 requires both `gl_username` AND `gl_pat`. If either is
unset (empty string or missing), the push URL becomes malformed. GitLab PATs work with
the `oauth2` pseudo-username, eliminating the need for a separate username variable.

**Affected scope:** Every push attempt. The failure mode is silent — `${gl_username}`
expands to empty string, URL becomes `https://:${gl_pat}@...`, git sends malformed auth.

### RC-3: No pre-push credential check (confidence: HIGH)

**Evidence:** The push command template in CLAUDE.md has no guard. An agent runs the raw
command, gets "HTTP Basic: Access denied", then must diagnose whether the var is unset,
the token expired, or the host is down. This wastes cycles and produces inconsistent
error classification across sessions.

---

## Structural weaknesses

1. **Push command is duplicated in prose** — CLAUDE.md, AGENTS.md, and 3 plan files each
   contain the full push URL. When the variable name changes (as now), all must update.
   No DRY mechanism for markdown command templates.

2. **No askpass implementation** — the documented security practice ("transient
   credential/askpass handling") was never built. The inline URL approach is the
   actual mechanism. This is pragmatically fine on Windows with GCM (the inline URL
   prevents GCM dialog interception), but the docs describe a mechanism that doesn't
   exist.

3. **No governance validator for credential naming** — validators cover source structure,
   LOC, monolith detection, etc. None scans binding documents for retired credential
   variable names. Drift can recur silently.

---

## What should be preserved

- GitLab remote URL: `gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git`
- Security rules: never print/log/commit/embed token values
- GitHub push command and `GH_TOKEN` variable — unchanged
- All safety rails in supervisor code — they match on "git push" string, not variable names
- `.gitlab-ci.yml` — uses `$CI_*` built-in vars, unrelated
- The `EXTERNAL_BLOCKER` classification system for push failures
- The `gate.py` coordination hook — doesn't touch `git push`
- All Python source and test files — zero changes needed

---

## What must be redesigned

1. **Variable naming** — consolidate 6 names to `gitlab_token` everywhere
2. **Push command format** — `oauth2:${gitlab_token}` instead of `${gl_username}:${gl_pat}`
3. **Push command template** — add a pre-push guard that validates the env var exists
4. **Binding rule** — add explicit canonical declaration + retired names list to CLAUDE.md
5. **Askpass documentation** — remove reference to non-existent askpass mechanism, document
   the actual inline-URL approach honestly
6. **Drift prevention** — memory entry for cross-session enforcement

---

## Production-grade target design

### Architecture

Single authoritative declaration in CLAUDE.md (the file every session reads first).
AGENTS.md references CLAUDE.md by section name. All other files are downstream consumers.

### Push command template (with pre-push guard)

```bash
# GitLab push (validates credential before attempting)
[ -n "$gitlab_token" ] || { echo "EXTERNAL_BLOCKER: gitlab_token system env var not set"; false; } && \
git push "https://oauth2:${gitlab_token}@gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git" main
```

This catches the most common failure mode (unset variable) BEFORE the push attempt,
with a properly classified error message. If the token is set but expired/invalid,
the git error still occurs — but that's a TRUE_EXTERNAL_GATE (token rotation required).

### State model

```
Machine-level system env var: gitlab_token
  ↓ (shell expansion)
Push command: https://oauth2:${gitlab_token}@gitlab.recruitize.ai/...
  ↓ (HTTPS Basic Auth)
GitLab server: validates PAT
```

No intermediate state. No credential caching. No helper scripts. The simplest
possible execution path — which is exactly what the current system uses, minus
the variable name confusion and the two-variable requirement.

### Failure handling

| Failure | Detection | Classification |
|---------|-----------|---------------|
| `gitlab_token` not set | Pre-push guard `[ -n "$gitlab_token" ]` | `EXTERNAL_BLOCKER: gitlab_token system env var not set` |
| Token expired/invalid | Git returns "HTTP Basic: Access denied" | `EXTERNAL_BLOCKER: gitlab_token_expired_or_invalid` |
| Host unreachable | Git returns DNS/connection error | `EXTERNAL_BLOCKER: gitlab_host_unreachable` |

---

## Implementation

### Phase 1 — CLAUDE.md (authoritative source)

**Edit `CLAUDE.md` lines 485-489.** Replace the push commands block:

```
  **Verified push commands (2026-08-30):**
  - GitHub: `git push "https://${GH_TOKEN}@github.com/babar-raza/format-factory.git" main`
  - GitLab: `[ -n "$gitlab_token" ] || { echo "EXTERNAL_BLOCKER: gitlab_token not set"; false; } && git push "https://oauth2:${gitlab_token}@gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git" main`
    (if GitLab host unreachable: classify as `EXTERNAL_BLOCKER: gitlab_host_unreachable`)
  - Do NOT use `git push origin` or `git push github` directly (GCM dialog blocks headless mode).

  **GitLab Credential Variable Rule (BINDING — NON-NEGOTIABLE):**
  `gitlab_token` (all lowercase) is the SOLE authorized environment variable for GitLab
  authentication in this repository and any repository extracted from it. It MUST be set
  as a machine-level Windows system environment variable containing a GitLab PAT.
  No other variable name is permitted for any purpose. This rule is permanent.
  - **Push:** `https://oauth2:${gitlab_token}@...` — `oauth2` is the pseudo-username.
  - **API (curl):** `--header "PRIVATE-TOKEN: $gitlab_token"`
  - **glab CLI:** `GITLAB_TOKEN="$gitlab_token" glab ...` (transient per-command only;
    `GITLAB_TOKEN` uppercase MUST NOT exist as a persistent environment variable.)
  - **Retired (NEVER use):** `gl_pat`, `gl_username`, `gl_password`, `gl_token`,
    `gitlab_pat`, and any persistent `GITLAB_TOKEN`. These names are dead.
  - **Security:** Never print, log, commit, or embed the token value. The inline-URL
    approach (not askpass) is the actual push mechanism on this repository.
  - **Pre-push guard:** Always validate `[ -n "$gitlab_token" ]` before push attempts.
```

### Phase 2 — AGENTS.md (references CLAUDE.md)

**Edit `AGENTS.md` lines 1234-1241.** Replace AG4.2a:

```
**AG4.2a Push Credentials (verified 2026-08-30).** Use these env-var-based push commands:

- **GitHub** (`github` remote): `git push "https://${GH_TOKEN}@github.com/babar-raza/format-factory.git" main`
  — `GH_TOKEN` is available in the shell environment.
- **GitLab** (`origin` remote — `gitlab.recruitize.ai`): `[ -n "$gitlab_token" ] || { echo "EXTERNAL_BLOCKER: gitlab_token not set"; false; } && git push "https://oauth2:${gitlab_token}@gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git" main`
  — `gitlab_token` (all lowercase, machine-level Windows system env var) is the sole
  authorized GitLab credential variable. See CLAUDE.md §"GitLab Credential Variable Rule"
  for the full binding, retired names, and security rules.
- **Do NOT** use `git push origin` or `git push github` directly — the GCM dialog blocks in headless mode.
- **Do NOT** hardcode any token values in committed files (AGENTS.md §AC6).
```

### Phase 3 — Governance documentation

**Edit `docs/governance/python-library-extraction-standard.md` lines 655-665.**

Change `gl_token` → `gitlab_token` and remove the askpass reference (it doesn't exist):

```
### GitLab Authentication

When `gitlab_token` is provided through the environment:

- never print it;
- never log it;
- never commit it;
- never embed it in `origin`;
- push via inline URL with `oauth2` pseudo-username;
- keep `origin` as the clean HTTPS URL.
```

### Phase 4 — Active plan files

**`plans/.claude/crystalline-sauteeing-cupcake.md`** — 6 edits:
- Lines 82, 401, 2821: `gl_token` → `gitlab_token`
- Lines 2609, 2620, 2791: `gl_pat` → `gitlab_token`

**`plans/.claude/spicy-giggling-robin.md`** — 2 edits:
- Line 29: Replace `Use \`gl_pat\`/\`gl_username\` from environment via temporary \`GIT_ASKPASS\`` with `Use \`gitlab_token\` from environment (oauth2 pseudo-username); never print/log/commit tokens`
- Line 819: `gl_username/gl_pat` → `gitlab_token`

### Phase 5 — Historical plan/report files

**`plans/.claude/snappy-swinging-metcalfe.md`** — bulk update. The file is a CLOSED plan
(CI audit), but contains active push command templates that agents might re-read.

Pattern: every `$gitlab_pat` → `$gitlab_token`, every `$gl_username:$gl_password` →
header-based auth with `$gitlab_token`, push URL `${gl_username}:${gl_pat}` →
`oauth2:${gitlab_token}`. Lines 55, 139-141, 147, 151-153, 158, 210, 221, 228, 486, 572.

**`reports/skills-rff6/mainline-sync-verification-20260804.md`** line 84:
push URL → `oauth2:${gitlab_token}`

### Phase 6 — Memory entry

Create `memory/gitlab-token-canonical-var.md`:

```yaml
---
name: gitlab-token-canonical-var
description: "gitlab_token (lowercase, machine-level sys var) is the SOLE GitLab credential; gl_pat/gl_username/gl_token/gitlab_pat permanently retired"
metadata:
  type: feedback
---
```

Body: the binding rule, all 6 retired names, the three auth patterns (push, curl, glab),
why (6 names caused real auth failures), and pointer to CLAUDE.md as authority.

**Why:** fragmented credential naming caused session-to-session inconsistency and a
documented 52-commit push failure in the libxliff extraction (crystalline-sauteeing-cupcake).

**How to apply:** before any GitLab push, API call, or credential reference, use
`gitlab_token` exclusively. Flag any other name as a violation.

Update `memory/MEMORY.md` with one-line entry.

---

## Verification strategy

### 1. Retired-name scan (regression gate)
```bash
grep -rn "gl_pat\|gl_username\|gl_password\|\bgl_token\b\|gitlab_pat" \
  CLAUDE.md AGENTS.md docs/ plans/.claude/ reports/skills-rff6/ \
  | grep -v "Retired.*NEVER use" | grep -v "dead"
```
**Expected:** Zero matches outside the retired-names list itself.

### 2. Canonical name in all authorities
```bash
grep -c "gitlab_token" CLAUDE.md AGENTS.md docs/governance/python-library-extraction-standard.md
```
**Expected:** All three files return ≥1.

### 3. Push URL format
```bash
grep -n "oauth2.*gitlab_token.*gitlab.recruitize" CLAUDE.md AGENTS.md
```
**Expected:** Exactly 2 matches (one per file).

### 4. Pre-push guard present
```bash
grep -n '\[ -n "\$gitlab_token" \]' CLAUDE.md AGENTS.md
```
**Expected:** Exactly 2 matches.

### 5. No source/test file changes
```bash
git diff --name-only -- tools/ tests/ src/
```
**Expected:** Empty.

### 6. Functional smoke test (requires env var to be set)
```bash
echo "${gitlab_token:0:4}..." # first 4 chars only, proves var exists
git ls-remote "https://oauth2:${gitlab_token}@gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git" HEAD
```
**Expected:** Shows ref hash (proves token + oauth2 format works). If "Access denied":
token is expired/invalid — `EXTERNAL_BLOCKER: gitlab_token_expired_or_invalid`.

### 7. Safety rails unaffected
```bash
grep -c "git.push\|git_push" tools/supervisor/autonomous_loop_runner.py tools/supervisor/autonomous_host_runner.py
```
**Expected:** Same counts as before (no changes to these files).

---

## Tradeoffs and risks

| Concern | Assessment |
|---------|-----------|
| `gitlab_token` env var not yet set on machine | Doc-only migration; no runtime breakage until a push is attempted. User must set the var as a prerequisite. |
| PAT expired (the actual failure in crystalline-sauteeing-cupcake) | The pre-push guard catches "not set" but can't detect "expired". Expired tokens are TRUE_EXTERNAL_GATEs. The `git ls-remote` smoke test validates token health. |
| glab CLI requires uppercase `GITLAB_TOKEN` | Transient pass-through `GITLAB_TOKEN="$gitlab_token" glab ...` handles this. Documented in the binding rule. |
| Old sessions with `gl_pat` in context memory | CLAUDE.md binding rule overrides at session start. Memory entry reinforces. |
| Askpass docs describe non-existent mechanism | Fixed: Phase 3 replaces "transient credential/askpass" with the actual inline-URL approach. |
| grep false positives from gap-ledger `_gl_path` | Verification grep excludes `tools/` and `tests/`. The `\b` word boundary in `\bgl_token\b` avoids `_gl_token` substring matches. |
| Historical plan files become technically inaccurate | They're already inaccurate (documenting multiple candidate names for an expired token). Updating them to the canonical name improves accuracy. |

**Rejected alternative — askpass wrapper script:** Building the askpass mechanism
described in docs would add complexity (temp file creation, cleanup, Windows path
issues) for minimal security gain over inline URLs on a single-user dev machine.
The askpass approach was tried once and failed (crystalline-sauteeing-cupcake line
2612). The inline URL with pre-push guard is simpler and proven.

**Rejected alternative — governance validator (V227):** A new validator scanning for
retired variable names is warranted long-term but out of scope for this migration.
The binding rule + memory entry provides enforcement at the session level. If drift
recurs, a validator can be added then.

---

## Final assessment

**STRUCTURAL_REDESIGN_REQUIRED**

The current state has duplicated authority (6 variable names, no canonical declaration),
a two-variable push command where one suffices, no pre-push validation, and documentation
describing a non-existent askpass mechanism. The fix is:

1. Canonical declaration with permanent retirement of old names (CLAUDE.md)
2. Single-variable push format using `oauth2` pseudo-username
3. Pre-push guard catching the most common failure mode (unset variable)
4. Honest documentation of the actual mechanism (inline URL, not askpass)
5. Memory entry preventing cross-session drift

No runtime code changes. No test file changes. No CI changes. The entire migration
is documentation and binding-rule edits across 7 files + 1 new memory file.


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-08-31T04:58:30.358483+00:00"
  locked_by: "585f135481a6"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
