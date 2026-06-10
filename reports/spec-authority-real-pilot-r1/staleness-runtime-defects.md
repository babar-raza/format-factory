# Staleness Runtime Defects
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Summary

The staleness detection subsystem (`spec_digestor.py::check_staleness()`) functioned
correctly for all 4 pilot sources. One limitation was identified — no auto-trigger
mechanism exists to enqueue recomputation automatically when staleness is detected.

## Staleness Check Results

All 4 sources returned `status: "FRESH"` in Pilot R1 (expected — fixture SHA-256
does not change between runs).

Synthetic test: Providing an altered SHA-256 for `src-zst-rfc8878` correctly returned
`status: "STALE"` with `stale: true`. See `staleness-test-result.json`.

## Defects

### D-STALE-001 — No automatic recomputation trigger
**Symptom:** `check_staleness()` returns `stale: true` but no downstream recomputation
is triggered automatically. The caller must manually check the return value and initiate
recomputation.
**Root cause:** `spec_digestor.py` is a pure computation module with no side effects.
No observer/event system exists.
**Impact:** A stale source could be used for requirement extraction without refreshing.
**Severity:** MEDIUM — safe for fixture-based Pilot R1; risk increases for Pilot R2 with
real network fetches.
**Proposed fix for R2:** Add a `recomputation_queue.jsonl` append in `check_staleness()`
when `stale: true`. The queue is polled by the pilot coordinator before each pipeline run.

### D-STALE-002 — No timestamp-based staleness (TTL)
**Symptom:** Staleness is computed from SHA-256 comparison only. A source that has been
re-fetched with identical content (same SHA-256) is always FRESH, even if the fetch is old.
**Root cause:** No TTL or last-fetched-at check in the digest model.
**Impact:** For RFC text that is amended with errata (same URL, different content), staleness
detection works correctly (SHA-256 will differ). For sources with TTL requirements (e.g.,
re-check every 30 days), no mechanism exists.
**Severity:** LOW for Pilot R1 (fixture-based, no TTL needed).
**Proposed fix for R2:** Add `last_ingested_at` field to vault snapshot; support optional
`max_age_days` in source registration.

## No Blocking Defects

Both defects are non-blocking for Pilot R1. The `recomputation-queue.json` produced by the
pilot driver shows an empty queue (expected — all sources FRESH).

## Verdict

`STALENESS_FUNCTIONAL_FOR_PILOT_R1 — 2_NON_BLOCKING_DEFECTS_DOCUMENTED_FOR_R2`
