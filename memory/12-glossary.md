---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run008
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 12 — Glossary

| Term | Meaning |
|---|---|
| Acquisition pack | Per-format evidence package with manifest, spec evidence, legal notes, sample sources, parser notes. |
| Artifact index | Local-only YAML index under `.local/` tracking artifacts, visibility, hashes, staleness, and reuse state. |
| Bundle | Zip file produced by execution agent for human upload and review. |
| DD3 | Deferred decision about whether commercial source lives in public monorepo or private repo. |
| Evidence-only | Visibility classification for artifacts that inform implementation but are not released. |
| FODS | Flat OpenDocument Spreadsheet, proposed first pilot. |
| Gate | Human-approved checkpoint in the acquisition pipeline. |
| Gate 9 | Product Mapping Complete, creates implementation planning, not product source. |
| Gate 10 | OSS readiness/release readiness after OSS source exists. |
| Gate 11 | Commercial readiness/release readiness after commercial source exists and review passes. |
| Gnumeric | Proposed second spreadsheet candidate after FODS. |
| Local-only | Stored on disk but not committed, typically under `.local/`. |
| Memory package | `/memory` files preserving chat history, rationale, decisions, and current state for agents. |
| Neutral model | Language-neutral schema connecting format evidence to product implementations. |
| Oracle | Reference tool used for comparison, not absolute truth if a spec exists. |
| Phase 0 | Foundation and governance only. No format-specific work. |
| Phase 1A | Future candidate scoring and Gate 1 review preparation. |
| Phase 1B | Post-Gate-1 transition only after human approval. |
| Phase 2 | Evidence and legal pack creation after Gate 1 approval. |
| Phase 3 | Prototype, neutral model, oracle, fuzzing, security, product mapping. |
| Phase 4 | Product implementation after proper authorization. |
| Public | Visibility classification safe for open-source release. |
| Spec cache | Local system for caching official specs/materials under `.local/spec-cache/`. |
| WIP limit | Limit on concurrent formats in active gate bands. |
