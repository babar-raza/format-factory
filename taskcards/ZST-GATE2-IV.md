---
taskcard_id: ZST-GATE2-IV
title: "ZST Gate 2 — Independent Verification Sprint — Pending Authorization"
type: gate_packet
sprint: null
created_by_sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
created_at: "2026-05-15"
status: pending_authorization
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
---

# Taskcard: ZST-GATE2-IV

## Purpose

Per DEC-034 (AGENTS.md §V), an independent agent verification sprint is required before
presenting Gate 2 evidence for human review. This taskcard tracks that verification sprint.

## DEC-034 Requirement

> "Agent-requested human review requires independent agent verification sprint first
> (separate session)."

Gate 2 was executed by R14. Before any human is asked to formally review Gate 2, an
independent verification sprint in a separate session must:
1. Re-validate RFC 8878 + RFC 9659 SHA-256 checksums
2. Confirm spec-index.yaml entries are valid
3. Re-run tests/skills/test_zst_spec_cache_gate2.py (20 tests)
4. Verify registry gate_2 fields match evidence
5. Confirm no forbidden artifacts (generated requirements, src mutations)

## Current State

Gate 2 evidence is: `evidence_cached_pending_independent_verification`

## Trigger

Issue IV execution prompt: FORMAT-FACTORY-ZST-GATE2-IV-SWARM-001 (separate session)
