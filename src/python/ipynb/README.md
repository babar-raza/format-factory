# Format Factory — ipynb

Parse, edit, and write Jupyter Notebook (.ipynb) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-15T19:34:54+00:00 source=package-metadata -->
```bash
pip install format-factory-ipynb
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from ipynb.ipynb_codec import load_ipynb, write_ipynb, probe_ipynb
from ipynb.models import add_cell, add_output_representation

# Detect and load
assert probe_ipynb("notebook.ipynb")
model = load_ipynb("notebook.ipynb")
print(model["nbformat"], len(model["cells"]))

# Mutate: append a cell, then attach an output MIME representation
model = add_cell(model, cell_type="markdown", source="# New section")
write_ipynb(model, "notebook-edited.ipynb")
```

## Features

- Cell id preservation (nbformat 4.5 required field)
- Markdown/raw cell attachments
- First-class output MIME-bundle API (`add_output_representation`, `get_output_representation`)
- Structural mutation API (`add_cell`, `remove_cell`, `clear_outputs`)
- Notebook schema/structural validation
- Cell types (code/markdown/raw) and output types (stream/display_data/execute_result/error)

**Not yet supported:** nbformat v1-3 upgrade/downgrade (targets nbformat v4.x notebooks — the standard since ~2016). See `reports/spec-coverage/ipynb-deferred.json`.

## License

<!-- BEGIN:README-LICENSE generated=2026-07-15T19:34:54+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-15T19:34:54+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Jupyter Notebook |
| Track | python |
| Package | format-factory-ipynb |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Jupyter Project nbformat v4.5 |
| QName coverage | 3/3 implemented |
| Source files | 16 |
| Test files | 11 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-15T19:34:54+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
