---
visibility: generated
generated_by: codex
---

# R90 Generated Next Sprint Acceleration Layer

The supervisor generators now require the governed product acceleration inputs:

- `.local/supervisor/selected-product-gaps.json`
- `.supervisor/skill-registry.yaml`
- `reports/r90/product-code-change-ledger.json`

Generated next-sprint prompts prohibit direct ad-hoc `src/` edits. Product-code changes must use a
governed skill or generated execution handoff and must be recorded in the ledger. Generated work
also retains dogfood export, package/install proof, evidence declaration, and `autonomous-cycle`
lanes.

## Verification

- `python -m py_compile tools/supervisor/generate_next_worker_prompt.py tools/supervisor/generate_supervisor_packet.py`: PASS
- `.local/venv/Scripts/python.exe -m pytest tests/supervisor/test_r90_generated_next_sprint.py tests/supervisor/test_evidence_declaration.py tests/supervisor/test_r86_supervisor_truth_repair.py tests/supervisor/test_r87_supervisor_truth.py -q`: 52 passed
- `.local/venv/Scripts/python.exe -m pytest tests/taskmaster/ -q`: 27 passed
- `.local/venv/Scripts/python.exe tools/supervisor/validate_product_code_ledger.py --ledger reports/r90/product-code-change-ledger.json`: PASS
- Full `tests/supervisor/` run: 100 passed, 1 failed in adjacent
  `test_r90_product_acceleration.py`; its all-backfill assertion conflicts with a newly added
  `GOVERNED_PRODUCT_CHANGE` ledger entry.
