# Next Acceleration Sprint Prompt (R113 Preview)

## Suggested Focus Areas

### 1. Severity Escalation
Repeated medium violations across sprints should auto-promote to high.
Track violation history and escalate when a check fails 3+ consecutive sprints.

### 2. Stale Context-Pack Reference Detector
Detect when context-pack.yaml references stale sprint IDs or missing files.
Add as 19th anti-skip detector.

### 3. Stream-Specific Evidence-Review Routing
Per-stream evidence-review files to avoid global last-writer-wins contamination.
Similar to the next-sprint.md fix but for evidence-review.json.

### 4. Anti-Skip Regression Test Harness
Systematic regression tests that replay prior sprint packages against
the current anti-skip checker to verify no false positives/negatives introduced.
