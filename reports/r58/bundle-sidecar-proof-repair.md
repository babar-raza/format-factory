# R58 Bundle/Sidecar/Proof Protocol Repair

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Train:** B
**Date:** 2026-05-24

---

## Problem Repaired

R57 defects IV-R57-002 and IV-R57-003:
- Sidecar committed to repo was bundled INSIDE the ZIP under `repo/reports/r57/`
- Sidecar schema used `bundle_sha256` field; validator expected `sha256`

---

## Protocol Repair

### Canonical sidecar schema (write_sidecar_proof.py)

write_sidecar_proof.py already produces canonical `sha256` field. The R57 failure was due
to manual sidecar writing that used `bundle_sha256`. Protocol enforcement:
- New sidecars MUST use `sha256` as the primary field
- Validator now accepts `bundle_sha256` as backward-compat fallback only
- R58 forward: always use `write_sidecar_proof.py`, never write sidecar manually

### Sidecar must not be committed to repo

The sidecar `.sha256-proof.json` proves the final ZIP's SHA-256. If it's committed to the
repo, it gets bundled inside the ZIP under `repo/`, making it unable to prove the ZIP's SHA
(circular dependency). Fix:
- Do not commit sidecar to repo
- Write sidecar to `.local/` (gitignored) only
- The repo-committed `reports/r57/r57-pass2-final.zip.sha256-proof.json` is a historical record of R57 state (not a valid proof)

### New validator check: check_repo_sidecar_not_inside_zip

Added to `tools/evidence/validate_evidence_bundle.py`:
```python
def check_repo_sidecar_not_inside_zip(zf, bundle_path) -> list[str]:
```
Detects when a sidecar for the current bundle is embedded inside the ZIP.

### New validator check: backward compat for bundle_sha256

```python
claimed_sha = sidecar.get("sha256") or sidecar.get("bundle_sha256", "")
```
Allows R57-style sidecars to still validate during the transition period.

---

## Previously Unwired Checks Now Wired

Functions that existed in R56 but were never called:
- `check_scoreboard_finality` — now wired in Train C
- `check_embedded_sidecar_bundle_match` — now wired
- `check_nested_zips_allowed` — now wired
- `check_package_claim_policy_consistency` — now wired

---

## Tests Added

- tests/evidence/test_r58_external_sidecar_protocol.py (9 tests)
- tests/evidence/test_r58_sidecar_schema_canonical.py (11 tests)
- tests/evidence/test_r58_embedded_sidecar_rejected.py (9 tests — covers B+C)

**All 29 tests: PASS**
