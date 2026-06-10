# Prompt Quality Failure Analysis

## Sprint: mainstream-r112

## Failure Summary
- Check: `no_wrong_stream`
- Result: FAIL
- Forbidden found: `['tools/supervisor/']`
- Source: `.local/supervisor/reviews/mainstream-r111/prompt-quality-result.json`

## Generated Prompt Analysis
Source: `.local/supervisor/reviews/mainstream-r111/combined-next-worker-prompt.md`

### All `tools/supervisor/` References

| # | Line | Reference | Full Context |
|---|------|-----------|-------------|
| 1 | 48 | `tools/supervisor/supervisor_loop.py` | `python tools/supervisor/supervisor_loop.py autonomous-cycle` |
| 2 | 63 | `tools/supervisor/validate_product_code_ledger.py` | `python tools/supervisor/validate_product_code_ledger.py --ledger ...` |
| 3 | 91 | `.local/supervisor/selected-product-gaps.json` | `Load .local/supervisor/selected-product-gaps.json before choosing product work` |
| 4 | 314 | `tools/supervisor/autonomous_cycle.py` | `py_compile tools/supervisor/autonomous_cycle.py` |
| 5 | 315 | `tools/supervisor/supervisor_loop.py` | `py_compile tools/supervisor/supervisor_loop.py` |
| 6 | 316 | `tools/supervisor/generate_supervisor_packet.py` | `py_compile tools/supervisor/generate_supervisor_packet.py` |
| 7 | 325 | `tools/supervisor/supervisor_loop.py` | `python tools/supervisor/supervisor_loop.py autonomous-cycle` |

### Classification

| # | Classification | Rationale |
|---|---------------|-----------|
| 1 | ALLOWED_GOVERNANCE_COMMAND | Mandatory evidence submission per CLAUDE.md |
| 2 | ALLOWED_GOVERNANCE_COMMAND | Mandatory ledger validation per governed skill |
| 3 | ALLOWED_GOVERNANCE_DATA | Gap selection data consumed by Mainstream |
| 4 | UNNECESSARY_REFERENCE | py_compile of supervisor tools not needed in Mainstream |
| 5 | UNNECESSARY_REFERENCE | py_compile of supervisor tools not needed in Mainstream |
| 6 | UNNECESSARY_REFERENCE | py_compile of supervisor tools not needed in Mainstream |
| 7 | ALLOWED_GOVERNANCE_COMMAND | Duplicate of #1 — mandatory evidence submission |

### Summary
- **4 ALLOWED_GOVERNANCE_COMMAND** (mandatory per CLAUDE.md/AGENTS.md)
- **1 ALLOWED_GOVERNANCE_DATA** (gap selection data, consumed not modified)
- **3 UNNECESSARY_REFERENCE** (py_compile checks that should be removed from Mainstream prompts)
- **0 WRONG_STREAM_IMPLEMENTATION** (no supervisor implementation tasks)

### Corrected Rule Recommendation

The `no_wrong_stream` prompt-quality check should use an allowlist:

**Allowed patterns in Mainstream prompts:**
- `tools/supervisor/supervisor_loop.py autonomous-cycle` — evidence submission
- `tools/supervisor/validate_product_code_ledger.py` — ledger validation
- `.local/supervisor/selected-product-gaps.json` — data reference
- `tools/supervisor/build_declaration_review_package.py` — review package build

**Forbidden patterns in Mainstream prompts:**
- `tools/supervisor/*.py` as an implementation target (edit/fix/add/refactor)
- `tools/supervisor/` in a "Train" or "Lane" title as the deliverable
- Any reference to supervisor tool internals (classes, functions, bugs to fix)

### Conclusion
The `no_wrong_stream` failure is a **false positive**. The Mainstream prompt references supervisor tools exclusively as governance commands, not as implementation targets. The check needs an allowlist for mandatory governance invocations.
