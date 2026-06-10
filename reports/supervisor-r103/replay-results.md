# Replay Results

## Packages Replayed

### Mainstream R105
- Stream detection: mainstream (PASS)
- Declaration-review package: YES
- No legacy markers: PASS
- Grades: valid enums (PASS)
- Classification: product progress real, under-packaged (no sprint-specific reports pre-R103)

### Acceleration R103
- Stream detection: acceleration (PASS)
- Declaration-review package: YES
- No legacy markers: PASS
- Grades: valid enums (PASS)
- Classification: tool progress real, generated artifacts incomplete

### Supervisor R102
- Stream detection: supervisor (PASS)
- Declaration-review package: YES
- No legacy markers: PASS
- Grades: valid enums (PASS)
- Classification: control-plane progress real, cross-stream contaminated (tests_supporting empty, reports not in ZIP)

### Skills R101
- Stream detection: skills (PASS)
- Declaration-review package: YES
- No legacy markers: PASS
- Grades: valid enums (PASS)
- Classification: governed execution progress real

## Grading Engine Accuracy
6 synthetic tests prove the grading engine produces mixed grades:
- OVERCLAIMED for missing evidence
- REWORK_REQUIRED for missing paths and failed tests
- ACCEPTED_WITH_LIMITATIONS for stub tests
- NOT_ATTEMPTED for not-started items
- Mixed input produces mixed output (not rubber-stamp)

## Conclusion
Replay confirms real progress across all streams with specific deficiencies identified.
Not all-accepted: grading engine correctly rejects/downgrades synthetic edge cases.
