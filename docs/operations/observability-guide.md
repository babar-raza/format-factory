# Observability Guide — Format Factory

## Overview

Format Factory provides structured logging, health checks, and CI artifacts to support
operational visibility into the supervisor pipeline and format acquisition process.

---

## Structured Logging

**Module:** `tools/supervisor/logging_config.py`

The supervisor pipeline uses JSON-structured logging via Python's `logging` module:

```python
from logging_config import configure_logging
logger = configure_logging("my_component")
logger.info("operation started", extra={"format": "fods", "gate": 7})
```

**Log format:** JSON with fields: `timestamp`, `level`, `logger`, `message`, plus any `extra` fields.

**Log output:** `stderr` by default; redirect to file with: `python script.py 2> pipeline.log`

---

## Health Check

**Script:** `tools/health_check.py`

Validates project health in a single command:

```bash
python tools/health_check.py
# Output: health status, import checks, registry validation
```

**What it checks:**
- Format package imports (FODS, FODT, CSV, etc.)
- Registry YAML validity (`registry/format-registry.yaml`)
- Governance validator imports
- Supervisor tool imports

Run before any sprint to verify the environment is clean.

---

## CI Artifacts

Every CI run (GitHub Actions) produces:

| Artifact | Job | Contents |
|----------|-----|---------|
| `coverage-report` | `test-full` (3.11) | `coverage.xml` — line-level coverage |
| `test-results-fast` | `test-fast` (PR only) | JSON test results for layer 0-3 |

**Coverage:** 89–92% across Python 3.10/3.11/3.12 (measured in CI, uploaded per run).

---

## Test Runner with Layer Filtering

**Script:** `tools/test_runner.py`

Run a subset of tests by layer for fast feedback:

```bash
python tools/test_runner.py --layer 1  # Layer 0+1: format unit tests only
python tools/test_runner.py --layer 3  # Layer 0-3: + supervisor/governance tests
python tools/test_runner.py --layer 6  # Layer 0-6: full suite
```

**Layer mapping** (defined in `tests/conftest.py`):
- Layer 0: Health checks, import smoke
- Layer 1: Single-format unit tests (tests/python/)
- Layer 3: Integration — supervisor, governance, evidence
- Layer 4: Golden — roundtrip, cross-format, export
- Layer 5: Broad — packaging, skills, AI tests
- Layer 6: Full suite

---

## Governance Validator Metrics

The supervisor pipeline records evidence quality scores per sprint:

- **Evidence quality score:** 0.0–1.0 (calculated by governance_validators.py)
- **Work item grades:** VERIFIED / ACCEPTED / ACCEPTED_WITH_LIMITATIONS / REJECTED
- **Sprint verdict:** ACCEPTED / ACCEPTED_WITH_REWORK / OVERCLAIMED / REJECTED

**View latest:** `cat reports/supervisor/work-item-grades.yaml`

---

## Sprint Evidence Trail

Each sprint leaves a permanent evidence trail:

```
reports/supervisor/
├── session-resume.md          # Current sprint state
├── evidence-review.md         # Detailed evidence assessment
├── work-item-grades.yaml      # Per-item verdicts
├── latest-cycle-summary.md    # Sprint closeout summary
└── latest-review.md           # Full review output

.local/supervisor/reviews/<run_id>/
└── declaration-review-package.zip  # Signed evidence bundle (SHA-256 verified)
```

---

## Format Registry Status

**File:** `registry/format-registry.yaml`

Query format gate status:

```python
import yaml
with open("registry/format-registry.yaml") as f:
    reg = yaml.safe_load(f)
# Check FODS gate status
fods = next(f for f in reg["formats"] if f["id"] == "fods")
print(fods["gates"])
```

---

## Adding Observability

To add logging to a new supervisor tool:

```python
from logging_config import configure_logging
logger = configure_logging(__name__)

def my_function():
    logger.info("Starting operation", extra={"tool": "my_tool"})
    # ... do work ...
    logger.info("Operation complete", extra={"result": "success"})
```

To add a health check probe:

```python
# In tools/health_check.py — add to the checks list:
{"name": "my_format_import", "check": lambda: __import__("my_format.parser")}
```
