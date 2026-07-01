---
artifact_id: TC-0013-fods-gate3-sample-corpus-execution
artifact_type: taskcard
path: taskcards/TC-0013-fods-gate3-sample-corpus-execution.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 3 sample corpus execution taskcard for FODS. Created run025. Executed run026 (2026-05-05): 4 samples created, validated 4/4 PASS, provenance confirmed. Spec Navigation Layer built (884 sections, 940 chunks). Independent verification (DEC-034) completed run027: SHA-256 hashes verified, 4/4 PASS re-confirmed. Gate 3 PASSED (Babar Raza, 2026-05-05, run028). TC-0013 COMPLETED run028."
---

# TC-0013: FODS Gate 3 — Sample Corpus Execution

**Taskcard ID:** TC-0013
**Phase:** 3 (Gate 3 execution)
**Gate:** Gate 3 (Sample Corpus Ready)
**Status:** completed
**Created:** 2026-05-05 (run025)
**Created by:** claude-sonnet-4-6 (run025)
**Executed:** 2026-05-05 (run026)
**Executed by:** claude-sonnet-4-6 (run026)
**Blocking:** Gate 3 approval
**Blocked by:** Independent verification (DEC-034) and Gate 3 human approval

---

## Execution Status (run026)

**Authorization:** Explicit Gate 3 execution prompt issued by human (run026, 2026-05-05).

Execution state:
- Gate 2: PASSED (Babar Raza, 2026-05-05)
- Gate 3 execution: AUTHORIZED and EXECUTED (run026)
- Corpus: 4 samples created, validated 4/4 PASS
- Spec Navigation Layer: COMPLETE (884 sections, 940 chunks, sample-requirements.yaml)
- Provenance: 4 entries confirmed in samples/_provenance.yaml
- Next: Independent verification (DEC-034), then Gate 3 human approval

---

## Objective

Execute the Gate 3 corpus plan defined in `acquisition-packs/fods/sample-sources.md`. Produce a minimum sample corpus of 4 FODS files with confirmed provenance, then request independent verification (DEC-034) and Gate 3 human approval.

---

## Prerequisites

- [x] Gate 2 passed — Babar Raza (2026-05-05, run023)
- [x] TC-0010 corpus plan drafted (run024) and normalization-verified (run025)
- [x] TC-0012 Phase 2 complete — full extraction done; citations.yaml available (run025)
- [x] Spec section references verified against normalized text (run025)
- [x] Explicit Gate 3 execution prompt issued by human (run026, 2026-05-05)
- [x] TC-0013 explicitly assigned to an agent in the execution prompt (run026)

---

## Context

The corpus plan is complete. The normalized spec has been fully extracted. The following facts from the normalized spec inform the sample requirements:

| Element | Spec Section | Role in FODS |
|---|---|---|
| `<office:document>` | §3.1.2 | Root element for all flat XML (FODS) documents |
| `<office:spreadsheet>` | §3.7 | Spreadsheet content container (required for spreadsheet FODS) |
| §2.2.4 | §2.2.4 | ODF Spreadsheet document conformance requirements |
| §9.4 | §9.4 | Spreadsheet Document Content structure |
| §20.8.3 | §20.8.3 | Most frequently cross-referenced attribute section (44 refs) |

These facts were derived from `.local/spec-cache/fods/1.3/normalized/` artifacts (local-only, not committed).

---

## Scope

### In scope

1. Create synthetic FODS samples (project-owned, Apache-2.0)
2. Create `tools/samples/create_fods_samples.py` script
3. Create `samples/by-format/fods/` directory with sample files
4. Create `samples/_provenance.yaml` entries for each sample
5. Verify samples are valid FODS (XML well-formed, correct mimetype)
6. Produce corpus plan execution report

### Out of scope — FORBIDDEN

- Gate 3 self-approval — FORBIDDEN (human-only)
- Parser development — FORBIDDEN (Gate 4)
- Neutral model — FORBIDDEN (Gate 5)
- Product source (`src/`) — FORBIDDEN (Gate 9+)
- Prototype — FORBIDDEN (Gate 4)
- Any sample with license CC-BY-ND, CC-NC, or unknown/unconfirmed — FORBIDDEN
- Creating `samples/by-format/fods/` before this taskcard is explicitly authorized — FORBIDDEN

---

## Planned Sample Files (pre-execution plan — see Acceptance Criteria for actual executed files)

The names below were the planning names. Actual executed names differ (see Acceptance Criteria and `samples/_provenance.yaml`).

| Planned File (pre-execution) | Sample Type | Executed As |
|---|---|---|
| `minimal.fods` | minimal_valid | `minimal-spreadsheet.fods` |
| `empty.fods` | empty_trivial | (merged into minimal — single sheet with one cell) |
| `core-data.fods` | core_data | `multi-sheet-basic.fods` + `typed-values-basic.fods` |
| `edge-case.fods` | edge_case | `formula-basic.fods` |

All executed samples: project-owned, Apache-2.0, reproducible from `tools/samples/create_fods_samples.py`.

---

## Steps (to be executed after explicit Gate 3 prompt)

1. Read `AGENTS.md`, verify phase and gate authorization.
2. Read `plans/master-plan.md`, verify Gate 3 execution is authorized.
3. Read `acquisition-packs/fods/sample-sources.md` for corpus plan.
4. Read `docs/gates.md` Gate 3 criteria.
5. Read `samples/_policy.md` for sample acquisition policy.
6. Create `tools/samples/create_fods_samples.py` — Python script to generate FODS files.
7. Run script: produce 4 sample files to a staging location.
8. Verify each sample is XML well-formed.
9. Create `samples/by-format/fods/` directory.
10. Place verified samples in `samples/by-format/fods/`.
11. Create/update `samples/_provenance.yaml` with entries for all 4 samples.
12. Run validation check: all provenance entries have `provenance_status: confirmed`.
13. Produce corpus execution report (bundle-metadata/corpus-execution-report.md).
14. Request independent agent verification sprint (DEC-034).
15. After verification: request Gate 3 human approval.

---

## Acceptance Criteria

- [x] `samples/by-format/fods/minimal-spreadsheet.fods` — valid FODS, project-owned (PASS, run026)
- [x] `samples/by-format/fods/multi-sheet-basic.fods` — valid FODS, project-owned (PASS, run026)
- [x] `samples/by-format/fods/typed-values-basic.fods` — valid FODS, project-owned (PASS, run026)
- [x] `samples/by-format/fods/formula-basic.fods` — valid FODS, project-owned (PASS, run026)
- [x] `samples/_provenance.yaml` — 4 entries with `provenance_status: confirmed`
- [x] `tools/samples/create_fods_samples.py` exists and is reproducible
- [x] `tools/samples/validate_fods_samples.py` — validation: 4/4 PASS
- [x] No samples with blocked licenses present (all Apache-2.0)
- [x] Spec Navigation Layer: sections.jsonl (884), chunks.jsonl (940), page-map.yaml
- [x] sample-requirements.yaml and parser-requirements-draft.yaml produced
- [x] Independent verification sprint completed (DEC-034) — run027: SHA-256 hashes verified, 4/4 PASS re-confirmed, nav tools smoke-tested
- [x] Gate 3 human approval recorded in `registry/format-registry.yaml` — PASSED (Babar Raza, 2026-05-05, run028)

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TC-0010 corpus plan | DONE | acquisition-packs/fods/sample-sources.md |
| TC-0012 normalization | PHASE 2 DONE | run025: full extraction, citations.yaml available |
| Gate 2 PASSED | DONE | Babar Raza, 2026-05-05 |
| Explicit Gate 3 execution prompt | DONE | Issued run026 (2026-05-05) |

---

## Related Files

- `acquisition-packs/fods/sample-sources.md` — corpus plan (planning document)
- `samples/_policy.md` — sample acquisition policy
- `samples/_provenance.yaml` — provenance registry (to be created/updated during execution)
- `docs/gates.md` Gate 3 — gate criteria
- `docs/governance/legal-and-licensing.md` — license acceptability rules
- `taskcards/TC-0010-fods-gate3-sample-corpus-planning.md` — planning parent
- `taskcards/TC-0012-specification-normalization-layer.md` — normalization (Phase 2 done)
- `.local/spec-cache/fods/1.3/normalized/` — normalized spec artifacts (local-only)
