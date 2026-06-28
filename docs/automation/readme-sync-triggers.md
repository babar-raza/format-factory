# README Sync Triggers

Run README sync after changes that affect generated package claims:

- Python `pyproject.toml` or .NET `.csproj` version/package metadata changes.
- `shared/qname-registry/{format}.yaml` changes.
- New or removed files under `tests/{track}/{format}/`.
- New or removed source files under `src/{track}/{format}/`.
- Sprint closeout, as a best-effort freshness check.
- Before release or package preparation.

Freshness check:

```bash
python tools/readme_sync/run_sync.py --mode drift-only
```

Full sync:

```bash
python tools/readme_sync/run_sync.py --mode full
```
