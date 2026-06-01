# Train B — CLAUDE.md Closeout Instruction Repair

Status: VERIFIED_ALREADY_PRESENT

## Verification

CLAUDE.md lines 20-43 contain the Sprint Closeout section with all required elements:

1. Write evidence-declaration.yaml - PRESENT (line 24-26)
2. Run autonomous-cycle --declaration - PRESENT (line 31-33)
3. Exit code 0 = accepted - PRESENT (line 38)
4. Exit code 3 = rework needed - PRESENT (line 39)
5. Do NOT use legacy run-on-latest --bundle - PRESENT (line 43)
6. Section location: between "After Reading session-resume.md" (line 14) and "Governance" (line 45) - CORRECT

## Grep Proof

```
grep -n "Sprint Closeout" CLAUDE.md
20:## Sprint Closeout (MANDATORY -- do this at the end of every sprint)

grep -n "autonomous-cycle" CLAUDE.md
32:   python tools/supervisor/supervisor_loop.py autonomous-cycle \

grep -n "run-on-latest" CLAUDE.md
43:Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.
```

No rewrite needed. Change is uncommitted from prior session.
