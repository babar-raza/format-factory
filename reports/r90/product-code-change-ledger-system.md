---
visibility: generated
generated_by: codex
---

# Product-Code Ledger System

`tools/supervisor/validate_product_code_ledger.py` validates the JSON ledger.

## Enforcement

- It inspects committed changes after `tracking_base_ref`.
- It also inspects staged, unstaged, and untracked `src/` changes.
- It does not require a clean git worktree.
- A changed file must have a ledger reference with its current SHA-256.
- A deleted file must have a ledger reference with `state: deleted`.

Run:

```text
python tools/supervisor/validate_product_code_ledger.py
```

Exit `0` means the ledger covers detected source changes. Exit `1` means at
least one source change or ledger structure error requires repair.
