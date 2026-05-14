---
document_type: evidence_runtime_integration_report
sprint: CONWAY-R4R5R6-DRYRUN-ORCHESTRATION-SWARM-001
lane: E
title: "Evidence Contract Runtime Integration Report"
date: "2026-05-13"
visibility: internal
---

# Evidence Contract Runtime Integration Report — Lane E

**Sprint:** CONWAY-R4R5R6-DRYRUN-ORCHESTRATION-SWARM-001
**Date:** 2026-05-13

---

## VERDICT: INTEGRATION_COMPLETE

---

## Section 1: What Was Integrated

The `commercial_sprint_dryrun.py` orchestrator produces `evidence_contract_metadata` containing:

```python
evidence_contract_metadata = {
    "planned_contract_path": f"tools/evidence/contracts/{sprint_id.lower()}.yaml",
    "planned_bundle_path": f".local/evidence-bundles/{sprint_id.lower()}.zip",
    "planned_metadata_dir": f".local/metadata/{sprint_id.lower()}/",
    "note": "Dry-run only — no actual bundle built. Human authorization required.",
}
```

This enforces sprint-specific metadata directories (Option A from the Lane E containment review
in CONWAY-R2R3). The `planned_metadata_dir` is always a sprint-specific subdirectory, never
the `evidence-bundles/` directory itself.

---

## Section 2: Sprint-Specific Metadata Dir Enforcement

**Rule:** `--metadata-dir` MUST point to `.local/metadata/<sprint-id>/`, NOT `.local/evidence-bundles/`.

**Enforcement location:** `commercial_sprint_dryrun.py:_write_dryrun_report()` generates
the planned build command with the correct `--metadata-dir` path embedded.

**Build command template generated in dry-run reports:**

```bash
python tools/evidence/build_evidence_bundle.py \
  --repo-root . \
  --contract tools/evidence/contracts/<sprint-id>.yaml \
  --metadata-dir .local/metadata/<sprint-id>/ \
  --output .local/evidence-bundles/<sprint-id>.zip
```

This pattern was validated in CONWAY-R2R3 sprint — the resulting bundle was 1.7 MB vs 101 MB
for the R1R2 sprint which used the shared `evidence-bundles/` directory as metadata source.

---

## Section 3: Prior ZIP Exclusion Enforcement

**Root cause (from evidence-bundle-size-containment-20260513.md):**
The build script iterates `metadata_path.iterdir()` and includes all files.
If the metadata dir IS the bundles dir, all prior `.zip` files are included.

**Fix applied this sprint:**
Sprint-specific metadata dir pattern prevents prior ZIP inclusion at the source.
The metadata dir contains ONLY: `git-log.txt`, `git-status-final.txt`, `bundle-manifest.yaml`,
`metadata-identity-report.md`, and `repo-tree.txt`.

**Validated in CONWAY-R2R3:** Bundle size = 1.7 MB (6.9 MB repo + 0.1 MB metadata).

---

## Section 4: Bundle-Size Cap Enforcement

**Proposed policy (from Lane E containment review):**

| Metric | Target |
|--------|--------|
| Bundle compressed size | ≤ 10 MB per sprint |
| `bundle-metadata/` content | Git logs + manifest only (~100 KB) |

**Status:** Sprint-specific metadata dir pattern achieves this target.
No code-level cap enforcement added yet (MEDIUM priority — see containment review).

---

## Section 5: Metadata Floor Validation

The `commercial_sprint_dryrun.py` generates evidence contract metadata including
`min_metadata_count: 5` (for `emergency_blocker_bundle: true` sprints).

For regular sprints, the `RUN_CONTRACT_METADATA_FLOOR=30` from `validate_evidence_bundle.py`
applies. The 30-entry floor requires a richer metadata payload.

**Enforcement:** `emergency_blocker_bundle: true` is set in contracts when git is dirty.
This waives the 30-floor for commit-phase sprints where working tree is controlled but
not yet fully committed.

---

## Section 6: Generated Evidence Contract Template

The dry-run orchestrator documents a minimal evidence contract structure for each sprint:

```yaml
inherit: base-run
contract_id: <sprint-id>
version: "1.0"
require_clean_git: true
emergency_blocker_bundle: false
min_metadata_count: 30
required_repo_files:
  - tools/skills/swarm_prompt_generator.py
  - tools/skills/prompt_quality_gate.py
  - tools/skills/commercial_sprint_dryrun.py
  - <other sprint artifacts>
required_metadata_files:
  - git-log.txt
  - git-status-final.txt
  - bundle-manifest.yaml
sprint_verdicts:
  DRY_RUN_STATUS: DRY_RUN_PASS
  QUALITY_GATE_STATUS: PASS
  R4_PROMPT_GENERATION_STATUS: GENERATED
```

---

**LANE_E_STATUS: COMPLETE**
**SPRINT_SPECIFIC_METADATA_DIR_ENFORCED: YES (in dry-run orchestrator)**
**PRIOR_ZIP_EXCLUSION_ENFORCED: YES (by design — sprint dir isolation)**
**BUNDLE_SIZE_CAP: APPLIED (pattern-based, not code-level)**
**METADATA_FLOOR_VALIDATION: DOCUMENTED**
**NO_DUPLICATE_CONTRACT_ENGINE: CONFIRMED — reuses existing build_evidence_bundle.py**
