---
visibility: generated
generated_by: codex
---

# Full-Suite Failure Triage

The authoritative repository-wide Python run completed with:

`6835 passed, 12 failed, 26 skipped`

The failures are inherited repository-state defects outside the R90 governed
Python Netpbm source edit:

| Failure group | Count | Inherited cause |
|---|---:|---|
| `tests/evidence/test_auto_proof_bundle.py` | 5 | Tracked R84 sidecar `reports/r84/r84-pass3-final.sha256-proof.json` is embedded in generated bundles. |
| `tests/evidence/test_r28_evidence_automation.py` | 1 | Existing R88 evidence contract lacks `contract_id` or `verdict`. |
| `tests/evidence/test_r84_review_package_top_level_artifacts.py` | 2 | Existing R84 review package lacks `raw-package-install-logs/` and `final-metadata/` top-level directories. |
| `tests/invariants/` | 3 | Same tracked R84 sidecar violates `INV-006`. |
| `tests/packaging/test_r60_artifact_source_commit.py` | 1 | Stale assertion expects 10 packages; existing artifact report contains 11 including SYLK. |

R90 focused validation remains clean:

- Supervisor acceleration tests: `101 passed`
- Python Netpbm tests: `351 passed`
- .NET FODS tests: `191 passed`
- .NET FODT tests: `176 passed`
- .NET Netpbm tests: `94 passed`
- Product-code ledger validation: `PASS`

R90 does not silently repair or delete inherited artifacts outside the sprint
scope. The generated next sprint must carry these as explicit repair work.
