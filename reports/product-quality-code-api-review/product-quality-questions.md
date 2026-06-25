# Product Quality Review — Key Questions to Answer

These are the concrete questions the review execution sprint must answer
for each product. Answers must be source-verified, not claimed.

## API Quality Questions

### For Every Product
1. What are all the public classes?
2. What are all the public methods and properties?
3. Are method names predictable for a developer unfamiliar with the codebase?
4. Is there a consistent Load/Save/Export pattern across formats?
5. Do similar methods have consistent names across products? (e.g., Load vs LoadFile vs Parse)
6. Are there stream-based overloads alongside path-based ones?
7. Are all exception types custom and named? Do they carry useful messages?
8. Are return types appropriate (IReadOnlyList vs List, nullable vs throw)?
9. Can a developer discover the API from intellisense alone?
10. How many steps does a basic load → inspect → save workflow require?

### Python-Specific
11. What does `from fods import *` actually expose? Is the list manageable?
12. Are there type hints on all public functions?
13. Is there a curated `__all__` or is it dynamic generation?
14. Are dict return types documented with their keys?
15. Can the package be imported cleanly after `pip install`?

### .NET-Specific
16. Are generics used appropriately or avoided in favor of simpler types?
17. Are init-only or readonly properties used where mutation should be prevented?
18. Is `sealed` applied to document classes to prevent inheritance misuse?
19. Are there overloads for common use cases (e.g., GetCellValue with default)?
20. Do exporters return string vs write to file vs both?

## Architecture Questions

21. Are parser, model, writer, and exporter in separate files/classes?
22. Is there a god class with >30 public methods?
23. Do model objects directly expose XML/JSON internals (e.g., XElement)?
24. Can the writer be used without the parser (independent creation)?
25. Can the parser be tested without the writer?
26. Are internal helpers appropriately internal/private?
27. Do Python packages inherit from `_shared/_base_codec.py`? If not, why?
28. Are Python `Spec/` and `Compat/` subdirectories behavioral or architecture-only?
29. Is there evidence of significant code duplication across formats?
30. Are error classes appropriate (not all exceptions inherit from base Exception)?

## Feature Questions

31. Can a FODS spreadsheet be loaded, a cell edited, and the result saved with the edit preserved?
32. Can a FODT document have a paragraph appended and then saved?
33. Can a NetPBM image be loaded, flipped horizontally, and saved as valid PBM?
34. Can a ZST file be compressed AND decompressed in .NET? (Expected: compress missing)
35. Can a NDJSON document be filtered and the result written to a new file?
36. Can a CSV file be loaded, a row added, and saved as valid CSV?
37. Can a SYLK file have a cell value changed and be saved as valid SYLK?
38. Can a DIF file be loaded and written back?
39. Can a PBM P4 (binary) file be parsed correctly?
40. Can a QOI file be encoded from raw pixel data?
41. Does Python FODP have a write_fodp function? (Expected: NO)
42. Does .NET ZST have a ZstWriter class? (Expected: NO)
43. Does FODT .NET expose table operations? (Spec/Table/* exists — check if wired)
44. Does NetpbmExporter produce physical output files?
45. Does FODS Python have a clear "primary" API vs "secondary" API?

## Test Quality Questions

46. What is the ratio of behavior-testing tests to smoke tests for FODS .NET?
47. Do malformed-input tests exist for FODS, FODT, CSV, NDJSON, NetPBM?
48. Are there roundtrip tests (load → modify → save → reload → verify)?
49. Are tests organized by feature or by sprint iteration?
50. Do tests verify physical output (check exported file contents)?
51. Are tests using the public API naturally or reaching into private internals?
52. Is there an installed-package integration test for Python packages?

## Examples/Docs/Packaging Questions

53. Does `edit_save_fods.py` run against an installed `fods` package (not `src.python.fods`)?
54. Is there a README.md at `src/net/fods/` (csproj references it)?
55. Is there a README.md at `src/python/fods/`?
56. Do pyproject.toml files have `authors`, `[project.urls]`, `keywords`, `classifiers`?
57. Do any Python packages have CLI entry points (`[project.scripts]`)?
58. Are there type stub files (`.pyi`) for any Python package?
59. Does `docs/api/pbm.md`, `docs/api/pgm.md`, `docs/api/ppm.md` exist and have content?
60. Do examples produce inspectable output (files, printed data)?

## Claim vs Reality Questions

61. Is Gate 11 for FODS actually approved? (csproj says yes, source header says in_progress)
62. Are all 14 claimed "PROOF_LEVEL_4+" Python formats actually at that level?
63. Does poc-targets.yaml correctly reflect SYLK `get_row_count` and `get_column_count` public API?
64. Are all 5 claimed FODT exporters functional (HTML/Markdown/TXT — yes; PDF/PNG — stub check)?
65. Are all claimed Python installed-workflow proofs real (installed package, not src.python)?
