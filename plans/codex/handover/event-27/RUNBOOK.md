---
artifact_id: FF6-EVENT-27-RUNBOOK
artifact_type: immutable_checkpoint_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Event 27 Resume Runbook

1. Fetch GitLab `origin/main`.
2. Verify commit `59ef8ee2e1b4e37168e4c7094687fac0a6098a79`
   is an ancestor of `origin/main`.
3. Validate the complete FF6 journal and confirm Event 27 occurs exactly once
   with hash
   `9a1783b0705468fec1e9f9fda96f61ab4b1da32a161d128a3120a8bf689686c2`.
4. Confirm the controller still selects XLIFF
   `XLF-04-BATCH-005`; if a later event exists, follow the later event.
5. Query coordination and classify all dirty paths before claiming work.
6. If the XLIFF Batch 005 scope is live-owned, preserve it and select UBL-03
   as the safe disjoint fallback. Do not repeat UBL-01, UBL-02, or Event 27.
7. If XLIFF is safely ownable, resume Batch 005 from immutable Event 26 inputs
   plus Event 27 controller state. Preserve all 25 source-bound obligation
   rows; the 80 missing expected IDs, 78 coarse dispositions, non-modal prose,
   and tamper-binding defects remain open until proven closed.
8. For UBL-03, compile every declaration reachable from all 91 roots. Retain
   exact references, namespaces, inheritance, sequence/choice/order,
   cardinality, facets, wildcards, substitution groups, and stable anonymous
   identities. Reject unresolved, duplicate, ambiguous, remote, drifting, or
   nondeterministic graph inputs.
9. A bounded implementation commit precedes the next plan-control event.
   Append no event until independent evidence passes.
10. Preserve `0/6` certification and all `UNASSESSED` promotions until the
    full production proof graph computes otherwise.

Mandatory checks before mutation:

```powershell
git fetch origin main
git status --short --branch
git merge-base --is-ancestor 59ef8ee2e1b4e37168e4c7094687fac0a6098a79 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
.venv\Scripts\python.exe tools\evidence\check_current_state_consistency.py
```

The current root packet contains the full coordination, skill, state-machine,
checkpoint, validation, and cross-provider handback rules.
