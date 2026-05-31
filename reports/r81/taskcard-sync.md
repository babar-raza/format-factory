# Taskcard Sync

**sprint_id:** FORMAT-FACTORY-R81-FINAL-ARTIFACT-REPAIR-R79-CLOSURE-PRODUCT-ADVANCEMENT-VALIDATOR-HARDENING-20260530

## Open Taskcards (Carried Forward)

### TC-SUP-REPLAY-001
- **Title:** Include supervisor replay fixture in future bundles
- **Status:** OPEN
- **What's needed:** After running `supervisor_loop.py run-on-latest` against a real prior bundle, package the input fixture (prior bundle ZIP + contract) as `replay-input.zip` inside the evidence ZIP.
- **Blocked by:** Requires a supervisor run-on-latest execution in a clean environment.

### TC-R79-CLOSURE-001
- **Title:** Commit R79 product code and build R79 evidence bundle
- **Status:** OPEN
- **What's needed:** Explicit human approval to `git commit` R79 product changes, then run `build_evidence_bundle.py` with the R79 contract.
- **Blocked by:** Governance rule — no commit without explicit human request.

## New Taskcards (Created This Sprint)

### TC-R81-SIDECAR-DELIVERY-001
- **Title:** Include sidecar proof inside bundle or deliver as part of a multi-file package
- **Status:** OPEN
- **Background:** R80 reviewer ran validator without sidecar proof file, causing validation failure. Sidecar is external by design but must accompany the bundle.
- **Options:** (a) Include sidecar JSON in `reports/<sprint>/` as required_repo_file — implemented in R81; (b) deliver as a multi-file package ZIP.
- **Resolution in R81:** R80 sidecar included in R81 bundle as `reports/r81/r80-sidecar-proof.json`. Pattern established for future sprints.

### TC-R81-AUTHORITATIVE-TEST-001
- **Title:** Add AUTHORITATIVE_TEST_RESULT to all future sprint evidence bundles
- **Status:** OPEN (partially resolved in R81)
- **What's needed:** Every sprint must include a metadata file with `AUTHORITATIVE_TEST_RESULT: N passed, M failed, K skipped` as a top-level field, covering the full test suite run for that sprint.
- **Validator enforcement:** See Lane 3 hardening.

### TC-R81-IV-NO-PLACEHOLDER-001
- **Title:** Prevent [to be filled] placeholders in IV/fresh-extract reports inside bundle
- **Status:** OPEN (resolved in R81 via two-pass build)
- **What's needed:** IV files must be written with actual results (or delegation labels for SHA-circular fields) before bundle build. Never use `[to be filled]` as a value — use delegation labels instead.
- **Validator enforcement:** SUP-V-010 added to validate_supervisor_evidence_bundle.py (Lane 3).

### TC-R79-WHEEL-SELF-CONTAINED-001
- **Title:** Include FODS wheel artifact in evidence bundles for installed-wheel test portability
- **Status:** OPEN
- **Background:** `test_r79_installed_fods_workflow.py` has 8 tests that require the FODS wheel installed. In a fresh-extract environment, these skip. To enable 8/8 pass from fresh extract, include `format_factory_fods-0.1.0.dev0-py3-none-any.whl` in the bundle.
- **Where:** `installed_artifact_policy: self_contained` in contract + wheel listed in required_repo_files + test detects wheel from bundle and installs it.
