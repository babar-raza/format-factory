# Product-First Acquisition Train — Sprint Preflight

Sprint ID: FORMAT-FACTORY-PRODUCT-FIRST-AUTONOMOUS-ACQUISITION-TRAIN-001
Run ID: product-first-acquisition-train
Date: 2026-06-06

## Package 118 Baseline (Autonomy Guard)
- SHA-256: 3358550e093a5793f3d2e84e7aa16e7279738c8c64a7871ca5714b7b524ecab2
- Proof: non-dry-run LOCAL_DETERMINISTIC H3 execution (action post-closeout-sprint11-d60f8ca9)
- advisory_prompt_executable=false confirmed
- This is the autonomy guard proof — not product progress

## Mode
PRODUCT-FIRST: real source changes, tests, usable outputs.

## Dirty State Classification
Pre-existing dirty state: supervisor reports, .supervisor/ state, src/net/ (prior sprint
source changes not committed). No active product mutation on those files this sprint.

## Anti-Skip Caveats (Non-Blocking, Classified Here)
- missing_lane_ledger: recorded in touched-files-ledger.jsonl below
- missing_sample_outputs: will be produced in Lane 4
- dirty_git_state: classified above (pre-existing, not from this sprint)

## Freeze
- SYLK: tests import write_sylk from installed package — write_sylk missing. Pre-existing
  breakage. Do not repair this sprint (out of scope).
- ZST: unrelated to selected tasks.
- Gate 11 / commit / push: external gates, not this sprint.

## Selected Product Scope
1. ABW Python: add export_to_html() function
2. ABW Python: add get_metadata() function
3. Gnumeric Python: add export_to_json() function

Allowed paths:
- src/python/abw/abw_codec.py
- src/python/gnumeric/gnumeric_codec.py
- tests/python/abw/ (new test file)
- tests/python/gnumeric/ (new test file)
- examples/python/abw/ (example)
- examples/python/gnumeric/ (example)
- reports/product-first-acquisition-train/

Forbidden paths:
- src/net/ (no .NET changes)
- src/python/sylk/ (pre-existing breakage, out of scope)
- poc-targets.yaml (propose delta only, no direct mutation)
- registry/ (propose delta only)
- AGENTS.md, GOVERNANCE.md
