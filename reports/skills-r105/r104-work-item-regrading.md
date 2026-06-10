# R104 Work Item Regrading (Train A -- R105)

**Reviewer:** Train A, Skills R105
**Date:** 2026-06-03
**Sprint under review:** skills-r104

---

## Regrading Table

| Item | R104 Grade | R105 Regrade | Reason |
|------|-----------|-------------|--------|
| W0-R103-ACCEPTANCE | ACCEPTED | ACCEPTED_WITH_LIMITATIONS | Path-evidence only, no test proof. Single markdown report with no automated verification that R103 verdict was correctly interpreted or that 6 carry-forward issues are accurately documented. |
| W1-ADOPTION-ENFORCEMENT | ACCEPTED | ACCEPTED_WITH_LIMITATIONS | YAML enforcement packages exist for 3 streams but no tests validate their schema, rule completeness, or grade-impact definitions. `tests_supporting: []` in declaration. |
| W2-SKILL-PROMOTION | ACCEPTED | ACCEPTED_VERIFIED | 21 tests pass covering command file structure (12 sections), frontmatter, registry consistency (18 active, 2 draft). Command validation JSON confirms 23/23 commands pass with 0 errors. |
| W3-VALIDATOR-HARDENING | ACCEPTED | ACCEPTED_VERIFIED | 50/50 tests pass across 3 test files. Raw log present (1.25s runtime). Both command-validation and transcript-validation JSON results present with structured pass/fail data. |
| W4-PROOF-TRANSCRIPTS | ACCEPTED | ACCEPTED_VERIFIED | 4 transcripts validate against registry via transcript validator. 3 PASS (dry-run), 1 FAIL (anti-bypass-demo -- expected behavior). Covers .NET, Python, governance, and anti-bypass scenarios. |
| W5-LEDGER-BRIDGE | ACCEPTED | ACCEPTED_WITH_LIMITATIONS | Bridge design doc and remediation template YAML exist but no tests validate the workflow or template structure. No integration test with supervisor grading pipeline. |
| W6-STREAM-ISOLATION | ACCEPTED | ACCEPTED_WITH_LIMITATIONS | Stream isolation documented as infrastructure limitation but not enforced. Skills agent can still modify supervisor/mainstream artifacts. 5 orphan commands flagged as cross-stream contamination. |
| W7-EVIDENCE-MANIFEST | ACCEPTED | ACCEPTED_VERIFIED | 48 artifacts enumerated, 0 missing. Manifest is internally consistent and machine-parseable. Artifact types correctly classified. |

## Summary

- **ACCEPTED_VERIFIED:** 4 items (W2, W3, W4, W7)
- **ACCEPTED_WITH_LIMITATIONS:** 4 items (W0, W1, W5, W6)
- **OVERCLAIMED / REJECTED:** 0 items

No items are rejected. The R104 sprint delivered real value, but the grading was too generous for items that relied solely on file existence as proof. The regrade downgrades 4 items to ACCEPTED_WITH_LIMITATIONS to reflect the absence of automated test coverage.

---

## Next-Action Mapping

### What not to repeat
- Do not produce adoption enforcement packages or bridge designs without at least one test validating their schema and core assertions. Path-existence is insufficient evidence for ACCEPTED grade.
- Do not claim stream isolation as completed when it is documented-only with no enforcement mechanism.

### What to harden
- **Transcript enforcement in grading:** Integrate transcript validation results into the supervisor grading pipeline so that missing or invalid transcripts automatically downgrade work items.
- **Stream-state validation:** Add a pre-commit or pre-sprint check that detects when a skills-stream agent modifies files outside its allowed paths (`reports/skills-*`, `.supervisor/skill-registry.yaml`, `.claude/commands/`, `tests/python/supervisor/`).
- **Enforcement package testing:** Write schema-validation tests for the 3 adoption enforcement YAMLs.

### What to carry forward
- **LIVE handoff execution:** R104 created the ledger-remediation-template but did not execute any LIVE handoffs. R105 should execute at least 2 LIVE handoffs with ledger entries.
- **Orphan command conversion:** 5 orphan commands identified by the command validator need to be either registered as governed skills or formally deprecated.
- **Stream field in evidence declaration:** Add a `stream` field to the evidence-declaration schema so that cross-stream contamination can be detected automatically.

### What to delegate
- **LIVE source changes to Mainstream:** Any skill execution that modifies `src/` files must be delegated to the Mainstream stream via a governed handoff. The skills stream should produce the handoff YAML; Mainstream executes it.
- **Supervisor pipeline integration:** Transcript-in-grading enforcement requires changes to `tools/supervisor/grade_declared_work.py`, which is owned by the Supervisor stream.
