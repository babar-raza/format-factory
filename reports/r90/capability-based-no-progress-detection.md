---
visibility: generated
generated_by: codex
---

# Capability-Based No-Progress Detection

`tools/supervisor/detect_product_progress.py` builds local capability snapshots
from the product ledger and POC matrix, or compares snapshot files supplied with
`--snapshot`.

The detector reads the default threshold from
`.supervisor/policies.yaml`:

```text
autonomous_continuation.no_progress_max_consecutive: 2
```

It reports `NO_PROGRESS` after the configured number of consecutive unchanged
snapshot intervals. A ledger entry or a matrix capability-status change alters
the snapshot fingerprint and resets the stagnant interval count.

Examples:

```text
python tools/supervisor/detect_product_progress.py --write-snapshot .local/supervisor/product-progress/r90.json
python tools/supervisor/detect_product_progress.py --snapshot old-1.json --snapshot old-2.json
```

Exit `0` means progress exists or the threshold has not been reached. Exit `2`
means the no-progress threshold has been reached.
