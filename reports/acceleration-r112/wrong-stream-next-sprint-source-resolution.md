# Wrong-Stream Next-Sprint Source Resolution — R112

## Problem
R111 anti-skip reported detected_stream=skills for the global next-sprint.md, but the R111 package was acceleration.

## Source Analysis
- Path read: reports/supervisor/next-sprint.md (workspace global)
- Source kind: workspace (live file, not packaged)
- The global file is last-writer-wins — after R111, skills-r111, supervisor-r109, and skills-r112 all ran and overwrote it
- At the time of R111's anti-skip check, the file was from whatever stream ran last

## Fix
detect_wrong_stream_next_sprint now records:
- path_read: exact file path read
- source_kind: workspace | package | generated | global_state
- is_blocking: true only for INVALID_WRONG_STREAM (current-authority misclassification)
- authority: classification from stream-output authority model

## Behavior
- Global file from different stream: ARCHIVED_LAST_WRITER_SNAPSHOT, is_blocking=false
- Same-stream file: CURRENT_STREAM_AUTHORITY, is_blocking=false
- Non-global wrong-stream authority: INVALID_WRONG_STREAM, is_blocking=true

## Tests
- TestWrongStreamSourceResolution: 6 tests covering all paths
