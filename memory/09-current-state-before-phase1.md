---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run015; updated run015–run021 to reflect Phase 2 active, Gate 1 passed, TC-0007 independently verified and fixed, TC-0009 Gate 2 evidence upgraded to SUPPORTED_BY_CACHED_SOURCE
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 09 — Current State (Phase 2 Active)

This file captures the current state after run017. Phase 0 has been accepted. Phase 1A FODS scoring is complete. Gate 1 has been approved by Babar Raza. Phase 2 (FODS Spec and Legal Evidence Planning) is now active — awaiting an explicit Phase 2 execution prompt.

**Last updated:** run021 (combined: hygiene + settings.json fix + spec acquisition + Gate 2 evidence upgrade; master-plan.md v2.17).

## Current status

| Item | Status |
|---|---|
| Phase | Phase 2: FODS Spec and Legal Evidence Planning |
| Phase 0 accepted | YES — 2026-05-04 (run015, human-authorized) |
| Phase 1A complete | YES — FODS scored 93/100 (run015), independently verified (run016) |
| Gate 1 status | **PASSED** — approved by Babar Raza, 2026-05-04 (run017) |
| Gate 2 status | **evidence_cached_pending_independent_verification** — run019 draft + run020 verification + run021 spec acquisition + evidence upgrade |
| Active formats | fods (gate_1: passed; gate_2: evidence_cached_pending_independent_verification) |
| Registry | FODS entry with scoring (93/100, Accept band); gate_1: passed; gate_2: evidence_cached_pending_independent_verification |
| FODS acquisition pack | EXISTS — acquisition-packs/fods/ (5 files; spec-evidence.md + legal-notes.md upgraded run021 to SUPPORTED_BY_CACHED_SOURCE) |
| TC-0001 status | COMPLETED — Gate 1 approved (run017) |
| TC-0007 status | **completed_independently_verified_run020** — spec_index.py schema fixed, refresh_check.py encoding fixed |
| TC-0009 status | **evidence_cached_pending_independent_verification** — Gate 2 draft run019; verified run020; spec acquired + evidence upgraded run021 |
| Phase 2 allowed | YES — Gate 1 passed; TC-0009 governs next steps |
| Phase 2 Gate 2 evidence | CACHE-BACKED — spec downloaded run021 (24.27 MB); 6/8 fast-path items; primary claims SUPPORTED_BY_CACHED_SOURCE; awaiting project lead sign-off |
| Samples | None |
| Schemas | None |
| Prototypes | None |
| Product source | None |
| CI workflows | None |
| Commercial source folder | Must not exist |
| Specs downloaded | YES — ODF 1.3 Part 3 PDF (24.27 MB, sha256:92cfe64...b066) downloaded run021; stored at .local/spec-cache/fods/1.3/ (gitignored) |
| Commits made | c9d02da (run015); c79f2d1 (run017); 0c97256 (run018 via run019); 589c1af (run019); 1e69121 (run020 tooling fixes); e8ab83f (run020 evidence leftovers) |
| Uncommitted | run021 changes (settings.json, spec-evidence.md, legal-notes.md, pack.yaml, registry, TC-0007, TC-0009, master-plan v2.17, memory/06, memory/09) — pending commit |
| Master plan version | 2.17 (as of run021) |
| AGENTS.md sections | A through V (22 sections) |
| Memory integration | Completed run010; AGENTS.md Section U added |
| Source layout propagated | YES — completed run011 (master-plan.md v2.8) |
| Memory reconciliation | Completed run013 — stale pending-propagation notes removed |
| Independent verification rule | Added run016 (DEC-034, AGENTS.md Section V, GOVERNANCE.md Section 15) |

## Run history as of this memory update

| Run | Stream | Purpose |
|---|---|---|
| run001-run008 | Main execution | Foundation, healing, canonicalization, governance, gate semantics, spec-cache |
| run009 | Main execution | Spec-cache governance cleanup (TC-0007 correction, authorization model) |
| run010 | Memory stream | Memory integration (AGENTS.md Section U, GOVERNANCE.md memory rule, TC-0008) |
| run011 | Main execution | Product source-layout reconciliation (format-first layout propagated to master plan v2.8, all docs) |
| run012 | Memory stream | Memory sync after run009/run010 and human source-layout expectation (stale notes added) |
| run013 | Main execution | Source-layout verification; stale pending-propagation notes removed from memory; docs updated; master-plan v2.9 |
| run014 | Main execution | Phase 0 closure-readiness sprint; full governance audit of all 45 files; stale "run003 bundle" reference fixed; file count corrected (44→45); 28 search patterns verified; memory updated; master-plan v2.10 |
| run015 | Combined sprint | Phase 0 accepted (all 36 checks PASS); G-001/G-002 closed; Phase 0 baseline commit made; FODS scored 93/100 (Accept band); registry entry created; TC-0001 updated; master-plan v2.11 |
| run016 | Independent verification sprint | All run015 claims independently verified; new governance rule DEC-034 added (independent verification before human review); AGENTS.md Section V added; GOVERNANCE.md Section 15 added; 5 memory files updated; master-plan v2.12 |
| run017 | Gate 1 approval + Phase 2 setup | Gate 1 approved (Babar Raza, 2026-05-04); registry updated; TC-0001 closed; acquisition-packs/fods/ skeleton created; TC-0009 created; 6 memory files updated; combined commit made; master-plan v2.13 |
| run018 | State reconciliation (committed via run019) | README.md, ROADMAP.md, settings.json Phase 2, master-plan v2.14 healed. G-HEAL-018–025. No commit in run018. |
| run019 | Combined sprint | run018 committed (0c97256). TC-0007 spec_index.py + acquire_spec.py + refresh_check.py. TC-0009 Gate 2 evidence draft (spec-evidence.md, legal-notes.md). Committed run019 (589c1af). master-plan v2.15. |
| run020 | Independent verification + schema reconciliation + spec acquisition attempt | 5 TC-0007 fixes: spec_index.py schema, acquire_spec.py warning, refresh_check.py encoding, docs/specification-cache.md, settings.json. Spec download blocked (--allow-network denied). Pre-download spec-index.yaml metadata entry created. Evidence updated (5/8 fast-path). G-021 logged. Committed 1e69121 + e8ab83f. master-plan v2.16. |
| run021 | Combined sprint: hygiene + settings.json fix + spec acquisition + evidence upgrade | __pycache__ removed; settings.json deny rule for acquire_spec removed (T3 authorization); ODF 1.3 Part 3 PDF acquired (24.27 MB, sha256:92cfe64...b066); spec-evidence.md upgraded to SUPPORTED_BY_CACHED_SOURCE; legal-notes.md 6/8 checklist; TC-0007 status → completed_independently_verified_run020; TC-0009 + pack.yaml + registry + master-plan v2.17 + memory/06 + memory/09 updated. Commit pending. |

## Latest known evidence bundles

```text
run015: phase0-run015-phase0-acceptance-and-scoring-[timestamp].zip
run016: run016-independent-verification-sprint.zip
run017: run017-gate1-approval-phase2-setup-[timestamp].zip
run019: run019-phase2-spec-cache-and-evidence-staging/ (staging dir; no canonical zip)
run020: run020-verify-cache-and-strengthen-gate2-staging/ (staging dir; no canonical zip)
run021: run021-spec-acquisition-and-gate2-upgrade-20260504.zip  ← CURRENT (canonical; pending creation)
```

## Source layout (PROPAGATED — run011, CONFIRMED run013)

The format-first source layout is now in `plans/master-plan.md` v2.8+:

- `src/net/{format}/` — .NET product workspace per format (e.g., `src/net/odp/`)
- `src/python/{format}/` — Python FOSS product workspace per format (e.g., `src/python/odp/`)

Old paths are OBSOLETE: `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/`. Do not create these.

.NET FOSS packaging: deferred as DEC-033. Must resolve before Gate 10 .NET release.

## Gate 2 evidence status (run019+run020+run021)

Phase 2 execution prompt was issued in run019. TC-0009 Gate 2 evidence draft completed. run020 strengthened the evidence. run021 acquired the spec and upgraded all primary claims.

- `acquisition-packs/fods/spec-evidence.md` — primary source, XML structure, security analysis; run021 upgraded key claims to SUPPORTED_BY_CACHED_SOURCE; sha256 and download date recorded
- `acquisition-packs/fods/legal-notes.md` — Category 1 fast-path checklist 6/8 items confirmed (run021 added actual download confirmation); 2 items pending project lead review/sign-off
- `acquisition-packs/fods/pack.yaml` — gate_2 status = evidence_cached_pending_independent_verification; spec_cache section shows downloaded:true, sha256, file_size_bytes
- `registry/format-registry.yaml` — gate_2.status = evidence_cached_pending_independent_verification; full download details in notes

Spec DOWNLOADED (run021). ODF 1.3 Part 3 PDF (OpenDocument-v1.3-os-part3-schema.pdf) acquired from OASIS official source. Size: 24,270,588 bytes. sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066. Stored at .local/spec-cache/fods/1.3/ (gitignored). spec-index.yaml validates VALID/CURRENT.

## TC-0007 spec-cache tooling (run019+run020)

Three scripts in `tools/spec-cache/`, independently verified and fixed in run020:
- `spec_index.py` — REQUIRED_FIELDS restructured (run020 fix): always-required vs nullable post-download fields; pre-download entries now valid
- `acquire_spec.py` — spurious redistribution_permitted=False warning removed (run020 fix)
- `refresh_check.py` — Windows cp1252 encoding bug fixed (U+2500 → ASCII hyphen, run020 fix)

`docs/specification-cache.md` — schema expanded and Stage 2 lifecycle corrected (run020).

## Next required actions

1. Human reviews legal-notes.md fast-path checklist (2 pending items: patent search waiver + project lead sign-off).
2. Human Gate 2 sign-off — run020 serves as independent verification (DEC-034); spec now cached (run021).
3. After human Gate 2 approval: update registry gate_2.status → passed; update master-plan v2.18.
