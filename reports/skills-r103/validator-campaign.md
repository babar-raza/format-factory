# Validator Campaign (Skills R103 Wave 2)

## Validators Run

| # | Validator | Tool | Result | Pos Tests | Neg Tests |
|---|-----------|------|--------|-----------|-----------|
| 1 | Command file validator | validate_claude_commands.py | 18/18 PASS | 12 | (in test suite) |
| 2 | Skill registry validator | validate_claude_commands.py (cross-ref) | 20 skills, 5 orphan warnings | (via cmd validator) | (via cmd validator) |
| 3 | Transcript validator | validate_skill_transcript.py | 13/15 PASS (2 anti-bypass FAIL) | 7 | 8 |
| 4 | Product-code ledger | validate_product_code_ledger.py | FAIL (uncommitted .NET src) | N/A (mainstream) | N/A (mainstream) |
| 5 | Context-pack skill mapping | context-pack-skill-snapshot.yaml | 20 skills snapshot | N/A | N/A |

## Test Counts

- Command validator tests: 12 (all PASS)
- Transcript validator tests: 17 (7 positive, 8 negative, 2 directory) (all PASS)
- **Total: 29 tests, 29 PASS, 0 FAIL**

## Validator Results (packaged)

- `validator-results/command-validation.json` — 18/18 commands pass
- `validator-results/transcript-validation-r103.json` — 13/15 PASS, 2 FAIL (expected)
- `validator-results/transcript-validation-r102-transcripts.json` — R102 transcript revalidation
- `validator-results/ledger-validation.json` — FAIL (mainstream .NET concern)
- `validator-results/anti-bypass-demos.json` — 9/9 PASS

## Raw Logs (packaged)

- `raw-logs/test-validators.log` — 29 passed pytest output

## Notes

- Ledger validator failure is a mainstream concern (uncommitted .NET src changes). Skills stream does not own .NET source commits.
- Context-pack skill mapping is a snapshot comparison, not a validator with pos/neg tests. Full validator planned for R104.
