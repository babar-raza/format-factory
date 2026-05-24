# R62 R61 Defect Ledger

**Sprint:** FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
**Date:** 2026-05-24

| ID | Severity | Category | Description | Repair Train | Status |
|----|----------|----------|-------------|--------------|--------|
| IV-R61-001 | critical | sidecar | External sidecar not delivered with uploaded ZIP | Train C | REPAIRED |
| IV-R61-002 | critical | sidecar | Contract sidecar_required: true but no sidecar present | Train C | REPAIRED |
| IV-R61-003 | critical | validation | Validation without sidecar fails (not self-verifying) | Train C | REPAIRED |
| IV-R61-004 | high | proof | Internal proof SHA ≠ uploaded ZIP SHA (must use sidecar) | Train C | REPAIRED |
| IV-R61-005 | high | packaging | Python wheels/sdists absent from R61 bundle | Train D | REPAIRED |
| IV-R61-006 | medium | packaging | Python artifact manifest references external R60 bundle | Train D | REPAIRED |
| IV-R61-007 | high | installed | R61 new Python APIs not proven from installed wheels | Train E | REPAIRED |
| IV-R61-008 | medium | ai | AI was fixture/passive only; no contradiction reviewer | Train B | REPAIRED |
