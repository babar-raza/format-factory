# Next Supervisor Prompt — Generated R105

## Stream: supervisor
## Sprint: next supervisor sprint (R104+)

## Focus
ADVANCE: Supervisor infrastructure — grading, continuation, stream prompts, evidence model

## Tasks
- Integrate package identity validator into autonomous-cycle pipeline
- Add stream-aware grading that checks for cross-stream contamination
- Improve evidence-review to detect wrong-stream supervisor state
- Update continuation signal to track stream identity

## Evidence Closeout
- Write evidence-declaration.yaml
- Run autonomous-cycle
- Build declaration review package

## File Boundaries
- Allowed: tools/supervisor/, .supervisor/, reports/supervisor/
- Forbidden: src/net/, src/python/ (product code — supervisor stream only)
