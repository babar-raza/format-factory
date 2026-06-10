# Sample Mainstream Next Prompt

## Sprint Identity
- Sprint ID: FORMAT-FACTORY-MAINSTREAM-R113-PRODUCT-DEPTH-CONTINUATION-001
- Prior sprint: mainstream-r112
- Stream: mainstream

## Preflight
Read: CLAUDE.md, AGENTS.md, plans/master-plan.md, product-capability-matrix/poc-targets.yaml, reports/mainstream-r112/selected-mainstream-gaps-r112.json

## Sprint Goal
Continue product depth: save/export workflows, object model enrichment, FOSS hardening, dogfood proofs.

## Governed Product Rules
- Load `reports/mainstream-r112/selected-mainstream-gaps-r112.json` (stream-local authority)
- No direct ad-hoc src/ edits — use governed skills
- Every src/ change must be in product-code ledger
- Run ledger validator after product changes

## Evidence Rules
- Write `.local/evidences/<run_id>/evidence-declaration.yaml`
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>`
- Include tests_supporting field for all product items
- Package raw logs, source diffs, skill transcripts

## Trains
| Train | Title |
|-------|-------|
| A | Governance Preflight |
| B-D | Commercial .NET depth (FODS/FODT/Netpbm) |
| E-G | FOSS depth (ZST/Netpbm-Python/SYLK) |
| H-I | Dogfood/export proofs |
| J | Evidence closeout |

## Hard Prohibitions
- No git push/commit without authorization
- No Gate 8/11 approval
- No commercial_product_ready=true
- No supervisor/acceleration tool edits

## Note
This is a SAMPLE prompt showing the corrected structure. Stream-local gap selection replaces `.local/supervisor/selected-product-gaps.json`. Governance command invocations (autonomous-cycle, ledger validator) are allowed.
