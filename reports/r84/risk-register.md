# R84 Risk Register

**Sprint:** FORMAT-FACTORY-R84
**Date:** 2026-05-31

## Risk 1: 3-Pass Bundle Build Complexity

**Risk:** 3-pass bundle protocol adds complexity; any PENDING remaining in final-verdict triggers validator failure.
**Mitigation:** Clear sequencing checklist; validator catches PENDING before sidecar is written.
**Severity:** HIGH

## Risk 2: build_supervisor_review_package.py Modification

**Risk:** Adding top-level dirs to review package changes the tool behavior and may break existing tests.
**Mitigation:** Add new --extra-top-level-dirs parameter; keep existing behavior intact.
**Severity:** MEDIUM

## Risk 3: ZST Dependency Classification

**Risk:** Including zstandard wheel adds legal/license provenance responsibility.
**Mitigation:** Classify ZST as DEPENDENCY_RESOLUTION_REQUIRED instead; include raw failing log.
**Severity:** LOW (we take the classification path)

## Risk 4: .NET Test Environment

**Risk:** dotnet SDK version mismatch or missing test binaries.
**Mitigation:** Run dotnet --info first; capture exact SDK; if fail, document blocker.
**Severity:** MEDIUM

## Risk 5: Full Test Suite Count Drift

**Risk:** New tests may not be collected in all configurations.
**Mitigation:** Run targeted R84 test files + verify count before bundle build.
**Severity:** LOW

## Risk 6: Supervisor Loop Trigger

**Risk:** supervisor_loop.py may fail or be blocked.
**Mitigation:** Capture exit code and output; document blocker if any.
**Severity:** LOW

## Risk 7: Review Package Size

**Risk:** Adding raw logs + all directories at top level may make review package large.
**Mitigation:** Accept larger size; review package is evidence artifact, not distribution.
**Severity:** LOW
