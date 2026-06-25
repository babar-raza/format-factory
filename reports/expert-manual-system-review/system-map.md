# System Map — Format Factory
# Expert Manual System Review Phase 1
# Generated: 2026-06-25

## Overview

Format Factory is a commercial library factory system with two product tracks:

1. **.NET Commercial Track** — 10 projects under `src/net/`, targeting NuGet publication
2. **Python FOSS Track** — 20 packages under `src/python/`, targeting PyPI publication (Apache-2.0)

These product tracks are governed, validated, and accelerated by an autonomous machinery layer.

## Product Layer

### .NET Products (src/net/)

| Project | Format Type | LOC | Commercial Gate | Notes |
|---------|-------------|-----|-----------------|-------|
| FormatFactory.Fods | Spreadsheet (flat XML) | 3,569 | G11-G Approved | Strongest product. Full DOM, 7 exporters |
| FormatFactory.Fodt | Document (flat XML) | 2,543 | G11-G Approved | Strong. Full DOM, 5 exporters |
| FormatFactory.Netpbm | Image family | 1,940+ | In progress | Rich transforms/filters/analyzer |
| FormatFactory.Csv | Tabular | 380 | In progress | Thin. Load/save only |
| FormatFactory.Tsv | Tabular | 410 | In progress | Thin. Has CSV dogfood export |
| FormatFactory.Ndjson | JSON lines | 419 | In progress | Thin. Has CSV dogfood export |
| FormatFactory.Zst | Compression | 233 | In progress | Probe-only. NO decompression. |
| FormatFactory.Html | Target writer | 118 | Not a format product | Utility for FODS/FODT exporters |
| FormatFactory.Markdown | Target writer | 84 | Not a format product | Utility for FODT exporter |
| FormatFactory.Txt | Target writer | 70 | Not a format product | Utility for FODT exporter |

### Python FOSS Products (src/python/)

| Package | Format Type | Key LOC | Write | Export | Compat/ | Notes |
|---------|-------------|---------|-------|--------|---------|-------|
| fods | Spreadsheet | Full | YES | YES | 12 | Most complete Python product |
| fodt | Document | Full | YES | YES(txt/md/html) | 10 | Most complete Python product |
| abw | Document | Full | YES | YES | 2 | AbiWord format |
| csv | Tabular | Full | YES | — | 3 | Has csv_writer.py |
| dif | Spreadsheet | Medium | YES | YES(html) | 3 | DIF format |
| fodg | Drawing | Large (fodg_codec) | YES | YES(txt/json) | 2 | OpenDocument Drawing |
| fodp | Presentation | Medium | NO write_fodp | YES(txt/csv/json) | 2 | Read+export only |
| gnumeric | Spreadsheet | 760 | YES | YES(csv/json) | — | Dict model |
| ndjson | JSON lines | 570+analytics | YES | — | 1 | Full model |
| ods | Spreadsheet (ZIP) | Medium | YES | YES(csv) | — | Has ods_writer.py |
| odt | Document (ZIP) | Medium | YES | — | — | ODT writer added |
| pbm | Bitmap image | Medium | NO | YES(pgm/ppm) | — | P1/P4 format |
| pgm | Grayscale image | Medium | NO | YES(ppm) | — | P2/P5 format |
| ppm | Color image | Medium | NO | — | — | P3/P6 format |
| qoi | Image | Medium | YES(encoder) | — | — | QOI format |
| sylk | Spreadsheet | 741 | YES(file-based) | YES(csv) | 3 | File-based mutations |
| toml | Config | 728 | YES | — | — | TOML format |
| tsv | Tabular | Medium | YES | — | 3 | Tab-separated |
| xcf | Image | 1,272 | NO | — | — | GIMP format |
| zst | Compression | 1,549 | NO raw | — | — | Via zstandard library |

## Autonomous Machinery Layer

### Supervisor Infrastructure

```
tools/supervisor/
├── autonomous_cycle.py       (2,406 LOC) — Main sprint execution cycle
├── check_continuation.py     (~500 LOC) — Continue/stop decisions
├── governance_validators.py  (3,181 LOC) — 50 validators (V1-V68)
├── sprint_executor.py        (Large)    — Sprint runner with many modes
├── grade_declared_work.py    (Large)    — LLM-based evidence grader
├── generate_next_worker_prompt.py        — Next sprint prompt generation
├── stop_reason_adjudicator.py            — Classifies stop signals
├── gap_ledger_to_work_items.py           — Converts gaps to work items
├── capability_feature_compiler.py        — Compiles capabilities
├── autonomous_task_generator.py          — Task generation
├── write_plan_lock.py                    — Plan lock management
└── [40+ more scripts]
```

### Skills Layer (.supervisor/skill-registry.yaml)

- **65 skills** registered
- registry_status: active_fail_closed
- Notable: add-analytics-function is deprecated (still in registry)
- Notable: several skills have empty implementation_paths (prompt-only enforcement)
- Missing CI: ci_transcript_verification skill is backlog

### Specification Authority Layer

```
.local/spec-cache/
├── sal-facts-fods.json    (4,988 facts) — CHAIN_INTACT
├── sal-facts-fodt.json    (4,936 facts) — CHAIN_INTACT
└── [10 more formats]      — CHAIN_BROKEN_AT_SAL
```

### Requirement & Capability Authority

```
reports/capability-layer/
├── gap-ledger.json         (1,132 gaps, 1,131 with "unknown" category)
├── unified-capability-map.json
├── gap-sal-traceability-*.json
└── [other generated reports]
```

**Critical issue:** Gap ledger taxonomy is broken. 99.9% of gaps have "unknown" category.
This makes gap routing, prioritization, and category-based filtering impossible.

### Evidence System

```
.local/evidences/
└── [per-sprint evidence bundles with declarations and ZIPs]
```

Evidence bundles are generated consistently but quality grading requires LLM API keys
(`GPT_OSS_ENDPOINT` or `PROFESSIONALIZE_BASE_URL`). Without these, spec-parity items
get `DEFERRED_WITH_REASON` — silent evidence quality degradation.

### Authority Registries

```
registry/
├── format-registry.yaml           (25 formats scored, legal categories, gates)
├── parity-matrix.yaml             (FODS=COMPLETE, FODT=VERIFIED, others partial)
├── source-structure-baseline.json (LOC caps, known violations)
└── known-failure-ledger.yaml      (pre-existing failures catalog)

shared/qname-registry/
└── [20 format-specific YAML files with qname→class mappings]

product-capability-matrix/
└── poc-targets.yaml               (capability matrix with PASS/FAIL per format)
```

## Data Flow

```
Spec Documents → SAL Parser → .local/spec-cache/ → QName Registry → Product Source
                                                          ↓
Gap Ledger ← Gap Generator ← Capability Compiler ← Capability Map
      ↓
Work Items ← gap_ledger_to_work_items.py
      ↓
Sprint Prompt ← generate_next_worker_prompt.py
      ↓
Sprint Execution (Autonomous Cycle)
      ↓
Evidence Declaration → Governance Validators → Grade → Review Package
      ↓
check_continuation.py → CONTINUE or STOP
```

## System Maturity Summary

| Layer | Maturity | Key Gap |
|-------|---------|---------|
| .NET Products | FODS/FODT: HIGH; others: LOW-MEDIUM | ZST probe-only; CSV thin |
| Python FOSS | FODS/FODT: HIGH; most others: MEDIUM | FODP no write; PPM no write |
| Supervisor | L3-L4 | LOC violations; LLM grader dependency |
| Skills | L2-L3 | No CI enforcement; empty implementation_paths |
| SAL | L4 for ODF; L0 for 10 formats | CHAIN_BROKEN_AT_SAL for CSV/TOML/etc |
| Gap Ledger | L1 (data exists, taxonomy broken) | 99.9% unknown category |
| Evidence | L3 | LLM grader dependency; advisory only without it |
| Governance | L4 | 50 validators; both enforce LOC but violate it themselves |
