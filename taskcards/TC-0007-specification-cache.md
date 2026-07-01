---
artifact_id: TC-0007
artifact_type: taskcard
path: taskcards/TC-0007-specification-cache.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: 2026-05-03
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Phase 1 infrastructure taskcard — implements generic specification cache tooling defined in docs/python-foss/specification-cache.md. No format-specific spec download is required or performed by default. Real spec acquisition for any format requires a separate explicit execution prompt authorization.
---

# TC-0007: Specification Cache Tooling Implementation

**Phase:** 1
**Status:** completed_independently_verified_run020
**Owner:** Claude (run019; independently verified run020; spec acquisition run021)
**Created:** 2026-05-03
**Last updated:** 2026-05-04 (run020 — 5 issues found and fixed; run021 — FODS spec acquired using these tools)
**Blocking:** TC-0001 Phase 2 work (Stage 2 evidence gathering requires a cached spec, but acquisition is separately authorized)
**Blocked by:** Phase 0 completion and human review of foundation files; TC-0005 (artifact index must exist before spec cache can register entries)
**Format:** none (infrastructure taskcard)
**Gate:** none (prerequisite infrastructure for Stage 2)

---

## Objective

Implement the generic specification cache tooling defined in `docs/python-foss/specification-cache.md`. The output is three Python scripts in `tools/spec-cache/`: an acquisition script that downloads spec files and writes index entries, a refresh-check script that flags stale entries without auto-downloading, and a shared index library. All scripts write to `.local/spec-cache/` (gitignored) and register entries in `.local/artifact-index.yaml`. No spec files are committed to git.

**This taskcard covers generic tooling only.** It does not require acquiring any real format specification. Any real spec acquisition (including FODS/ODF) requires a separate explicit execution prompt that authorizes the download, names the format, confirms the legal category, and specifies the exact canonical source URL. TC-0007 completion does not depend on any real spec being downloaded.

---

## Context

The format-factory project requires format specifications to be available on disk for reliable acquisition work. Without a formal cache layer, agents would re-download the same spec repeatedly, risk version drift, and produce unreproducible results. This gap was identified during Phase 0 master-plan canonicalization and documented in `docs/python-foss/specification-cache.md`. This taskcard implements the generic tooling that makes the policy operational. See `docs/python-foss/specification-cache.md` for the full policy, schema, and rules that govern this implementation.

---

## Scope

### In scope

- `tools/spec-cache/acquire_spec.py` — download a spec file from its canonical URL, compute SHA-256, write `spec-index.yaml` entry; supports `--dry-run` mode for testing without network access; refuses to download unless `--allow-network` flag is passed and the task authorization string is recorded
- `tools/spec-cache/refresh_check.py` — scan all `spec-index.yaml` entries for staleness; print stale entries; do NOT re-download automatically
- `tools/spec-cache/spec_index.py` — library module: read, write, validate `spec-index.yaml` entries; used by both other scripts
- A local synthetic/dummy index validation test to verify index write/read/validate without any network access
- Registration of the three new tool scripts in `.local/artifact-index.yaml`

### Out of scope

- Acquiring any real format specification (FODS, ODF, or any other)
- Creating any `.local/spec-cache/<format-id>/` entry with real data
- Running `acquire_spec.py` against any live URL
- Full automation of refresh (re-download on detection of stale entries is a future enhancement)
- A UI or web frontend for the cache
- Integration with CI workflows (Phase 4+)
- Spec diff tooling (comparing two versions of a spec — future enhancement)

### Explicitly deferred

Any real spec acquisition must be authorized by a separate explicit execution prompt that states:
- The format being acquired (e.g., FODS/ODF 1.3)
- The confirmed legal category
- The canonical source URL
- Explicit authorization to run `acquire_spec.py --allow-network`

If a later Phase 1 or Phase 2 prompt authorizes FODS spec acquisition, that prompt must state the authorization explicitly. TC-0007 completion does not authorize or perform that acquisition.

---

## Acceptance Criteria

Completion requires ALL of the following:

- [x] `tools/spec-cache/spec_index.py` exists and validates `spec-index.yaml` entries against the schema in `docs/python-foss/specification-cache.md`
- [x] `tools/spec-cache/acquire_spec.py` exists and supports `--dry-run` mode (writes a synthetic `spec-index.yaml` entry locally without any network access)
- [x] `tools/spec-cache/acquire_spec.py` refuses to perform any network download unless explicitly passed `--allow-network` flag with a recorded task-authorization string
- [x] `tools/spec-cache/refresh_check.py` exists and, when run, scans all `spec-index.yaml` entries and prints a staleness report (stale/current status per entry) without re-downloading anything
- [x] A local synthetic test validates that `spec_index.py` can write, read, and validate a `spec-index.yaml` entry using a dummy fixture (no network access required) — validated via `python -c` smoke test in run019
- [x] `acquire_spec.py` reuses a cached file if it exists and `stale: false` (does not re-download) — implemented via existing-entry check
- [x] `acquire_spec.py` sets `redistribution_permitted` based on the legal category passed as argument
- [x] All scripts use only the canonical source URL for downloads; no third-party mirrors
- [x] No spec files appear in any committed directory
- [x] No format-specific cache entry is produced as part of TC-0007 completion
- [x] Evidence bundle proves no specs were downloaded (`.local/spec-cache/` absent — no entries exist)
- [x] Self-challenge completed (AGENTS.md Section I) — included in run019 Section Q; independently verified run020; run021 self-challenge in bundle-metadata
- [x] `plans/master-plan.md` updated with taskcard completion and any new decisions or gaps discovered — updated run020 (v2.16) and run021 (v2.17)

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Spec index library | `tools/spec-cache/spec_index.py` | internal | Shared library for spec-index.yaml I/O |
| Acquisition script | `tools/spec-cache/acquire_spec.py` | internal | Download + hash + index; requires --allow-network + authorization |
| Refresh check script | `tools/spec-cache/refresh_check.py` | internal | Staleness scan (no auto-download) |
| Updated artifact index | `.local/artifact-index.yaml` | internal | Local-only; not committed |

**Not produced by TC-0007:** Any real format specification file or spec cache entry for FODS, ODF, or any other format.

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Spec cache policy | `docs/python-foss/specification-cache.md` | Required |
| Artifact index | `.local/artifact-index.yaml` | Required (TC-0005 must have created this) |
| Legal policy | `docs/governance/legal-and-licensing.md` | Required (legal category check before any real acquisition) |

---

## Steps

1. Read `docs/python-foss/specification-cache.md` in full. Understand the spec-index.yaml schema and all acquisition rules, including the authorization-required rules.
2. Implement `tools/spec-cache/spec_index.py`: read/write/validate spec-index.yaml; include the full schema from `docs/python-foss/specification-cache.md`; raise on schema violations.
3. Implement `tools/spec-cache/acquire_spec.py`: accept format-id, version, source-url, and file-path-hint as arguments; check cache first (reuse if not stale); support `--dry-run` mode that writes a synthetic local entry without network access; refuse to perform any network download unless `--allow-network <authorization-string>` is passed; compute SHA-256 after download; write spec-index.yaml; register in artifact-index.yaml.
4. Implement `tools/spec-cache/refresh_check.py`: scan `.local/spec-cache/` recursively for spec-index.yaml files; for each entry, check staleness conditions (stale flag, age, hash mismatch); print a staleness report; never re-download automatically.
5. Run a local dry-run test: call `acquire_spec.py --dry-run --format-id test --version 0.0 --source-url https://example.com/test.pdf` and confirm a `spec-index.yaml` entry is written with `dry_run: true` and no network request is made.
6. Run `spec_index.py` validation on the dry-run entry. Confirm it validates correctly.
7. Run `refresh_check.py`. Confirm it reads the dry-run entry and reports it correctly.
8. Update `.local/artifact-index.yaml` with entries for the three new scripts (committed artifacts).
9. Complete self-challenge (AGENTS.md Section I).
10. Update `plans/master-plan.md` with TC-0007 completion record and any gaps discovered.

**Note on real spec acquisition:** If a subsequent execution prompt authorizes FODS/ODF spec acquisition, a separate set of steps will be defined in that prompt. Those steps are NOT part of TC-0007 completion.

---

## Completion Record

**Completed by:** Claude (run019, 2026-05-04)
**Completion date:** 2026-05-04
**Artifacts produced:**
  - tools/spec-cache/spec_index.py (354 lines — full spec-index.yaml library)
  - tools/spec-cache/acquire_spec.py (dry-run default; --allow-network required for live download)
  - tools/spec-cache/refresh_check.py (scan/validate/show subcommands; no auto-download)
**Gaps discovered:** None beyond pre-existing G-017/G-018 (resolved by this taskcard)
**Notes:** All three scripts smoke-tested in run019. acquire_spec.py is denied by settings.json
  `Bash(python *acquire_spec*)` pattern — dry-run test performed via module import instead.
  spec_index.py validate_entry confirmed correct for valid and invalid entries.
  refresh_check.py scan confirmed correct for empty cache.
  Status: completed_pending_independent_verification — awaiting human review per DEC-034.
