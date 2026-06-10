# Sprint Preflight
# Sprint: FORMAT-FACTORY-AUTONOMOUS-HOST-LOOP-FALSE-POSITIVE-REPAIR-001
# Date: 2026-06-06

## Sprint Goal

Correct the false-positive HOST_LOOP_SMOKE_PROVEN proof from package 107.
Implement strict autonomy validation and prove a real iteration or classify the honest blocker.

## Governance

- AGENTS.md: read — no commits, no push, no Gate approval
- Hard rules: no product work, no format additions, no product sprint activation
- Scope: tools/supervisor/external_host_loop.py, tests/supervisor/test_external_host_loop.py,
         reports/autonomous-host-loop-repair/**, next-action contracts

## Prior Sprint Context

- Package 107: FORMAT-FACTORY-AUTONOMOUS-EXTERNAL-HOST-BOOTSTRAP-001
- Claimed: HOST_LOOP_SMOKE_PROVEN / H5 autonomy
- Finding: FALSE_POSITIVE_HOST_PROOF — 5 bugs, child wrote nothing, parent synthesized proof
- Correction: Must reclassify as INVALID_FALSE_POSITIVE_PRIOR_PROOF

## What is Allowed This Sprint

- Modify external_host_loop.py
- Modify test_external_host_loop.py
- Create reports/autonomous-host-loop-repair/** files
- Create schema v2 next-action.json
- Create strict smoke prompt
- Run host loop live invocations
- Build evidence bundle

## Hard Stops

- No git commit, push, or merge
- No Gate 8 or Gate 11 approval
- No NuGet/PyPI publication
- No MCP activation
- No product sprint work
- No false H5 claim (parent must not create proof file)
