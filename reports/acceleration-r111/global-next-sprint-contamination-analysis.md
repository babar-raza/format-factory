# Global Next-Sprint Contamination Analysis — R111

## Problem
`reports/supervisor/next-sprint.md` says `# Stream: mainstream` even when generated from an Acceleration sprint.

## Root Cause Chain
1. `autonomous_cycle.py` Step 7b calls `generate_packet(repo_root, stream=detected_stream)` — CORRECT
2. `supervisor_loop.py` `cmd_autonomous_cycle()` then calls `cmd_next(args)` — second pass
3. `cmd_next()` invokes `generate_supervisor_packet.py` via subprocess
4. `main()` in generate_supervisor_packet.py calls `synthesize_sprint_tasks(review, contradictions, repo_root)` WITHOUT stream
5. `synthesize_sprint_tasks` defaults to `stream="mainstream"`
6. The mainstream result overwrites the correct stream-specific result from Step 7b

## Fix Applied
Added stream detection to `main()` in `generate_supervisor_packet.py`:
```python
sprint_id = review.get("sprint_id", "unknown")
stream = detect_stream_from_sprint_id(sprint_id)
tasks = synthesize_sprint_tasks(review, contradictions, repo_root, stream=stream)
next_sprint_text = generate_next_sprint_md(review, contradictions, memory_snippet, tasks, stream=stream)
```

## Verification
- `detect_stream_from_sprint_id("FORMAT-FACTORY-ACCELERATION-R110-...")` returns "acceleration"
- 5 stream detection tests in test_r111_stream_output_authority.py all pass
