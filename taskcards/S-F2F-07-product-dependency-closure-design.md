# Taskcard S-F2F-07: Product Dependency Closure Design

## 1. Taskcard ID and Title
S-F2F-07: Product Dependency Closure Design (Documentation Only)

## 2. Status
proposed_pending_human_approval

## 3. Purpose
Create design documentation for Python AST-based and Roslyn-inspired product dependency
closure strategies. This taskcard produces design documents ONLY — no schemas, no tools,
no placeholder files, no stubs. The documents describe how a future tool would trace the
public API surface of src/python/{format}/ and src/net/{format}/ to determine
FOSS/commercial boundaries. Implementation requires product gate authorization (Gate 10+).
This taskcard itself requires FODS Gate 8 PASSED plus explicit human authorization.

## 4. Phase
P1 — Product Dependency Closure Design

## 5. Scope
- docs/product-dependency-closure.md (overview of both language tracks)
- docs/python-product-closure-strategy.md (Python AST strategy)
- docs/dotnet-product-closure-strategy.md (Roslyn-inspired strategy)
NO schemas, NO tools, NO placeholder files.

## 6. Out of Scope
- schemas/product/ (not in this sprint — requires separate explicit authorization)
- tools/product/ (not in this sprint)
- src/python/ (product source not started)
- src/net/ (product source not started)
- Any parser, neutral model, or sample
- Any gate changes

## 7. Inputs
- plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md (Layer 7 design notes)
- docs/governance/release-control.md (FOSS/commercial boundary policy)
- plans/master-plan.md (Section 4: Feature Tier Model)

## 8. Outputs
- docs/product-dependency-closure.md
- docs/python-product-closure-strategy.md
- docs/dotnet-product-closure-strategy.md

## 9. Exact Files Allowed
- docs/product-dependency-closure.md
- docs/python-product-closure-strategy.md
- docs/dotnet-product-closure-strategy.md
- tools/evidence/contracts/s-f2f-07-product-closure-design.yaml (sprint contract)
- memory/ (if updated)

## 10. Exact Files Forbidden
- schemas/product/**
- tools/product/**
- src/python/**
- src/net/**
- Any schema files (JSON or YAML) for product API surface
- Any stub or placeholder implementation files
- registry/format-registry.yaml

## 11. Validation Commands
```bash
# Design docs exist
ls docs/product-dependency-closure.md && echo "OK"
ls docs/python-product-closure-strategy.md && echo "OK"
ls docs/dotnet-product-closure-strategy.md && echo "OK"
# No schema or tool files created
ls schemas/product/ 2>/dev/null && echo "FAIL: schemas/product exists" || echo "OK"
ls tools/product/ 2>/dev/null && echo "FAIL: tools/product exists" || echo "OK"
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-07-*.zip \
  --contract tools/evidence/contracts/s-f2f-07-product-closure-design.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-07-product-closure-design.yaml
BUNDLE_VALIDATION: PASS required
Must confirm schemas/product/ and tools/product/ are ABSENT.

## 13. Rollback
Delete docs/product-dependency-closure.md.
Delete docs/python-product-closure-strategy.md.
Delete docs/dotnet-product-closure-strategy.md.
Revert commit.

## 14. MAIN SPRINT Non-Deviation Rule
This sprint creates documentation files only. No gate changes. No registry modifications.
MAIN SPRINT is unaffected.

## 15. Format-Agnostic Requirement
All three docs must describe strategies that apply to any format in src/python/{format}/
and src/net/{format}/, not just FODS or FODT.

## 16. Approval Required Before Execution
HARD PREREQUISITE: FODS Gate 8 (security review) must be PASSED before this sprint can begin.
Human authorization prompt must explicitly name "S-F2F-07 Product Dependency Closure Design"
AND confirm Gate 8 is PASSED.
Schema and tool creation require SEPARATE explicit authorization after docs are reviewed.

## 17. Dependencies
- FODS Gate 8: PASSED (hard prerequisite — not currently satisfied as of run044)
- S-F2F-00: completed (plan repair)
- This taskcard is gated on product-track progress, not playbook system progress

## 18. Done Definition
DONE when:
- All 3 design docs present and non-empty (>= 200 lines each)
- ZERO schema files in schemas/product/
- ZERO tool files in tools/product/
- Docs clearly state "no implementation until Gate 10+ authorization"
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit
