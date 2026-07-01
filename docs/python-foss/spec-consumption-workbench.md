---
artifact_id: spec-consumption-workbench-v1
artifact_type: documentation
path: docs/python-foss/spec-consumption-workbench.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Spec Consumption Workbench v1 design document. Defines how large specs are converted into agent-consumable task-specific knowledge. Created run030 (2026-05-06)."
---

# Spec Consumption Workbench — Design Document

**Document type:** Architecture Design
**Created:** run030 (2026-05-06)
**Status:** v1 — implemented for FODS; generic design complete

---

## 1. Problem Statement

Specification documents for file formats can be very large:
- ODF 1.3 Part 3: 782 pages, 2.16 million characters of extracted text, 940 chunks
- Future formats (XLSX, DOCX, PDF) may be substantially larger

Agents cannot reliably hold full specification text in context memory:
- Loading 50,000+ lines of spec text exhausts context windows
- Repeated ad hoc reading is slow, error-prone, and produces inconsistent citations
- Different agents performing the same gate work may consult different spec sections, producing non-comparable evidence
- Without provenance, it is impossible to verify that a claim about the spec is correct

The Spec Consumption Workbench solves this by converting a large spec into a hierarchy of small, task-specific, provenance-backed artifacts that agents consume without ever loading the full text.

---

## 2. Architecture

```
immutable cached spec (PDF / HTML)
        ↓
normalized text + pages (text.txt, pages.jsonl)
        ↓
navigation indexes (sections.jsonl, chunks.jsonl, page-map.yaml)
        ↓  [deterministic + lexical retrieval]
verified facts (verified-facts.yaml)
        ↓
requirement packs (sample-requirements.yaml, parser-requirements.yaml, ...)
        ↓
coverage matrices (sample-coverage-matrix.yaml, parser-coverage-matrix.yaml)
        ↓
task-specific retrieval packets (task-packets/gate4-parser-packet.yaml, ...)
        ↓
gate evidence artifacts (parser-notes.md, spec-evidence.md, ...)
        ↓  [optional future]
vector recall layer (embeddings, NOT authority — future TC-0016)
```

Each layer builds on the one below it. The full spec text stays local-only at the normalized
layer. All committed evidence artifacts contain only citations and summaries, not raw spec text.

---

## 3. Required Artifact Types

### 3.1 Committed artifacts (tracked in git)

| Artifact | Path | Purpose |
|---|---|---|
| `parser-requirements.md` | `acquisition-packs/{format}/` | Human-readable parser requirements with spec citations |
| `sample-requirements.yaml` | (exported, may be committed summary) | Sample-level requirements |
| `parser-requirements.yaml` | (exported, may be committed summary) | Parser requirement pack summary |
| `model-requirements.yaml` | (committed draft for Gate 5+) | Neutral model requirements |
| Query tools | `tools/spec-normalize/` | Deterministic + lexical retrieval |
| Workbench tools | `tools/spec-normalize/` | Requirement pack and task packet generators |

### 3.2 Local-only artifacts (`.local/spec-cache/{format}/{version}/workbench/`)

| File | Purpose |
|---|---|
| `verified-facts.yaml` | Verified claims about the spec, each with provenance |
| `requirement-packs/sample-requirements.yaml` | Full sample requirements with citations |
| `requirement-packs/parser-requirements.yaml` | Full parser requirements with citations |
| `requirement-packs/model-requirements-draft.yaml` | Neutral model requirements draft |
| `coverage/sample-coverage-matrix.yaml` | Requirement → sample coverage mapping |
| `coverage/parser-coverage-matrix.yaml` | Requirement → prototype behavior mapping |
| `task-packets/gate3-sample-packet.yaml` | Gate 3 task packet (sample creation) |
| `task-packets/gate4-parser-packet.yaml` | Gate 4 task packet (parser implementation) |
| `task-packets/gate5-model-packet-draft.yaml` | Gate 5 task packet draft (neutral model) |
| `workbench-report.md` | Summary report of workbench build |

---

## 4. Agent Consumption Workflow

An agent working on a gate follows this workflow:

```
Step 1: Identify task and gate
        └─ e.g. "Gate 4: implement FODS parser"

Step 2: Load task packet for this gate
        └─ .local/spec-cache/fods/1.3/workbench/task-packets/gate4-parser-packet.yaml
        └─ This packet is small (<200 lines), cites all relevant spec sections

Step 3: For each requirement in the packet:
        a. Use deterministic query (Tier 1) to retrieve spec section
        b. If Tier 1 fails, use lexical query (Tier 2)
        c. Record the citation (page, section_id, source_hash)

Step 4: Validate citations
        └─ Verify source_hash matches cached spec
        └─ Verify page/section is correct

Step 5: Update verified-facts.yaml (local-only)
        └─ Add new fact with claim_id, claim, provenance, confidence

Step 6: Produce gate evidence
        └─ parser-notes.md, spec-evidence.md, etc.
        └─ Include only citations, not raw spec text
```

---

## 5. Provenance Schema

Every item in a workbench artifact must include provenance:

```yaml
provenance:
  format_id: fods
  spec_id: odf-1.3-part3
  spec_version: "ODF 1.3"
  source_sha256: "sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066"
  normalized_artifact: text.txt        # which normalized artifact was used
  page_start: 90                       # spec page number (start)
  page_end: 95                         # spec page number (end), null if single page
  section_id: "3.1.2"                 # from sections.jsonl
  chunk_id: "fods-chunk-042"          # from chunks.jsonl, null if page-based
  claim_id: "FACT-FODS-001"           # stable claim ID
  extraction_method: "tier1_section"  # tier1_section | tier1_element | tier2_keyword | manual
  verification_status: "verified"     # draft | verified | disputed
  confidence: high                    # high | medium | low
  created_by: "claude-sonnet-4-6 (run030)"
  updated_at: "2026-05-06"
```

All requirement packs and task packets must include per-requirement provenance in this schema.

---

## 6. Size Rules

- **Task packet:** must be concise — typically under 200 lines of YAML
- **Full chunks stay local-only:** `chunks.jsonl` (940 entries for FODS) must never be committed
- **Full spec text stays local-only:** `text.txt` must never be committed
- **Evidence bundles:** include only sanitized summaries, not full workbench artifacts
- **Verified facts:** the full `verified-facts.yaml` is local-only; committed artifacts
  reference fact IDs by citation

---

## 7. Retrieval Rules

See `docs/ai/spec-retrieval-strategy.md` for the full hybrid retrieval hierarchy.
Summary:

1. **Deterministic first (Tier 1):** `--section`, `--element`, `--page`
2. **Lexical second (Tier 2):** `--keyword`, `--sample-req`
3. **Vector third (future only, Tier 3):** not yet implemented; not an authority layer

**Additional workbench rules:**
- Every requirement must trace to a Tier 1 or Tier 2 citation before use in gate evidence
- No requirement may cite "implicit knowledge" without a backup citation query
- If a query returns 0 results, log as `confidence: low` and request a human review
- Workbench artifacts are format-isolated: no FODS requirement may appear in an XLS packet

---

## 8. Refresh Rules

When the spec source changes:

```
spec PDF changes (sha256 mismatch)
→ invalidate: text.txt, pages.jsonl, sections.jsonl, chunks.jsonl
→ invalidate: verified-facts.yaml, all requirement packs
→ invalidate: all task packets
→ invalidate: future vector indexes (when built)
→ log gap: G-SPEC-STALE-{format}-{version}
→ re-run: normalize, index, build_spec_workbench
```

When a parser requirement changes:
- Update the affected requirement pack
- Update the coverage matrix
- Update affected task packets
- Re-validate dependent prototype assertions

---

## 9. Gate Mapping

| Gate | Primary workbench artifact | Notes |
|---|---|---|
| Gate 2 | Legal/spec evidence packet | Spec version, source URL, legal category |
| Gate 3 | Sample requirement packet | Which spec sections define each sample's content |
| Gate 4 | Parser requirement packet | Which spec sections each parser requirement traces to |
| Gate 5 | Model requirement packet | Which parsed fields map to neutral model nodes |
| Gate 6 | Oracle/compatibility packet | Test oracle spec citations |
| Gate 7 | Fuzz/malformed packet | Spec-defined malformed inputs |
| Gate 8 | Security packet | Spec-defined dangerous inputs (zip bombs, XXE, etc.) |
| Gate 9 | Product mapping packet | Tier → spec section → product feature mapping |

---

## 10. Tooling (Phase 3 — run030)

Four tools added under `tools/spec-normalize/`:

| Tool | Purpose |
|---|---|
| `build_spec_workbench.py` | Build full FODS workbench from existing normalized artifacts |
| `build_requirement_pack.py` | Build or update a specific requirement pack (sample, parser, model) |
| `validate_requirement_pack.py` | Validate provenance completeness of a requirement pack |
| `export_task_packet.py` | Export a concise, gate-scoped task packet |

All tools:
- Operate on local-only normalized artifacts
- Never read from remote sources
- Never call LLM endpoints
- Never create embeddings or vector DB
- Output local-only detailed artifacts under `.local/spec-cache/{format}/{version}/workbench/`
- Output sanitized summaries for evidence bundles only

---

## 11. Implementation Status (FODS — run030)

| Artifact | Status | Location |
|---|---|---|
| Workbench tools (4) | created run030 | `tools/spec-normalize/` |
| verified-facts.yaml | created run030 | local-only: `.local/.../workbench/` |
| parser-requirements.yaml (pack) | created run030 | local-only |
| sample-requirements.yaml (pack) | created run030 | local-only |
| model-requirements-draft.yaml | created run030 | local-only |
| gate4-parser-packet.yaml | created run030 | local-only |
| parser-coverage-matrix.yaml | created run030 | local-only |
| workbench-report.md | created run030 | local-only |

**Seeding note:** FODS v1 workbench artifacts are seeded from existing gate artifacts
(parser-requirements.md, sample-requirements.yaml, parser-requirements-draft.yaml)
and marked `seeded_from_gate_artifacts`. Richer automated extraction from chunks is
tracked in TC-0021 (independent quality review).

---

## 12. Revision History

| Run | Change |
|---|---|
| run030 | Document created. Spec Workbench v1 design finalized. FODS workbench built. |
