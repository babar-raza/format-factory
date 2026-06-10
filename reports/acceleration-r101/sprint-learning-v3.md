# Train G: Sprint Learning v3

## Changes
- All 7 report generators validated with positive and negative tests
- Reports validated: agent-learning-notes, speed-bottlenecks, next-agent-briefing, manual-process-to-skill-candidates, parallelization-suggestions, repeated-command-inventory, shallow-evidence-warnings

## Tests Added (6 new)
- `test_learning_notes_has_sections` — validates 4 sections + grade summary
- `test_speed_bottlenecks_has_sections` — validates blocked/failed section
- `test_next_agent_briefing_has_sections` — validates 3 sections
- `test_skill_candidates_with_manual` — validates manual pattern detection
- `test_generate_all_files_exist` — all 7 files exist with content
- `test_generate_all_negative_missing_inputs` — graceful fallback on missing inputs
