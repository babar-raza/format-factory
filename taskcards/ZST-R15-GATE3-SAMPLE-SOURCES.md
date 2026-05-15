---
taskcard_id: ZST-R15-GATE3-SAMPLE-SOURCES
title: "ZST Gate 3 — Sample Source Acquisition — Pending R15 Authorization"
type: gate_packet
sprint: null
created_by_sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
created_at: "2026-05-15"
status: pending_authorization
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
---

# Taskcard: ZST-R15-GATE3-SAMPLE-SOURCES

## Current State: PENDING_AUTHORIZATION

Gate 2 has been passed. Gate 3 (sample source acquisition) is NOT yet authorized.
A separate R15 execution prompt is required to begin sample source identification.

Note per delegated execution model (GOVERNANCE.md §2.1a): this taskcard does NOT
constitute a live "Babar must approve" blocker for delegation purposes. Gate 3 simply
has not been authorized yet. An R15 execution prompt authorizes it.

## Gate 3 Work (NOT YET STARTED)

1. Identify open-license .zst sample files from authoritative sources
2. Record candidate sample sources (URLs only — no downloading without Gate 3 authorization)
3. Classify each source: license, provenance, open/proprietary
4. Create sample-sources.md in acquisition-packs/zst/
5. Prepare Gate 3 evidence

## Pre-conditions for R15

- Gate 2 PASSED: YES (R14, 2026-05-15)
- RFC 8878 + RFC 9659 cached: YES
- spec-evidence.md complete: YES
- Gate 3 IVswarm recommended before human review (DEC-034)

## Trigger

Issue R15 prompt: FORMAT-FACTORY-R15-ZST-GATE3-SAMPLE-SOURCE-ACQUISITION-SWARM-001
