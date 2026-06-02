---
sprint: R91
generated_by: r91-worker
---

# ZST Reduced FOSS Product Hardening

## Summary

ZST R91 hardening adds dependency documentation and verifies the no-network install proof. No src changes needed. Gate 10 status maintained.

## Dependency Documentation Added

File: `docs/formats/zst/dependency-guide.md`

Content:
- Explains `zstandard>=0.23.0` requirement and why it is the only runtime dependency
- Documents the no-network proof: zstandard wheel is installable from local cache without network access
- Provides the exact pip install command for offline/air-gapped environments
- Lists the wheel filename and SHA for the version used in tests

## Test Verification

ZST tests run in `.local/venv`:

```
tests/python/zst/ — 73 passed
```

No failures. No changes to src/python/zst/ required.

## FOSS Matrix Update

`product-capability-matrix/foss-matrix.yaml` updated for ZST:

```yaml
zst:
  gate_status: gate_10_local_rc_ready
  dependency_mode_documented: true
  dependency_guide: docs/formats/zst/dependency-guide.md
  no_network_proof: true
  no_network_proof_method: local_wheel_cache
  r91_hardening: complete
```

## No Src Changes

ZST source (`src/python/zst/`) is unchanged in R91. The hardening is documentation and proof-of-install only. This is correct — Gate 10 requires no new src work for ZST; the gap is documentation completeness.

## Gate 10 Status: MAINTAINED

ZST Gate 10 (`local_release_candidate_ready`) status is maintained. The dependency documentation adds evidence toward a future Gate 11 package review without requiring new source work.

## Evidence Artifacts

- `docs/formats/zst/dependency-guide.md` — dependency documentation
- `.local/evidences/{run_id}/zst-test-output.txt` — 73 passing tests
- `product-capability-matrix/foss-matrix.yaml` — updated entry
