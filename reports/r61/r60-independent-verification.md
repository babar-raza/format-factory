# R60 Independent Verification

**Sprint Being Verified:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**IV Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**IV Date:** 2026-05-24
**IV Verdict:** R60_BROAD_PRODUCT_AND_ARTIFACT_PROGRESS_ACCEPTED_SELF_VERIFYING_CLOSURE_REJECTED

## Summary

R60 delivered genuine product progress (4 new capabilities, 103+ tests, .NET consumer proof,
packaging normalization). However, the self-verifying closure protocol has 12 defects that
prevent RC acceptance. R61 must repair all 12 before claiming closure.

## Defects Confirmed

### IV-R60-001: Sidecar Not Physically In Bundle (CRITICAL)

**Category:** sidecar delivery
**Command:**
```
python -c "
import zipfile
with zipfile.ZipFile('.local/r60-pass2-final.zip') as zf:
    sidecar_inside = [n for n in zf.namelist() if 'sha256-proof' in n]
    print('Sidecar inside ZIP:', sidecar_inside)
"
```
**Result:** `Sidecar inside ZIP: []`
**Finding:** The sidecar file `reports/r60/r60-pass2-final.zip.sha256-proof.json` is gitignored and local-only. It is NOT inside the bundle ZIP. Anyone receiving the ZIP cannot validate it without separately receiving the sidecar file.
**Severity:** CRITICAL — external sidecar must accompany the ZIP for offline validation.

---

### IV-R60-002: Pass 2 SHA In final-verdict Mismatches True Final Bundle (CRITICAL)

**Category:** SHA integrity
**Command:**
```
python -c "
import hashlib
with open('.local/r60-pass2-final.zip', 'rb') as f:
    sha = hashlib.sha256(f.read()).hexdigest()
print('Actual bundle SHA256:', sha)
print('final-verdict Pass2 SHA:', 'd2ab8404730a5b47547186c45e6e0da89ce730d7b4b6a4604dc96afe6357e295')
"
```
**Result:**
- Actual bundle SHA256: `f8b6f8cec04e6a1f69ac84a0519938cf282b860b0db25348f73616e5ae7f7c42`
- final-verdict Pass2 SHA: `d2ab8404730a5b47547186c45e6e0da89ce730d7b4b6a4604dc96afe6357e295`
- Match: False
**Finding:** The SHA written in `reports/r60/final-verdict.md` as `BUNDLE_VALIDATION_PASS_2_SHA` is the interim Pass 2 SHA (before the true final was built). The true final bundle has SHA `f8b6f8ce...` (confirmed by sidecar). A reviewer comparing the final-verdict SHA to the delivered bundle will find a mismatch.
**Severity:** CRITICAL — authoritative document references wrong SHA.

---

### IV-R60-003: Validation Without Sidecar Fails (HIGH)

**Category:** validation integrity
**Command:**
```
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/r60-pass2-final.zip \
  --contract tools/evidence/contracts/r60-current-head-rc-sidecar.yaml \
  --check-no-pending
```
**Finding:** Without `--sidecar-proof` argument, validation fails because contract has `sidecar_required: true` and the sidecar is not embedded in the bundle. Additionally, `final-bundle-validation-proof.txt` inside the bundle is a placeholder (see IV-R60-004), which causes `--check-no-pending` to fail.
**Severity:** HIGH — cannot be validated standalone without sidecar.

---

### IV-R60-004: final-bundle-validation-proof.txt Is Placeholder In Bundle (HIGH)

**Category:** proof file integrity
**Command:**
```
python -c "
import zipfile
with zipfile.ZipFile('.local/r60-pass2-final.zip') as zf:
    content = zf.read('bundle-metadata/final-bundle-validation-proof.txt').decode('utf-8')
    print(repr(content))
"
```
**Result:** `'PLACEHOLDER \xef\xbf\xbd will be replaced after candidate validation'`
**Finding:** The `final-bundle-validation-proof.txt` inside the bundle contains only a placeholder string. It was never replaced with actual validation results before the bundle was built. This means `--check-no-pending` on the bundle content finds PENDING-equivalent content.
**Severity:** HIGH — proof file is meaningless inside the bundle.

---

### IV-R60-005: Package Tests Require .local/package-builds Path (HIGH)

**Category:** packaging replay
**Command:**
```python
# In test_r60_artifact_source_commit.py:
BUILD_DIR = PROJECT_ROOT / ".local" / "package-builds" / "python-foss"
```
**Finding:** `tests/packaging/test_r60_artifact_source_commit.py` references `PROJECT_ROOT / ".local" / "package-builds" / "python-foss"` — a hardcoded local path that does not exist in an extracted bundle. Running these tests from an extracted bundle directory will fail on all 8 test cases.
**Severity:** HIGH — packaging replay from extracted bundle not possible.

---

### IV-R60-006: Extracted-Bundle Replay Test Does Not Cover R60 Bundle (HIGH)

**Category:** packaging replay
**Command:**
```python
# In test_r59_extracted_bundle_package_replay.py:
for candidate in ["r59-pass2-final.zip", "r58-pass2-final.zip"]:
    path = PROJECT_ROOT / ".local" / candidate
```
**Finding:** The extracted-bundle replay test `test_r59_extracted_bundle_package_replay.py` only looks for `r59-pass2-final.zip` or `r58-pass2-final.zip` — not the R60 bundle. There is no `test_r60_extracted_bundle_package_replay.py` that exercises the R60 bundle. The R60 bundle's extracted-bundle replay is not proven.
**Severity:** HIGH — R60 bundle replay not tested.

---

### IV-R60-007: .nupkg Files Not Physically In Bundle (CRITICAL)

**Category:** .NET self-contained delivery
**Command:**
```
python -c "
import zipfile
with zipfile.ZipFile('.local/r60-pass2-final.zip') as zf:
    nupkgs = [n for n in zf.namelist() if n.endswith('.nupkg')]
    print('NuPkg files inside ZIP:', nupkgs)
"
```
**Result:** `NuPkg files inside ZIP: []`
**Finding:** No `.nupkg` files are physically included in the bundle. The `dotnet-nupkg-manifest.yaml` references paths like `.local/r60-consumer-proof/local-feed/FormatFactory.Fods.0.1.0-tier0.nupkg` — these are local paths that do not exist in an extracted bundle. Anyone receiving the bundle cannot perform the .NET consumer proof without separately obtaining the NuGet packages.
**Severity:** CRITICAL — .NET self-contained delivery not achieved.

---

### IV-R60-008: dotnet-nupkg-manifest.yaml Uses SHA Prefix Not Full SHA-256 (HIGH)

**Category:** SHA integrity
**File:** `.local/r60-metadata/dotnet-nupkg-manifest.yaml`
**Content:**
```yaml
sha256_prefix: "35712390"   # FormatFactory.Fods
sha256_prefix: "bfdfbd48"   # FormatFactory.Fodt
```
**Finding:** Both NuGet package entries use `sha256_prefix` (8-character prefix) instead of full 64-character SHA-256. This violates the evidence integrity requirement. An 8-character prefix provides only ~4 billion possible values and cannot be used for authoritative verification.
**Severity:** HIGH — non-authoritative SHA reference.

---

### IV-R60-009: artifact_source_commit Conflated With final_git_head (HIGH)

**Category:** commit identity
**File:** `.local/r60-metadata/source-commit-proof.txt`
**Content:**
```
R60 FINAL HEAD: 61780e4cbd33100460ba872ded5b96c1feae2847
```
**Finding:** The source-commit-proof.txt calls `61780e4` the "FINAL HEAD" but this is actually the mega-train commit (the last source/package-affecting commit). The actual final HEAD is `1171b4f` (chore: update final-verdict with pass 2 SHA). There is no explicit distinction between `artifact_source_commit` (61780e4) and `final_git_head` (1171b4f) in any R60 metadata file.
**Severity:** HIGH — commit identity conflated; no policy defined.

---

### IV-R60-010: Reports Reference 61780e4 As "Final HEAD" (MEDIUM)

**Category:** documentation accuracy
**File:** `reports/r60/` (multiple)
**Finding:** R60 reports and metadata files describe `61780e4` as "R60 FINAL HEAD" which is inaccurate. `61780e4` is the mega-train commit; the true final HEAD after all chore commits is `1171b4f`. This creates confusion when comparing the source commit to git HEAD.
**Severity:** MEDIUM — documentation accuracy.

---

### IV-R60-011: No Explicit artifact_source_commit / final_git_head Policy (MEDIUM)

**Category:** policy gap
**Finding:** There is no documented or enforced distinction between `artifact_source_commit` (the commit from which packages were built) and `final_git_head` (the commit at bundle validation time, after chore commits). The validator does not check for or require this field. Without this policy, future sprints will continue to conflate these concepts.
**Severity:** MEDIUM — policy gap enabling repeat defect.

---

### IV-R60-012: Extracted-Bundle Replay Not Proven For R60 (MEDIUM)

**Category:** replay integrity
**Finding:** There is no evidence that the R60 bundle can be extracted to a clean directory and used to replay the packaging proof without any `.local/` dependencies. The existing replay tests (IV-R59 era) use R59 or R58 bundles. R60-specific replay has not been demonstrated.
**Severity:** MEDIUM — replay completeness.

---

## Product Progress Accepted (Real Work Delivered)

Despite the 12 closure defects, the following R60 work is genuine and accepted:

- 4 new FODS/FODT capabilities: `workbook_sheet_summary`, `workbook_empty_rows`, `document_word_count`, `document_table_summary`
- 103+ new tests all passing
- All 10 Python packages rebuilt from R60 HEAD (61780e4)
- Installed smoke proving 8 R59/R60 APIs from installed wheel
- Packaging suite normalized: no skips
- .NET consumer restore + run with actual output
- TSV Gate 8: 16 security regression tests
- Phase Audit 11: RC reproducibility PASS
- Test results: 2749 non-AI, 617 AI, 302 .NET passed

## Reclassification

**Previous verdict:** R60_SELF_VERIFYING_SIDECAR_PASS_CURRENT_HEAD_RC_CLOSURE_COMPLETE
**Reclassified verdict:** R60_BROAD_PRODUCT_AND_ARTIFACT_PROGRESS_ACCEPTED_SELF_VERIFYING_CLOSURE_REJECTED

**Rationale:** 3 CRITICAL defects (sidecar not in ZIP, SHA mismatch, .nupkg not in bundle) prevent acceptance of the self-verifying closure claim. These are not edge cases — they are the core closure requirements that R60 claimed to fulfill.
