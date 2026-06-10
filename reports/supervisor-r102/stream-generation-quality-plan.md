# Stream-Aware Generation Quality Plan

## Objective
Non-mainstream prompts must not contain generic product language.

## Quality Checks (all enforced by tests)
1. Section header: mainstream="New Product Work", supervisor="Supervisor Infrastructure Work",
   acceleration="Acceleration Tooling Work", skills="Governed Skill Work"
2. Lane manifests: mainstream mentions "Dogfood"; non-mainstream do NOT mention "Dogfood export"
3. Rules: mainstream references product-code-change-ledger; non-mainstream enforce "stream boundary"
4. Stream label: every prompt contains `# Stream: {stream}`
5. No generic focus: non-mainstream never contains "Continue normal mega-train lanes"

## Test Coverage
- tests/supervisor/test_r102_stream_prompt_quality.py: 11 tests
- tests/supervisor/test_r101_stream_aware_packet.py: 31 tests (from R101)
