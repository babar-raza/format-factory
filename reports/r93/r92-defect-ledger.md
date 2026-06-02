---
sprint: R93
generated_by: r93-worker
train: A
---

# R92 Defect Ledger (R93 Train A)

Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

## Defects

### D92-01 — evidence-review.json overwritten by legacy bundle-validator [HIGH]

**Category:** Supervisor pipeline
**Affected file:** reports/supervisor/evidence-review.json
**Root cause:** After `autonomous_cycle.py` ran correctly for R92 and bridge_to_legacy_format wrote the correct `evidence-review.json`, a secondary invocation of `validate_evidence_for_supervisor.py` was run (likely by a legacy pipeline path) with the declaration-review-package.zip as input. This overwrote the correctly-bridged evidence-review.json with bundle-validation failure output (sprint_id: "unknown", BUNDLE_VALIDATION: FAIL).
**Evidence:** reports/supervisor/evidence-review.json shows validator_output with BUNDLE_VALIDATION: FAIL; bundle_path points to declaration-review-package.zip
**Resolution (R93):** Train F — add declaration-mode check to `supervisor_loop.py autonomous-cycle` to NOT call legacy review/validate path after declaration-based cycle

### D92-02 — next-sprint.md has sprint_id: "unknown" and tests: 0/0 [HIGH]

**Category:** Supervisor packet generator
**Affected file:** reports/supervisor/next-sprint.md, reports/supervisor/session-resume.md
**Root cause:** Consequence of D92-01 — generate_supervisor_packet.py reads the corrupted evidence-review.json and produces next-sprint.md with "Source sprint: unknown" and "tests: 0 passed, 0 failed"
**Resolution (R93):** Train C — fix generate_supervisor_packet.py to read from declaration directly when declaration path is available; fallback to evidence-review.json only when no declaration is present

### D92-03 — Work-item grading only checks path existence [MEDIUM]

**Category:** grade_declared_work.py
**Affected file:** tools/supervisor/grade_declared_work.py
**Root cause:** Current grading logic assigns ACCEPTED if all evidence_paths exist on disk. It does not check: file content, test passage for test evidence paths, SHA consistency, or acceptance criteria fulfillment
**Resolution (R93):** Train D — enhance grading to check test file content, verify SHA-256 from materializer manifest, check for acceptance criteria patterns

### D92-04 — No context-pack in review package [MEDIUM]

**Category:** Infrastructure gap
**Affected files:** .supervisor/context-pack.yaml (missing), tools/supervisor/build_context_pack.py (missing)
**Root cause:** Context pack was never implemented. Every generated sprint prompt needs a machine-readable snapshot of the current project state (test counts, POC matrix, recent sprint outcomes, current mode)
**Resolution (R93):** Train B — create build_context_pack.py and .supervisor/context-pack.yaml

### D92-05 — MCP status unverified [LOW]

**Category:** Supervisor packet
**Affected file:** reports/supervisor/approval-gates.md
**Root cause:** MCP_STATUS is classified based on .vscode/mcp.json file presence alone, without checking if MCP server is actually responding or configured correctly
**Resolution (R93):** Train E — create check_mcp_status.py to classify MCP accurately

### D92-06 — product-code-change-ledger.json sprint field says "R90" [LOW]

**Category:** Ledger metadata
**Affected file:** reports/r90/product-code-change-ledger.json
**Root cause:** The ledger was created in R90 and lives at reports/r90/. It correctly stores all governed changes but its own metadata says sprint: R90 even though it's been updated through R92
**Resolution (R93):** Not a defect to fix — ledger lives at a fixed path (r90/), the sprint metadata is the creation sprint. The path is correct per the governance model. Document as WONTFIX in R93 context.

### D92-07 — git_status_final says uncommitted but work was committed [LOW]

**Category:** Declaration accuracy
**Affected file:** .local/evidences/r92/evidence-declaration.yaml
**Root cause:** The R92 declaration was written before the commit was made (correct — commit requires user authorization). After commit at e283822, the declaration still shows "uncommitted". This is by design (declarations are written pre-commit), but creates a perception gap.
**Resolution (R93):** Document as EXPECTED_BEHAVIOR. Include post-commit SHA in declaration.

### D92-08 — Acceleration layer not enforced automatically [MEDIUM]

**Category:** Governance
**Affected file:** tools/supervisor/validate_product_code_ledger.py
**Root cause:** The validator only checks the ledger file for structure. It does not scan git diff for src/* changes that lack ledger entries. An ungoverned src change could be made without detection until the human reviewer notices.
**Resolution (R93):** Train I — update validate_product_code_ledger.py to scan staged/unstaged src changes and cross-reference with ledger entries

## Summary

| Severity | Count | Resolved in R93 |
|----------|-------|----------------|
| HIGH | 2 | 2 (Trains C, F) |
| MEDIUM | 3 | 3 (Trains B, D, I) |
| LOW | 3 | 1 (Train E), 2 WONTFIX/EXPECTED |
| **Total** | **8** | **6** |

## Status: DEFECT LEDGER COMPLETE
