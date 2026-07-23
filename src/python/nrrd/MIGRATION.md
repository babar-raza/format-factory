# Import migration

| Alpha symbol | Production symbol |
|---|---|
| `nrrd.load_nrrd` | `format_factory.nrrd.load_nrrd` or typed `load` |
| `nrrd.write_nrrd` | `format_factory.nrrd.write_nrrd` or typed `dump` |
| `nrrd.probe_nrrd` | `format_factory.nrrd.probe_nrrd` or diagnostic `probe` |
| `nrrd.NrrdDocument` | `format_factory.nrrd.NrrdDocument` |

The production wheel does not install the alpha top-level package.
