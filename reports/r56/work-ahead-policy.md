# R56 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-23

## Scope Boundaries

### What R56 MAY do

1. Add tests for any feature claimed in R55 or R56 deliverables
2. Implement FODT hyperlink preservation (`text:a` parse + write round-trip)
3. Implement FODT nested list hierarchy (2+ levels, `text:list` inside `text:list-item`)
4. Advance CSV/TSV to Gate 5 (neutral model + sample/oracle proof)
5. Add writer/export support for PGM/PBM/PPM if tractable
6. Advance SYLK and DIF with deepening tests
7. Build Python wheels for fods/fodt (R55 changed them; rebuild required for correctness)
8. Run .NET bounded verification with dotnet SDK 10.0.204
9. Audit acquisition spec-cache for 4+ formats
10. Run AI fixture-mode tests (no live endpoint unless authorized)
11. Update format-completion-matrix.yaml after tests pass
12. Create fods.yaml and fodt.yaml in release-manifests/python-foss/
13. Repair R55 scoreboard to reflect actual delivery state

### What R56 MUST NOT do

1. Push to remote repository
2. Publish any package to PyPI or NuGet
3. Self-approve Gate 8 or Gate 11
4. Set `commercial_product_ready: true`
5. Run `git reset --hard`, `git stash drop`, or `git clean -f`
6. Hide stale R55 reports by overwriting them — use R56 corrective authority files
7. Emit nested `.zip` files into the final R56 bundle metadata without explicit contract documentation
8. Claim package RC complete unless wheel artifacts are physically inside `bundle-metadata/package-artifacts/`
9. Use R55 `final-bundle-validation-proof.txt` as valid evidence for R56

## Work-Ahead Rule

Any train that completes early MUST look for the next safe adjacent work:
- Train A finishes IV → begin Train J doc sync for R55-relevant facts
- Train B finishes validator tests → run them to confirm pass
- Train C finishes hyperlinks → run FODT test suite to confirm no regression
- Train D finishes wheels → run package smoke from extracted artifact dir, not source tree
- Train F finishes format advancement → update matrix if tests pass
