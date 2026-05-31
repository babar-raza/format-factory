# R83 Train J — ZST Dependency Replay and Package Policy

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## ZST Classification (Confirmed from R82)

**Classification:** ZST_DEPENDENCY_MODE_CLASSIFICATION: CONFIRMED

ZST (Zstandard) Python FOSS track depends on the `zstandard` library:
- `zstandard>=0.25.0` (pinned in pyproject.toml)
- Not a pure-Python implementation — wraps libzstd C library
- This is a deliberate design decision (not a gap)

## Dependency Mode Policy

| Mode | Description | ZST Status |
|------|-------------|------------|
| self_contained | No external deps | NO — requires zstandard |
| external_ref | Documents dep, user installs | YES |
| local_rc | Available as local RC | YES |

ZST policy: `installed_artifact_policy: external_ref`
The `zstandard` package must be separately installed by the user.

## Replay Classification

R82 replay confirmed:
1. `pip install zst-0.1.0.dev0-py3-none-any.whl`
2. `pip install zstandard>=0.25.0`
3. `import zst` → SUCCESS
4. `zst.probe(filepath)` → returns probe dict
5. `zst.decompress_zst(data)` → returns bytes

ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED remains correct classification.

## Package Manifest Entry

```yaml
- format: zst
  version: 0.1.0.dev0
  artifact_policy: external_ref
  requires: zstandard>=0.25.0
  gates_passed: 1-10
  commercial_product_ready: false
```

## ZST_DEPENDENCY_REPLAY: CONFIRMED_CONSISTENT_WITH_R82

