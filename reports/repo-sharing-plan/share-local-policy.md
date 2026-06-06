# Share / Local Policy
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04

## Legend

| Class | Meaning | Action |
|-------|---------|--------|
| A | SHARE_IN_REMOTE | Track and push to GitHub |
| B | LOCAL_ONLY | Keep gitignored; never push |
| C | ARCHIVE_NOT_REMOTE | Keep tracked as-is; do not force-add more historical sprint data |
| D | CONDITIONAL_SHARE | Sanitize or review before push |
| E | MUST_NOT_SHARE | Must never appear in remote; currently correctly handled |

---

## Full Path Policy Table

| Path | Current Git State | Class | Reason | Required Action |
|------|-------------------|-------|--------|-----------------|
| `src/` | Tracked (M — some files) | **A** | Product source code — Python + .NET parsers/converters | Commit modified files |
| `tests/` | Tracked + 276 untracked | **A** | Test suites — validation proof for all formats | `git add tests/` |
| `examples/` | Tracked + 17 untracked | **A** | Usage examples — onboarding for colleagues | `git add examples/` |
| `docs/` | Tracked + 42 untracked | **A** | Governance, architecture, prompt templates | `git add docs/` |
| `plans/` | Tracked + 1 untracked | **A** | Master plan + healing plans | `git add plans/` |
| `state/` | Tracked (M) | **A** | Authoritative project state snapshot | Commit modified |
| `registry/` | Tracked (clean) | **A** | Format registry — gate authority | No action needed |
| `product-capability-matrix/` | Tracked (M) | **A** | POC target capability matrix | Commit modified |
| `tools/` | Tracked + 32 untracked (M) | **A** | Supervisor pipeline, evidence tools, validators | `git add tools/` + commit modified |
| `taskcards/` | Tracked (clean) | **A** | Sprint task definitions | No action needed |
| `acquisition-packs/` | Tracked (clean) | **A** | Format acquisition specifications | No action needed |
| `memory/` | Tracked + 2 untracked | **A** | Sprint knowledge base | `git add memory/` |
| `schemas/` | Tracked (clean) | **A** | JSON/YAML validation schemas | No action needed |
| `samples/` | Tracked (clean) | **A** | Sample format files used by tests | No action needed |
| `prototypes/` | Tracked (clean) | **A** | Early prototype code | No action needed |
| `generated-requirements/` | Tracked (clean) | **A** | Generated requirements docs | No action needed |
| `release-manifests/` | Tracked (clean) | **A** | Release/gate manifests | No action needed |
| `templates/` | Tracked (clean) | **A** | Document templates | No action needed |
| `.supervisor/` | Tracked + 1 untracked (M) | **A** | Supervisor config, schemas, prompts | `git add .supervisor/` + commit modified |
| `.claude/` | Tracked + 6 untracked (M) | **A** | Claude Code session config + commands | `git add .claude/` + commit modified |
| `reports/supervisor/` | Tracked (M) — BUG blocks new | **A** | Live sprint state (session-resume, approval-gates, etc.) | Fix `.gitignore` /reports bug first; sanitize product-gap-selection.md |
| `reports/repo-sharing-plan/` | Untracked — BUG blocks | **A** | This planning run output | Fix `.gitignore` /reports bug; then `git add -f` or fix first |
| `.gitignore` | Tracked (M) | **A** | Repo hygiene — needs /reports fix + minor additions | Apply proposed patch |
| `.env.example` | Tracked (clean) | **A** | Safe API key template (empty values) | No action needed |
| `CLAUDE.md` | Tracked (clean) | **A** | Session instructions | No action needed |
| `AGENTS.md` | Tracked (clean) | **A** | Governance authority | No action needed |
| `.vscode/*.example.json` | Tracked (clean) | **A** | Safe MCP config templates | No action needed |
| `.local/` | Untracked/gitignored | **B** | Evidence runs, packages, venvs (~957 MB) — correctly gitignored | No action needed |
| `.venv/`, `venv/`, `env/` | Gitignored | **B** | Python virtual environments | No action needed |
| `bin/`, `obj/` | Gitignored | **B** | .NET build outputs | No action needed |
| `TestResults/` | Gitignored | **B** | .NET test results | No action needed |
| `__pycache__/`, `*.pyc` | Gitignored | **B** | Python bytecode | No action needed |
| `.pytest_cache/` | Gitignored | **B** | Pytest cache | No action needed |
| `.vs/` | Gitignored | **B** | Visual Studio IDE state | No action needed |
| `.supervisor/state/` | Gitignored | **B** | Supervisor runtime state | No action needed |
| `.ruflo/`, `.swarm/` | Gitignored | **B** | External orchestration tool runtime state | No action needed |
| `.vscode/mcp.json` | Gitignored | **B** | Actual MCP config with credentials | No action needed |
| `.env`, `.env.*` | Gitignored | **E** | Credentials — correctly gitignored | No action needed |
| `reports/r*/` (historical) | Tracked (M — some) | **C** | 1867 files of historical sprint evidence | Commit M files; do not force-add new r* sprint dirs |
| `reports/supervisor/product-gap-selection.md` | Tracked (M) | **D** | Contains C:/Users/prora/... absolute path leak | Sanitize line 1: replace absolute path with `./` before push |

---

## Pre-Push Checklist

1. **[CRITICAL]** Fix `.gitignore` — remove both `/reports` lines (173 and 174)
2. **[REQUIRED]** Sanitize `reports/supervisor/product-gap-selection.md` line 1
3. **[REQUIRED]** Verify staged diff contains no `prora` username or API keys:
   ```bash
   git diff --cached | grep -i "prora\|api_key\|password\|token\|secret"
   # Must return empty
   ```
4. **[REQUIRED]** Confirm no new `.env` files are staged:
   ```bash
   git diff --cached --name-only | grep "\.env"
   # Must return empty (except .env.example)
   ```
5. **[REQUIRED]** Confirm `.local/` is not staged:
   ```bash
   git diff --cached --name-only | grep "^\.local/"
   # Must return empty
   ```

---

## Summary Counts

| Class | Paths | Approximate Files | Status |
|-------|-------|-------------------|--------|
| A — SHARE | 25 paths | ~3800 tracked + ~375 untracked | Commit + push (after fixes) |
| B — LOCAL_ONLY | 10+ patterns | ~957 MB | Already gitignored |
| C — ARCHIVE | reports/r*/ | ~1867 | Keep tracked as-is |
| D — CONDITIONAL | 1 file | product-gap-selection.md | Sanitize first |
| E — MUST_NOT_SHARE | .env variants | 0 tracked | Already gitignored |
