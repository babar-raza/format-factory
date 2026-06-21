# /build-evidence-bundle

Build and validate an evidence bundle for the current phase/sprint.

## Usage

```
/build-evidence-bundle <run_id>
```

Example: `/build-evidence-bundle fods-gate11-prep-20260618`

## What This Command Does

1. **Locate evidence declaration** — Find `.local/evidences/<run_id>/evidence-declaration.yaml`
2. **Validate declaration** — Run `sprint_executor_validate.py --repair`
3. **Run governance validators** — Execute `autonomous_cycle.py` for full validation
4. **Build ZIP bundle** — Run `build_declaration_review_package.py`
5. **Report outcome** — Print bundle path and SHA-256

## Required Inputs

- `run_id` — Evidence run ID matching `.local/evidences/<run_id>/` directory

## Steps

```
1. Confirm .local/evidences/<run_id>/evidence-declaration.yaml exists
2. Run declaration validator:
   python tools/supervisor/sprint_executor_validate.py \
     .local/evidences/<run_id>/evidence-declaration.yaml --repair
3. If FAIL: fix errors, stop, report
4. Run supervisor cycle:
   python tools/supervisor/autonomous_cycle.py \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
5. Check exit code: 0=OK, 3=rework, 1/9=error
6. Build review package:
   python tools/supervisor/build_declaration_review_package.py \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
7. Print absolute bundle path and SHA-256
8. Run check_continuation.py to confirm continue verdict
```

## Output Format

```
Evidence bundle complete:
  Path: C:\Users\prora\...\<run_id>\declaration-review-package.zip
  SHA-256: <hash>
  Size: <bytes>
  Artifacts: <count>
  Continuation: CONTINUE / STOP (reason)
```

## Allowed Paths

- `.local/evidences/<run_id>/` (declaration source)
- `.local/supervisor/reviews/<run_id>/` (build output)

## Validation

Complete when:
- Bundle ZIP exists at listed path
- SHA-256 printed
- `check_continuation.py` verdict reported
