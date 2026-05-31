# Runtime Output Inclusion Proof

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Supervisor Runtime Outputs in R80 Bundle

The following `reports/supervisor/` files are listed in the R80 contract's `required_repo_files`
and will be verified as present in the final ZIP:

| File | Status | Purpose |
|---|---|---|
| reports/supervisor/evidence-review.json | PRESENT (confirmed ls) | Structured evidence review output |
| reports/supervisor/evidence-review.md | PRESENT | Human-readable evidence review |
| reports/supervisor/contradictions.md | PRESENT | Contradiction detection output |
| reports/supervisor/next-sprint.md | PRESENT | Next sprint prompt |
| reports/supervisor/next-sprint-taskmaster.json | PRESENT | TM import format |
| reports/supervisor/next-ruflo-lanes.json | PRESENT | Ruflo lane plan |
| reports/supervisor/approval-gates.md | PRESENT | Gate classification |
| reports/supervisor/session-resume.md | PRESENT | Fresh session briefing |

## Pre-Build Verification

```bash
$ ls reports/supervisor/
approval-gates.md
contradictions.json
contradictions.md
discovery-summary.md
evidence-review.json
evidence-review.md
memory-sync-report.md
next-ruflo-lanes.json
next-sprint-taskmaster.json
next-sprint.md
session-resume.md
```

All 8 required files are present. Additional files (contradictions.json, discovery-summary.md,
memory-sync-report.md) are not required by the contract but will be included by the builder
as they are in the repo working tree.

## Why This Wasn't in Previous Bundle

The previous bundle (dual-orchestration-supervisor-e2e) was built before the supervisor
run-on-latest was executed and before reports/supervisor/ was created. Since the files were
not listed in required_repo_files, they were absent from the ZIP.

## Validation Method

Post-build, the R80 bundle will be verified with:
```python
zf = zipfile.ZipFile('r80-bundle.zip')
supervisor_files = [n for n in zf.namelist() if 'reports/supervisor/' in n]
assert len(supervisor_files) >= 8, f"Expected 8 files, got {len(supervisor_files)}"
```

This check is also automated in `validate_supervisor_evidence_bundle.py` check SUP-V-004.
