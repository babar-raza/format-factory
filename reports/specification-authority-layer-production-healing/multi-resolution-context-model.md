# Multi-Resolution Context Model
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

The Specification Authority Layer provides spec content at 8 resolution levels.
Higher resolution = more detail, more tokens; lower resolution = more compact, less detail.
Context packs are assembled from the appropriate resolution level for the consuming task.

---

## Resolution Levels

### Level 1 — Raw Snapshot
**Description:** Exact byte-for-byte copy of the spec document as ingested.
**Token range:** Unbounded (can be megabytes)
**Use case:** Archival; provenance proof; SpecParser input
**Subsystem:** SpecVault
**State:** raw_snapshot (C)
**When to use:** Never directly in LLM context; always go through parser first

---

### Level 2 — Parsed Section Tree
**Description:** Structured JSON with sections, tables, examples extracted from raw snapshot.
**Token range:** 10,000–100,000 tokens
**Use case:** Full spec review; detailed requirement extraction
**Subsystem:** SpecParser
**State:** parsed_artifact (D)
**When to use:** Requirement extraction; detailed spec analysis; multi-pass processing

---

### Level 3 — Normalized Artifact
**Description:** Canonical cross-format JSON with typed requirements, data types, error codes.
**Token range:** 5,000–50,000 tokens
**Use case:** Cross-format requirement comparison; normalization-layer reasoning
**Subsystem:** SpecNormalizer
**State:** normalized_artifact (E)
**When to use:** Cross-format analysis; requirement graph construction

---

### Level 4 — Indexed Chunks/Tables
**Description:** Lexically indexed chunks and tables for search and retrieval.
**Token range:** Variable (retrieved by query)
**Use case:** Targeted lookup of specific sections, fields, error codes
**Subsystem:** SpecIndexer
**State:** indexed_artifact (F)
**When to use:** Answering specific questions about a spec without full context

---

### Level 5 — Compressed Digest
**Description:** Compressed summary preserving requirements but reducing prose/examples.
**Token range:** 1,000–5,000 tokens
**Use case:** Context-window-constrained tasks; broad spec orientation
**Subsystem:** SpecDigestor
**State:** digest_artifact (G)
**When to use:** When full parsed artifact exceeds token budget; initial spec orientation

---

### Level 6 — Section Summaries
**Description:** One-sentence summaries per section; requirement list without proof text.
**Token range:** 200–1,000 tokens
**Use case:** High-level spec navigation; format overview
**Subsystem:** SpecDigestor (high-compression mode)
**State:** digest_artifact (G) with target_token_budget=low
**When to use:** Multi-format overview tasks; planning before deep dive

---

### Level 7 — Format Capsule
**Description:** Single-paragraph synthesis of the format: key properties, main requirements,
notable constraints, licensing status.
**Token range:** 50–200 tokens
**Use case:** Format selection decisions; user-facing format descriptions
**Subsystem:** SpecDigestor (capsule mode)
**State:** digest_artifact (G) with mode=capsule
**When to use:** Choosing between formats; product capability matrix entries

---

### Level 8 — Task Context Pack
**Description:** Assembled context pack for a specific implementation or test task.
Contains: relevant requirements (verified), relevant sections, data types, examples,
requirement_ids, source_snapshot_ids, manifest.sha256.
**Token range:** 500–8,000 tokens (task-dependent)
**Use case:** Implementation handoff; test generation; coverage validation
**Subsystem:** ContextPackBuilder
**State:** context_pack (J)
**When to use:** Any production AI task that requires spec authority

---

## Resolution Selection Rules

| Task Type | Recommended Resolution | Rationale |
|-----------|----------------------|-----------|
| RequirementExtractor run | Level 2–3 | Needs full structure |
| SpecVerifier proof | Level 2 | Needs original text for provenance |
| Implementation handoff | Level 8 | Deterministic, minimal, verified |
| Test generation | Level 8 | Requirements + examples only |
| Coverage audit | Level 3–4 | All requirements visible |
| Format overview | Level 7 | Single paragraph sufficient |
| Cross-format comparison | Level 3 | Normalized schema required |
| Context-window limited | Level 5–6 | Compressed but requirement-preserving |

---

## Context Pack Assembly from Levels

A ContextPackBuilder task context pack (Level 8) typically contains:
- Verified requirements from Level 3 (normalized_artifact)
- Relevant sections from Level 2 (parsed_artifact) for provenance
- Examples from Level 2 for implementation guidance
- Manifest from ContextPackBuilder (manifest.sha256, source_sha256s, index_version)

The assembler selects minimum required levels to fit the target token budget while
preserving all required requirements for the task.
