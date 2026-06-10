---
sprint: mainstream-R99
train: I
ledger: R99-GOVERNED-PACKAGE-INSTALL-PROOF-001
---

# Package Install Proof — R99

## Installed Python Packages (7 total)

| Package | Version | Import Path |
|---------|---------|-------------|
| aspose-format-factory-fods | 0.1.0.dev0 | `import fods` |
| aspose-format-factory-fodt | 0.1.0.dev0 | `import fodt` |
| aspose-format-factory-pbm | 0.1.0.dev0 | `import pbm` |
| aspose-format-factory-pgm | 0.1.0.dev0 | `import pgm` |
| aspose-format-factory-ppm | 0.1.0.dev0 | `import ppm` |
| aspose-format-factory-sylk | 0.1.0.dev0 | `import sylk` |
| aspose-format-factory-zst | 0.1.0.dev0 | `import zst` |

## New in R99
- PPM wheel installed (was missing in prior sprints)
- SYLK wheel installed (was missing in prior sprints)

## Dogfood Example Verification
- `examples/python/ppm/pgm_to_ppm_example.py` — PASS (new R99)
- `examples/python/pbm/pbm_to_pgm_example.py` — previously verified

## .NET Products (3 test projects)
- FODS: `tests/net/fods/*.csproj`
- FODT: `tests/net/fodt/*.csproj`
- Netpbm: `tests/net/netpbm/*.csproj`

## Status: PACKAGE INSTALL PROOF PASS
