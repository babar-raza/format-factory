# R83 Train T — Reproducibility and Closeout Automation

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## Reproducibility Tool Status

Tool: `tools/repro/reproduce_format.py`

Repairs from R82:
- Canonical import namespace comments fixed: no longer reference `NOT aspose_format_factory_*`
- Uses `import fods`, `import fodt`, `import zst` correctly in smoke scripts

## Closeout Automation Checklist

| Step | Automated | Tool |
|------|-----------|------|
| Build inner evidence ZIP | YES | build_evidence_bundle.py |
| Generate sidecar | YES | --verify flag |
| Build delivery package | YES | build_delivery_package.py |
| Build supervisor review package | YES | build_supervisor_review_package.py |
| SHA capture | YES | subprocess + hashlib |
| final-verdict update | MANUAL | Edit file then git commit |
| State snapshot | SEMI | state_snapshot.py (manual trigger) |
| master-plan update | MANUAL | Edit file then git commit |

## R83 Closeout Protocol

1. All trains complete
2. Run pytest to confirm authoritative test result
3. Run state_snapshot.py (Train U)
4. Update master-plan.md (Train U)
5. Update all metadata files (no PENDING)
6. git commit -m "feat(r83): all trains complete"
7. Build Pass 1 ZIP → capture SHA
8. Update final-verdict.md Pass 1 SHA → commit
9. Build Pass 2 ZIP + sidecar → capture SHAs
10. Update final-verdict.md Pass 2 + sidecar SHAs → commit
11. Build delivery package → capture SHAs
12. Build supervisor review package → capture SHA
13. Update external metadata (not PENDING)
14. Final commit
15. Print: UPLOAD PRIMARY ARTIFACT: r83-supervisor-review-package.zip

## REPRODUCIBILITY_CLOSEOUT: PROTOCOL_DOCUMENTED

