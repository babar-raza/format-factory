# Spec Data Lifecycle Model — 13 States
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

All spec artifacts pass through a 13-state lifecycle. Transitions are enforced by SpecGovernanceRuntime.
No artifact may skip a state. State is recorded in the artifact's metadata record.

---

## State Definitions

| State | Code | Description | Entry Subsystem |
|-------|------|-------------|-----------------|
| A | source_candidate | Proposed source URL not yet registered | External / user |
| B | registered_source | Source approved in SpecSourceRegistry | SpecSourceRegistry |
| C | raw_snapshot | Immutable snapshot stored in SpecVault (sha256 assigned) | SpecVault |
| D | parsed_artifact | SpecParser produced structured JSON from raw snapshot | SpecParser |
| E | normalized_artifact | SpecNormalizer applied canonical cross-format schema | SpecNormalizer |
| F | indexed_artifact | SpecIndexer completed versioned indexing | SpecIndexer |
| G | digest_artifact | SpecDigestor produced compressed digest | SpecDigestor |
| H | candidate_requirement | RequirementExtractor produced unverified requirement | RequirementExtractor |
| I | verified_requirement | SpecVerifier confirmed requirement with provenance | SpecVerifier |
| J | context_pack | ContextPackBuilder assembled deterministic pack with manifest.sha256 | ContextPackBuilder |
| K | usage_record | ContextPack consumed; recorded in usage ledger | Usage ledger writer |
| L | coverage_record | Coverage validator evaluated requirement coverage | Coverage validator |
| M | refresh_event | Staleness check triggered re-ingestion from state B | SpecGovernanceRuntime |

---

## State Machine Transitions

```
source_candidate (A)
  ─[SpecSourceRegistry.register()]─► registered_source (B)
  ─[rejected]─► REJECTED (terminal, not in active pipeline)

registered_source (B)
  ─[SpecVault.ingest()]─► raw_snapshot (C)

raw_snapshot (C)
  ─[SpecParser.parse()]─► parsed_artifact (D)
  ─[source sha256 changed]─► triggers refresh_event (M) for all downstream

parsed_artifact (D)
  ─[SpecNormalizer.normalize()]─► normalized_artifact (E)
  ─[parse failed]─► PARSE_ERROR (re-try or manual review)

normalized_artifact (E)
  ─[SpecIndexer.index()]─► indexed_artifact (F)  [AND]
  ─[SpecDigestor.digest()]─► digest_artifact (G)  [AND]
  ─[RequirementExtractor.extract()]─► candidate_requirement (H)

indexed_artifact (F)
  ─[source sha256 changed]─► stale=true; must re-index before context pack build

digest_artifact (G)
  ─[included in ContextPack]─► context_pack (J)

candidate_requirement (H)
  ─[SpecVerifier.verify()]─► verified_requirement (I)
  ─[verification rejected]─► stays at H (rejection record created)

verified_requirement (I)
  ─[RequirementGraph.add()]─► included in graph (cross-cutting)
  ─[ContextPackBuilder includes]─► context_pack (J)

context_pack (J)
  ─[stream consumes]─► usage_record (K)
  ─[coverage validator runs]─► coverage_record (L)

usage_record (K)
  ─[terminal, append-only]

coverage_record (L)
  ─[gaps found]─► may trigger additional RequirementExtractor run

refresh_event (M)
  ─[re-ingest from registered_source (B)]─► new raw_snapshot (C)
  ─[all downstream from C marked stale]
```

---

## Stale Propagation Chain

When a raw_snapshot SHA-256 changes (source updated):
```
raw_snapshot (C) SHA changed
  → parsed_artifact (D): stale = true
  → normalized_artifact (E): stale = true
  → indexed_artifact (F): stale = true
  → digest_artifact (G): stale = true
  → candidate_requirement (H): stale = true
  → verified_requirement (I): stale = true (re-verification required)
  → context_pack (J): stale = true (cannot be used until refreshed)
```
SpecGovernanceRuntime blocks context pack build from stale artifacts.

---

## State Storage

Each artifact maintains a metadata record:
```json
{
  "artifact_id": "<uuid>",
  "state": "<state_code>",
  "source_snapshot_id": "<sha256>",
  "entered_at": "<ISO datetime>",
  "entered_by": "<subsystem_name>",
  "stale": false,
  "stale_reason": null
}
```

---

## Terminal States

| State | Terminal? | Notes |
|-------|-----------|-------|
| REJECTED | Yes | Source registration rejected |
| PARSE_ERROR | No | Re-try eligible |
| usage_record (K) | Yes | Append-only, never modified |
| coverage_record (L) | Yes | Point-in-time evaluation |
| refresh_event (M) | Quasi-terminal | Creates new pipeline from B |
