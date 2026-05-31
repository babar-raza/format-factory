# Memory Sync

**sprint_id:** FORMAT-FACTORY-R81-FINAL-ARTIFACT-REPAIR-R79-CLOSURE-PRODUCT-ADVANCEMENT-VALIDATOR-HARDENING-20260530

## Facts Updated in MEMORY.md

### R80 True Verdict
- R80 bundle validates with sidecar: BUNDLE_VALIDATION: PASS, SIDECAR_PROOF_VALIDATION: PASS
- R80 review found 8 defects (D-R80-01 through D-R80-08)
- R80 clean closure not accepted: IV files had [to be filled], AUTHORITATIVE_TEST_RESULT missing, sidecar not delivered alongside bundle

### R81 Sprint
- Sprint ID: FORMAT-FACTORY-R81-FINAL-ARTIFACT-REPAIR-R79-CLOSURE-PRODUCT-ADVANCEMENT-VALIDATOR-HARDENING-20260530
- Run number: r81
- Key repairs: sidecar included in bundle, AUTHORITATIVE_TEST_RESULT added, IV files pre-filled, R79 wheel claim corrected

### Installed-Wheel Test Behavior
- `test_r79_installed_fods_workflow.py`: 8 tests pass with wheel installed locally; 8 skip in extracted env without wheel
- Both are CORRECT behavior — tests have appropriate skip logic
- Claim must be: "8 passed (local, wheel installed)" or "8 skipped (extracted, no wheel)"

### New Taskcards
- TC-R81-SIDECAR-DELIVERY-001: include sidecar inside bundle
- TC-R81-AUTHORITATIVE-TEST-001: AUTHORITATIVE_TEST_RESULT in every bundle
- TC-R81-IV-NO-PLACEHOLDER-001: no [to be filled] in IV files inside bundle
- TC-R79-WHEEL-SELF-CONTAINED-001: wheel artifact in bundle for installed-wheel portability

### Pattern: Two-Pass Bundle Build
To avoid circular SHA dependency with IV files:
1. Build Pass 1 → compute SHA → fill IV files with Pass 1 SHA
2. Build Pass 2 (IV files have Pass 1 SHA — one-generation-behind)
3. Generate sidecar for Pass 2 — sidecar is authoritative
This is the established R75+ pattern. The inner SHA in IV reports will be Pass 1's SHA; the sidecar proves Pass 2's SHA.
