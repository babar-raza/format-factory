# Import migration

The alpha import `ipynb` is replaced by `format_factory.ipynb`.

| Alpha symbol | Production symbol |
|---|---|
| `ipynb.load_ipynb` | `format_factory.ipynb.load_ipynb` or typed `load` |
| `ipynb.write_ipynb` | `format_factory.ipynb.write_ipynb` or typed `dump` |
| `ipynb.probe_ipynb` | `format_factory.ipynb.probe_ipynb` or diagnostic `probe` |
| `ipynb.IpynbDocument` | `format_factory.ipynb.IpynbDocument` |

The production wheel does not install the alpha top-level package.
