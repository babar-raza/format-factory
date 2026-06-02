---
visibility: generated
generated_by: codex
---

# Skill-or-Handoff Decision Tree

Implemented by `tools/supervisor/choose_skill_or_handoff.py`.

1. Use a registered governed skill when scope fits.
2. Generate an execution handoff when no safe skill fits.
3. Stop for external authority when required.
4. Preserve prior functional source and ledger-backfill it when it predates governance.
