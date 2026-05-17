# Audit Claim Verification Matrix
**Sprint:** FORMAT-FACTORY-SKILLS-PRD-HARDENING-001
**Date:** 2026-05-17

All claims verified against real repo files in this session. No claim accepted from memory alone.

| ID | Claim | Files Inspected | Verdict | Evidence |
|----|-------|----------------|---------|---------|
| A1 | 5 active commands in `.claude/commands/` | `.claude/commands/_readme.md` lines 32-36 | CONFIRMED | _readme table has 5 rows; files exist on disk |
| A2 | 7 planned commands missing | `TC-0004-commands-skills.md` status field | CONFIRMED | TC-0004 status: NOT_STARTED; 7 planned command rows in _readme |
| A3 | 7 planned commands denied in settings.json | `settings.json` lines 105-111 | CONFIRMED | Deny entries for all 7: score-format, create-acquisition-pack, check-gate, create-taskcard, reproduce-master-plan, build-evidence-bundle, check-release-boundary |
| B1 | `/export-plan-context` hardcodes R11/R12/R13 files | `export-plan-context.md` lines 44-57 | CONFIRMED | memory/27, memory/28, reports/planning/r11-*, weekly-report-r12-*, r13-readiness hardcoded |
| B2 | All hardcoded files exist on disk | `reports/planning/` directory listing | CONFIRMED | All 5 planning report files verified present |
| B3 | Command succeeds silently with stale output | Command logic + absence of staleness guard | CONFIRMED | No staleness check in Python snippet; no warning path |
| B4-NEW | `export-plan-context.md` is UNTRACKED in git | `git status --short` | CONFIRMED | `?? .claude/commands/export-plan-context.md` |
| C1 | `/memory-sprint` Step 14 says "Commit" | `memory-sprint.md` line 25 | CONFIRMED | "Stage only MEMORY_SPRINT_ALLOWED files. Commit." |
| C2 | `settings.json` denies `Bash(git commit *)` | `settings.json` line 113 | CONFIRMED | `{"type":"deny","tool":"Bash","input":{"command":"git commit *"}}` |
| C3 | Output format says "Commit hash." | `memory-sprint.md` line 41 | CONFIRMED | Output Format section: "Commit hash." |
| D1 | `settings.json` description stale (FODT G1-8, DEC-033 blocking) | `settings.json` lines 4-5 | CONFIRMED | description: "FODT Gates 1-8 ALL PASSED", "blocked DEC-033" |
| D2 | DEC-033 shown as blocking; resolved 2026-05-12 | `settings.json` line 5; `memory/35` lines 1-9 | CONFIRMED | DEC-033 resolved Option B per memory/35; settings.json still says "blocked DEC-033" |
| E1 | Step 1 hardcodes `memory/09-current-state-before-phase1.md` | `evidence-review-next-prompt.md` line 14 | CONFIRMED | "Read memory/09-current-state-before-phase1.md" in Step 1 |
| E2 | Step 7 has `--contract <contract>` placeholder | `evidence-review-next-prompt.md` line 22 | CONFIRMED | "python tools/evidence/validate_evidence_bundle.py --bundle <bundle_path> --contract <contract>" |
| E3 | 93 contracts in directory | `tools/evidence/contracts/` listing | CONFIRMED | 93 .yaml files (plus r21 = 94 total now including untracked) |
| F1 | Python command layer undocumented | `AGENTS.md` grep, methodology docs grep | CONFIRMED | Zero matches for `tools/skills/commands` in AGENTS.md or any methodology doc |
| F2 | Python commands scoped to fods/fodt only | `commercial_sprint.py` content | CONFIRMED | Runtime block at line 15: "Format {format_name} not yet supported" for non-fods/fodt |
| F3 | Tests use underlying modules, not entry points | `tests/skills/` — 11 files | CONFIRMED | Imports: `format_context_resolver`, `lane_selector` — not `format_context.py`, `lane_select.py`, `commercial_sprint.py` |
| G1 | No frontmatter schema validation for command files | `schemas/skills/` — 6 files | CONFIRMED | No schema for `.claude/commands/*.md` frontmatter |
| G2 | No phase-available/gate-required enforcement | No tooling found in tools/ | CONFIRMED | No validator script found |
| H1 | Plan hardening score is self-reported | `plan-hardening-checklist.md` manual only | CONFIRMED | Checklist is prose-only; no automated scorer |
| I1 | TC-0004 exists as NOT_STARTED | `taskcards/TC-0004-commands-skills.md` | CONFIRMED | status: NOT_STARTED |
| I2 | Settings prerequisite undocumented in TC-0004 | `taskcards/TC-0004-commands-skills.md` full read | CONFIRMED | No PREREQUISITES section; no mention of settings.json deny entries |
| J1 | `test_zst_gate6_oracle.py` is untracked | `git status --short` | SUPERSEDED | File was committed in R19 commit 2dcd7f8 — not in untracked list |
| K1-NEW | `docs/agent-methodology-index.md` missing `/export-plan-context` | Section 5 — 4 rows only | CONFIRMED | Section 5 lists 4 commands; `_readme.md` lists 5; gap = `/export-plan-context` |
| K2-NEW | R19 memory sprint not executed | `memory/` listing — highest = 35 (R18 era) | CONFIRMED | memory/36 does not exist; R19 bundle at `.local/r19-bundle.zip` |
| K3-NEW | `format-factory.zip` untracked, not gitignored | `git status`, `.gitignore` | CONFIRMED | `?? format-factory.zip` in status; not in .gitignore |
