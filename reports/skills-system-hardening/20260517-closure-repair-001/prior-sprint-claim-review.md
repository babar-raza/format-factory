# Prior Sprint Claim Review
**Sprint:** SKILLS-PRD-HARDENING-001-CLOSURE-REPAIR-001
**Parent sprint:** FORMAT-FACTORY-SKILLS-PRD-HARDENING-001
**Date:** 2026-05-17
**Purpose:** Independently verify prior sprint implementation claims before closure repair

## Verification Results

| # | Claim | Source File | Verdict |
|---|-------|-------------|---------|
| 1 | settings.json DEC-033 blocking language removed | `.claude/settings.json` line 4 | CONFIRMED — description says "RESOLVED 2026-05-12 (Option B: .NET Commercial Only)"; no "blocked DEC-033" |
| 2 | settings.json ZST G1-7 present | `.claude/settings.json` line 4 | CONFIRMED — "ZST Gates 1-7 PASSED (G5 waived)" in description |
| 3 | settings.json description_last_updated = r19-skills-hardening | `.claude/settings.json` line 3 | CONFIRMED — `"description_last_updated": "r19-skills-hardening"` |
| 4 | evidence-review-next-prompt.md Step 0 present | verified in prior reads | CONFIRMED — Step 0 dependency preflight present with 6 required files |
| 5 | evidence-review-next-prompt.md no memory/09 in operational steps | verified in prior reads | CONFIRMED — memory/09 only in changelog comment, not in operational Steps |
| 6 | evidence-review-next-prompt.md contract guidance present | verified in prior reads | CONFIRMED — Step 6 has sort-by-mtime and fallback base-run.yaml guidance |
| 7 | memory-sprint.md COMMIT_PENDING_HUMAN_APPROVAL present | verified in prior reads | CONFIRMED — present in Step 14 and Output Format |
| 8 | memory-sprint.md no false autonomous commit claim | verified in prior reads | CONFIRMED — PERMISSION NOTE + permission dialog documentation present |
| 9 | export-plan-context.md staleness guard present | `.claude/commands/export-plan-context.md` lines 86-97 | CONFIRMED — fires automatically after zip creation |
| 10 | export-plan-context.md R18 memory files (34/35) in list | `.claude/commands/export-plan-context.md` lines 61-62 | CONFIRMED — memory/34 and memory/35 present; however memory/38 now exists (STALENESS_WARNING will fire) |
| 11 | AGENTS.md J4/CURRENT_INTERNAL_ONLY added | `AGENTS.md` line 152 | CONFIRMED — J4 with CURRENT_INTERNAL_ONLY classification present |
| 12 | docs/agent-methodology-index.md /export-plan-context row present | `docs/agent-methodology-index.md` line 78 | CONFIRMED — row present with correct path and description |
| 13 | TC-0004 PREREQUISITES section added | `taskcards/TC-0004-commands-skills.md` lines 78-88 | CONFIRMED — PREREQUISITES with all 7 Write() entries present |

## Contract Schema Defects (Primary Closure Repair Target)

| Key Used | Correct Key | Enforcement |
|----------|-------------|-------------|
| `required_metadata:` | `required_metadata_files:` | Not enforced with wrong key — validator shows "0 checked" |
| `forbidden_content:` | `forbidden_paths:` | Not enforced with wrong key — validator shows "0 checked" |

Additionally, `forbidden_content` listed `src/python/` and `src/net/` — these MUST NOT be in
`forbidden_paths` for a full-repo bundle (those source files are legitimately in the bundle).
Correct forbidden_paths for full-repo model: only `.env` and `node_modules/**`.

## Memory Currency Gap

- Latest memory in repo: `memory/38-r21-foss-release-readiness-and-gate11-preexecution-20260517.md`
- Latest memory in export-plan-context.md standard list: `memory/35-r18-...`
- Action: Add memory/38 and `reports/planning/r21-registry-pack-taskcard-roadmap-memory-normalization-report-20260517.md` to export-plan-context.md standard list

## Conclusion

All 13 prior sprint implementation claims CONFIRMED. Two contract schema defects require closure repair. Memory/38 gap requires export-plan-context.md update.
