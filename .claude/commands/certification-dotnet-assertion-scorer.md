---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-dotnet-assertion-scorer

Score the quality of assertions in .NET (C#) test files and write a
`dotnet-assertion-quality.json` evidence file.

## What It Does

1. Scans C# test files for assertion patterns (Assert.AreEqual, Should().Be(), etc.)
2. Scores each assertion: strong vs. weak
3. Writes `reports/certification/{fmt}/dotnet-assertion-quality.json`

## Usage

```bash
python tools/certification/dotnet_assertion_scorer.py \
  --path tests/dotnet/{fmt} \
  --output reports/certification/{fmt}/dotnet-assertion-quality.json
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)

## Allowed Paths

- `tools/certification/dotnet_assertion_scorer.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if .NET assertion scoring fails
- Stop if the execution would modify any file under src/

## Output Format

- Certification report JSON written to `reports/certification/<format_id>/`
- Summary: total items, passing, failing, score
- Actionable findings for any failing items
