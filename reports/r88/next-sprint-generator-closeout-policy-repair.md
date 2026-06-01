# Train C — Next-Sprint Generator Closeout Policy Repair

Status: VERIFIED_ALREADY_PRESENT

## Verification

.supervisor/prompts/next-sprint-generator.md contains all required updates:

1. Lane 7 uses autonomous-cycle --declaration (line 92-93) - PRESENT
2. Requires evidence-declaration.yaml (line 89) - PRESENT
3. ZIP is optional/export-only (line 122) - PRESENT
4. Insufficient sprint markers include no-declaration and no-cycle (lines 104-106) - PRESENT
5. Legacy run-on-latest marked as replaced (line 95) - PRESENT

## Grep Proof

```
grep -n "autonomous-cycle" .supervisor/prompts/next-sprint-generator.md
92:     python tools/supervisor/supervisor_loop.py autonomous-cycle \
122:   - Mandatory evidence rules (must write evidence-declaration.yaml, run autonomous-cycle; ZIP optional for export only)

grep -n "run-on-latest" .supervisor/prompts/next-sprint-generator.md
95:   - This replaces the legacy `run-on-latest --bundle` command
```

No rewrite needed. Change is uncommitted from prior session.
