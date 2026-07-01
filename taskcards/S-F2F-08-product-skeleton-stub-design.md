# Taskcard S-F2F-08: Product Skeleton/Stub Design

## 1. Taskcard ID and Title
S-F2F-08: Product Skeleton/Stub Design (Documentation Only)

## 2. Status
proposed_pending_human_approval

## 3. Purpose
Create design documentation for a product skeleton/stub generator that would produce
minimal compilable stubs for src/python/{format}/ and src/net/{format}/ based on the
public API surface determined by S-F2F-07 (Product Dependency Closure Design). This
taskcard produces a design document ONLY — no generator tool, no stub files, no placeholder
implementations. Implementation requires product gate authorization (Gate 10+). This
taskcard itself requires P1 (S-F2F-07) complete AND Gate 10 progress AND explicit human
authorization.

## 4. Phase
P2 — Product Skeleton/Stub Design

## 5. Scope
- docs/product-skeleton-generator.md (design document only)
  - Must describe the skeleton generator algorithm for any format_id
  - Must describe Python stub generation strategy (src/python/{format}/)
  - Must describe .NET stub generation strategy (src/net/{format}/)
  - Must explicitly state: no implementation until Gate 10+ authorization
  - Must be >= 150 lines

NO tool files. NO stub files. NO placeholder implementations. NO src/python/ or src/net/ files.

## 6. Out of Scope
- tools/product/ (not in this sprint)
- src/python/ (product source not started)
- src/net/ (product source not started)
- schemas/product/ (requires separate explicit authorization after docs reviewed)
- Any actual stub or skeleton file
- Any parser, neutral model, or sample
- Any gate changes

## 7. Inputs
- docs/product-dependency-closure.md (output of S-F2F-07)
- docs/python-product-closure-strategy.md (output of S-F2F-07)
- docs/dotnet-product-closure-strategy.md (output of S-F2F-07)
- plans/master-plan.md (Section 4: Feature Tier Model)
- docs/governance/release-control.md (FOSS/commercial boundary policy)

## 8. Outputs
- docs/product-skeleton-generator.md

## 9. Exact Files Allowed
- docs/product-skeleton-generator.md
- tools/evidence/contracts/s-f2f-08-product-skeleton-design.yaml (sprint contract)
- memory/ (if updated)

## 10. Exact Files Forbidden
- tools/product/**
- src/python/**
- src/net/**
- schemas/product/**
- Any stub, skeleton, or placeholder implementation files
- Any tool implementation files
- registry/format-registry.yaml

## 11. Validation Commands
```bash
# Design doc exists
ls docs/product-skeleton-generator.md && echo "OK"
# No implementation or stub files created
ls tools/product/ 2>/dev/null && echo "FAIL: tools/product exists" || echo "OK"
ls src/python/ 2>/dev/null && echo "FAIL: src/python exists" || echo "OK"
ls src/net/ 2>/dev/null && echo "FAIL: src/net exists" || echo "OK"
ls schemas/product/ 2>/dev/null && echo "FAIL: schemas/product exists" || echo "OK"
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-08-*.zip \
  --contract tools/evidence/contracts/s-f2f-08-product-skeleton-design.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-08-product-skeleton-design.yaml
BUNDLE_VALIDATION: PASS required
Must confirm tools/product/, src/python/, src/net/, and schemas/product/ are ABSENT.

## 13. Rollback
Delete docs/product-skeleton-generator.md.
Revert commit.

## 14. MAIN SPRINT Non-Deviation Rule
This sprint creates a documentation file only. No gate changes. No registry modifications.
MAIN SPRINT is unaffected.

## 15. Format-Agnostic Requirement
docs/product-skeleton-generator.md must describe a skeleton generator strategy that applies
to any format in src/python/{format}/ and src/net/{format}/, not just FODS or FODT. The
format_id must be a required parameter in any described generator algorithm.

## 16. Approval Required Before Execution
HARD PREREQUISITES (all three must be satisfied):
1. S-F2F-07 (Product Dependency Closure Design) must be COMPLETED — the three design docs
   (docs/product-dependency-closure.md, docs/python-product-closure-strategy.md,
   docs/dotnet-product-closure-strategy.md) must exist and have been reviewed by a human.
2. Gate 10 progress must be demonstrated for at least one format (product-track gates).
3. Human authorization prompt must explicitly name "S-F2F-08 Product Skeleton/Stub Design"
   AND confirm S-F2F-07 is completed AND Gate 10 progress.

Tool and implementation creation require SEPARATE explicit authorization after docs are reviewed.

## 17. Dependencies
- S-F2F-07: COMPLETED (hard prerequisite — not currently satisfied)
- Gate 10 progress: must be demonstrated (hard prerequisite — not currently satisfied;
  FODS is currently at Gate 7 planning_ready as of run044)
- P1 docs reviewed by human before P2 can begin

## 18. Done Definition
DONE when:
- docs/product-skeleton-generator.md present and non-empty (>= 150 lines)
- Document clearly describes skeleton generator algorithm (format-agnostic)
- Document explicitly states "no implementation until Gate 10+ authorization"
- ZERO tool files in tools/product/
- ZERO source files in src/python/ or src/net/
- ZERO schema files in schemas/product/
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit
