# Overlap Check
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

## Parallel Sprint: Spec Authority R2
- Status: COMPLETED (ACCEPTED) — no active changes
- Input isolation: All R2 inputs taken as frozen snapshots (one-time copy, SHA-256 recorded)
- Write prohibition: reports/spec-authority-real-pilot-r2/ and .local/evidences/spec-authority-real-pilot-r2/ are FORBIDDEN writes
- No live dependency on R2 output files

## File Ownership

### Owned by this sprint (write-allowed)
- reports/requirement-capability-real-pilot-r1/**
- .local/evidences/requirement-capability-real-pilot-r1/**
- .local/supervisor/reviews/requirement-capability-real-pilot-r1/**
- tests/requirement_capability_authority/** (new test file)

### Shared reads (read-only)
- .local/evidences/spec-authority-real-pilot-r2/context-packs/ (frozen snapshots)
- product-capability-matrix/poc-targets.yaml (read-only)
- registry/format-registry.yaml (read-only)
- src/net/**, src/python/** (read-only)
- tests/supervisor/test_r100_*.py (read-only)

### Forbidden writes
- src/net/**, src/python/**
- tests/net/**, tests/python/**
- product-capability-matrix/poc-targets.yaml
- registry/format-registry.yaml
- reports/spec-authority-real-pilot-r1/**
- reports/spec-authority-real-pilot-r2/**

## Contradictions: None detected.
## Overlap with Spec Authority R2: None (R2 is COMPLETE, inputs frozen).
