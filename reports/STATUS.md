# Status — Format Factory Sprint Status

Generated: 2026-06-05T03:36:22Z
**Latest sprint:** FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
**Verdict:** DOTNET_DOGFOOD_ARCHITECTURE_GAP_CONFIRMED_AND_ROUTED
**Autonomous Cycle:** Exit 0 — 18/18 ACCEPTED, Autonomous Continue: True
**Evidence bundle SHA-256:** `62e3e462996107131bfb83bde5aebd8461adfc11a3f168c9b6bb1be47fbfbf92`
**Evidence bundle:** `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\dotnet-dogfood-architecture-gap\declaration-review-package.zip`

---

## Architecture Gap: .NET Dogfood Writer Libraries (CONFIRMED)

The top 4 gaps (score=125 each) are architecture-blocked: no standalone Format Factory .NET writer
libraries exist for CSV, HTML, Markdown, or TXT. The `/add-dogfood-export` skill MUST NOT be invoked
for these gaps. Routes have been reclassified and guardrails applied.

| Gap | Writer Needed | Exists | Status |
|-----|--------------|--------|--------|
| fods-to-csv-dotnet | FormatFactory.Csv | NO | ARCHITECTURE_BLOCKED |
| fods-to-html-dotnet | FormatFactory.Html | NO | ARCHITECTURE_BLOCKED |
| fodt-to-markdown-dotnet | FormatFactory.Markdown | NO | ARCHITECTURE_BLOCKED |
| fodt-to-txt-dotnet | FormatFactory.Txt | NO | ARCHITECTURE_BLOCKED |

**Next step:** CREATE-DOTNET-CSV-WRITER-001 (see `reports/dotnet-dogfood-architecture-gap/future-sprint-options.md`)

---

## Prior Sprint Status (2026-06-01)

## Task Summary

| ID | Title | Status | Owner | Score |
|----|-------|--------|-------|-------|
| T-BRIDGE-01 | bridge_to_legacy_format() in autonomous_cycle.py | DONE | Agent B | 5/5 |
| T-BRIDGE-02 | Wire cmd_autonomous_cycle to call cmd_next | DONE | Agent B | 5/5 |
| T-SCHEMA-01 | jsonschema validation in evidence_declaration.py | DONE | Agent B | 4/5 |
| T-LEGACY-01 | Deprecation warnings on 3 legacy entry points | DONE | Agent B | 5/5 |
| T-VALIDATE-01 | Create R86 evidence declaration | DONE | Agent C | 5/5 |
| T-VALIDATE-02 | Run autonomous-cycle E2E with bridge | DONE | Agent C | 5/5 |
| T-PLAN-01 | Amend master-plan.md Section 40.5 + Section 41 | DONE | Agent D | 5/5 |

## Test Results
- 84/84 supervisor tests passing
- R86 real-sprint validation: 7/7 items ACCEPTED, exit 0, session-resume.md regenerated

## Remaining Gaps
- T-SCHEMA-01 scored 4/5: jsonschema library is optional (graceful degradation). Full enforcement requires `pip install jsonschema` in the venv.
- No new test specifically for the bridge adapter (covered by E2E validation only).

---

## 2026-06-05 — FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001

**Verdict:** README_REFRESH_PLAN_READY_FOR_EXECUTION (planning sprint)
**Taskcards:** 8/8 COMPLETE
**Review package SHA-256:** `551d5f9b33483184462d002a9aec633ba209a699a4d761671dc5bf14c2beb0ac`
**Review package:** `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\readme-refresh-plan\declaration-review-package.zip`

### Summary

README.md was reviewed and mapped against actual repo state (R118, 2026-06-05).
The README is ~100 sprints stale (last updated pre-R93). A full replacement plan was created
with 14 new sections, evidence-backed content plan, execution prompt, and validation checks.

### Key Findings

| Item | Status |
|------|--------|
| README stale sections | 5 major stale sections identified |
| Missing architecture topics | 14 missing topics (four-stream model, AI boundary, etc.) |
| Netpbm .NET in Products table | MISSING from README — CONFIRMED at src/net/netpbm/ |
| FOSS targets (ZST/PBM/SYLK) | MISSING from README — CONFIRMED in poc-targets.yaml |
| Status section sprint ref | R18 (100 sprints stale) — current is R118 |
| Recommended strategy | FULL REPLACEMENT (not patch) |

### Outputs Created

- reports/readme-refresh-plan/ (12 files)
- .local/evidences/readme-refresh-plan/ (declaration + manifest)
- reports/readme-refresh-plan/final-single-go-readme-update-prompt.md — EXECUTION READY

### NOT Done (by design)

- README.md was NOT edited (planning sprint only)
- No product source changes
- No commit, no push, no Gate approval, no external tool install
