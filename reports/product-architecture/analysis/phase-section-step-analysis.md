# Phase-Section-Step Analysis
Generated: 2026-07-04

## TC-ARC-000 (Preflight)
Children: 000-01 (plan read + authority) → 000-02 (preflight record) → 000-03 (deep analysis) → 000-04 (requirements + traceability) → 000-05 (DAG + state machine + verdict)
Micro-steps: ~24 total. Output: 39 artifact files in reports/product-architecture/analysis/.

## TC-ARC-001 (Authority Binding)
Children: 001-01 (read registry files) → 001-02 (HEAD SHA) → 001-03 (SAL counts) → 001-04 (write mission.yaml)
Micro-steps: ~16. Output: architecture-mission.yaml with confirmed authority sources + SAL totals.

## TC-ARC-002 (Dual Architecture Contract)
Children: 002-01 (Python FODS spec+Compat) → 002-02 (.NET FODS inspection) → 002-03 (Python CSV) → 002-04 (write contract)
Key finding to document: Python FODS = MINOR_REALIGNMENT (models.py wraps dicts); .NET FODS = QNAME_MODEL_DECOMPOSITION.

## TC-ARC-003 (QName Hierarchy)
Children: 003-01 (read canonical-class-inventory) → 003-02 (qname-coverage) → 003-03 (office+table nodes) → 003-04 (style+text nodes) → 003-05 (write+validate)
Output must have ≥13 QName nodes with all owning_type fields populated.

## TC-ARC-004 (Source Layout)
Children: 004-01 (survey all format dirs) → 004-02 (.NET targets) → 004-03 (Python targets) → 004-04 (write file)
Output: 30 entries with target_layout + delta fields.

## TC-ARC-005 through TC-ARC-018
Each follows the pattern in plan-part-deep-analysis.yaml. Execution order enforced by dependency DAG.
