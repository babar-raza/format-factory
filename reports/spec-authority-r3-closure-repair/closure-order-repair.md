# Closure Order Repair
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001
Lane: B — Closure Order Repair
Generated: 2026-06-05

## Problem

The R3 sprint built the review package ZIP partway through the closure sequence,
before final-git-status.txt was created and before review-package-proof.md had
real values. This created 3 closure-order defects (C2, C3, C4).

## Correct Closure Order (Invariant)

The ZIP must be the LAST artifact built. The correct order is:

```
Step 1:  Run all tests; capture raw logs
Step 2:  Create final-git-status.txt
Step 3:  Create final-adversarial-independent-verification.md
Step 4:  Write evidence-declaration.yaml (complete, with all paths)
Step 5:  Write evidence-manifest.yaml (complete)
Step 6:  Run autonomous-cycle --declaration ...
Step 7:  Verify exit code = 0; check anti-skip violations = 0
Step 8:  [ONLY AFTER exit 0 and 0 violations]:
         Write review-package-proof.md (with placeholder SHA initially)
Step 9:  Run build_declaration_review_package.py
Step 10: Compute SHA-256, byte-size, file-count from the actual ZIP
Step 11: Update review-package-proof.md with actual SHA, byte-size, file-count
Step 12: Verify internal consistency:
         - proof SHA == sha256.json zip_sha256
         - proof byte-size == sha256.json zip_size_bytes
         - proof artifacts_missing == sha256.json artifacts_missing_count (= 0)
Step 13: NO FURTHER FILE CHANGES after Step 11 (ZIP is now final)
         If review-package-proof.md is included in the ZIP:
           → Rebuild ZIP after Step 11 and recompute SHA
           → Loop once: Step 9→10→11 again (proof now has correct hash)
           → ZIP is now self-consistent
```

## Why the R3 ZIP Is Not Self-Consistent

The R3 ZIP was built at a point analogous to Step 9 above, but:
- Step 2 (final-git-status.txt) had not yet been done
- Step 11 (updating proof with real SHA) had not yet been done
- Step 8 produced a placeholder proof

Result: ZIP contains outdated proof and missing final-git-status.

## Tooling Fix: Not Required

No tooling change is needed. The build_declaration_review_package.py tool
works correctly. The issue was execution order, not tooling.

The fix is operational: enforce the closure order documented above.

## R3C Implementation

For R3C, the closure order is:
1. All report files created (Lanes A–F complete)
2. final-git-status.txt created
3. evidence-declaration.yaml written with all paths
4. evidence-manifest.yaml written
5. Autonomous-cycle run (exit 0)
6. build_declaration_review_package.py run
7. SHA-256 computed
8. review-package-proof.md written with actual SHA
9. No further changes to any file

Since review-package-proof.md is included in the evidence_artifacts, and the ZIP
is built BEFORE review-package-proof.md has real values, there is an inherent
chicken-and-egg. The solution: review-package-proof.md is NOT listed in evidence_artifacts.
Instead, it is listed only as a report_created path. This way the ZIP is built
before the proof, the proof is written after the ZIP, and there is no self-reference.
