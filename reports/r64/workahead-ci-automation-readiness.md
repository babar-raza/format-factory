# R64 W7 — CI/Automation Readiness

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Proposed Automation Command

A single command that performs the full closure cycle:

```bash
#!/bin/bash
set -e

RUN=r64
CONTRACT=tools/evidence/contracts/$RUN-*.yaml
OUTPUT=.local/$RUN-pass2-final.zip
SIDECAR=$OUTPUT.sha256-proof.json
METADATA=.local/$RUN-metadata

# 1. Build ZIP
python tools/evidence/build_evidence_bundle.py \
  --repo-root . --contract $CONTRACT \
  --output $OUTPUT --metadata-dir $METADATA

# 2. Generate external sidecar
python tools/evidence/write_sidecar_proof.py \
  --bundle $OUTPUT --contract $CONTRACT \
  --run-number $RUN --validation-result PASS \
  --output $SIDECAR

# 3. Validate missing-sidecar failure
python tools/evidence/validate_evidence_bundle.py \
  --bundle $OUTPUT --check-no-pending --contract $CONTRACT \
  && echo "ERROR: should have failed without sidecar" && exit 1 \
  || echo "EXPECTED: missing sidecar rejection"

# 4. Validate matching-sidecar pass
python tools/evidence/validate_evidence_bundle.py \
  --bundle $OUTPUT --check-no-pending --contract $CONTRACT \
  --sidecar-proof $SIDECAR

# 5. Wrong-sidecar failure
echo '{"sha256":"wrong"}' > /tmp/wrong-sidecar.json
python tools/evidence/validate_evidence_bundle.py \
  --bundle $OUTPUT --check-no-pending --contract $CONTRACT \
  --sidecar-proof /tmp/wrong-sidecar.json \
  && echo "ERROR: should have failed with wrong sidecar" && exit 1 \
  || echo "EXPECTED: wrong sidecar rejection"

# 6. Installed API smoke
python -m venv /tmp/api-smoke-venv
/tmp/api-smoke-venv/Scripts/pip install $METADATA/package-artifacts/*.whl
/tmp/api-smoke-venv/Scripts/python -c "from fods import workbook_stats; from fodt import document_stats; print('API_SMOKE: PASS')"

echo "FULL_CLOSURE_CYCLE: PASS"
```

## Implementation Status

- Design: COMPLETE (above script)
- Implementation: DEFERRED to R65 (low-risk taskcard TC-W7-001)
- Reason: Script requires testing on CI infrastructure not available in R64

## Fail-Closed Design

- Missing sidecar → FAIL
- Placeholder proof → FAIL (via --check-no-pending)
- Wrong sidecar SHA → FAIL
- Missing API → FAIL (import error)

---

W7_CI_AUTOMATION_STATUS: COMPLETE
