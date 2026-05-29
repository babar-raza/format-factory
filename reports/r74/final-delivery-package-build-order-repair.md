# R74 Final Delivery Package Build-Order Repair

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** C

---

## Root Cause: R73 Stale SHA Defect (IV-R74-001)

The R73 inner evidence ZIP (r73-pass2-final.zip, SHA ffa23117...) contained a stale
`reports/r73/final-verdict.md` that showed:

- `BUNDLE_VALIDATION_PASS_2_SHA: e4784a0f...` (stale — pre-bundle value)
- `SIDECAR_SHA: fdff3bb9...` (stale)
- `DELIVERY_PACKAGE_RECORDED_SHA: 4f2b2917...` (stale)

**Root cause:** The ZIP was built from commit f2d0c6b state. Subsequent commits b7cc298 and 72c620f
updated final-verdict.md in the repo but no new ZIP build was triggered with those commits' state.
The ZIP on disk (ffa23117) was never replaced, so its internal final-verdict remained at the
f2d0c6b-era values.

This is a structural build-order violation: the inner ZIP claimed correct SHAs in its
external-facing reports, but the ZIP contents contradicted those claims.

---

## Two-Layer Final Artifact Protocol

### Layer Definition

**Layer 1 — Inner Evidence ZIP (self-contained, committed-state snapshot)**
- Built from a committed git HEAD
- Content snapshot must exactly match that HEAD — no file in the ZIP may differ from the committed repo
- The ZIP's internal final-verdict.md MAY have `DELIVERY_PACKAGE_RECORDED_SHA: external_delivery_manifest_authoritative` (semantic label) — it MUST NOT contain a concrete outer SHA (circular dependency: the outer package SHA cannot be known until the outer package is built, which happens after the ZIP is built)
- The ZIP's internal final-verdict.md MUST have the final PASS_2_SHA and SIDECAR_SHA filled in BEFORE the ZIP is built (not after)

**Layer 2 — Outer Delivery Package (standalone, generated-after artifacts)**
- Built AFTER the final git commit that seals Pass 2 SHA and Sidecar SHA
- Contains: inner ZIP + sidecar `.sha256-proof.json` + delivery manifest + supervisor readme
- The outer delivery manifest records: inner ZIP SHA, sidecar file SHA, outer package SHA
- The outer delivery manifest is the authoritative source for the outer package SHA
- Files inside the outer package that reference the outer SHA (e.g. delivery-manifest.json) are
  PART of the outer package and are generated simultaneously — they do not require a post-build commit

### Separation of Concerns

| Artifact | Who owns it | When built | May contain outer SHA? |
|---|---|---|---|
| Inner ZIP final-verdict.md | Committed repo file | After Pass 2 + Sidecar commits | No — use semantic label |
| Sidecar .sha256-proof.json | Generated (not committed) | After final commit | No |
| Delivery manifest .json | Generated (not committed) | After outer package exists | Yes |
| Outer delivery package .zip | Generated (not committed) | After inner ZIP + sidecar | N/A (it IS the outer) |

---

## Build Protocol (Canonical, R74+)

```
Step 1: Commit all source changes (clean git status required)
Step 2: Run full test suite — record AUTHORITATIVE_TEST_RESULT
Step 3: Update final-verdict.md with AUTHORITATIVE_TEST_RESULT
Step 4: Build Pass 1 bundle from committed HEAD
Step 5: Record BUNDLE_VALIDATION_PASS_1_SHA in final-verdict.md; commit
Step 6: Build Pass 2 bundle from committed HEAD (re-records same metadata; git-status-final.txt will be clean)
Step 7: Generate sidecar proof (write_sidecar_proof.py --validation-result PASS)
Step 8: Record BUNDLE_VALIDATION_PASS_2_SHA + SIDECAR_SHA in final-verdict.md; commit
        DELIVERY_PACKAGE_RECORDED_SHA must be set to: external_delivery_manifest_authoritative
Step 9: Build Pass 3 (final) bundle from committed HEAD — this ZIP now contains the correct SHAs
        because Step 8 committed them before this build
Step 10: Build outer delivery package from: Pass 3 ZIP + sidecar + delivery manifest + readme
Step 11: Record outer delivery SHA in delivery-package-validation-summary.txt (NOT in final-verdict.md)
         No git commit needed for outer-SHA-only metadata updates to untracked/local files
```

**Key invariant:** The final ZIP built in Step 9 must be built from the SAME git HEAD that contains
the filled-in PASS_2_SHA and SIDECAR_SHA. Steps 6-7-8-9 form an atomic sequence where the zip
in Step 9 is the authoritative product.

**Anti-pattern (R73 violation):** Build ZIP → update final-verdict → commit → no new ZIP build.
This leaves a ZIP whose internal state predates the final SHA commits.

---

## Validation (Self-Inspectable Check)

To verify no stale-SHA defect exists in the final ZIP, run:

```
unzip -p <sprint>-pass3-final.zip "repo/reports/<sprint>/final-verdict.md" | grep "BUNDLE_VALIDATION_PASS_2_SHA:"
```

The SHA shown MUST match the value in `reports/<sprint>/final-verdict.md` on disk.

R73 would have FAILED this check (zip shows e4784a0f, disk shows ffa23117).
R74 must PASS this check.

---

## Conclusion

The R73 defect was caused by skipping the final ZIP rebuild after committing the Pass 2 and
delivery SHAs. The two-layer protocol above prevents this by requiring the ZIP (Step 9) to be
built AFTER all SHA-update commits (Step 8). The outer delivery package SHA is never written
into the inner ZIP — only into standalone generated artifacts (delivery manifest) that are
part of the outer package, not the inner.

BUILD_ORDER_REPAIR: PASS
