"""autonomous_cycle_extensions — optional session-start hooks for autonomous_cycle.py.

These hooks extend autonomous_cycle.py without modifying it (LOC cap workaround).
To activate a hook, add a 2-line try/import block at the desired step in autonomous_cycle.py:

    try:
        from autonomous_cycle_extensions.knowledge_freshness_hook import run_hook
        run_hook()
    except Exception:
        pass  # Non-blocking — never fail the sprint

TC-P3-002 note: wiring into autonomous_cycle.py requires LOC reclaim sprint first
(current cap: 2465/2465, zero headroom). See TC-P3-002-SUB-001.
"""
