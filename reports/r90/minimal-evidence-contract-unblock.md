---
visibility: generated
generated_by: codex
---

# Minimal Evidence Contract Unblock

R89 fresh validation produced `BUNDLE_VALIDATION: FAIL` and `SIDECAR_PROOF_VALIDATION: PASS`.
The R89 sidecar is truthful for hash integrity but wrong to claim canonical validation pass.

R90 will include an exact `AUTHORITATIVE_TEST_RESULT:` metadata line in its declaration evidence
directory and will not claim ZIP bundle validation success unless a fresh validator run succeeds.
The eight shallow R89 metadata files are not rebuilt because R90 uses the declaration-driven path.
