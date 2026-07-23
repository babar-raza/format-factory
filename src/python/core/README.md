---
visibility: generated
generated_by: codex
---

# format-factory-core

Small, dependency-free primitives shared by Format Factory’s independently
publishable Python format libraries.

The package contains only:

- the common exception hierarchy;
- immutable validation diagnostics and source locations;
- configurable resource limits; and
- path/stream protocols and probe results.

It contains no format model, parser, writer, registry, converter, plugin
loader, analytics, agent, or governance runtime.

```python
from format_factory.core import ResourceLimits, ValidationReport

limits = ResourceLimits(max_input_bytes=8 * 1024 * 1024)
report = ValidationReport()
assert report.is_valid
```

Python 3.11 through 3.14 is supported.
