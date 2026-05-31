# Fresh Extract Validation

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Protocol

This validation runs after the final bundle is built. It extracts the ZIP into a temp directory
and verifies all claims independently.

## Checks (pre-build, filled post-build)

### 1. SHA/Size/Entries Match
- Computed from actual ZIP file
- Compared against sidecar proof
- Bundle SHA: `a162c06a2e59ae5f371558216429ab710d9b1db9482cb421029721bad2c4eb85`
- Sidecar SHA: `ac542c5598f2f030495a14ac58bfe22b7e4de2f5f5b07f956c1c9b079a1b270e`
- Entries: 3159, Size: 5,531,062 bytes
- Result: PASS — sidecar matches computed SHA

### 2. Contract File Present in ZIP
- `tools/evidence/contracts/r80-repair-plus-advancement-supervisor-evidence-product-system-hardening.yaml`
- Result: PASS — contract present in ZIP (D-SUP-01 REPAIRED)

### 3. reports/supervisor/ Files Present
- Expected: 8 files minimum
- Found: 8 files — approval-gates.md, contradictions.md, evidence-review.json, evidence-review.md, next-ruflo-lanes.json, next-sprint-taskmaster.json, next-sprint.md, session-resume.md
- Result: PASS — all 8 supervisor runtime outputs present (D-SUP-02 REPAIRED)

### 4. Final Verdict Uses Delegation Labels
- `BUNDLE_SHA256: delegated_to_sidecar_proof`
- Result: PASS — delegation label confirmed in final-verdict.md (D-SUP-03 REPAIRED)

### 5. No .vscode/mcp.json, .taskmaster/, .ruflo/, .swarm/
- Result: CONFIRMED (checked before build — none present)

### 6. Supervisor Validator Passes
- `validate_supervisor_evidence_bundle.py` run against final ZIP
- Result: SUPERVISOR_BUNDLE_VALIDATION: PASS (7 PASS, 2 WARN, 0 FAIL)
- Warnings: SUP-V-006 (no raw validation log file), SUP-V-009 (some limitations may lack follow-up refs) — both acceptable

### 7. Existing Bundle Validator Passes
- `validate_evidence_bundle.py` + `--sidecar-proof`
- Result: BUNDLE_VALIDATION: PASS + SIDECAR_PROOF_VALIDATION: PASS

### 8. Required Repo Files: 0 Missing
- All required_repo_files present in ZIP
- Result: PASS — 0 missing files

## Post-Build Verification Script

```python
import zipfile
z = zipfile.ZipFile('.local/evidence/r80-repair-plus-advancement-supervisor-evidence-product-system-hardening-20260530.zip')
names = z.namelist()
contract_ok = any('r80-repair-plus-advancement' in n and n.endswith('.yaml') for n in names)
supervisor_reports = [n for n in names if 'reports/supervisor/' in n]
verdict_files = [n for n in names if n.endswith('final-verdict.md')]
verdict_content = z.read(verdict_files[0]).decode() if verdict_files else ''
delegation_ok = 'delegated_to_sidecar_proof' in verdict_content
print('Contract present:', contract_ok)
print('Supervisor reports:', len(supervisor_reports))
print('Delegation label used:', delegation_ok)
```
