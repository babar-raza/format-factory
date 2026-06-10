# R98 Agent Learning Notes

## What was fast (R93-R97)
- .NET API addition: well-defined pattern (add method + 8 tests) completes quickly
- Python test-only sprints: no src changes needed, just test files
- Supervisor autonomous-cycle: runs in seconds

## What was shallow
- Query-only APIs (GetCellCount, GetParagraphCount) add tests but not product depth
- Summary-only test evidence hides test quality from grader

## What should become a skill
- Lane execution recording (manual today, should be automated)
- Raw test log capture (redirect test output to file, include in evidence)
- Source diff capture (git diff > file, include in materializer)

## What evidence was missing
- Raw test output logs
- Skill invocation transcripts
- Source diffs per sprint
- Ledger deltas per sprint

## What should next agent do first
1. Prioritize same-format save and export APIs over shallow queries
2. Capture raw test logs for every test run
3. Use governed skill invocation with transcript
4. Update lane execution ledger for every train

## What should next agent avoid
- Adding more GetX() query APIs — focus on edit/save/export
- Skipping test evidence file paths in tests_supporting
- Leaving skill registry stale
