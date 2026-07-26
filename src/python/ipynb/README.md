# Format Factory — Jupyter Notebook

Typed, bounded parsing and deterministic writing for Jupyter Notebook
nbformat 4.0 through 4.5.

> This package is under production migration. The package chassis and
> compatibility characterization are implemented; full obligation and
> interoperability certification remain computed release gates.

## Installation

```bash
pip install format-factory-ipynb
```

Python 3.11 through 3.14 is supported. The separately installed
`format-factory-core` package supplies diagnostics and resource-limit types.

## Common lifecycle

```python
from format_factory.ipynb import dump, load, probe, validate

result = probe("notebook.ipynb")
if not result:
    raise ValueError(result.reason)

document = load("notebook.ipynb")
report = validate(document)
if not report:
    raise ValueError(report.errors)

document.add_cell("markdown", "# New section")
dump(document, "notebook-edited.ipynb")
```

`load` defaults to strict mode. `mode="preservation"` retains safe unknown
JSON members. The library parses notebook structure only and never executes
code.

## Active-content handling

Notebook Markdown, attachments, and output MIME bundles can carry active
HTML, SVG, JavaScript, and external resource references. Sanitization is
therefore explicit and reportable:

```python
from format_factory.ipynb import (
    SanitizationMode,
    SanitizationPolicy,
    sanitize,
)

preview = sanitize(document)  # lossless: reports, never changes content
if preview.findings:
    report = sanitize(
        document,
        policy=SanitizationPolicy(mode=SanitizationMode.QUARANTINE),
    )
```

The available modes are:

- `LOSSLESS`: preserve content exactly and report every classified payload.
- `REMOVE`: remove each unsafe renderable payload while retaining safe MIME
  alternatives.
- `QUARANTINE`: move unsafe payloads into non-rendered
  `metadata.format_factory.security.quarantine` entries.
- `MARK_UNTRUSTED`: retain payloads and add digest-only untrusted markers.

`dry_run=True` previews mutating modes. Classification is bounded by
`ResourceLimits` and never renders, executes, imports, opens, or resolves
content. Removal is deliberately conservative: the complete renderable
payload is removed rather than partially rewriting arbitrary markup and
claiming that the remainder is safe.

## Public namespace

The supported namespace is `format_factory.ipynb`. The earlier top-level
`ipynb` alpha namespace is not included in built distributions. See
`MIGRATION.md` for symbol mappings.

## Security boundary

Input size and nesting are bounded by default and configurable with
`format_factory.core.ResourceLimits`. The security policy and disclosure
process are documented in `SECURITY.md`.

## Current scope

- Typed notebook, cell, and output views
- Deterministic JSON serialization
- Cell-ID normalization and structural validation
- Unknown JSON-member preservation
- MIME-bundle helpers and structural mutation
- Explicit active-content classification, removal, quarantine, and marking
- Installed-package CLI and analytics in isolated modules

Version conversion and complete differential certification against the
official `nbformat` implementation are tracked as mandatory obligations and
are not claimed by this package chassis.

## License

Apache-2.0
