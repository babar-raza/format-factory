# Adversarial Review

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Review Method

Independent reviewer attempts to find weaknesses, overclaims, and undetected gaps in the sprint deliverables.

## Questions Challenged

**Q1: Do the Lane 1 repairs actually fix the defects, or just document them?**

A: D-SUP-01 and D-SUP-02 are fixed by adding the relevant files to `required_repo_files` in the R80 contract. The bundle builder will include them. D-SUP-03 is fixed by using delegation labels in the inner final-verdict.md. D-SUP-04 is documented with a taskcard (TC-SUP-REPLAY-001) — not yet fixed, but clearly bounded as a known limitation.

Result: **PASS** — repairs are structural, not cosmetic.

**Q2: Do the R79 product tests prove the GAP-FODT-STRUCT-001 fix works in production?**

A: `TestFodtStructuralGapRepaired` includes `test_append_then_roundtrip_preserves_paragraph` which parses a real FODT file, appends a paragraph, writes it, re-parses, and verifies the paragraph is present. This is a functional roundtrip test. **PASS**.

**Q3: Can the supervisor validator be bypassed by crafting a bundle that passes all 9 tests but still has defects?**

A: Yes — the validator checks specific patterns. A bundle that doesn't claim supervisor run-on-latest will skip SUP-V-004. A bundle that uses delegation labels will pass SUP-V-005 regardless. These are design tradeoffs: the validator catches the most common failure modes without being too strict.

Result: **ACCEPTABLE LIMITATION** — validator is a quality floor, not a security boundary. Noted.

**Q4: Is the replay still truly missing a fixture? Can an external reviewer reproduce it?**

A: Yes — the replay input bundle (`.local/evidence/dual-orchestration-supervisor-e2e-20260530-165603.zip`) is gitignored and will not be in the R80 ZIP. An external reviewer cannot reproduce the supervisor replay from the ZIP alone. This remains an open limitation (TC-SUP-REPLAY-001). The replay output (`reports/supervisor/`) IS included.

Result: **ACCEPTABLE LIMITATION** — documented and taskcard-backed.

**Q5: Are any governance files modified?**

A: Checked: AGENTS.md, GOVERNANCE.md, plans/master-plan.md, registry/ — all unchanged (confirmed via git diff, none of these files appear in the diff).

Result: **PASS**.

**Q6: Is MODE 4 MCP activation still blocked?**

A: Yes. No `.vscode/mcp.json` created. No MCP servers registered. No Ruflo daemon started. No change to approval gate status.

Result: **PASS**.

**Q7: Are the R79 test files in the bundle even though they're untracked?**

A: Yes — `build_evidence_bundle.py` includes files listed in `required_repo_files` regardless of git tracking status, as long as the files exist in the working tree. Confirmed: `tests/packaging/test_r79_installed_fods_workflow.py` and `test_r79_package_source_sync.py` exist and are listed in the R80 contract.

Result: **PASS**.

**Q8: Does the final-verdict.md inside the ZIP use delegation labels? Or does it have a stale SHA?**

A: The `reports/r80/final-verdict.md` was written before the bundle build with `BUNDLE_SHA256: delegated_to_sidecar_proof`. This prevents the circular SHA problem. **PASS**.

## Summary

| Question | Result |
|---|---|
| Q1: Lane 1 repairs structural? | PASS |
| Q2: GAP-FODT-STRUCT-001 fix functional? | PASS |
| Q3: Validator bypassable? | ACCEPTABLE LIMITATION |
| Q4: Replay fixture missing? | ACCEPTABLE LIMITATION (TC-SUP-REPLAY-001) |
| Q5: Governance files untouched? | PASS |
| Q6: MODE 4 still blocked? | PASS |
| Q7: Untracked files in bundle? | PASS |
| Q8: Delegation labels used? | PASS |

**Score:** 6/8 PASS, 2 ACCEPTABLE LIMITATIONS
