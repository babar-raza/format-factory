---
visibility: generated
generated_by: codex
---

# Migration from the alpha package

The 0.1 alpha imported from `ubl` and returned untyped dictionaries for
Invoice, CreditNote, and Order. The production namespace is:

```python
from format_factory.ubl import load, dump, validate
```

`load()` now returns a typed root class backed by a lossless structural XML
tree. The old `load_ubl`, `write_ubl`, and analytics helpers remain in the
repository for characterization testing, but are not included in the 0.2
wheel. Use `document.root`, `document.root_name`, and tree traversal while
the curated Invoice, CreditNote, and Order workflow layer is migrated.
