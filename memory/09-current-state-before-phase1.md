---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run015; updated run015–run019 to reflect Phase 2 active, Gate 1 passed, TC-0007 tooling implemented, TC-0009 Gate 2 evidence draft complete
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 09 — Current State (Phase 2 Active)

This file captures the current state after run017. Phase 0 has been accepted. Phase 1A FODS scoring is complete. Gate 1 has been approved by Babar Raza. Phase 2 (FODS Spec and Legal Evidence Planning) is now active — awaiting an explicit Phase 2 execution prompt.

**Last updated:** run019 (combined sprint: run018 committed 0c97256; TC-0007 spec-cache tooling implemented; TC-0009 Gate 2 evidence draft completed; master-plan.md v2.15).

## Current status

| Item | Status |
|---|---|
| Phase | Phase 2: FODS Spec and Legal Evidence Planning |
| Phase 0 accepted | YES — 2026-05-04 (run015, human-authorized) |
| Phase 1A complete | YES — FODS scored 93/100 (run015), independently verified (run016) |
| Gate 1 status | **PASSED** — approved by Babar Raza, 2026-05-04 (run017) |
| Gate 2 status | **evidence_draft_pending_independent_verification** — run019 draft complete |
| Active formats | fods (gate_1: passed; gate_2: evidence_draft_pending_independent_verification) |
| Registry | FODS entry with scoring (93/100, Accept band); gate_1: passed; gate_2: evidence_draft |
| FODS acquisition pack | EXISTS — acquisition-packs/fods/ (5 files; spec-evidence.md + legal-notes.md updated run019) |
| TC-0001 status | COMPLETED — Gate 1 approved (run017) |
| TC-0007 status | **completed_pending_independent_verification** — spec_index.py, acquire_spec.py, refresh_check.py |
| TC-0009 status | **evidence_draft_pending_independent_verification** — Gate 2 draft completed run019 |
| Phase 2 allowed | YES — Gate 1 passed; TC-0009 governs next steps |
| Phase 2 Gate 2 evidence | DRAFTED — awaiting independent verification + project lead sign-off |
| Samples | None |
| Schemas | None |
| Prototypes | None |
| Product source | None |
| CI workflows | None |
| Commercial source folder | Must not exist |
| Specs downloaded | None (T3 not authorized in run019; spec claims are SUPPORTED_BY_RECORDED_URL or PLAUSIBLE) |
| Commits made | c9d02da (run015); c79f2d1 (run017); 0c97256 (run018 via run019) |
| Uncommitted | run019 changes (TC-0007 scripts, TC-0009 evidence, master-plan v2.15) — authorized for commit |
| Master plan version | 2.15 (as of run019) |
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
| run019 | Combined sprint | run018 committed (0c97256). TC-0007 spec_index.py + acquire_spec.py + refresh_check.py. TC-0009 Gate 2 evidence draft (spec-evidence.md, legal-notes.md). master-plan v2.15. |

## Latest known evidence bundles

```text
run015: phase0-run015-phase0-acceptance-and-scoring-[timestamp].zip
run016: run016-independent-verification-sprint.zip
run017: run017-gate1-approval-phase2-setup-[timestamp].zip
run019: run019-phase2-spec-cache-and-evidence-staging/ (staging dir; zip pending)  ← CURRENT
```

## Source layout (PROPAGATED — run011, CONFIRMED run013)

The format-first source layout is now in `plans/master-plan.md` v2.8+:

- `src/net/{format}/` — .NET product workspace per format (e.g., `src/net/odp/`)
- `src/python/{format}/` — Python FOSS product workspace per format (e.g., `src/python/odp/`)

Old paths are OBSOLETE: `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/`. Do not create these.

.NET FOSS packaging: deferred as DEC-033. Must resolve before Gate 10 .NET release.

## Gate 2 evidence status (run019)

Phase 2 execution prompt was issued in run019. TC-0009 Gate 2 evidence draft completed.

- `acquisition-packs/fods/spec-evidence.md` — filled with primary source, XML structure, security analysis (SUPPORTED_BY_RECORDED_URL + PLAUSIBLE_PENDING_VERIFICATION)
- `acquisition-packs/fods/legal-notes.md` — Category 1 fast-path checklist 4/7 items confirmed; 3 items pending project lead review
- `acquisition-packs/fods/pack.yaml` — gate_2 status updated to evidence_draft_pending_independent_verification
- `registry/format-registry.yaml` — gate_2 status and evidence_drafted_by updated

Spec NOT downloaded (T3 not authorized). Source hash = null. All claims are SUPPORTED_BY_RECORDED_URL or PLAUSIBLE_PENDING_VERIFICATION.

## TC-0007 spec-cache tooling (run019)

Three scripts implemented in `tools/spec-cache/`:
- `spec_index.py` — library for spec-index.yaml CRUD, validation, staleness check, SHA-256
- `acquire_spec.py` — dry-run by default; `--allow-network` requires T3 authorization
- `refresh_check.py` — scan/validate/show subcommands; no auto-download

Smoke tests: spec_index.py validate_entry PASS, refresh_check.py scan PASS (empty cache).

## Next required actions

1. Commit run019 changes (authorized by run019 execution prompt).
2. Independent verification sprint (separate session, DEC-034) for TC-0007 + Gate 2 evidence.
3. Project lead reviews legal-notes.md fast-path checklist (3 pending items).
4. Human Gate 2 sign-off.
