# Prompt-Quality Blocker Packet

## Sprint: mainstream-r113
## Target: Supervisor stream prompt-quality validator

## Problem
The `no_wrong_stream` check in the prompt-quality validator fails any Mainstream prompt containing `tools/supervisor/` references. This blocks autonomous continuation even when all product work is accepted.

## Root Cause
The check uses a simple substring match: if `tools/supervisor/` appears anywhere in the generated next-worker prompt, it flags `no_wrong_stream: FAIL`. It does not distinguish between:
1. **Governance commands** - mandatory per CLAUDE.md (e.g., `autonomous_cycle.py`, `validate_product_code_ledger.py`)
2. **Implementation targets** - actual Supervisor stream work (e.g., fixing bugs in supervisor scripts)

## Classification of All References

### Allowed Governance Commands (MUST pass)
| Reference | Context | Rationale |
|-----------|---------|-----------|
| `tools/supervisor/autonomous_cycle.py --declaration` | Evidence submission | CLAUDE.md mandatory closeout |
| `tools/supervisor/validate_product_code_ledger.py` | Ledger validation | Source governance |
| `tools/supervisor/build_declaration_review_package.py` | Review package | MEMORY.md mandatory |
| `.local/supervisor/selected-product-gaps.json` | Gap data | Read-only consumption |

### Unnecessary References (should be removed from generated prompts)
| Reference | Context | Fix |
|-----------|---------|-----|
| `py_compile tools/supervisor/autonomous_cycle.py` | Compile check | Remove from template |
| `py_compile tools/supervisor/supervisor_loop.py` | Compile check | Remove from template |
| `py_compile tools/supervisor/generate_supervisor_packet.py` | Compile check | Remove from template |

### Wrong-Stream Implementation (correctly blocked - ZERO found)
None. No R111 or R112 Mainstream prompt references Supervisor implementation tasks.

## Proposed Fix (for Supervisor stream)
Add an allowlist to the `no_wrong_stream` check:

```python
GOVERNANCE_ALLOWLIST = [
    "tools/supervisor/autonomous_cycle.py",
    "tools/supervisor/validate_product_code_ledger.py",
    "tools/supervisor/build_declaration_review_package.py",
    ".local/supervisor/selected-product-gaps.json",
    ".local/supervisor/continuation-signal.json",
]
```

References matching the allowlist should be excluded from the `forbidden_found` list.

## Evidence
- R112 classification: reports/mainstream-r112/prompt-quality-classification.json
- R112 analysis: reports/mainstream-r112/prompt-quality-failure-analysis.md
- R111 prompt-quality result: .local/supervisor/reviews/mainstream-r111/prompt-quality-result.json
- R112 prompt-quality result: .local/supervisor/reviews/mainstream-r112/prompt-quality-result.json
