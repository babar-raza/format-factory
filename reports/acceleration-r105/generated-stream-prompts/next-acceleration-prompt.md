# Next Acceleration Prompt — Generated R105

## Stream: acceleration
## Sprint: FORMAT-FACTORY-ACCELERATION-R105-PACKAGE-IDENTITY-SELF-CONTAINMENT-AND-ACCELERATION-ADVANCEMENT-001

## Focus
ADVANCE: Acceleration tooling — package identity validator, anti-skip checker, gap selector, prompt quality validator

## Repair Lane
- Fix package identity contamination (global state labeled as stream-primary)
- Fix stale gap inclusion in review packages
- Add dirty-state classification to evidence declarations

## Advancement Lane
- Add package identity validator (validate_package_identity.py)
- Improve anti-skip checker to 11 detectors (dirty git state, wrong-stream gaps)
- Add prompt quality validator (validate_prompt_quality.py)
- Generate fresh per-stream gaps with stream provenance

## Evidence Closeout
- Write evidence-declaration.yaml at .local/evidences/acceleration-r105/
- Run autonomous-cycle: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>
- Build declaration review package and report ZIP path + SHA-256

## File Boundaries
- Allowed: tools/supervisor/, tests/supervisor/, .supervisor/, reports/acceleration-r105/
- Forbidden: src/net/, src/python/ (product code — acceleration stream only)
