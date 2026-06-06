# Repository Inventory
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04

## Classification Legend
- A = SHARE_IN_REMOTE
- B = LOCAL_ONLY (already gitignored or should be)
- C = ARCHIVE_NOT_REMOTE
- D = CONDITIONAL_SHARE (requires sanitization or decision)
- E = MUST_NOT_SHARE

---

## Top-Level Directory Inventory

| Path | Exists | Tracked Files | Untracked Files | Purpose | Gitignored | Classification | Notes |
|------|--------|--------------|----------------|---------|------------|----------------|-------|
| `src/` | YES | ~97 | 0 | Product source — Python + .NET parsers/converters | No | **A** | Core deliverable |
| `tests/` | YES | ~596 | ~276 | Test suites for all formats | No | **A** | New tests are untracked — safe to add |
| `examples/` | YES | ~19 | ~17 | Usage examples (Python + .NET) | No | **A** | New examples untracked — safe to add |
| `docs/` | YES | ~116 | ~42 | Governance, architecture, prompt templates | No | **A** | New governance + prompt dirs untracked |
| `plans/` | YES | ~4 | ~1 (healing/) | Sprint master plan + healing plans | No | **A** | Keep tracked |
| `state/` | YES | ~4 | 0 | Project state snapshots | No | **A** | current-state.md is team authority |
| `registry/` | YES | ~5 | 0 | Format registry YAML — gate authority | No | **A** | Never modify without human approval |
| `product-capability-matrix/` | YES | ~5 | 0 | POC target capability matrix | No | **A** | Team-visible capability status |
| `tools/` | YES | ~351 | ~32 | Supervisor pipeline, evidence tools, validators | No | **A** | All tools safe to share |
| `taskcards/` | YES | ~185 | 0 | Sprint task definitions | No | **A** | Historical sprint taskcards |
| `acquisition-packs/` | YES | ~165 | 0 | Format acquisition specifications | No | **A** | Technical specs for format targets |
| `memory/` | YES | ~71 | ~2 | Sprint knowledge base | No | **A** | Team knowledge — share |
| `schemas/` | YES | ~34 | 0 | JSON/YAML schemas | No | **A** | Validation schemas |
| `samples/` | YES | ~126 | 0 | Sample format files | No | **A** | Used by tests |
| `prototypes/` | YES | ~17 | 0 | Early prototype code | No | **A** | Historical reference |
| `generated-requirements/` | YES | ~17 | 0 | Generated requirements docs | No | **A** | Historical reference |
| `release-manifests/` | YES | ~15 | 0 | Release/gate manifests | No | **A** | Gate evidence |
| `templates/` | YES | ~5 | 0 | Document templates | No | **A** | Generic templates |
| `.supervisor/` | YES | ~24 | ~1 | Supervisor config, schemas, prompts | No (excl. state/) | **A** | `.supervisor/state/` is gitignored ✓ |
| `.claude/` | YES | ~20 | ~6 | Claude Code session config + commands | No | **A** | New commands untracked — safe to add |
| `reports/supervisor/` | YES | ~21+ | 0* | Live sprint state (session-resume, approval-gates, next-sprint) | **BUG: /reports ignores new** | **A** | Sanitize product-gap-selection.md first |
| `reports/r*/` (historical) | YES | ~1846 | 0* | Historical sprint evidence | **BUG: /reports ignores new** | **C** | Keep tracked as-is; don't force-add more |
| `reports/repo-sharing-plan/` | YES | 0* | 0* | This planning run output | **GITIGNORED by /reports BUG** | **A** | Needs /reports fix to be trackable |
| `.local/` | YES | 0 | 0 | Evidence, packages, venvs (~957 MB) | YES (.local/) | **B** | Already gitignored ✓ |
| `.venv/`, `venv/` | if present | 0 | 0 | Python virtual environments | YES | **B** | Already gitignored ✓ |
| `bin/`, `obj/` | generated | 0 | 0 | .NET build outputs | YES | **B** | Already gitignored ✓ |
| `TestResults/` | generated | 0 | 0 | .NET test results | YES | **B** | Already gitignored ✓ |
| `.vs/` | if present | 0 | 0 | Visual Studio IDE state | YES | **B** | Already gitignored ✓ |
| `.supervisor/state/` | YES | 0 | 0 | Supervisor runtime state | YES | **B** | Already gitignored ✓ |
| `dist/` | if present | 0 | 0 | Python distributions | YES | **B** | Already gitignored ✓ |
| `build/` | if present | 0 | 0 | Build outputs | YES | **B** | Already gitignored ✓ |
| `node_modules/` | if present | 0 | 0 | Node packages | YES | **B** | Already gitignored ✓ |
| `.vscode/` | YES | 2 | 0 | VSCode config — only .example.json files tracked | mcp.json gitignored | **D** | settings.json not tracked (good) |

*Zero shown due to /reports gitignore bug

---

## Special Files

| File | Tracked | Classification | Notes |
|------|---------|----------------|-------|
| `AGENTS.md` | YES | A | Governance — never modify without human |
| `CLAUDE.md` | YES | A | Session instructions |
| `.gitignore` | YES | A | Needs /reports fix + minor additions |
| `.env.example` | YES | A | Safe template |
| `.vscode/mcp.dual-orchestration.*.example.json` | YES | A | Safe templates |
| `.vscode/mcp.json` | NO (gitignored) | B | Actual MCP config — correct ✓ |
| `reports/supervisor/product-gap-selection.md` | YES (M) | D | Contains C:/Users/prora/... — sanitize first |

---

## Summary Counts

| Classification | Directory Count | File Count (approx) |
|---------------|----------------|---------------------|
| A — SHARE | ~25 paths | ~3800 (tracked + untracked) |
| B — LOCAL_ONLY | ~10 paths | ~957 MB (gitignored) |
| C — ARCHIVE | reports/r*/ | ~1846 tracked files |
| D — CONDITIONAL | 2 items | product-gap-selection.md, .vscode/ |
| E — MUST_NOT_SHARE | 0 standalone files | None (all .env files gitignored) |
