# Requirements-vs-Actual Matrix

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Scope:** All major system claims as of R53

## Status Key

| Status | Meaning |
|--------|---------|
| MET | Evidence fully supports the claim |
| PARTIALLY_MET | Evidence supports part of the claim; gap exists |
| NOT_MET | Claim is not supported by evidence |
| OVERCLAIMED | Claim was stated but evidence shows it is false |
| STALE | Evidence is outdated and needs refresh |
| CONTRADICTORY | Multiple pieces of evidence conflict |
| NOT_VERIFIABLE | Insufficient information to determine status |

## Governance / Evidence

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-GOV-001 | Bundle built by build_evidence_bundle.py, validated by validate_evidence_bundle.py | MET | — |
| REQ-GOV-002 | EVIDENCE_BUNDLE: printed only after BUNDLE_VALIDATION: PASS | MET | — |
| REQ-GOV-003 | Final proof must not have PASS 2 PENDING for clean baseline | PARTIALLY_MET | R52 had PENDING; R53 introduces sidecar protocol |

## Physical Invariants

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-PHYS-001 | INV-001 through INV-005 PASS | MET | — |

## State / Final-Verdict Consistency

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-STATE-001 | state/current-state.md reflects latest sprint verdict | PARTIALLY_MET | R52 state overclaims; R53 will correct |
| REQ-STATE-002 | Validator detects Format C verdict (## Verdict + backtick) | MET | — |

## Final Proof / Sidecar

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-PROOF-001 | External sidecar proof file exists for each bundle | PARTIALLY_MET | R52 sidecar retroactive; R53 produces sidecar in closeout |

## Package Artifact Baseline

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-PKG-001 | Sprint claiming baseline contains artifacts or has explicit policy | NOT_MET (R52) | R52 overclaimed; R53 creates policy |
| REQ-PKG-002 | Installed Python wheels smoke from extracted bundle | PARTIALLY_MET | No fresh R52/R53 extracted-bundle smoke |
| REQ-DOTNET-001 | .NET nupkgs install + consumer proof | PARTIALLY_MET | dotnet test path hangs; last known pass: R51 |

## Object Model

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-OBJ-001 | FODS/FODT parse→edit→save→reload | MET | 402 Python tests pass |

## Preservation

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-PRES-001 | TC-0054: FODS formula preservation | MET | R53: 7 tests pass |
| REQ-PRES-002 | TC-0057: FODT heading preservation | NOT_MET | Not implemented |
| REQ-PRES-003 | TC-0058: FODT list preservation | NOT_MET | Not implemented |
| REQ-PRES-004 | TC-0059: FODT table preservation | NOT_MET | Not implemented |

## Export Dogfooding

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-EXPORT-001 | FODT TXT export dogfooding proof | PARTIALLY_MET | Export exists; no installed-wheel replay |

## AI / LLM

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-AI-001 | No ungoverned LLM calls | MET | Scan found 1 governed call only |
| REQ-AI-002 | No false embeddings/retrieval claim | MET | Lexical: real; Vector: explicitly deferred |
| REQ-AI-003 | Agent Metrics telemetry proof | PARTIALLY_MET | Fixture mode; no live post in R52/R53 |

## Phase Audits

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-PHASE-001 | Phase Audit 4 CONDITIONAL_PASS gaps tracked | PARTIALLY_MET | TC-0054 closed; 3 of 4 TCs still open |

## Memory / Self-Verification

| ID | Requirement | Status | Gap |
|----|-------------|--------|-----|
| REQ-MEM-001 | Memory entry for current sprint | MET | memory/58-r53-... created |
| REQ-MATRIX-001 | Requirements-vs-actual matrix | MET | This document |
| REQ-GAP-001 | Gap ledger with taskcards | MET | reports/r53/gap-ledger.md |

## Summary Counts

| Status | Count |
|--------|-------|
| MET | 11 |
| PARTIALLY_MET | 8 |
| NOT_MET | 4 |
| OVERCLAIMED | 0 (R52 corrected) |

All NOT_MET and PARTIALLY_MET items have entries in the gap ledger.
