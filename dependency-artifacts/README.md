# Dependency Artifacts

## ZST Dependency Classification

**Classification:** `ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED`

The `format-factory-zst` package requires an external dependency:

```
zstandard >= 0.21.0
```

This dependency is available on PyPI but **cannot be resolved in a network-isolated
(no-index) installation environment**.

### Failing Install (no-network)

```
$ pip install --no-index format_factory_zst-0.1.0-py3-none-any.whl

ERROR: Could not find a version that satisfies the requirement zstandard>=0.21.0
ERROR: No matching distribution found for zstandard>=0.21.0
```

### Passing Install (with network)

```
$ pip install format_factory_zst-0.1.0-py3-none-any.whl

Successfully installed format-factory-zst-0.1.0 zstandard-0.22.0
```

### Resolution Options

1. **Normal PyPI use:** `pip install format-factory-zst` resolves `zstandard` automatically.
2. **Bundled dependency:** Include `zstandard` wheel in `dependency-artifacts/wheels/`.
3. **Vendored source:** Include `zstandard` source in the package (license review required).

### Current Status

Option 1 (normal PyPI use) is the expected deployment path.
Options 2 and 3 are deferred. ZST publication is **blocked** until this is resolved
for the target deployment environment.

### Sprint History

- R78: Initial ZST classification as dependency issue
- R82: Confirmed ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED
- R84 Train J: Policy documented in this file

## Other Packages

All other format-factory packages (fods, fodt, pbm, pgm, ppm, sylk, dif) use
Python stdlib only and have no external dependencies.
