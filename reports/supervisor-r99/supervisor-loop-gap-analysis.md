# Supervisor Loop Gap Analysis

## Current Loop Flow
```
Worker writes evidence-declaration.yaml
  -> autonomous_cycle.py --declaration <path>
    Step 1: validate_declaration()
    Step 2: inspect_declaration()
    Step 2b: evidence manifest generate/validate
    Step 3: grade_all()
    Step 4: generate_prompt()
    Step 5: write cycle manifest
    Step 6: copy summaries to reports/supervisor/
    Step 7: bridge_to_legacy_format() [writes JSON only]
    Step 8: write continuation signal
```

## Missing Steps (identified in Train A audit)
1. **Materialize** — between Step 2b and Step 3, should call materialize() to capture diffs, SHAs, source snapshots
2. **Regenerate legacy markdown** — Step 7 writes JSON but does not regenerate session-resume.md, approval-gates.md, next-sprint.md
3. **Rebuild context pack** — not called at all; should run after Step 3 to capture fresh state
4. **Rebuild review package** — not called; should be optional step after Step 6

## Desired Loop Flow
```
Worker writes evidence-declaration.yaml
  -> autonomous_cycle.py --declaration <path>
    Step 1: validate_declaration()
    Step 2: inspect_declaration()
    Step 2b: evidence manifest generate/validate
    Step 2c: materialize_declared_evidence() [NEW]
    Step 3: grade_all()
    Step 4: generate_prompt()
    Step 5: write cycle manifest
    Step 6: copy summaries to reports/supervisor/
    Step 7: bridge_to_legacy_format() + regenerate markdown [FIXED]
    Step 7b: build_context_pack() [NEW]
    Step 8: write continuation signal
```
