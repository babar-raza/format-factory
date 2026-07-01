# Specification Normalization Layer

**Document type:** Policy — Phase 2+ Foundation
**Last reviewed:** 2026-05-05 (run026: Spec Navigation Layer complete)
**Authority:** This document governs the conversion of cached specification source files into local-only machine-readable derived artifacts. It is a companion to `docs/python-foss/specification-cache.md`.

---

## 1. Purpose

The specification cache stores immutable source files: official PDFs, HTML specs, schema files, and registry documents. These are the authoritative reference artifacts. But raw source files are not directly usable by agents for structured reasoning, structured sampling, or parser requirement extraction.

The Specification Normalization Layer converts cached source specifications into local-only machine-readable derived artifacts for agent use. These artifacts enable:

- Structured access to spec sections, tables, and schema references
- Extraction of parser-relevant requirements with source citations
- Sample planning informed by spec-defined data structures
- Oracle comparison grounded in verified spec facts
- Neutral model design using spec-extracted type information

**Original spec PDF = immutable local source artifact. Never modified. Never committed.**

**Normalized artifacts = derived working materials. Local-only. Provenance-traced. Never the authority.**

---

## 2. Scope

The normalization layer applies to any cached specification file under `.local/spec-cache/`. The scope includes:

- PDF specifications (standards body publications)
- HTML specifications
- XML schema files (XSD, RNG, DTD)
- RFC text (plain text or HTML)
- Vendor-published format documentation

The normalization layer does NOT apply to:
- Evidence pack files (committed, in `acquisition-packs/`)
- Sample files (acquired separately, in `samples/by-format/`)
- Product source code

---

## 3. Original Spec Artifact Policy

1. The original cached spec file is the single authoritative source for all spec-derived claims.
2. The cached spec file is never modified, never deleted by automation, and never committed to git.
3. The spec file's SHA-256 must be recorded in `spec-index.yaml` and verified before any normalization run.
4. If the SHA-256 of the cached file does not match the recorded hash, normalization must stop, log a gap, and wait for human resolution. Do not normalize a potentially corrupted file.
5. Normalization always reads from the cached file; it never reads from the original remote URL.

---

## 4. Derived Artifact Policy

1. All normalized artifacts are stored under `.local/spec-cache/{format-id}/{version}/normalized/` (gitignored).
2. Normalized artifacts are never committed to git unless:
   a. The artifact contains only metadata (path, hash, page count, section titles) — no spec text.
   b. Human review has explicitly approved the content for commitment.
   c. Redistribution rights are confirmed.
   For most standards body documents, full extracted text may not be redistributed. Default: local-only.
3. Evidence pack files (`acquisition-packs/`) may contain short cited excerpts (≤ 3 sentences), page/section references, and summary claims with provenance. They must not contain bulk extracted text.
4. Evidence bundles must not contain normalized full-text artifacts.
5. Stale normalized artifacts (source file changed, hash mismatch) must be regenerated before use.

---

## 5. Normalized Artifact Types

The following artifact types may be produced under `.local/spec-cache/{format-id}/{version}/normalized/`:

| Artifact | Description | Example filename |
|---|---|---|
| Plain text | Full text extraction from PDF | `text.txt` |
| Page JSONL | Per-page text and metadata | `pages.jsonl` |
| Section map | Detected section titles and page ranges | `sections.jsonl` |
| Chunks | Semantically chunked text with provenance | `chunks.jsonl` |
| Tables | Extracted tables as structured data | `tables/table_001.json` |
| Figures | Figure references with page/caption | `figures/figures.jsonl` |
| Page map | Page numbers to section headings | `page-map.yaml` |
| Citation map | Citations, cross-references | `citations.yaml` |
| Verified facts | Agent-verified spec facts with citations | `verified-facts.yaml` |
| Parser requirements | Spec sections relevant to parsing | `parser-requirements.yaml` |
| Extraction report | Summary of what was extracted | `extraction-report.md` |
| Source manifest | Hash verification and source provenance | `source-manifest.yaml` |
| Normalization plan | What will be extracted and how | `normalization-plan.md` |

---

## 6. Provenance Schema

Every normalized artifact must have provenance traceable to the source. For individual claims extracted into `verified-facts.yaml` or `parser-requirements.yaml`, the provenance record must include:

```yaml
provenance:
  source_url: "https://..."         # Canonical URL of the spec
  source_local_path: ".local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf"
  source_sha256: "sha256:92cfe64..."  # Hash of the source file
  page: 42                           # Page number (1-indexed)
  page_range: "42-44"               # Page range if claim spans multiple pages
  section: "3.2.1"                  # Section ID if determinable
  section_title: "Table Content"     # Section title if available
  extraction_method: "manual|tool:normalize_pdf.py|tool:other"
  extracted_at: "2026-05-05T07:00:00Z"
  derived_artifact_path: ".local/spec-cache/fods/1.3/normalized/verified-facts.yaml"
  derived_artifact_sha256: "sha256:..."  # Hash of the derived artifact
```

This provenance enables:
1. Verification that the claim comes from the canonical, hash-verified source.
2. Reproducibility: given the source hash and page/section, the claim can be re-verified.
3. Traceability from product behavior back to spec text.

---

## 7. Local-Only Storage Rules

```
.local/spec-cache/
  {format-id}/
    {version}/
      spec.pdf                    (or spec.html, spec.xml, etc.) — immutable source
      spec-index.yaml             — provenance and metadata
      normalized/
        source-manifest.yaml      — hash verification
        text.txt                  — full text (local-only)
        pages.jsonl               — per-page content
        sections.jsonl            — section map
        chunks.jsonl              — chunked content
        tables/                   — extracted tables
        figures/                  — figure references
        page-map.yaml             — page-to-section map
        citations.yaml            — citation map
        verified-facts.yaml       — agent-verified facts with provenance
        parser-requirements.yaml  — parser-relevant requirements
        extraction-report.md      — extraction summary
        normalization-plan.md     — planned extraction
```

`.local/` is gitignored. All items under `.local/spec-cache/` are local-only and never committed.

**If `.local/` is lost:** The source spec can be re-acquired (with authorization). The normalized artifacts must be regenerated from the re-acquired source. Normalized artifacts are reproducible from the source given the normalization tooling.

---

## 8. Copyright and Redistribution Rules

1. Most standards body documents (OASIS, W3C, ECMA, ISO, IETF) are freely accessible but restrict redistribution of the document text itself.
2. `redistribution_permitted: false` in `spec-index.yaml` means extracted text from that document should not be committed, included in bundles, or shared externally.
3. Short cited excerpts (≤ 3 sentences) in evidence files are generally acceptable under fair use / reasonable reliance principles, but this is not a legal opinion. When in doubt, cite the section reference only.
4. Full text extraction (`text.txt`, `pages.jsonl`) is local-only by default regardless of `redistribution_permitted` value.
5. An agent must not include spec text in LLM prompts that are sent to remote endpoints. Spec text may be used with local-only LLM endpoints if redistribution is not implicated. See `docs/ai/llm-endpoint-strategy.md`.

---

## 9. Agent Usage Rules

1. Before using normalized artifacts, verify `source-manifest.yaml` shows SHA-256 match against the current cached spec file.
2. Do not treat normalized artifacts as authoritative. The source spec is authoritative. Normalized artifacts are working materials.
3. If a normalized artifact is stale (source hash mismatch), regenerate it before use. Do not use stale normalized artifacts.
4. When making a claim in evidence files, cite the source (source_url, sha256, page, section), not just the normalized artifact.
5. If normalization tooling is not available or fails, log a gap and proceed with manual spec review from the cached source PDF.

---

## 10. Claim Verification Rules

1. Every claim in `verified-facts.yaml` must have been verified against the source text by an agent (not inferred from memory or prior context).
2. Verification means: the agent read the cited page/section of the cached spec and confirmed the claim matches the spec text.
3. Claims must use the evidence classification system:
   - `[SUPPORTED_BY_NORMALIZED_ARTIFACT]` — extracted from spec with citation
   - `[SUPPORTED_BY_CACHED_SOURCE]` — verified directly from cached spec (no normalization needed)
   - `[PLAUSIBLE_PENDING_VERIFICATION]` — technically plausible but not yet verified from source
   - `[SPECULATION]` — not grounded in spec text; must not appear in production evidence

---

## 11. Gate Relationships

| Gate | Normalization Role |
|---|---|
| Gate 2 (Evidence Complete) | Source spec must be cached (spec-index.yaml). Claims must be `[SUPPORTED_BY_CACHED_SOURCE]` or `[SUPPORTED_BY_NORMALIZED_ARTIFACT]`. Normalization is optional but recommended. |
| Gate 3 (Sample Corpus Ready) | Sample categories should map to spec-defined data structures. Normalization can provide section maps and table references to inform sample planning. Normalization not required to pass Gate 3, but absence must be noted. |
| Gate 4 (Prototype Complete) | Parser prototype must be grounded in spec-defined parsing rules. `parser-requirements.yaml` (or equivalent manual extraction) is required before Gate 4 may begin. If normalization is not available, an explicit gap or waiver must be logged. |
| Gate 5 (Neutral Model Defined) | Neutral model must be designed against spec-verified type information. `verified-facts.yaml` with type/schema entries is the recommended input. |
| Gate 6 (Oracle Comparison) | Discrepancies must be verified against the cached spec. Normalization enables efficient targeted lookup. |
| Gate 7 (Fuzz Testing) | Edge case identification benefits from normalized section/table access. |
| Gate 8 (Security Review) | Threat model grounded in spec-defined edge cases; normalization useful but not required. |

---

## 12. Evidence Bundle Rules

1. Evidence bundles must NOT include full extracted text (`.local/spec-cache/*/normalized/text.txt`, `pages.jsonl`, `chunks.jsonl`, full `tables/`).
2. Evidence bundles MAY include sanitized snapshots under `bundle-metadata/`:
   - `normalization-source-manifest-snapshot.yaml` (hash verification metadata)
   - `normalization-extraction-report-snapshot.md` (what was extracted, without content)
   - `normalization-plan-snapshot.md` (what is planned)
3. Evidence bundles must NEVER include the source spec PDF.

---

## 13. Failure Modes and Gaps

| Failure | Handling |
|---|---|
| PDF extraction library unavailable | Log gap G-NORM-001. Create normalization-plan.md and tooling orientation. Do not force extraction. |
| Source spec hash mismatch | Log gap G-NORM-002. Stop normalization. Flag for human review. |
| Section detection fails | Log gap G-NORM-003. Record in extraction-report.md. Proceed with available output. |
| Normalization incomplete before Gate 4 | Log gap G-NORM-004. Gate 4 cannot begin without parser-requirements.yaml or explicit waiver. |
| Normalized artifact stale | Regenerate from source. Log gap if regeneration not possible. |
| LLM endpoint call attempted | BLOCKED. Normalization tools must not call remote LLM endpoints. |

---

## 14. Implementation

| Component | Phase | Path | Status |
|---|---|---|---|
| This policy document | Phase 2+ | `docs/python-foss/specification-normalization.md` | Created run024; updated run026 |
| Tool orientation | Phase 2+ | `tools/spec-normalize/_readme.md` | Created run024 |
| PDF normalization tool | Phase 2+ | `tools/spec-normalize/normalize_pdf.py` | Created run024; functional run025 |
| Citation map tool | Phase 2+ | `tools/spec-normalize/build_citation_map.py` | Created run024; functional run025 |
| Validation tool | Phase 2+ | `tools/spec-normalize/validate_normalized_spec.py` | Created run024; functional run025 |
| Dependencies | Phase 2+ | `tools/spec-normalize/requirements.txt` | Created run025 (PyYAML, pdfminer.six) |
| Section index tool | Phase 3+ | `tools/spec-normalize/build_section_index.py` | Created run026 |
| Chunk index tool | Phase 3+ | `tools/spec-normalize/build_chunk_index.py` | Created run026 |
| Spec query tool | Phase 3+ | `tools/spec-normalize/query_normalized_spec.py` | Created run026 |
| Sample req exporter | Phase 3+ | `tools/spec-normalize/export_sample_requirements.py` | Created run026 |
| TC-0012 taskcard | Phase 2+ | `taskcards/TC-0012-specification-normalization-layer.md` | Created run024; Phase 2 complete run025 |

### Spec Navigation Layer (added run026)

The Spec Navigation Layer is a set of four tools built on top of the normalized spec artifacts. They convert the 50,000-line `text.txt` into indexed, query-able artifacts. **Agents must use these tools instead of scanning `text.txt` directly.**

**Run order (after normalization):**
1. `build_section_index.py` → `sections.jsonl`, `page-map.yaml`
2. `build_chunk_index.py` → `chunks.jsonl`, `navigation-report.md`
3. `query_normalized_spec.py` → on-demand cited excerpts (no persistent output)
4. `export_sample_requirements.py` → `sample-requirements.yaml`, `parser-requirements-draft.yaml`

**FODS 1.3 navigation layer status (run026):**
- `sections.jsonl`: 884 sections extracted from TOC
- `chunks.jsonl`: 940 chunks, 423,290 words indexed
- `page-map.yaml`: 705 pages mapped to sections
- `sample-requirements.yaml`: 4 sample requirements (Gate 3)
- `parser-requirements-draft.yaml`: 10 draft parser requirements (Gate 4)

---

## 15. Relationship to Other Documents

- `docs/python-foss/specification-cache.md` — source spec acquisition policy (companion document)
- `docs/python-foss/acquisition-workflow.md` — how normalization fits the acquisition pipeline
- `docs/gates.md` — gate requirements referencing normalization
- `docs/governance/legal-and-licensing.md` — redistribution rules that limit normalized text commits
- `docs/governance/release-control.md` — visibility classification for normalized artifacts (evidence-only)
- `docs/ai/llm-endpoint-strategy.md` — rules about spec text in LLM prompts
- `docs/ai/ai-assisted-acquisition-pipeline.md` — AI platform consumes normalized artifacts (mandatory input)
- `docs/ai/ai-platform-operating-model.md` — AI platform requires spec normalization for all AI/embedding use
- `AGENTS.md` — agent rules for using normalized artifacts
- `taskcards/TC-0012-specification-normalization-layer.md` — implementation taskcard
- `taskcards/AI-SPEC-NORMALIZATION-INTEGRATION.md` — AI platform normalization linkage taskcard
- `tools/spec-normalize/` — normalization tooling
