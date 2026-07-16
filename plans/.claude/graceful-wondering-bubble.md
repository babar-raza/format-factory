# GAP-FORENSIC-008 as a Symptom: SAL Layer Production Hardening + QOI Op-Code Seeding

## Context

GAP-FORENSIC-008 reports that QOI's 7 op-codes (OP_RGB, OP_RGBA, OP_INDEX, OP_DIFF, OP_LUMA, OP_RUN, OP_END) have zero SAL facts, so the DECODE_PIXELS capability has working code but no spec-backed justification (chain `BROKEN_AT_B2`). The bounded fix — add 7 facts, backfill references — treats the symptom. Investigation shows the symptom is produced by structural defects in the SAL layer that will regenerate this same class of gap on every rerun unless fixed. This plan fixes the machinery first, then seeds QOI through the hardened path.

## Symptoms vs Root Causes vs Structural Weaknesses

### Symptoms (visible)
- **S1** — QOI: 3 facts for 10 raw spec units (`spec_to_fact_ratio=0.3`); DECODE_PIXELS untraceable. Per `raw-spec-unit-register.yaml`, XCF (also binary) has 42/42 = 1.0 and ABW 36/36 = 1.0 — QOI is an outlier against the repo's own achieved standard, not a norm for binary formats.
- **S2** — Stale denormalized counts: `python-qname-architecture.json` says `sal_facts_count: 2` for QOI (real: 3), 2 for XCF (real: 42), 2 for TOML (real: 65).
- **S3** — Stale gap ledger: `GAP-CHAIN-QOI-SAL-MRH-001` claims 0 QOI facts exist (real: 3).
- **S4** — Capability overclaim: 126 QOI capabilities trace to 3 facts (`fact_to_cap_ratio=42`, worst in portfolio); capabilities are `POC_DERIVED_NOT_SPEC_DERIVED`.

### Root causes
- **RC-A: No completeness gate at the spec→fact boundary (B2).** Facts were seeded manually (June 2026, `sal_master_runner.py`, `structural_fact_manual`) with no check against a spec-unit inventory. The denominator (10 raw units) was only computed retroactively by a one-time forensic audit. Nothing prevents the next format from shipping at ratio 0.3.
- **RC-B: The canonical fact store is ephemeral.** `.local/spec-cache/sal-facts-latest.json` (14,644 facts) is gitignored (`.gitignore:7`), yet ~20 tools read it (`audit_sal_to_qname.py`, `capability_compiler.py`, `autonomous_cycle.py`, …). The committed truth is fragmented: `shared/sal-fact-overrides.yaml` (partial overlay, admits in its own header it exists "so facts survive fresh checkout"), `shared/sal-fact-id-aliases.json`, registry snapshots. A fresh checkout cannot reconstruct the database from committed artifacts.
- **RC-C: Lossy, order-dependent merge semantics.** `merge_sal_facts.py:144-155` **replaces** the entire per-format entry when the per-format file has more facts. FACT-QOI-003 (added directly to the combined DB by TC-SAL-CLOSE-13) would be silently destroyed by the next merge because it isn't in `sal-facts-qoi.json`. Count-comparison ("more wins") is a clobber with a guard, not a merge.
- **RC-D: Denormalized counts with no reconciliation.** `sal_facts_count`, `total_aliases`, `spec_facts_total` are hand-maintained in 4+ files; no validator recomputes them. Drift is monotonic and invisible (S2, S3).
- **RC-E: No fact→code binding at the granularity capabilities are claimed.** `spec_fact_ref` is scalar and class-level; the op-code constants in `qoi_parser.py:35-40` (`QOI_OP_RGB = 0xFE` …) are never mechanically checked against any fact. Traceability is asserted in registries, never verified against source.

### What breaks consistency across reruns
1. Ephemeral canonical store → different sessions/machines see different fact databases (RC-B).
2. Clobber-merge → final DB depends on the *order* of taskcard operations; direct-DB additions are lost on the next merge (RC-C).
3. Three coexisting fact schema variants (FACT-QOI-001/002 minimal style, FACT-QOI-003 provenance-block style, FODS workbench style) — each writer picks one, each consumer normalizes differently.
4. Every writer must remember to update every denormalized copy; none reliably do (RC-D).
5. Gap registers and reports are point-in-time snapshots that contradict the data they describe within weeks (S3).

## What to Preserve (works, don't weaken)

- **Coarse qname architecture.** 3 QOI qnames with op-codes as `Chunk.CHUNK_TYPES` matches the repo-wide pattern (FODS 4,988 facts/12 qnames; ZST 94/3; XCF 42/4). Facts are fine-grained; qnames are structural. No new qnames, no new spec classes.
- **SAL-* stable ID scheme** + `sal-fact-id-aliases.json` mapping.
- **`audit_sal_to_qname.py`** — already override-aware; keep as-is.
- **The overrides-overlay concept** — it is the embryo of the correct design (committed supplement); it's just partial.
- **`raw-spec-unit-register.yaml`** — the completeness denominator already exists; reuse it, don't rebuild it.
- **Merge tool's never-downgrade instinct** — keep the property, change the mechanism to fact-level union.
- **Oracle layer** — QOI oracle is VERIFIED; semantic decode correctness stays the oracle's job, not SAL's.

## Design

**Pivot:** for manually-seeded formats, the committed layer becomes canonical and `.local/` becomes a derived artifact; merges become union-by-fact_id; reconciliation becomes a registered governance validator instead of a forensic discovery.

### Phase 1 — Canonical committed per-format fact stores

Create `shared/sal-facts/{format}.yaml` (committed) for the 14 manually-seeded formats listed in `merge_sal_facts.py:_FORMAT_FILE_CANDIDATES` (csv, tsv, toml, abw, dif, gnumeric, sylk, ndjson, xcf, zst, qoi, pbm, pgm, ppm). One normalized schema per `schemas/sal-facts/sal-facts-schema.json` `spec_fact` def, with `fact_id` **mandatory** and `qname` (legacy FACT-*) retained for compatibility.

Migration: a one-shot script exports each format's current entry from `sal-facts-latest.json` (union'd with `sal-fact-overrides.yaml` entries) into the committed file. For QOI this yields the existing 3 facts; Phase 3 adds 7 more.

**Deliberately out of scope:** FODS/ODS/ODT/FODT/FODP (thousands of extraction-pipeline facts with PDFs as provenance). Different problem, working pipeline — don't destabilize it. The committed-store pattern covers exactly the formats whose facts have no reproducible source.

### Phase 2 — Merge tool: union semantics + drift check

Rewrite `merge_sal_facts.py` merge core:
- Union by `fact_id` (fall back to `qname` for legacy records). Existing facts never dropped.
- Conflict (same `fact_id`, different `claim`) → hard error listing both; never silent overwrite.
- Deterministic output: facts sorted by `fact_id`, stable JSON key order → reruns byte-identical.
- New `--check` mode: reports per-format divergence between committed store, per-format cache, and combined DB without writing; exit non-zero on drift. This is what CI/governance calls.
- Regression test suite `tests/tools/test_merge_sal_facts.py` including the explicit FACT-QOI-003-loss scenario (per-format file missing a fact that exists in combined → union preserves it).

### Phase 3 — Seed QOI op-code facts (the original gap, via the hardened path)

Add to `shared/sal-facts/qoi.yaml` (then compile to `.local/` via the Phase-2 tool):

| ID | SAL ID | element_qname | Claim (spec §3, "QOI Specification 2021") |
|----|--------|---------------|-------|
| FACT-QOI-004 | SAL-QOI-00004 | qoi:op-rgb | QOI_OP_RGB: tag 0xFE (0b11111110), 3 payload bytes r,g,b; 4 bytes total |
| FACT-QOI-005 | SAL-QOI-00005 | qoi:op-rgba | QOI_OP_RGBA: tag 0xFF (0b11111111), 4 payload bytes r,g,b,a; 5 bytes total |
| FACT-QOI-006 | SAL-QOI-00006 | qoi:op-index | QOI_OP_INDEX: 2-bit tag 0b00, 6-bit index into 64-entry running pixel array; 1 byte |
| FACT-QOI-007 | SAL-QOI-00007 | qoi:op-diff | QOI_OP_DIFF: 2-bit tag 0b01, dr/dg/db 2-bit each, bias 2 (range −2..1); 1 byte |
| FACT-QOI-008 | SAL-QOI-00008 | qoi:op-luma | QOI_OP_LUMA: 2-bit tag 0b10, 6-bit dg (bias 32) + 4-bit dr−dg / db−dg (bias 8); 2 bytes |
| FACT-QOI-009 | SAL-QOI-00009 | qoi:op-run | QOI_OP_RUN: 2-bit tag 0b11, 6-bit run length, bias −1 (run 1..62; 63/64 reserved) |
| FACT-QOI-010 | SAL-QOI-00010 | qoi:op-end | QOI_OP_END: 8-byte terminator 7×0x00 + 0x01 (op-level encoding; stream semantics = FACT-QOI-003) |

Then update the derived/companion stores:
- `shared/sal-fact-id-aliases.json`: 7 new aliases; `total_aliases` 14650 → 14657 (Phase 4 validator recomputes this thereafter).
- `shared/sal-fact-overrides.yaml`: 7 entries (audit-tool compatibility until the committed store is wired in everywhere; `added_by: GAP-FORENSIC-008`).
- `registry/python-qname-architecture.json` QOI entry: `sal_facts_count`/`_consolidated` → 10, `source_fact_ids` → all 10 slugs, `last_updated` → 2026-07-15.
- `registry/python-qname-structural-facts.json`: 7 approved entries (qname `qoi:op-rgb` … `qoi:op-end`).
- `shared/qname-registry/qoi.yaml`: **no change** (`spec_fact_ref` is scalar by schema; `qoi:chunk` keeps SAL-QOI-00002 as the aggregate).

### Phase 4 — Reconciliation + completeness validator (registered, recurring)

One new governance validator (register per repo protocol; MEMORY.md: safe range V183–V188, count 210 → 211), running in `governance_validator_runner.py`:

1. **Count reconciliation:** recompute per-format fact counts from the stores; compare against `sal_facts_count` in `python-qname-architecture.json` and `total_aliases`/`spec_facts_total` headers. Mismatch → FAIL with expected/actual. Kills the S2/S3 drift class permanently, for all formats.
2. **Alias completeness:** every `fact_id` in committed stores has an alias entry; every `spec_fact_ref` in `shared/qname-registry/*.yaml` resolves.
3. **Completeness gate (B2):** for formats present in `raw-spec-unit-register.yaml` with state `ACCEPTED_VERIFIED`, `normalized_fact_count / raw_spec_units ≥ 0.8`. Below threshold → FAIL naming the format. QOI passes at 10/10 after Phase 3; currently-failing formats (netpbm per GAP-FORENSIC-007, ZST per -009) surface honestly as findings rather than being silently grandfathered — expect this and register follow-up gaps rather than lowering the threshold.

### Phase 5 — Fact→code binding for op-codes

Add optional `code_bindings` to fact records in the committed store:

```yaml
code_bindings:
  - file: src/python/qoi/qoi_parser.py
    symbol: QOI_OP_RGB
    expected: "0xFE"
```

The Phase-4 validator (or a sibling check in it) parses the file with `ast` and asserts the module-level constant equals `expected`. All 7 QOI facts get bindings (`qoi_parser.py:35-40` constants + `QOI_END_MARKER:29`). This converts "backfilled registry array" into a mechanically re-verified link on every governance run — the property that makes the fix durable across reruns.

**Honest limit:** this proves the constants match the spec claims, not that decode branch logic is correct. Branch semantics remain covered by the oracle (VERIFIED, 73/73) and roundtrip tests — correct separation of concerns, not a gap.

### Phase 6 — Close gaps as derived outcomes

- `forensic-gap-register.yaml` GAP-FORENSIC-008 → CLOSED with closure evidence.
- `gap-ledger` GAP-CHAIN-QOI-SAL-MRH-001 → updated (its "0 facts" claim corrected; close or re-scope).
- Re-run/refresh `pilots/qoi-pilot.yaml`: DECODE_PIXELS `chain_verdict: COMPLETE`, `spec_to_fact_ratio: 1.0`, ANOM-B12-005 resolved.
- `raw-spec-unit-register.yaml` QOI row: `normalized_fact_count: 10`, ratio 1.0.

## Execution Notes (repo governance)

- Registry/data seeding is not `src/` editing, but route through governed skills where they exist: `/ingest-spec-sal` covers fact ingestion mechanics; validator registration follows the validator-registry protocol (EP-3/EP-4).
- No product source changes; no oracle changes; no gate state changes.
- Order matters: Phases 1–2 (machinery) before Phase 3 (data) — per EP-4, don't push product-adjacent data through broken machinery; the QOI seed is the pilot proving the hardened path.

## Verification

1. **Merge tool tests:** `.venv/Scripts/pytest tests/tools/test_merge_sal_facts.py -v` — union, conflict-error, FACT-QOI-003-loss regression, determinism (two runs byte-identical).
2. **Drift check:** `python tools/spec/merge_sal_facts.py --check` → exit 0 across all covered formats after seeding.
3. **Audit:** `python tools/audit_sal_to_qname.py` → 0 QOI gaps.
4. **New validator:** run standalone against QOI (counts reconcile, aliases complete, ratio 1.0, 7/7 code bindings pass), then full `governance_validator_runner.py` → no regressions elsewhere, expected new findings on known-incomplete formats documented as gaps.
5. **Product tests:** `.venv/Scripts/pytest tests/python/qoi/ -q` → no regressions (no product code touched; this is a control).
6. **Fresh-checkout simulation:** in a temp clone/worktree without `.local/`, run the compile step → combined DB QOI entry regenerates with 10 facts, byte-identical on rerun.

## Tradeoffs, Risks, Limits

- **Repo weight vs reproducibility:** committing 14 per-format stores adds files, but replaces a fragmented 3-store overlay system with one canonical + one derived cache. Net complexity down; disk cost trivial (these formats have 2–94 facts each).
- **Scope boundary:** the ODF-family extraction pipeline is untouched. Its facts stay reproducible via its own pipeline; the committed-store pattern targets exactly the facts that currently have *no* reproducible source. If the extraction pipeline has its own drift problems, that is a separate investigation — not claimed solved here.
- **Merge-semantics change risk:** ~20 tools read the combined DB, but the file's schema is unchanged (same shape, plus mandatory `fact_id` on covered formats), so consumers should be unaffected. "Should" — verified by the full governance run and `--check` across all 25 formats before relying on it, not asserted.
- **Threshold honesty:** the 0.8 completeness gate will flag netpbm and ZST (known gaps GAP-FORENSIC-007/-009). That is the gate working. The cost is visible red until those are seeded; the alternative (grandfathering) recreates exactly the silent-gap failure mode this plan exists to remove.
- **Binding granularity limit:** constant-level assertions only. A wrong bias or bit-shift in a decode branch would pass the binding check and be caught only by the oracle. Accepted division of labor.
- **Dual end-marker facts (003 stream-level vs 010 op-level):** intentional but slightly redundant; documented in both facts' descriptions to prevent a future "dedup" from re-breaking the chain.


## Taskcard Status Summary

| TC-ID | Status | Evidence |
|-------|--------|----------|
| TC-GWB-001 | CLOSED | Phase 1: 14 committed stores at shared/sal-facts/*.yaml (427 facts); tools/spec/export_sal_fact_stores.py |
| TC-GWB-002 | CLOSED | Phase 2: merge_sal_facts.py union semantics + --check + bootstrap; tests/tools/test_merge_sal_facts.py 11/11 PASS |
| TC-GWB-003 | CLOSED | Phase 3: 7 QOI op-code facts SAL-QOI-00004..00010 seeded; aliases 14657; overrides 8 QOI entries; arch counts reconciled (9 formats) |
| TC-GWB-004 | CLOSED | Phase 4: V225 validator (governance_validators_ext7.py) registered; runner count 222, 0 skipped; tests/tools/test_governance_validator_v225.py 10/10 PASS |
| TC-GWB-005 | CLOSED | Phase 5: code_bindings on all 7 op-code facts verified against src/python/qoi/qoi_parser.py (7/7 pass in V225) |
| TC-GWB-006 | CLOSED | Phase 6: GAP-FORENSIC-008 CLOSED; GAP-CHAIN-QOI-SAL-MRH-001 CLOSED; qoi-pilot.yaml FULL_TRACEABILITY; raw-spec-unit-register qoi 10/10 |
| TC-GWB-007 | CLOSED | Verification: drift check exit 0; audit 0 QOI gaps; governance 222 ran/0 FAIL; QOI tests 819 pass; fresh-checkout bootstrap 14 formats/434 facts idempotent |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-15T14:53:28.077726+00:00"
  locked_by: "7600e39c6acc"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
