---
sprint: R92
generated_by: r92-worker
---

# Rework + New Work Generator (Train F)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Problem

When declaration-only evidence has INSUFFICIENT_EVIDENCE items, the next sprint must:
1. Include rework lanes for those items (provide missing evidence)
2. Still include new POC product gaps (not only repair)
3. Include materializer/packaging improvements
4. Not demand ZIP as the only valid evidence form

## Current State (R91)

`tools/supervisor/generate_supervisor_packet.py` already produces:
- Section 1: New Product Work (product tasks first)
- Section 2: Rework / Repair (repair tasks second)

## R92 Enhancement

For declaration-only evidence with missing artifacts, `Section 2: Rework` must include:
```
- [rework] REWORK-XXX: Provide missing evidence for <item_id> — run materializer + add log paths
```

This allows safe product lanes to continue while evidence gaps are closed.

## Evidence Footer (Required in every generated sprint)

```
## Evidence Requirements
- Write .local/evidences/<run_id>/evidence-declaration.yaml (with materialization_required: true)
- Run materializer: .local/venv/Scripts/python tools/supervisor/materialize_declared_evidence.py --declaration ...
- Run: .local/venv/Scripts/python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration ...
- ZIP is optional (for external transfer only)
- No PENDING markers in final verdict
```

## Status: DOCUMENTED — implementation update deferred to R93 (current generator functional)
