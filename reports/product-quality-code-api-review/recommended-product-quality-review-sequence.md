# Recommended Product Quality Review Sequence

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

This document prescribes the recommended order for reviewing all 30 products in detail
during Phase D (live read-only review) and Phase F (unified fix execution).

---

## Review Sequence Rationale

Products are ordered by:
1. Commercial priority first (.NET before Python)
2. Within .NET: highest maturity and most complex first (sets bar for others)
3. Within Python: highest maturity first; FOSS release candidates first
4. Lowest-scoring products last (less value in deep review of broken products)

---

## Detailed Review Sequence (30 Products)

### Batch 1 — .NET Commercial Products (Priority: Commercial Release)

| # | Product | Language | Score | Why First |
|---|---------|----------|-------|-----------|
| 1 | FODS | .NET | 3.4/5 | Most complex; highest test count; sets API patterns for other .NET products |
| 2 | FODT | .NET | 3.3/5 | Similar depth to FODS; different domain (document vs spreadsheet) |
| 3 | NetPBM | .NET | 3.4/5 | Image processing domain; unique transforms; best architecture |
| 4 | NDJSON | .NET | 2.8/5 | JSON domain; JsonElement leakage most impactful to fix |
| 5 | CSV | .NET | 2.0/5 | Baseline comparison for tabular formats |
| 6 | TSV | .NET | 2.2/5 | Compare against CSV; check consistency |
| 7 | ZST | .NET | 1.5/5 | CRITICAL: confirm write gap; verify no compress exists |
| 8 | HTML | .NET | 0.5/5 | Quick: writer-only; confirm internal-helper classification |
| 9 | Markdown | .NET | 0.5/5 | Same as HTML |
| 10 | TXT | .NET | 0.5/5 | Same as HTML |

### Batch 2 — Python FOSS Release Candidates (Priority: PY-5 readiness)

| # | Product | Language | Score | Why This Order |
|---|---------|----------|-------|----------------|
| 11 | FODS | Python | PY-4 | Most mature Python; dual API problem most impactful |
| 12 | FODT | Python | PY-4 | Peer to FODS Python; 5 exporters; strong |
| 13 | ODS | Python | PY-3 | ZIP-based; different from FODS flat XML; check writer |
| 14 | ODT | Python | PY-3 | Comparable to FODT; ODT writer recently added |

### Batch 3 — Python Image/Compression (Priority: Domain verification)

| # | Product | Language | Score | Why This Order |
|---|---------|----------|-------|----------------|
| 15 | PBM | Python | PY-3 | Best Python architecture; security tests; verify P4 binary |
| 16 | PGM | Python | PY-3 | PBM variant; check family consistency |
| 17 | PPM | Python | PY-3 | PPM variant; check family consistency |
| 18 | QOI | Python | PY-2 | Modern format; check encoder correctness |
| 19 | XCF | Python | PY-2 | Complex binary; verify real layer names fix |
| 20 | ZST | Python | PY-3 | Compare with ZST .NET; Python has compress, .NET doesn't |

### Batch 4 — Python Tabular and Config Formats

| # | Product | Language | Score | Why This Order |
|---|---------|----------|-------|----------------|
| 21 | GNUMERIC | Python | PY-3 | Gzipped XML; verify dict model depth |
| 22 | NDJSON | Python | PY-3 | Compare with NDJSON .NET; analytics masquerade risk |
| 23 | TOML | Python | PY-3 | Config format; verify dict mutation API |
| 24 | CSV | Python | PY-3 | Compare with CSV .NET |
| 25 | TSV | Python | PY-3 | Compare with TSV .NET |
| 26 | SYLK | Python | PY-3 | Verify file-based API quirk (set_cell_value takes paths) |
| 27 | DIF | Python | PY-3 | Flat cell model; verify write capability |

### Batch 5 — Python Document/Presentation Formats

| # | Product | Language | Score | Why This Order |
|---|---------|----------|-------|----------------|
| 28 | ABW | Python | PY-3 | AbiWord; append_paragraph API; verify roundtrip |
| 29 | FODG | Python | PY-3 | Drawing format; dict model; verify text access |
| 30 | FODP | Python | PY-2 | Read-only; verify no write_fodp; check example rename needed |

---

## Review Focus Per Product

### When reviewing FODS .NET (#1):
- Confirm GetColumnHeaders static inconsistency (PQ-018)
- Confirm no Load(Stream) overload (PQ-008)
- Count public methods in FodsDocument — how many total?
- Check if Gate 11 fix is needed in csproj vs source comment

### When reviewing FODT .NET (#2):
- Confirm Spec/Table/* are architecture_only stubs (PQ-012)
- Confirm no Load(Stream) overload (PQ-008)
- Check if FodtDocument.AddTable() or equivalent exists anywhere

### When reviewing NetPBM .NET (#3):
- Confirm NetpbmExporter is within-family only (PQ-013)
- Check if LoadStream and Load are both available (expected yes)
- Verify NetpbmExporter XML doc is absent (PQ-013 scope)

### When reviewing ZST .NET (#7):
- Read ZstDocument.cs line by line — confirm all init properties
- grep for ZstWriter.cs — confirm it does not exist
- Check ZstParser.Parse() — confirm file/bytes overloads only
- Classify: DEMO_PROTOTYPE or NOT_PRODUCT?

### When reviewing FODS Python (#11):
- Import `from fods import *` and count names
- Verify FodsDocument.load() vs parse_fods() — both working?
- Check FODS Python has consumer_roundtrip.py (expected yes)

### When reviewing ZST Python (#20):
- Confirm compress_string() and decompress_to_string() work
- Compare capabilities against ZST .NET (should be much stronger)
- Verify consumer_roundtrip.py passes

### When reviewing FODP Python (#30):
- Confirm no write_fodp() function
- Confirm consumer_roundtrip.py should be renamed consumer_inspect.py
- Check if user gets helpful error if they try to write

---

## Per-Product Review Time Estimate

| Batch | Products | Time Each | Batch Total |
|-------|---------|-----------|-------------|
| 1 (.NET) | 10 | 15–30 min | 2–4 hours |
| 2 (Python RC) | 4 | 15 min | 1 hour |
| 3 (Image/Comp) | 6 | 10 min | 1 hour |
| 4 (Tabular) | 7 | 10 min | 1.2 hours |
| 5 (Doc/Pres) | 3 | 10 min | 30 min |
| **Total** | **30** | | **6–8 hours** |

---

## Review Output Format

For each product reviewed, record:

```
Product: {name} {language}
Score: {current}/5 (or PY-{N})
Confirmed issues: [{PQ-IDs}]
New issues found: [{description}]
Verdict: CONFIRMED_AT_CURRENT_SCORE | REVISED_UPWARD | REVISED_DOWNWARD
Revision reason: {if applicable}
```
