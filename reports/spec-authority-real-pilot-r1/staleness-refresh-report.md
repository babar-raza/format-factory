# Staleness and Refresh Report — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Lane: F

---

## Staleness Engine

**Mechanism:** `check_staleness()` in `spec_digestor.py`

Algorithm:
1. Load stored digest from `.local/spec-artifacts/{source_id}-digest.json`
2. Compare `sha256_snapshot` in digest to current source SHA-256
3. If mismatch → `{"stale": True, "reason": "SHA256 changed: stored=... current=..."}`
4. If match → `{"stale": False, "reason": "Digest matches current snapshot."}`

---

## Real Source Staleness Results

All 4 pilot sources checked immediately after ingest — all fresh (expected: ingested in same session).

| Source | Stored SHA-256 | Current SHA-256 | Stale | Result |
|---|---|---|---|---|
| src-zst-rfc8878 | `c15ec66abc6489c0...` | `c15ec66abc6489c0...` | False | FRESH |
| src-netpbm-docs | `cec3030092754c36...` | `cec3030092754c36...` | False | FRESH |
| src-dif-softarts | `3065d192e05345a5...` | `3065d192e05345a5...` | False | FRESH |
| src-fods-oasis | `24e5975f6e7e2890...` | `24e5975f6e7e2890...` | False | FRESH |

**All sources: FRESH — no staleness detected.**

---

## Synthetic Staleness Test

**Goal:** Verify the staleness engine correctly detects when a source SHA-256 changes.
**Method:** Call `check_staleness("src-zst-rfc8878", "a" * 64)` — a fake current SHA-256.
**No real vault or digest files were mutated.**

| Test | Synthetic SHA | Stored SHA | Stale | Detected |
|---|---|---|---|---|
| Synthetic ZST stale | `aaaa...` (64 chars) | `c15ec66abc6489c0...` | True | **YES — DETECTED** |

**Result:** `stale=True, reason="SHA256 changed: stored=c15ec66abc6489c0... current=aaaaaaaaa..."`

Synthetic staleness test: **PASS** — engine correctly identifies when source has changed.

---

## Staleness Implications

When a source becomes stale:
- Downstream normalized artifacts may be invalid (parsed from old snapshot)
- Index may not reflect updated spec sections
- Digest content_digest may not match current source content
- Context packs referencing the stale source need recomputation

**Recomputation chain:** re-ingest → re-parse → re-normalize → re-index → re-digest → re-extract-requirements → rebuild-context-pack

---

## Missing Runtime Capabilities

The current implementation has staleness detection but lacks:
1. **Auto-trigger staleness scan**: No scheduled or event-driven staleness check
2. **Refresh pipeline**: No automatic re-ingest + pipeline re-run on stale detection
3. **Staleness propagation**: No mechanism to automatically mark downstream artifacts as stale

**Classification: KNOWN_LIMITATION — planned for Pilot R2**

---

## Recomputation Queue

See `recomputation-queue.json` for the advisory recomputation list (empty at sprint end — all sources fresh).
