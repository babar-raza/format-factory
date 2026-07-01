# tools/spec-normalize/

**Purpose:** Specification normalization tools. Convert cached local spec files into machine-readable derived artifacts for agent use.

**Phase availability:** Phase 2+

**Policy document:** `docs/python-foss/specification-normalization.md`

---

## Overview

The Specification Normalization Layer converts cached source specifications (PDFs, HTML, XML schemas) into structured local-only derived artifacts. These artifacts enable agents to reason about spec content without relying only on raw PDFs.

**Original spec → immutable source. Normalized artifacts → local-only working materials.**

All normalized artifacts are stored under:
```
.local/spec-cache/{format-id}/{version}/normalized/
```

These directories are gitignored. Normalized artifacts are never committed unless they contain only metadata (path, hash, section titles) and redistribution rights are confirmed.

---

## Tools in This Directory

| Script | Purpose | Network | LLM |
|---|---|---|---|
| `normalize_pdf.py` | Extract text, page map, section map from PDF | No | No |
| `build_citation_map.py` | Build citation map and verified-facts scaffolding | No | No |
| `validate_normalized_spec.py` | Validate normalized artifacts against source hash | No | No |

---

## Key Rules

1. **No network access.** These tools operate only on local files.
2. **No LLM endpoint calls.** These tools use only standard Python libraries or explicitly approved local extraction libraries.
3. **Source hash verification first.** Every tool must verify the cached spec SHA-256 matches `spec-index.yaml` before proceeding.
4. **Do not overwrite source files.** Normalized artifacts are written to the `normalized/` subdirectory only.
5. **Fail gracefully.** If a required extraction library is unavailable, the tool must report the missing dependency and write a `normalization-plan.md` describing what would be extracted.
6. **Provenance metadata always.** Even minimal runs must produce `source-manifest.yaml` with hash verification.

---

## Installation Notes

PDF normalization requires a PDF extraction library. The tools will attempt to use `pdfminer.six` or `pypdf2` if available. If neither is installed, the tool falls back to metadata-only mode.

To install optional PDF dependencies:
```bash
pip install pdfminer.six
```

Or:
```bash
pip install pypdf
```

---

## Usage

```bash
# Normalize FODS ODF 1.3 spec PDF
python tools/spec-normalize/normalize_pdf.py \
    --spec-dir .local/spec-cache/fods/1.3 \
    --format-id fods

# Build citation map from normalized output
python tools/spec-normalize/build_citation_map.py \
    --normalized-dir .local/spec-cache/fods/1.3/normalized \
    --format-id fods

# Validate normalized artifacts
python tools/spec-normalize/validate_normalized_spec.py \
    --spec-dir .local/spec-cache/fods/1.3 \
    --normalized-dir .local/spec-cache/fods/1.3/normalized
```

---

## Output Directory Structure

```
.local/spec-cache/{format-id}/{version}/normalized/
  source-manifest.yaml        — hash verification metadata
  normalization-plan.md       — what will be extracted
  extraction-report.md        — what was extracted
  text.txt                    — full text (if extraction succeeded)
  pages.jsonl                 — per-page content
  sections.jsonl              — section map
  page-map.yaml               — page number to section heading
  verified-facts.yaml         — agent-verified facts with provenance
  parser-requirements.yaml    — parser-relevant requirements
  citations.yaml              — citation map
  tables/                     — extracted tables
  figures/                    — figure references
```

---

## Status

Implemented run024 (2026-05-05). Tooling is a functional skeleton. Full extraction requires PDF library dependency. Falls back to metadata-only mode if library is unavailable. See TC-0012 for full implementation scope.
