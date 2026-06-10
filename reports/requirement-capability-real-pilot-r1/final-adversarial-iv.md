# Final Adversarial Independent Verification
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001
# Lane: O

## Verification Method

Each check is answered with PASS / PARTIAL / FAIL plus evidence path.
No FAIL answers are acceptable without a documented remediation.

---

## Checklist (15 checks)

### 1. All 5 pilots ran and produced proof graph nodes/edges
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/proof-graph/` — 81 nodes, 102 edges.
graph-manifest.json confirms node types: ProductRequirement, CapabilityClaim, ImplementationArtifact,
TestArtifact, DogfoodArtifact, EvidencePackage, UnsupportedFeature, SpecRequirementRef, StalenessEvent.
All 5 pilots (Netpbm, FODS, FODT, ZST, DIF) contributed nodes confirmed in claim-registry-report.md.

### 2. Coverage evaluation ran for all pilots with no import errors
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/coverage-records.jsonl` — 20 records,
one per capability claim (4 Netpbm, 6 FODS, 5 FODT, 3 ZST, 2 DIF).
`reports/requirement-capability-real-pilot-r1/proof-sufficiency-summary.json` — overall verdict present.
0 Python import errors; driver ran cleanly to completion.

### 3. Overclaim detection found the expected overclaim and remediated it
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/overclaim-detection-report.md` confirms:
- Pattern 2 fired on `claim:netpbm:save` (save + direction=write_only)
- Remediation: direction changed write_only → read_write
- After remediation: 0 outstanding overclaim errors
Repair documented in: `minimal-repair-report.md` (Repair 1 is the coverage evaluator; remediation is in driver).

### 4. Staleness invalidation correctly identified the synthetic stale claim
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/stale-claims.md` — confirms `claim:zst:old-compress`
detected via `stale_due_to` edge from stale StalenessEvent node.
`staleness-invalidation-report.md` — propagation chain documented.
`recomputation-queue.json` — stale claim queued for recomputation.

### 5. POC readiness correctly computed per pilot
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/poc-readiness.json` — Netpbm=READY,
FODS=PARTIAL (export claims blocked), FODT=PARTIAL (export claims blocked), ZST=PARTIAL (stale claim),
DIF=ACCEPTED_WITH_LIMITATIONS (empirical only, non-blocking).
`scoreboard.md` — summary table present.

### 6. Gap queue generated from proof graph state (not ad hoc)
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/mainstream-gap-queue.json` — queue entries
present for FODS export_csv, FODS export_html, FODT export_markdown, FODT export_txt, ZST recomputation.
Each entry has: gap_id, claim_id, missing_proof_type, next_action, recommended_lane.
`actionable-vs-blocked-gap-summary.json` — categorised by actionable vs blocked.

### 7. Supervisor verdict packet generated with source_graph_hash
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/supervisor-verdict-packet.json` — all 16 required
fields present including source_graph_hash, claims_checked, poc_readiness_verdict, false_pass_risks.
`supervisor-verdict-packet-report.md` — human-readable summary present.

### 8. POC targets sync proposal generated but poc-targets.yaml NOT mutated
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/poc-targets-sync-proposal.yaml` — proposal
document present with PROHIBITION header confirming no direct mutation.
`poc-targets-sync-proposal-review.md` — review notes confirm read-only proposal.
`product-capability-matrix/poc-targets.yaml` — unchanged (git status confirms M only for pre-existing
files; poc-targets.yaml is NOT in the modified list).

### 9. All 6 golden replay fixtures pass with determinism
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/golden-replay-results.json` — 6/6 PASS,
all_deterministic=true.
Test: `TestGoldenReplayFixtures::test_all_6_fixtures_pass` PASSED.
Test: `TestGoldenReplayFixtures::test_determinism_across_all_fixtures` PASSED.

### 10. 25/25 real-pilot-R1 tests pass
**PASS**
Evidence: `reports/requirement-capability-real-pilot-r1/raw-logs/rca-tests.log` — 25 passed, 0 failed.
All test classes present and passing. No PENDING markers.

### 11. Architecture-blocked exports (FODS CSV/HTML, FODT Markdown/TXT) correctly blocked
**PASS**
Evidence: Tests `test_fods_export_csv_blocked_in_pilot` and `test_fodt_export_markdown_blocked_in_pilot`
PASSED — confirm blocked status in coverage-records.jsonl.
`false-pass-false-stop-risk-report.md` — notes architecture-blocked exports and why they are blocked.

### 12. ai_draft proof rejected by graph validator (invariant 6)
**PASS**
Evidence: `TestAiDraftRejectedAsProof::test_ai_draft_impl_fails_invariant` PASSED.
GraphValidator raises invariant 6 error when ai_draft implementation is the only proof.
No ai_draft nodes appear in the pilot proof graph as accepted proof.

### 13. No product source files modified (src/net, src/python, tests/net, tests/python unchanged)
**PASS**
Evidence: Only files modified are in:
- `tools/requirements_authority/` (3 files: coverage_evaluator.py, overclaim_detector.py, validate_requirements_authority.py)
- `requirements-authority/fixtures/` (1 file: expected_coverage.json)
- `reports/requirement-capability-real-pilot-r1/` (all pilot reports)
- `tests/requirement_capability_authority/` (1 file: test_real_pilot_r1.py — new test file)
No src/net/**, src/python/**, tests/net/**, tests/python/** files modified.

### 14. No commits, no pushes, no MCP activation changes
**PASS**
Evidence: Sprint constraint affirmed. No git commit or push commands were executed.
CLAUDE.md prohibitions followed. MCP status unchanged from session-resume.md (ACTIVE MODE 4).

### 15. Spec Authority R2 evidence not mutated (frozen snapshot isolation)
**PASS**
Evidence: `input-snapshots/` directory contains frozen copies of R2 context packs with SHA-256 checksums.
`.local/evidences/spec-authority-real-pilot-r2/` — unchanged (no writes to this directory).
`00-preflight.md` — confirms R2 isolation approach.

---

## Summary

| Verdict | Count |
|---------|-------|
| PASS | 15 |
| PARTIAL | 0 |
| FAIL | 0 |

**Final Verdict:** `RCA_REAL_PILOT_R1_ACCEPTED_ALL_15_IV_CHECKS_PASS`

## Remaining Gaps (Not Blockers)

1. **FODT/SYLK Spec Authority not in R2**: FODT used fixture-backed input; SYLK not piloted.
   Future: Include FODT R3 spec and SYLK when available.
2. **Stale claim is synthetic**: The ZST stale claim was injected by the pilot driver for demonstration.
   Future: real staleness events will come from source-diff detection.
3. **Export claims require real target writer libraries**: FODS CSV/HTML and FODT Markdown/TXT exports
   remain blocked until standalone writer packages exist.
