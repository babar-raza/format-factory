---
visibility: generated
generated_by: codex
---

# Minimum Supervisor Memory Repair

The R90 repair scope replaces legacy `run-on-latest --bundle` operational guidance with:

```text
python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>
```

Historical memory entries remain append-only. Any stale legacy line is marked historical and
superseded rather than deleted.
