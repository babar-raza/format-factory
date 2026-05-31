# Lane 1 — Known Defect Repair

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Defects Repaired

### D-SUP-01: Contract file not in ZIP

**Root cause:** The contract YAML `tools/evidence/contracts/dual-orchestration-supervisor-e2e-20260530-165603.yaml` was not listed in `required_repo_files` in the contract itself, and was also untracked (not in the repo). The builder only packages files that are either tracked or explicitly required.

**Fix applied:**
1. R80 contract (`tools/evidence/contracts/r80-repair-plus-advancement-supervisor-evidence-product-system-hardening.yaml`) includes itself in `required_repo_files`:
   ```yaml
   - tools/evidence/contracts/r80-repair-plus-advancement-supervisor-evidence-product-system-hardening.yaml
   ```
2. The R80 contract is present in the repo (untracked is sufficient; build_evidence_bundle.py includes all required_repo_files from the working tree).

**Verification:** Bundle will contain `repo/tools/evidence/contracts/r80-repair-plus-advancement-supervisor-evidence-product-system-hardening.yaml`. See `runtime-output-inclusion-proof.md` for post-build verification.

**Prevention:** `tools/supervisor/validate_supervisor_evidence_bundle.py` check SUP-V-003 verifies contract is in ZIP.

---

### D-SUP-02: reports/supervisor/ not in ZIP when claimed

**Root cause:** The previous bundle was built before `reports/supervisor/` files were listed in `required_repo_files`. The evidence summary claimed supervisor runtime outputs as evidence but they were absent.

**Fix applied:**
R80 contract explicitly lists all 8 supervisor runtime outputs in `required_repo_files`:
```yaml
- reports/supervisor/evidence-review.json
- reports/supervisor/evidence-review.md
- reports/supervisor/contradictions.md
- reports/supervisor/next-sprint.md
- reports/supervisor/next-sprint-taskmaster.json
- reports/supervisor/next-ruflo-lanes.json
- reports/supervisor/approval-gates.md
- reports/supervisor/session-resume.md
```

All 8 files exist in `reports/supervisor/` (confirmed via `ls reports/supervisor/`).

**Prevention:** `validate_supervisor_evidence_bundle.py` check SUP-V-004 verifies reports/supervisor/ present when supervisor run is claimed.

---

### D-SUP-03: SHA/size/entry count mismatch

**Root cause:** Multiple rebuild iterations caused final-verdict.md to contain an intermediate SHA (`2b383ee0...`) rather than the final validated SHA (`8edb18ae...`). The circular SHA problem: updating final-verdict.md changes the bundle, which changes the SHA, requiring another update.

**Fix applied (two-part):**
1. R80 final-verdict.md inside the bundle uses a **delegation label**:
   ```
   BUNDLE_SHA256: delegated_to_sidecar_proof
   ```
   This avoids the circular SHA problem entirely. The sidecar is the authoritative SHA proof.

2. The external `reports/r80/final-verdict.md` (outside the bundle, written after build) contains the correct final SHA.

**Protocol going forward:**
- Inner bundle final-verdict.md: use delegation labels for SHA fields
- Sidecar: authoritative SHA proof
- External report: correct SHA for human reference (written after sidecar)

**Prevention:** `validate_supervisor_evidence_bundle.py` check SUP-V-005 accepts delegation labels as correct. Warns (not fails) on one-generation-behind SHA (since that's inherent).

---

### D-SUP-04: No replay fixture included in bundle when replay claimed

**Root cause:** The previous bundle claimed `supervisor_loop.py run-on-latest EXIT 0` but included no replay input bundle. An external extractor could not reproduce the replay.

**Fix applied:**
The R40 replay fixture is referenced explicitly and its location documented. However, the R40 bundle is in `evidence-bundles/` (a local directory, not in the ZIP).

For the R80 bundle:
1. The replay is run against the R40 fixture as before
2. The replay fixture path and SHA are documented in `replay-self-containment-proof.md`
3. A `LIMITATION: REPLAY_FIXTURE_NOT_BUNDLED` marker is added to final-verdict with a follow-up taskcard `TC-SUP-REPLAY-001`
4. The supervisor replay is run during this sprint and output is captured

**Taskcard created:** TC-SUP-REPLAY-001 — Include replay fixture ZIP inside evidence bundle for full self-containment.

---

## Summary

| Defect | Fix Type | Prevention |
|---|---|---|
| D-SUP-01 Contract not in ZIP | Self-referential required_repo_files | SUP-V-003 |
| D-SUP-02 reports/supervisor not in ZIP | Added to required_repo_files | SUP-V-004 |
| D-SUP-03 SHA mismatch | Delegation labels in inner bundle | SUP-V-005 |
| D-SUP-04 No replay fixture | Documented + taskcard | SUP-V-007 |
