# format-factory-xliff

Typed, bounded XLIFF 2.0/2.1 lifecycle support under the implicit
`format_factory` namespace.

```python
from format_factory.xliff import dump, load, validate

document = load("messages.xlf")
report = validate(document)
if report.is_valid:
    dump(document, "canonical.xlf")
```

This production chassis provides strict XML safety checks, typed core
containers, structured inline content, deterministic XML output, unknown
namespace preservation, validation diagnostics, and resource limits. It never
resolves skeleton or external resource references.

The package is still `0.2.0.dev0`. Complete XLIFF 2.1 module typing, official
schema execution, processing-requirement coverage, independent interoperability,
fuzzing, mutation, and release matrices remain certification obligations. XLIFF
2.2 is not accepted by the stable profile and XLIFF 1.2 is intentionally not
represented by this model.

See `MIGRATION.md` for alpha import-path changes and `SECURITY.md` for the
untrusted-input policy.
