# Specs Authority Layer — Pilot Rerun Plan
# Sprint: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001
# Generated: 2026-06-06

---

## Selected Pilot: FODS Root-Element Fact (FACT-FODS-001)

### Why FODS Is the Right Pilot

FODS is the best candidate for a bounded pilot because:

1. **Real spec PDF exists**: `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf` (24.27 MB, SHA-256 verified)
2. **Tools already built**: All normalization and authority layer tools are available
3. **10 manually seeded facts already exist**: Provides comparison baseline
4. **Working parser and tests**: FODS parser passes 547 .NET tests and ~30 Python tests
5. **Most complete acquisition history**: Gate 1-9 all passed with real human approval
6. **Smallest testable authority chain**: Root element rule is simple, unambiguous, and critical

The pilot is bounded to the FODS root element fact (FACT-FODS-001):
- Claim: "FODS root element is `office:document` with `office:mimetype` attribute"
- Source: ODF 1.3 Part 3, Section 3.1.2, Page ~90

This is the smallest pilot that proves the full authority chain.

---

## Pilot Scope

The pilot must prove this sequence end-to-end:

```
Real spec PDF (FODS 1.3)
  → normalize to text
  → extract candidate requirement mentioning "office:document"
  → verify fact via human review workflow
  → write to verified-facts-real.yaml
  → generate golden test that proves parser handles office:document correctly
  → test passes
  → code annotation added (// SPEC-FACT: FACT-FODS-001)
  → evidence package: spec-source → normalized-text → requirement → verified-fact → test → code
```

---

## Pilot Steps

### Step P1: Verify Source Integrity

```bash
# Confirm PDF is present and hash matches spec-index.yaml
ls -la .local/spec-cache/fods/1.3/
sha256sum .local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf
# Expected: sha256 matches 92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
```

Record output in: `reports/spec-authority/spec-authority-investigation-001/pilot-p1-source-verify.txt`

### Step P2: Normalize Spec PDF

```bash
mkdir -p .local/spec-normalize/fods/1.3/
python tools/spec-normalize/normalize_pdf.py \
  --input .local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf \
  --output-dir .local/spec-normalize/fods/1.3/ \
  --format-id fods \
  --version 1.3
```

Validate:
```bash
python tools/spec-normalize/validate_normalized_spec.py \
  --path .local/spec-normalize/fods/1.3/
```

Determinism check:
```bash
# Run normalization twice; compare SHA-256 of text.txt
sha256sum .local/spec-normalize/fods/1.3/text.txt
# Run again:
python tools/spec-normalize/normalize_pdf.py ...
sha256sum .local/spec-normalize/fods/1.3/text.txt
# Both SHA-256 values must be identical
```

Record output in: `reports/spec-authority/spec-authority-investigation-001/pilot-p2-normalization.txt`

### Step P3: Index the Spec

```bash
python tools/spec-normalize/build_section_index.py \
  --input .local/spec-normalize/fods/1.3/text.txt \
  --output .local/spec-normalize/fods/1.3/sections.yaml \
  --format-id fods

python tools/spec-normalize/build_chunk_index.py \
  --input .local/spec-normalize/fods/1.3/text.txt \
  --output .local/spec-normalize/fods/1.3/pages.jsonl \
  --format-id fods
```

Verify section 3.1.2 is in the section index:
```bash
python -c "import yaml; s=yaml.safe_load(open('.local/spec-normalize/fods/1.3/sections.yaml')); print([x for x in s if '3.1.2' in str(x)])"
```

Record output in: `reports/spec-authority/spec-authority-investigation-001/pilot-p3-index.txt`

### Step P4: Lexical Retrieval of Root Element

```bash
python tools/spec-normalize/query_normalized_spec.py \
  --format-id fods \
  --path .local/spec-normalize/fods/1.3/ \
  --section "3.1.2"

python tools/spec-normalize/query_normalized_spec.py \
  --format-id fods \
  --path .local/spec-normalize/fods/1.3/ \
  --keyword "office:document" --top-k 5
```

Expected: Returns spec text mentioning `office:document` with page number and section ID.

Record output in: `reports/spec-authority/spec-authority-investigation-001/pilot-p4-retrieval.txt`

### Step P5: Extract Candidate Requirements

```bash
python tools/specification-authority-layer/requirement_extractor.py \
  --source-id FODS-SPEC-001 \
  --input .local/spec-normalize/fods/1.3/text.txt \
  --sections .local/spec-normalize/fods/1.3/sections.yaml \
  --format-id fods \
  --output .local/spec-artifacts/FODS-SPEC-001-requirements-real.json
```

Verify: At least one requirement mentions `office:document` with `section_id` pointing to 3.1.2.

Record output in: `reports/spec-authority/spec-authority-investigation-001/pilot-p5-requirements.json`

### Step P6: Human Fact Verification

Display the candidate requirement for the root element to a human reviewer:
- Show: claim text + exact spec text at cited location + page number
- Human confirms: YES, this is what the spec says
- Update `verified-facts-real.yaml`:

```yaml
claim_id: FACT-FODS-011  # new verified fact
claim: "FODS root element is office:document"
confidence: high
verification_status: verified
validated_by: human
validated_at: "2026-06-06"
provenance:
  source_id: FODS-SPEC-001
  source_sha256: "sha256:92cfe64ee30a..."
  page_start: 90  # actual page from normalization
  section_id: "3.1.2"
  extraction_method: tier1_section
```

Record in: `.local/spec-cache/fods/1.3/workbench/verified-facts-real.yaml`

### Step P7: Write Golden Spec-Fact Test

Create `tests/net/fods/test_fods_spec_facts.py`:

```python
"""
Golden spec-fact tests for FODS.
Each test is backed by a verified fact from verified-facts-real.yaml.
"""

# SPEC-FACT: FACT-FODS-011 (root element is office:document)
def test_fods_root_element_is_office_document():
    """
    Verified fact: ODF 1.3 Part 3 §3.1.2 — root element must be office:document
    Source: .local/spec-cache/fods/1.3/workbench/verified-facts-real.yaml
    """
    minimal_fods = '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml"><office:body><office:spreadsheet/></office:body></office:document>'
    # Use existing FODS parser to parse and assert root element
    ...
```

Run test:
```bash
.local/venv/Scripts/python -m pytest tests/net/fods/test_fods_spec_facts.py -v
```

Record output in: `reports/spec-authority/spec-authority-investigation-001/pilot-p7-golden-test.txt`

### Step P8: Add Code Citation

In `src/net/fods/FodsParser.cs` (or equivalent), add:

```csharp
// SPEC-FACT: FACT-FODS-011 — ODF 1.3 §3.1.2: root element is office:document
private XElement ParseRootElement(XDocument doc) { ... }
```

Verify:
```bash
grep -r "FACT-FODS-011" src/net/fods/
```

### Step P9: Detect Stale/Missing Facts

```bash
# Simulate stale spec by checking refresh_check.py
python tools/spec-cache/refresh_check.py \
  --spec-dir .local/spec-cache/fods/1.3/ \
  --check-stale

# Simulate missing spec (rename spec-index.yaml temporarily)
# -> authority layer must report MISSING, not crash silently
```

Record: pilot-p9-staleness-detection.txt

### Step P10: Final Determinism Check

Run all pilot steps P2-P8 a second time from scratch (fresh `.local/spec-normalize/` output):
- SHA-256 of text.txt matches Step P2 output
- Requirement IDs for the root element requirement match Step P5 output
- Golden test still passes
- All existing spec_authority tests still pass

Record: `reports/spec-authority/spec-authority-investigation-001/pilot-p10-determinism.txt`

---

## Evidence Package

The pilot evidence package must include:

| File | Purpose |
|------|---------|
| pilot-p1-source-verify.txt | SHA-256 match proof |
| pilot-p2-normalization.txt | Normalization output + validator result |
| pilot-p3-index.txt | Section 3.1.2 found in index |
| pilot-p4-retrieval.txt | Lexical retrieval returning spec text |
| pilot-p5-requirements.json | Real extracted requirements |
| .local/spec-cache/fods/1.3/workbench/verified-facts-real.yaml | Human-verified facts |
| tests/net/fods/test_fods_spec_facts.py | Golden test file |
| pilot-p7-golden-test.txt | Golden test pass result |
| grep output showing FACT-FODS-011 in source | Code citation proof |
| pilot-p10-determinism.txt | Determinism proof |

---

## Pass/Fail Criteria

The pilot PASSES if and only if:
1. FODS spec PDF SHA-256 matches spec-index.yaml
2. Normalization produces text.txt with >100 pages
3. Section 3.1.2 found in section index
4. Lexical query for "office:document" returns result with page + section citation
5. Requirement extraction produces ≥1 candidate mentioning "office:document"
6. At least 1 fact promoted to verified status by human review
7. Golden spec-fact test passes
8. Code citation (FACT-FODS-011) present in source
9. All 223 existing spec_authority tests still pass
10. Determinism check: second run produces same SHA-256 for text.txt

The pilot FAILS if any of these criteria are not met. Record the specific failure point.

---

## Why This Pilot Is Representative

This bounded pilot proves the complete authority chain:
- Source acquisition (already done — FODS PDF cached)
- Normalization (new — must run)
- Indexing (new — must run)
- Lexical retrieval (new — must prove)
- Candidate extraction (new — must prove from real text)
- Human verification (new workflow — must implement)
- Verified fact persistence (new — must prove)
- Golden test from verified fact (new — must implement)
- Code citation (new annotation — must add)
- Stale detection (existing tool — must run)
- Determinism (new check — must prove)

If this chain works for FODS root element, it can be extended to:
- All other FODS facts (same PDF, same tools)
- Other formats once their specs are normalized (same tools, different inputs)
