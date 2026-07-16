# Format Factory — mtlx

Parse, edit, and write MaterialX (.mtlx) shading/material network files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-15T19:25:45+00:00 source=package-metadata -->
```bash
pip install format-factory-mtlx
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from mtlx.mtlx_codec import load_mtlx, write_mtlx
from mtlx.mtlx_graph import resolve_connections, get_connected_node

model = load_mtlx("material.mtlx")
print([m["name"] for m in model["materials"]])

# Real graph connection resolution -- not inert strings
for ng in model["node_graphs"]:
    index = resolve_connections(ng)
    upstream = get_connected_node(ng, ng["nodes"][0]["name"], "in")

write_mtlx(model, "material-copy.mtlx")  # preserves nodedef/typedef/look/propertyset and nodegraph internals
```

## Features

- Write-path preserves all element kinds: `nodedef`, `typedef`, `look`, `propertyset`, plain nodes, and `nodegraph` (including graph-level attributes and non-input/output children of internal nodes)
- Real graph connection resolution — `nodename`/`interfacename` references resolve to actual node objects, not inert strings
- Node category (not just data-type) tracking
- `volumematerial` support alongside `surfacematerial`
- Material and node-graph core structure

**Scope note:** semantic interpretation (resolving a look's material assignments, validating a nodedef against the ~800-node standard library, evaluating variant/collection membership) and multi-file `xi:include` resolution remain out of scope. See `reports/spec-coverage/mtlx-deferred.json`.

## License

<!-- BEGIN:README-LICENSE generated=2026-07-15T19:25:45+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-15T19:25:45+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | MaterialX |
| Track | python |
| Package | format-factory-mtlx |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Academy Software Foundation MaterialX v1.39 |
| QName coverage | 2/2 implemented |
| Source files | 14 |
| Test files | 7 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-15T19:25:45+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
