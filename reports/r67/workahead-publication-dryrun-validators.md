# R67 Work-Ahead W3 — Publication Dry-Run Validators

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

## PyPI Dry-Run Validators (No Upload)

Checks implemented (test-level):
1. Package name follows aspose-format-factory-{format} convention
2. Version is non-empty and not "UNKNOWN"
3. README.md exists
4. Apache-2.0 license declared
5. Wheel file present (.whl)
6. Hash manifest present (artifact-manifest.yaml)

Location: tests/evidence/test_r67_manifest_no_pending_final_commit.py (partially covers)
          tests/evidence/test_r67_manifest_hash_strictness.py (hash manifest)

## NuGet Dry-Run Validators (No Upload)

1. Package ID: FormatFactory.{Format}
2. Version: 0.1.0-tier0
3. .nupkg file present
4. Hash manifest has filename/size/sha256
5. Local feed readiness verified via .local/r67-metadata/package-artifacts/

Location: tests/evidence/test_r67_manifest_hash_strictness.py::TestDotnetManifestHashes

## Status

Publication gates remain BLOCKED. No upload performed.

W3_PUBLICATION_DRYRUN_VALIDATORS: COMPLETE
