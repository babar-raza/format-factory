# Sample-Output Detection Plan — R112

## What Counts as a Sample Output
1. Files under evidence_root/sample-outputs/ directory
2. Evidence-manifest.yaml artifacts with type: sample_output
3. Declaration evidence_artifacts with type: sample_output

## Implementation
- detect_missing_sample_outputs now accepts optional declaration and manifest_path parameters
- Checks all 3 sources; deduplicates by file path
- Returns sources dict showing where each output was found (directory/manifest/declaration)
- Backwards compatible: old callers without new params work exactly as before

## Tests
- TestSampleOutputDetectionRepair: 6 tests covering all paths
