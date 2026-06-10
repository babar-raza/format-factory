# Preflight — Acceleration R112

## Sprint Identity
- Sprint ID: FORMAT-FACTORY-ACCELERATION-R112-ANTISKIP-CONSISTENCY-SAMPLE-OUTPUT-DETECTION-AND-CONTINUATION-SEMANTICS-CAMPAIGN-001
- Stream: acceleration
- Prior sprint: FORMAT-FACTORY-ACCELERATION-R111-STREAM-OUTPUT-AUTHORITY-GLOBAL-NEXT-SPRINT-CLEANUP-AND-EVIDENCE-QUALITY-CAMPAIGN-001

## Preflight Checks
- [x] R111 evidence-declaration.yaml read
- [x] R111 evidence-manifest.yaml read
- [x] R111 supervisor-review.json read
- [x] R111 anti-skip-check-result.json read
- [x] R111 continuation-signal.json (stream-local) read
- [x] Global next-sprint.md read (stream: mainstream)
- [x] anti_skip_checker.py read
- [x] autonomous_cycle.py read
- [x] grade_declared_work.py read

## Identified Contradictions
1. Anti-skip all_pass=false but final IV/quota say all pass
2. missing_sample_outputs despite 5 sample_output artifacts in manifest
3. wrong_stream_next_sprint detected_stream=skills but package was acceleration
4. Continuation state=YES despite active low/medium violations
