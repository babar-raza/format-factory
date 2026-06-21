# Capability Layer Audit

**Sprint:** forensics-archaeology-20260621

---

## Infrastructure

### Tools

```
tools/supervisor/capability_compiler.py       — Capability-to-feature compiler (EXECUTABLE)
tools/supervisor/capability_verifier.py       — Verifier
tools/supervisor/capability_queue_consumer.py — Queue consumer
tools/capability_layer/                       — (check for additional tools)
```

### Data Files

```
reports/capability-layer/
├── gap-ledger.json                 (958 gaps)
├── unified-capability-map.json     (all formats)
├── commercial-capability-map.json  (.NET commercial)
├── foss-reduced-capability-map.json (Python FOSS)
├── gap-audit-2026-06-21.json       (latest audit)
├── investigation-matrix.md
├── investigation-report.md
├── action-queue.json               (pending actions)
└── pilots/                         (pilot definitions)
```

---

## Gap Ledger Analysis

- **Total gaps:** 958
- **Severity distribution:** All `severity: "unknown"` — the severity field is not populated
- **Status distribution:** Reviewed sample gap (`GAP-FODS-COMM-LOAD-001`) shows `status: "closed"`
- **Implication:** Either most gaps are closed (which would be good), or the status field is not maintained

### Gap ID Patterns

Sampled 20 gap IDs:
```
GAP-FODS-COMM-LOAD-001              (status: closed)
GAP-FODS-COMM-SAVE_SAME_FO-001
GAP-FODT-COMM-LOAD-001
GAP-FODT-COMM-SAVE_SAME_FO-001
GAP-Netpbm-COMM-SAVE_SAME_FO-001
GAP-CSV-FOSS-PROBE_CSV-001
GAP-DIF-FOSS-PROBE_DIF-001
GAP-FODG-FOSS-PROBE_FODG-001
GAP-FODS-COMM-RELOAD_AND_V-001
GAP-FODT-COMM-RELOAD_AND_V-001
GAP-Gnumeric-FOSS-PROBE_GNUMER-001
GAP-PBM-FOSS-PROBE_PBM-001
GAP-PGM-FOSS-PROBE_PGM-001
GAP-PPM-FOSS-PROBE_PPM-001
GAP-QOI-FOSS-PROBE_QOI-001
GAP-XCF-FOSS-PROBE_XCF-001
GAP-ABW-FOSS-WRITE_ABW-001
GAP-ABW-FOSS-EXPORT_TO_CS-001
GAP-ABW-FOSS-EXPORT_TO_JS-001
GAP-ABW-FOSS-EXPORT_TO_MA-001
```

**Format families:** FODS, FODT, CSV, DIF, FODG, Gnumeric, Netpbm, PBM, PGM, PPM, QOI, XCF, ABW
**Capability types:** LOAD, SAVE_SAME_FORMAT, RELOAD_AND_VALIDATE, PROBE, WRITE, EXPORT_TO_*

---

## Capability Compiler Assessment

The `capability_compiler.py` tool exists and is executable. Key findings:

1. **Loads SAL facts** — `load_sal_facts()` reads from `.local/sal-output/sal-facts-latest.json`
   (different path than `.local/spec-cache/` — potential path mismatch issue)

2. **Format family metadata** hardcoded — `FORMAT_FAMILIES` dict lists 15+ formats with
   spec, module_base, and family. This is static configuration, not dynamically derived.

3. **Gap record driven** — compiler takes `--gap-record` JSON input and generates taskcards
   from gap definitions. This means it IS gap-ledger-aware, not hardcoded like old pipeline.

4. **Output:** generates taskcards into `.local/evidences/<run_id>/taskcards/generated/`

**Verdict:** The capability compiler EXISTS and is PARTIALLY OPERATIONAL for formats with SAL
facts. For formats with 0 SAL facts (CSV, XCF), it generates generic taskcards without
spec-literal content.

---

## Does Capability Layer Consume SAL Facts?

**Answer: PARTIALLY**

- The compiler reads SAL facts from a specific path (`sal-facts-latest.json`)
- For FODS/FODT: YES — SAL facts are available and the compiler can reference them
- For CSV/XCF: NO — 0 facts, compiler falls back to generic generation
- The gap ledger itself does NOT encode SAL fact references — gaps have format/capability type but no `fact_ref` field
- The capability map files do not appear to directly reference FACT-FORMAT-NNN IDs

**Gap:** The pipeline from spec_fact → capability → feature is NOT end-to-end. Facts influence
generation only when the compiler explicitly queries the SAL cache for a format. There is no
systematic "capability is backed by fact F1, F2, F3" tracing.

---

## Advisory-Only Problem

Per the spec-to-feature correction plan: "gap-ledger.json is NEVER read by task generation;
action-queue has `advisory_only: true` on ALL items."

This appears to have been partially addressed — the capability compiler now takes gap records
as explicit input. But whether the autonomous task generator ACTUALLY feeds gap records to the
compiler during sprint generation is unconfirmed.

---

## Capability Layer Readiness

| Component | Status |
|-----------|--------|
| Gap ledger | EXISTS — 958 gaps, poor metadata quality |
| Capability compiler | EXISTS — partially executable |
| SAL fact consumption | PARTIAL — ODF formats only |
| Gap-to-taskcard pipeline | EXISTS — needs verification |
| Capability-to-feature tracing | MISSING — no fact_ref on gap records |
| CI integration | MISSING |

**Rating:** Orange — infrastructure exists but integration is incomplete and tracing is absent.
