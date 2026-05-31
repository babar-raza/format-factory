# R84 Supervisor Loop Trigger Proof

**Sprint:** FORMAT-FACTORY-R84
**Date:** 2026-05-31

## Trigger Command

```
python tools/supervisor/discover_latest_evidence.py
```

Expected output: path to `r84-supervisor-review-package.zip`

## Validation

The supervisor loop validates:
1. Evidence bundle against R84 contract
2. Sidecar SHA matches inner ZIP SHA
3. All required metadata files present
4. No PENDING markers in final-verdict

## Status

SUPERVISOR_LOOP_TRIGGER: READY
Will execute after final commit and print UPLOAD PRIMARY ARTIFACT path.
