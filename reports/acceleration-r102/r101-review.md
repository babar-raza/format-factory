# R101 Review

## What R101 Did Well
- Stale sprint detection added to gap selector
- UNSAFE_SCOPE and source_track classification in router
- Handoff generator enriched with implementation steps and stop conditions
- Lane recorder got stream_id and raw_log_path
- Progress detector classifies 5 progress types
- All 154 tests pass

## What R101 Did NOT Solve (adoption failures)
1. **Generic next prompts**: supervisor still generates one-size-fits-all next-sprint.md
2. **No next-best-action logic**: tools exist but nothing decides WHICH tool to run next
3. **No 3-sprint forecast**: each sprint is planned in isolation
4. **No anti-skip enforcement**: stale gaps can be ignored, raw logs can be missing
5. **Stream prompts not generated**: no per-stream execution guidance
6. **Tools improved but not used**: R101 improved 8 tools but no pipeline consumes them automatically

## R102 Must Fix
- Build next-best-action selector
- Build 3-sprint stream forecaster
- Build anti-skip detectors (4 types)
- Generate 4 stream-specific prompts
- Generate 4 stream-specific handoffs
- Prove end-to-end adoption in 4 dry runs
