# R85 Train A — Current Direction Correction

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Problem: Prior Direction

R83/R84 treated evidence closure (3-pass SHA bundle, sidecar proof, scoreboard COMPLETE) as the sprint's primary success criterion.
Product factory POC progress was measured secondarily.

This is backwards. Evidence is support infrastructure. The product is the success criterion.

## Correction Applied

### 1. memory/27-r85-product-factory-direction.md (NEW)
Core direction document. Required reading for all R85+ work.
Records:
- Evidence is support infrastructure, not finish line
- POC targets: 3 commercial .NET + 3 FOSS reduced
- Product success = load+edit+save+export+dogfood from installed package
- Local supervisor replaces manual ChatGPT handoff
- Dogfooding requirement with gap documentation protocol

### 2. memory/00-index.md (UPDATED)
Row added for memory/27-r85-product-factory-direction.md with summary.

### 3. .supervisor/project-memory.md (UPDATED)
R85 entry appended:
- direction_corrected: true
- product_factory_primary_goal: true
- evidence_role: SUPPORT_INFRASTRUCTURE_NOT_FINISH_LINE
- poc targets, supervisor loop, no commercial_product_ready

### 4. plans/master-plan.md — Section 40 (NEW)
Section 40 "Product-Factory POC Direction (R85+)" added at end of master-plan.
Includes:
- Mission restatement (repeatable product factory)
- POC targets table (3 commercial + 3 FOSS)
- Product success criteria (load/edit/save/export/dogfood)
- Dogfooding requirement (gap documentation protocol)
- Local supervisor loop mandate
- No-drift anchors

## docs/current-state-and-evidence-authority.md
Status: REVIEWED — existing content already frames evidence as authority chain.
No destructive edits. R85 addendum recorded in master-plan Section 40 instead.

## docs/commercial-product-capability-model.md
Status: REVIEWED — C0-C10 model exists. No change needed.
R85 Section 40.3 (product success criteria) aligns with C7+ definition.

## Correctness Verification

| Correction | Applied | Verified |
|-----------|---------|---------|
| memory/27 created with direction | YES | Read back confirmed |
| memory/00-index.md updated | YES | Row present |
| .supervisor/project-memory.md updated | YES | R85 entry appended |
| master-plan Section 40 added | YES | Section present |
| No overclaim of current product completion | YES | commercial_product_ready: false everywhere |
| No destruction of prior evidence records | YES | All prior SHA/bundle entries preserved |

## TRAIN_A_STATUS: COMPLETE
