---
sprint: R92
generated_by: r92-worker
---

# Package/Install Proof (Train T)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Installed Python Packages (R92 state)

| Package | Version | Import |
|---------|---------|--------|
| aspose-format-factory-fods | 0.1.0.dev0 | `import fods` |
| aspose-format-factory-fodt | 0.1.0.dev0 | `import fodt` |
| aspose-format-factory-pbm | 0.1.0.dev0 | `import pbm` |
| aspose-format-factory-pgm | 0.1.0.dev0 | `import pgm` |
| aspose-format-factory-zst | 0.1.0.dev0 | `import zst` |
| zstandard | 0.25.0 | (dependency) |

## .NET Build Status

| Project | Status |
|---------|--------|
| FormatFactory.Fods | PASS (207 tests) |
| FormatFactory.Fodt | PASS (193 tests) |
| FormatFactory.Netpbm | PASS (112 tests) |

## Wheel Rebuild Status

R92 source changes:
- `src/net/fods/FodsDocument.cs` — GetSheetNames() (Train K/L)
- `src/net/fodt/FodtDocument.cs` — GetHeadingParagraphs() (Train M)
- `src/net/netpbm/Model/NetpbmImage.cs` — FillRegion() (Train N)

These are .NET-only changes. No Python packages require wheel rebuild this sprint.

## Status: INSTALL PROOF CURRENT — NO REBUILD REQUIRED
