# Specs Authority Layer — Healing Design
# Sprint: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001
# Generated: 2026-06-06

---

## 1. Target Architecture

The healed specs authority layer must satisfy all 16 baseline requirements:

1. Immutable cached specs (ALREADY MET for FODS)
2. Source provenance for every spec (PARTIALLY MET — spec-index.yaml exists)
3. Source hashes and refresh invalidation (PARTIALLY MET — tools exist; persistence gap)
4. Format/spec-version isolation (ALREADY MET — per-format directories)
5. Normalized text/pages (MISSING for most formats — GAP-001)
6. Deterministic section/page/chunk indexes (MISSING — GAP-001)
7. Lexical search as minimum reliable retrieval path (MISSING — GAP-001)
8. Optional future embeddings/vector (DESIGN ONLY — correctly not implemented)
9. Verified facts from specs (ONLY 10 seeded facts for FODS — GAP-002, GAP-006)
10. Task-specific requirements from verified facts (CANDIDATE ONLY — GAP-006)
11. Strict provenance from requirement back to source spec (PARTIAL — schema designed, not populated)
12. No unverifiable AI requirements as authority (PARTIALLY ENFORCED — validate_generated_requirements.py)
13. No large spec text in evidence bundles (ALREADY MET — spec files gitignored)
14. Clear failure behavior for missing/stale specs (PARTIALLY IMPLEMENTED — tools exist, not wired)
15. Integration with acquisition workflow (ADVISORY ONLY — GAP-004, GAP-008)
16. Deterministic rerun of pilot (NOT ACHIEVABLE until GAP-001 and GAP-002 repaired)

---

## 2. Minimum Viable Repair (Phase 1)

The minimum viable repair produces a working spec authority chain for ONE format
(FODS, as it already has a cached PDF) and closes the four P1 gaps.

### MVR-1: Run Normalization Pipeline for FODS

**What to do:**
```bash
# FODS PDF is at .local/spec-cache/fods/1.3/ (gitignored, local only)
# Check if PDF file exists
ls .local/spec-cache/fods/1.3/*.pdf

# Create output directory
mkdir -p .local/spec-normalize/fods/

# Run normalize_pdf.py
python tools/spec-normalize/normalize_pdf.py \
  --input .local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf \
  --output .local/spec-normalize/fods/ \
  --format-id fods \
  --version 1.3

# Build section index
python tools/spec-normalize/build_section_index.py \
  --input .local/spec-normalize/fods/text.txt \
  --output .local/spec-normalize/fods/sections.yaml

# Build chunk index
python tools/spec-normalize/build_chunk_index.py \
  --input .local/spec-normalize/fods/text.txt \
  --output .local/spec-normalize/fods/pages.jsonl
```

**Expected outputs:**
- `.local/spec-normalize/fods/text.txt` — full normalized text
- `.local/spec-normalize/fods/sections.yaml` — section index
- `.local/spec-normalize/fods/pages.jsonl` — chunk index

**Validation:**
```bash
python tools/spec-normalize/validate_normalized_spec.py \
  --path .local/spec-normalize/fods/
```

### MVR-2: Replace Synthetic Seed Data with Real Extracted Requirements

**What to do:**
```python
# Wire requirement_extractor.py against real normalized text
python tools/specification-authority-layer/requirement_extractor.py \
  --source-id FODS-SPEC-001 \
  --input .local/spec-normalize/fods/text.txt \
  --sections .local/spec-normalize/fods/sections.yaml \
  --format-id fods \
  --output .local/spec-artifacts/FODS-SPEC-001-requirements.json
```

**Expected output:** `.local/spec-artifacts/FODS-SPEC-001-requirements.json` with
candidates extracted from real spec text (status="candidate").

### MVR-3: Build Minimal Human-Review CLI for Fact Promotion

**What to do:** Extend `tools/specification-authority-layer/spec_verifier.py` with a
review workflow:

```python
# review_facts.py — minimal CLI
# Reads candidate requirements from FODS-SPEC-001-requirements.json
# Shows user: claim + exact spec text at cited location
# User enters: v (verify), r (reject), s (skip)
# Writes to .local/spec-cache/fods/1.3/workbench/verified-facts.yaml
```

**Output:** verified-facts.yaml with `verification_status: "verified"` and
`validated_by: "human"` for each confirmed fact.

**Schema for a verified fact:**
```yaml
claim_id: FACT-FODS-011
claim: "<exact claim from spec>"
provenance:
  format_id: fods
  spec_id: odf-1.3-part3
  spec_version: "ODF 1.3"
  source_sha256: "sha256:92cfe6..."
  page_start: 142
  section_id: "9.1.2"
  chunk_id: "p142-c003"
  extraction_method: tier2_lexical
  verification_status: verified
  confidence: high
  validated_by: human
  validated_at: "2026-06-06"
```

### MVR-4: Add spec_fact_refs to Evidence Declaration Schema

**What to do:** Update `docs/automation/supervisor-worker-contract.md` and the
evidence validation logic:

```yaml
# In evidence-declaration.yaml — add to PRODUCT_SOURCE work items:
spec_fact_refs:
  - FACT-FODS-001
  - FACT-FODS-003
```

**Enforcement:** Update supervisor validation to warn (and eventually fail) if
a PRODUCT_SOURCE work item has empty spec_fact_refs.

---

## 3. Full Production Repair (Phase 2)

After Phase 1 is complete and validated for FODS:

### FPR-1: Run Normalization for All Formats with Spec Documents

For each format with a real spec document:
- ZST (RFC 8878 + RFC 9659 — text format, adapt normalizer)
- DIF (v1 spec document)
- CSV (RFC 4180 — text format)
- ABW (AWML 1.0 — XML spec)
- GNUMERIC (v10 — XML-based)
- PBM/PGM (Netpbm spec — text format)

Output: `.local/spec-normalize/<format>/` for each.

### FPR-2: Add Spec Fact Annotation Convention to Code

**Coding standard addition:**
```python
# In Python parser code:
# SPEC-FACT: FACT-FODS-001 (office:document root element)
def parse_root_element(self, xml_root):
    ...

# In C# code:
// SPEC-FACT: FACT-FODS-002 (office:mimetype attribute)
public string ParseMimeType(XElement root)
    ...
```

**Tooling:** Add a `tools/spec-normalize/check_code_citations.py` that verifies
each verified fact has at least one code citation.

### FPR-3: Generate Golden Spec-Fact Tests

For each verified fact, generate or write a test:

```python
# tests/net/fods/test_spec_facts.py
# SPEC-FACT: FACT-FODS-001
def test_fods_root_element_is_office_document():
    """FACT-FODS-001: FODS root element is office:document"""
    doc = FodsParser.Parse(MINIMAL_FODS_SAMPLE)
    assert doc.RootElement == "office:document"
```

### FPR-4: Persist Spec Source Registry

Initialize `.local/spec-source-registry/sources.jsonl` with all 9 cached formats.
Wire `spec_governance_runtime` into the acquisition task entry point so every
acquisition action logs to the registry.

### FPR-5: Wire Spec Authority into Supervisor Grading

Read `authority-integration-contract.json` in grading logic:
- spec_authority_status = MISSING → grade cap: CONDITIONAL
- spec_authority_status = PARTIAL → grade cap: PARTIAL_CREDIT
- spec_authority_status = COMPLETE → no cap

---

## 4. Data Model Changes

### 4.1 Spec Cache Entry (no changes needed — schema is correct)

Existing spec-index.yaml schema is adequate.

### 4.2 Normalized Spec Artifact Schema

Add to normalization output:
```yaml
# .local/spec-normalize/<format>/manifest.yaml
format_id: fods
spec_version: "1.3"
source_sha256: "sha256:92cfe6..."
normalized_at: "2026-06-06T..."
normalizer_version: "1.0"
page_count: 782
section_count: 412
chunk_count: 2348
```

### 4.3 Verified Fact Schema (extend current)

```yaml
claim_id: FACT-FODS-xxx       # required
claim: string                  # required — exact claim text
confidence: high|medium|low    # required
verification_status: verified|candidate|rejected|needs_review  # required
validated_by: human|automated  # required when verified
validated_at: ISO date         # required when verified
provenance:
  source_sha256: string        # required
  page_start: int              # required
  section_id: string           # required
  chunk_id: string             # optional
  extraction_method: tier1|tier2|tier3  # required
```

### 4.4 Evidence Declaration Schema (add)

```yaml
# For PRODUCT_SOURCE work items — add field:
spec_fact_refs:               # Optional for now, required in Phase 2
  type: array
  items:
    type: string
    pattern: "^FACT-[A-Z]+-[0-9]+"
```

### 4.5 Product Ledger Schema (add)

```json
{
  "spec_fact_ids": ["FACT-FODS-001", "FACT-FODS-002"]
}
```

---

## 5. Spec Cache Rules

1. No spec file may be downloaded without T3 authorization (6 conditions met)
2. spec-index.yaml must be written before any normalization runs
3. SHA-256 must be verified against spec-index.yaml before normalization
4. If SHA-256 changes, normalization must be re-run and all derived artifacts invalidated
5. Spec files are gitignored; spec-index.yaml is committed

---

## 6. Source Hash and Invalidation Rules

| Trigger | Action |
|---------|--------|
| `stale: true` in spec-index.yaml | Block normalization; require re-download with T3 authorization |
| SHA-256 mismatch at normalization time | Stop; log; require human decision |
| spec-index.yaml missing | Block all downstream work for that format |
| New spec version released | Create new version directory; run full pipeline for new version |

Staleness detection: `tools/spec-cache/refresh_check.py` — run weekly or on spec URL change.

---

## 7. Format/Spec-Version Isolation

Each format must have isolated directories:
- `.local/spec-cache/<format>/<version>/` — immutable source artifacts
- `.local/spec-normalize/<format>/<version>/` — derived normalization
- `.local/spec-artifacts/<FORMAT>-SPEC-<VERSION>-*.json` — extracted requirements
- Cross-format query isolation enforced by `query_normalized_spec.py` (format-id required)

---

## 8. Verified Fact Schema

(See Section 4.3 above)

Rules:
- status must be "candidate" on extraction
- status can only transition to "verified" via human review workflow
- status can only transition to "rejected" via human review workflow
- "needs_review" is valid intermediate state
- AI output must never set status to "verified" directly

---

## 9. Requirement Generation Schema

```yaml
# .local/spec-artifacts/<FORMAT>-SPEC-<VERSION>-requirements.json
source_id: FODS-SPEC-001
format_id: fods
spec_version: "1.3"
extraction_date: "2026-06-06"
requirements_count: N
requirements:
  - req_id: REQ-FODS-SPE-xxxxxx
    source_id: FODS-SPEC-001
    section_id: FODS-SPEC-001-sNNNN
    heading: "section heading"
    text_fragment: "exact spec text"
    keyword: "SHALL|MUST|SHOULD"
    format_id: fods
    status: "candidate"  # never "verified" on extraction
    extracted_at: ISO-datetime
```

---

## 10. Citation/Provenance Schema

Every verified fact, requirement, and context pack entry must carry:

```yaml
provenance:
  source_id: FODS-SPEC-001
  source_sha256: "sha256:92cfe6..."
  file_path: ".local/spec-cache/fods/1.3/spec.pdf"
  page_start: int
  page_end: int|null
  section_id: string
  chunk_id: string|null
  retrieval_tier: 1|2|3
  validated: bool
  validated_by: "human"|"automated"
```

---

## 11. Lexical Retrieval Requirements

Tool: `tools/spec-normalize/query_normalized_spec.py`

Required capabilities:
- `--section <id>` → return section text + citation
- `--element <name>` → return all pages mentioning that XML element
- `--keyword <terms>` → full-text search with BM25 ranking
- `--format-id <id>` → mandatory filter (format isolation)
- Output: always includes `source_sha256` + `page` + `section_id`

---

## 12. Optional AI/Embedding Support Role

When tools/ai/ is activated (Phase 3), the only permitted roles are:

| AI Role | Input | Output | Output Status |
|---------|-------|--------|--------------|
| Candidate section finder | Query + normalized spec | Section IDs | candidate_sections (not authority) |
| Gap detector | Verified facts + normalized spec | Uncovered sections | gap_candidates (not authority) |
| Contradiction detector | Impl requirement + spec text | Contradiction flag | requires_human_review |
| Draft test generator | Verified fact | Test code | candidate_test (requires human approval) |

AI must never output status="verified". This must be schema-enforced.

---

## 13. Tests Required

| Test | Covers | Priority |
|------|--------|----------|
| Normalization output exists for each cached format | GAP-001 | P1 |
| Extracted requirements come from real spec text (golden test) | GAP-002 | P1 |
| Candidate requirement cannot be set to "verified" by tool | GAP-006 | P1 |
| Human review CLI transitions status correctly | GAP-006 | P1 |
| Evidence declaration fails if PRODUCT_SOURCE missing spec_fact_refs | GAP-004 | P1 |
| Code citation check fails for missing FACT-xxx annotation | GAP-005 | P2 |
| Supervisor grades MISSING spec authority as CONDITIONAL | GAP-008 | P2 |
| Registry persisted after acquisition task | GAP-003 | P2 |
| Golden spec-fact test passes for each verified FODS fact | GAP-007 | P2 |

---

## 14. Migration Plan from Current State

**Step 1 (Safe — no breaking changes):**
- Run normalization for FODS only
- Validate normalized output
- Keep existing spec artifacts as-is (do not delete synthetic seed data yet)

**Step 2 (Replace synthetic seed data):**
- Run real requirement extractor against normalized FODS text
- Compare with existing synthetic requirements
- Replace FODS-SPEC-001-requirements.json with real extracted version
- Update build_proof_graph to use real requirements
- Run proof graph tests; fix regressions

**Step 3 (Evidence schema):**
- Add spec_fact_refs to evidence schema (optional, warn only)
- Run all existing declaration submissions through updated validator
- Fix any declarations that would fail (backfill spec_fact_refs where possible)

**Step 4 (Code annotations):**
- Add FACT-FODS-xxx annotations to FODS parser code
- Add tests for annotation presence

---

## 15. Backward Compatibility

- spec-index.yaml schema is additive — no breaking changes needed
- verified-facts.yaml schema extension is additive
- evidence declaration schema: add spec_fact_refs as optional (warn only) for 2 sprints, then required
- Product ledger schema: add spec_fact_ids as optional

---

## 16. Evidence and Proof Requirements

The healed spec authority layer must produce, for any format:

1. `spec-index.yaml` with SHA-256 verified ✓ (FODS)
2. `normalized/manifest.yaml` with source hash (NEW)
3. `normalized/text.txt` (NEW for most formats)
4. `spec-artifacts/<FORMAT>-SPEC-001-requirements.json` with real extracted requirements (NEW)
5. `workbench/verified-facts.yaml` with human-verified facts (PARTIAL for FODS)
6. At least one golden spec-fact test per verified fact (NEW)
7. At least one code citation per verified fact (NEW)

---

## 17. Rollback Plan

Phase 1 changes are all additive and local-only (`.local/` is gitignored):
- Running normalization adds files; removing `.local/spec-normalize/` is a clean rollback
- Replacing spec artifacts: old files are not git-tracked; no rollback needed for `.local/`
- Evidence schema change: revert the single field addition in supervisor-worker-contract.md

No Phase 1 changes affect committed code. Rollback is trivial.
