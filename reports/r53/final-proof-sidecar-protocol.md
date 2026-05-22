# Final Proof Sidecar Protocol

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Status:** ADOPTED — active policy from R53 onward

## Problem

A ZIP file cannot contain its own final SHA-256. The SHA-256 depends on the file's bytes,
which include the bytes of the internal proof file. Any SHA-256 written inside a ZIP is
self-referential: it would need to hash the ZIP containing itself.

R52 recognized this and left PASS 2 fields as PENDING inside the bundle. This was
correct but left the bundle in a state where no external authoritative proof existed.

## Chosen Policy: External Sidecar JSON

**Internal bundle proof (final-bundle-validation-proof.txt):**
- Records PASS 1 validation details (before bundle is sealed)
- Records PASS 2 _validation results_ (PASS/FAIL) but NOT the final SHA/size/entries
- PASS 2 SHA/size/entries field is omitted or set to "See external sidecar proof"

**External sidecar file (outside the ZIP):**
- Filename: `<bundle-name>.sha256-proof.json`
- Example: `r53-self-verifying-baseline.sha256-proof.json`
- Contains: final SHA-256, size_bytes, entry_count, validation_result, timestamp, git_head
- Written AFTER final bundle is built and validated
- MUST NOT be modified after writing

## Sidecar JSON Schema

```json
{
  "sidecar_version": "1.0",
  "run_number": "R53",
  "bundle_path": "/absolute/path/to/bundle.zip",
  "bundle_filename": "bundle.zip",
  "sha256": "<64-hex-sha256>",
  "size_bytes": 4357504,
  "entry_count": 2380,
  "contract_path": "tools/evidence/contracts/r53-....yaml",
  "validation_command": "python tools/evidence/validate_evidence_bundle.py ...",
  "validation_exit_code": 0,
  "validation_result": "PASS",
  "timestamp_utc": "2026-05-22T18:00:00+00:00",
  "git_head": "<40-hex-sha>"
}
```

## Tools

**Write sidecar:**
```bash
python tools/evidence/write_sidecar_proof.py \
  --bundle .local/evidence-bundles/<bundle>.zip \
  --contract tools/evidence/contracts/<contract>.yaml \
  --run-number R53 \
  --validation-result PASS
```

**Validate bundle + sidecar:**
```bash
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/<bundle>.zip \
  --contract tools/evidence/contracts/<contract>.yaml \
  --check-no-pending \
  --sidecar-proof .local/evidence-bundles/<bundle>.sha256-proof.json
```

## Verdict Rules

| State | Required Verdict Modifier |
|-------|--------------------------|
| Internal proof has PASS 2 PENDING SHA + external sidecar exists and validates | PASS — sidecar is authoritative |
| Internal proof has PASS 2 PENDING SHA + no external sidecar | `FINAL_PROOF_BLOCKED` |
| Internal proof claims a SHA that doesn't match bundle | Warning (PROOF_SHA_SIDECAR_RECOMMENDED) |
| External sidecar SHA mismatches actual bundle | FAIL — bundle was modified after sidecar was written |

## Sprint Closeout Sequence (Mandatory)

1. Write all reports
2. Update final-verdict.md (BUNDLE_VALIDATION: PASS, Pass 1 SHA recorded)
3. Commit final-verdict.md
4. Build Pass 2 bundle: `python tools/evidence/build_evidence_bundle.py ...`
5. Validate: `python tools/evidence/validate_evidence_bundle.py ... --check-no-pending`
6. Write external sidecar: `python tools/evidence/write_sidecar_proof.py ...`
7. Validate sidecar: `python tools/evidence/validate_evidence_bundle.py ... --sidecar-proof ...`
8. Do NOT modify bundle after step 6
9. Print `EVIDENCE_BUNDLE:` and `SIDECAR_PROOF:` in final response

## Internal Proof Content for R53+

For sprints using this protocol, the internal proof file should say:
```
PASS 2 RESULT: BUNDLE_VALIDATION: PASS
PASS 2 SHA-256: See external sidecar proof (.sha256-proof.json)
PASS 2 Entries: <N> | Size: <N> bytes (from validator output)
```

This is unambiguous and does not claim the impossible self-referential SHA.

## Retroactive R52 Sidecar

An R52 sidecar was created retroactively at:
`.local/evidence-bundles/r52-state-consistent-installed-artifact-baseline.sha256-proof.json`
SHA: `3aa7b823e4bc457cfefa972adb9a05bb4ee22b0d039adc7da2b6155f7fdceaf1`
This sidecar confirms R52 bundle integrity but does not change R52's verdict status.
