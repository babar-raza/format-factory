# Gap Analysis Beyond Original Audit
**Sprint:** FORMAT-FACTORY-SKILLS-PRD-HARDENING-001
**Date:** 2026-05-17

Gaps discovered during independent claim verification that were NOT in the original audit.

| Gap | Severity | Source Evidence | Decision |
|-----|----------|----------------|----------|
| `export-plan-context.md` not committed — fresh clone has broken `_readme.md` reference | CRITICAL | `git status --short` → `?? .claude/commands/export-plan-context.md` | Fix in this sprint: TC-SKILL-PRD-004 repairs content, TC-SKILL-PRD-000 stages file |
| No Step 0 dependency preflight in any active command | MEDIUM | Read all 5 command files — none start with dependency check | Add Step 0 to evidence-review-next-prompt, memory-sprint (export-plan-context gets Step 0 too) |
| R19 memory sprint missing | MEDIUM | `memory/` listing: highest = 35 (R18). R19 bundle exists at `.local/r19-bundle.zip` | Separate `/memory-sprint` session (TC-SKILL-PRD-009 DEFERRED) |
| `validate_evidence_bundle.py` has staged unstaged changes | MEDIUM | `git status --short` → modified in index | Defer — do not touch in this sprint |
| Python commands cannot resolve ZST/FODP/ABW format state | LOW | `commercial_sprint.py` runtime block; R20 now adds these formats to pipeline | Documented in AGENTS.md J4 classification (TC-SKILL-PRD-005) |
| `format-factory.zip` root artifact not in .gitignore | LOW | `git status --short` → `?? format-factory.zip`; not in `.gitignore` | Deferred cleanup sprint |
| R21 staged files in index from prior sprint session | MEDIUM | `git status --short` — 34 staged files not owned by this sprint | COMMIT BLOCKER: human decision required before this sprint's commit |
| R20 commits moved HEAD 2 commits ahead of plan | MEDIUM | `git log --oneline 2dcd7f8..HEAD` → 2 commits | HEAD_REBASELINED_SAFE — sprint-owned files untouched by R20 |
| R21 untracked report/taskcard files (30+) | LOW | `git status --short` → `??` entries | PREEXISTING_DEFERRED — not owned by this sprint |
| `memory-sprint.md` does not explain why metadata floor is 55 vs. 30 | LOW | `memory-sprint.md` reads 59 lines; no floor justification | Add inline note in Lane 2 (TC-SKILL-PRD-003) |
| `docs/agent-methodology-index.md` 4-command table inconsistent with `_readme.md` 5-command table | MEDIUM | `docs/agent-methodology-index.md` Section 5; `_readme.md` line 36 | Fix in Lane 4 (TC-SKILL-PRD-008) |
