---
version: "1.0"
last-updated: "2026-06-28"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-016
spec_qname_required: "false"
product_track: "governance"
---

# /certification-dashboard

Run the certification dashboard to regenerate the portfolio certification matrix across
all 20 Python FOSS formats.

## What It Does

1. Reads per-format certification reports from `reports/certification/{fmt}/`
2. Evaluates 9 dimensions: api_contract, traceability, stubs, exceptions, oracle,
   test_quality, roundtrip, package, consumer
3. Derives verdicts: CERTIFIED, CERTIFIED_WITH_KNOWN_GAPS, NOT_CERTIFIED, IN_PROGRESS, NOT_STARTED
4. Writes `reports/certification/portfolio-certification-matrix.json`
5. Writes `reports/certification/certification-report.md`

## Usage

```bash
python tools/certification/certification_dashboard.py
```

Optional arguments:
- `--output-json PATH` — custom JSON output path (default: reports/certification/portfolio-certification-matrix.json)
- `--output-md PATH` — custom Markdown output path (default: reports/certification/certification-report.md)

## Verification

```bash
.venv/Scripts/pytest tests/certification/ -q
```

Expected: 456 tests pass.

## Evidence

- `reports/certification/portfolio-certification-matrix.json`
- `reports/certification/certification-report.md`

## Related Tools

- `tools/certification/stub_detector.py` — material stub detection
- `tools/certification/exception_coverage_checker.py` — exception coverage audit
- `tools/certification/assertion_quality_scorer.py` — test quality scoring
- `tools/certification/inventory_extractor.py` — API contract extraction

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)

## Allowed Paths

- `tools/certification/certification_dashboard.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if required certification report files do not exist
- Stop if the portfolio matrix is inconsistent
