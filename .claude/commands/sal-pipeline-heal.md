---
version: "1.0"
last-updated: "2026-06-21"
phase-available: "all"
gate-required: null
created-by: TC-SAL-SKILL-001 (skill-governance-sync-sprint)
product_track: sal_infrastructure
---

# /sal-pipeline-heal

Execute one governed sprint of SAL (Specification Authority Layer) pipeline healing work.
This skill governs all implementation work against ROOT-01..ROOT-08 root causes documented
in `plans/snoopy-juggling-seal.md`.

**This is the REQUIRED skill for all TC-SAL-IMPL-* and TC-SAL-DIAG-* taskcards that are
NOT STARTED. No agent may modify SAL implementation files without first invoking this skill.**

## Purpose

Govern healing of the SAL source-to-consumption pipeline. The SAL pipeline is broken at
multiple stages (see Section 1.2 of snoopy-juggling-seal.md). This skill provides a
governed execution contract for each repair sprint so that:
1. All healing work is traceable to a specific taskcard and root cause.
2. Each sprint produces a skill transcript proving skill invocation.
3. No agent can modify SAL infrastructure files without a governing skill.
4. Evidence declarations can include `skill_id: sal-pipeline-heal` to satisfy V46 validator.

## Root Causes This Skill Governs

| Root Cause | Description | Taskcard |
|-----------|-------------|---------|
| ROOT-01 | sal_master_runner.py is a template generator, not a pipeline orchestrator | TC-SAL-IMPL-001 (COMPLETE) |
| ROOT-02 | Real spec cache orphaned — produced but never consumed after workbench | TC-SAL-IMPL-002 |
| ROOT-03 | Fact ID namespace incompatibility blocks end-to-end validation | TC-SAL-IMPL-001 (COMPLETE) |
| ROOT-04 | sources.jsonl schema mismatch with SpecSource dataclass | TC-SAL-IMPL-004 |
| ROOT-05 | Context packs structurally valid but semantically empty | TC-SAL-IMPL-005 (COMPLETE) |
| ROOT-06 | FODT has no normalized text despite sharing ODF source | TC-SAL-IMPL-003 |
| ROOT-07 | ZST RFC 8878 cached but never processed | TC-SAL-IMPL-002 |
| ROOT-08 | No semantic-unit census — no extraction denominator | TC-SAL-DIAG-008 |

## When to Run

Run this skill BEFORE any sprint that involves:
- Modifying `tools/specification-authority-layer/` files
- Reading or writing `.local/spec-cache/` workbench artifacts
- Running `sal_master_runner.py` with source-modifying flags
- Producing or validating `FACT-<FORMAT>-NNN` fact IDs
- Modifying `sal-facts-latest.json` or context packs

Do NOT run for read-only recon or evidence reviews.

## Required Inputs

- `taskcard_id` — the TC-SAL-IMPL-* or TC-SAL-DIAG-* taskcard being executed
- `format_id` — the format being processed (e.g., `fods`, `zst`, `fodt`)
- `root_cause_id` — the ROOT-0N being addressed (e.g., `ROOT-02`)
- `spec_cache_path` — path to the spec cache directory for this format
  (e.g., `.local/spec-cache/fods/1.3/`)
- `target_stage` — which pipeline stage is being healed:
  one of: `normalization`, `extraction`, `fact_id_repair`, `context_pack`, `census`, `schema_migration`

## Pre-Execution Checks (MANDATORY — stop if any fail)

1. Read `plans/snoopy-juggling-seal.md` to confirm taskcard status and dependencies.
2. Confirm the taskcard is NOT already COMPLETE.
3. Confirm all taskcard dependencies are met (per Section 11 DAG in the plan).
4. Confirm the spec cache path exists and contains a SHA-256 verified source file.
   - If spec cache is missing: this is a TRUE_EXTERNAL_GATE (spec acquisition required).
   - Do NOT proceed with empty or missing spec cache. Report: `BLOCKED_SPEC_CACHE_MISSING`.
5. Confirm `tools/specification-authority-layer/` contains the tool for the target stage.
6. Read the preservation constraints in Section 12 of snoopy-juggling-seal.md.

## Steps

1. **Read the governing plan** (`plans/snoopy-juggling-seal.md`) for the taskcard spec,
   allowed paths, forbidden paths, and acceptance criteria.
2. **Inventory current state** of the target stage:
   - What files exist in spec_cache_path?
   - What tools exist in `tools/specification-authority-layer/`?
   - What facts, if any, exist in the workbench?
3. **Execute the smallest correct change** for the target stage:
   - ROOT-02/ROOT-07: Run the extractor tool against the real spec cache.
   - ROOT-04: Fix the sources.jsonl schema mismatch.
   - ROOT-06: Generate FODT normalized text from ODF source.
   - ROOT-08: Run semantic census on available normalized text.
4. **Verify output artifacts** match the SAL Fact Contract (Section 2 of the plan):
   - Fact IDs use `FACT-<FORMAT>-NNN` namespace.
   - Each fact has: format_id, spec_id, spec_version, source_sha256, section_id, verification_status.
   - Facts stored in `verified-facts-review.yaml` under the format's workbench directory.
5. **Run focused tests** if test files exist for the modified tool.
6. **Write skill transcript** to `reports/skills-r<N>/skill-transcripts/sal-pipeline-heal-<taskcard_id>.json`
   with schema: `{skill_id, taskcard_id, format_id, root_cause_id, changed_files, output_artifacts, test_results, verdict}`.
7. **Update plan** status for this taskcard in `plans/snoopy-juggling-seal.md`.

## Mandatory Validations

- `spec_cache_verified`: spec cache path exists with SHA-256 file
- `tool_invoked`: at least one SAL tool was executed (not bypassed)
- `output_artifact_produced`: workbench artifact (YAML, JSON, or normalized text) was written
- `fact_ids_in_correct_namespace`: all produced fact IDs match `FACT-[A-Z]+-[0-9]+`
- `skill_transcript_written`: transcript JSON written to reports/skills-r<N>/skill-transcripts/

## Allowed Paths

- `tools/specification-authority-layer/` (read + targeted repair)
- `.local/spec-cache/<format>/<version>/workbench/` (write fact artifacts)
- `.local/sal-output/` (write runner output)
- `plans/snoopy-juggling-seal.md` (update taskcard status only)
- `reports/skills-r<N>/skill-transcripts/sal-pipeline-heal-<taskcard_id>.json` (write transcript)

## Forbidden Paths

- `src/python/` — no product source changes during SAL healing
- `src/net/` — no product source changes during SAL healing
- `registry/format-registry.yaml` — no gate state changes
- `plans/master-plan.md` — no plan modifications

## Preservation Constraints (from plan Section 12)

**NEVER:**
- Delete or overwrite verified facts already in workbench YAML files
- Modify `validate_spec_fact_refs.py` in ways that weaken validation
- Change fact IDs for already-validated facts
- Mark a taskcard COMPLETE without a skill transcript

## Output Format

```
SAL-PIPELINE-HEAL RESULT
------------------------
taskcard_id: TC-SAL-IMPL-XXX
format_id: <format>
root_cause_id: ROOT-0N
target_stage: <stage>
spec_cache_verified: true | false
tools_invoked: [<list>]
output_artifacts: [<paths>]
fact_count_produced: <N>
fact_id_namespace_valid: true | false
test_results: passed | failed | skipped
skill_transcript: reports/skills-r<N>/skill-transcripts/sal-pipeline-heal-<taskcard_id>.json
verdict: PROCEED | BLOCKED_SPEC_CACHE_MISSING | BLOCKED_DEPENDENCY_NOT_MET | ERROR
```

## Skill Transcript Schema

```json
{
  "skill_id": "sal-pipeline-heal",
  "taskcard_id": "TC-SAL-IMPL-002",
  "format_id": "zst",
  "root_cause_id": "ROOT-07",
  "changed_files": [],
  "output_artifacts": [],
  "test_results": "passed | failed | skipped",
  "fact_count_produced": 0,
  "fact_id_namespace_valid": true,
  "verdict": "PROCEED",
  "timestamp": "2026-06-21T00:00:00Z"
}
```

## Anti-Overclaim Rules (binding on all invocations)

Per Section 22 of snoopy-juggling-seal.md, do NOT:
1. Claim a taskcard complete without a transcript at the required path.
2. Claim fact extraction done without workbench YAML with FACT-<FORMAT>-NNN IDs.
3. Claim spec cache verified without SHA-256 hash file.
4. Claim a gate diagnostic complete without the output JSON artifact.

## Changelog

- 1.0 (2026-06-21): Initial version — TC-SAL-SKILL-001 (skill-governance-sync-sprint, SKILL-GAP-011)
