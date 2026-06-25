# Unified Product Quality Fix Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Objective

After Phase E pilot proves the fix → verify loop, execute all P0, P1, and P2 quality fixes
across all 30 Format Factory products. This plan defines the full fix sequence.

---

## Fix Sprint Organization

### Sprint QF-1: Release Blockers (P0)

**Goal:** Clear all release-blocking P0 problems. No product can advance to release without Sprint QF-1 completion.

| Fix | Problem | Product | Action | Effort |
|-----|---------|---------|--------|--------|
| QF-1-001 | PQ-007 | ZST .NET | Add ZstWriter class (see pilot plan) | L |
| QF-1-002 | PQ-006 | FODS .NET | Fix csproj PackageDescription Gate 11 claim | XS |
| QF-1-003 | PQ-002 | FODS Python | Designate class-based API as primary; add deprecation notice to dict API | L |
| QF-1-004 | PQ-009 | FODP Python | Add write_fodp() raising NotImplementedError; rename consumer_roundtrip.py → consumer_inspect.py | XS |

**Acceptance criteria for Sprint QF-1:**
- `ZstWriter.Compress(byte[])` + `ZstWriter.Decompress(byte[])` roundtrip test passes
- csproj description says "commercial_readiness_in_progress" not "Gate 11 approved"
- FODS Python `__init__.py` docs clearly identify `FodsDocument` as the primary API
- FODP Python `write_fodp()` raises `NotImplementedError` with helpful message
- All 4 PQ-ID statuses: RESOLVED

---

### Sprint QF-2: Packaging Completeness (P1)

**Goal:** All products can be published to NuGet and PyPI with complete, professional metadata.

| Fix | Problem | Products | Action | Effort |
|-----|---------|----------|--------|--------|
| QF-2-001 | PQ-004 | All Python (20) | Add authors, urls, keywords, classifiers, readme to pyproject.toml | S×20 |
| QF-2-002 | PQ-005 | All .NET (10) | Create README.md at each src/net/{format}/ | M×10 |
| QF-2-003 | PQ-014 | All Python (20) | Create README.md at each src/python/{format}/ | M×20 |

**Template for Python README.md:**
```markdown
# Format Factory — {FORMAT}

Parse, edit, and save {FORMAT} files with Format Factory.

## Installation

pip install aspose-format-factory-{format}

## Quick Start

from {format} import ...  # example

## API Reference

See [docs/api/{format}.md](../../../docs/api/{format}.md)

## License

MIT
```

**Template for .NET README.md:**
```markdown
# FormatFactory.{Format}

Commercial .NET library for reading and writing {FORMAT} files.

## Installation

dotnet add package FormatFactory.{Format}

## Quick Start

using FormatFactory.{Format};
var doc = {Format}Document.Load("file.{ext}");

## License

Commercial license. See LICENSE.
```

**Acceptance criteria for Sprint QF-2:**
- All 20 Python `pyproject.toml` files have: authors, [project.urls], keywords, classifiers, readme
- All 10 .NET `src/net/{format}/README.md` exist and are non-empty
- All 20 Python `src/python/{format}/README.md` exist and are non-empty

---

### Sprint QF-3: API Surface Cleanup (P1 + P2)

**Goal:** Eliminate wildcard imports, fix naming inconsistencies, add stream overloads.

| Fix | Problem | Products | Action | Effort |
|-----|---------|----------|--------|--------|
| QF-3-001 | PQ-001 | All Python (20) | Replace wildcard imports with explicit `__all__` lists | M×20 |
| QF-3-002 | PQ-008 | FODS .NET, FODT .NET | Add `Load(Stream stream)` overloads | S each |
| QF-3-003 | PQ-010 | NDJSON .NET | Add `NdjsonRecord` typed wrapper; expose as `IReadOnlyList<NdjsonRecord>` | M |
| QF-3-004 | PQ-011 | NDJSON .NET | Rename `Load(string content)` to `LoadFromContent(string ndjsonContent)` | XS |
| QF-3-005 | PQ-018 | FODS .NET | Remove static `GetColumnHeaders()` overload | XS |

**API fix process for PQ-001 (per package):**
1. Audit current wildcard exports: `python -c "import {pkg}; print(dir({pkg}))"`
2. Identify which names are intentional public API vs implementation details
3. Write explicit `__all__` list with only the intended public names
4. Test that `from {pkg} import *` still works for the canonical API
5. Verify IDE autocomplete shows only intended names

**PQ-001 curation guide:**
- KEEP: Document/Model classes (FodsDocument, FodsSheet, etc.), primary load/save functions
- KEEP: Exception types
- REMOVE: Internal helper functions (dict manipulation, XML node helpers)
- REMOVE: Module imports leaking into namespace (typing types, pathlib.Path, etc.)

**Acceptance criteria for Sprint QF-3:**
- `from fods import *` exposes only curated names (< 15 names instead of 50+)
- `FodsDocument.Load(stream)` compiles and loads from MemoryStream
- `FodtDocument.Load(stream)` compiles and loads from MemoryStream
- `NdjsonRecord` accessible from `from ndjson import NdjsonRecord`
- `NdjsonDocument.LoadFromContent(str)` works (Load(string) removed or aliased)
- `FodsDocument.GetColumnHeaders()` has no static overload

---

### Sprint QF-4: Examples and Documentation (P2)

**Goal:** All examples use installed-package imports. Developer experience verified.

| Fix | Problem | Products | Action | Effort |
|-----|---------|----------|--------|--------|
| QF-4-001 | PQ-003 | All Python (20) | Update examples to `from {pkg} import ...` with dev-path fallback | M |
| QF-4-002 | PQ-019 | Key Python packages | Add `[project.scripts]` CLI entry points | M |
| QF-4-003 | PQ-015 | HTML/MD/TXT .NET | Classify as internal helpers in registry docs | XS |
| QF-4-004 | Contradiction-001 | FODS .NET | Verify csproj Gate 11 fix propagated to NuGet metadata | XS |

**PQ-003 example update pattern:**
```python
# Before (dev-path only):
import sys
sys.path.insert(0, str(REPO_ROOT))
from src.python.fods import FodsDocument

# After (installed-package with dev fallback):
try:
    from fods import FodsDocument
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[3]))
    from src.python.fods import FodsDocument
```

**PQ-019 CLI entry points (for key packages):**
```toml
[project.scripts]
fods-inspect = "fods.cli:main"
fodt-inspect = "fodt.cli:main"
pbm-inspect = "pbm.cli:main"
```

**Acceptance criteria for Sprint QF-4:**
- `pip install aspose-format-factory-fods && python examples/python/fods/edit_save_fods.py` runs without sys.path hack
- `fods-inspect sample.fods` prints document summary
- HTML/Markdown/TXT removed from public product registry

---

### Sprint QF-5: Deferred Quality Improvements (P3)

**Goal:** Technical debt reduction — test naming, type stubs, dead code removal.

| Fix | Problem | Products | Action | Effort |
|-----|---------|----------|--------|--------|
| QF-5-001 | PQ-013 | NetPBM .NET | Add XML doc to NetpbmExporter | XS |
| QF-5-002 | PQ-016 | All Python | Delete or wire _shared/ base classes | S |
| QF-5-003 | PQ-017 | FODS .NET, FODT .NET | Rename sprint-named tests → feature-named | L |
| QF-5-004 | PQ-020 | Key Python packages | Generate .pyi stub files | L |

**PQ-003 is resolved in Sprint QF-4. PQ-017 is deferred to QF-5 due to rename risk (100+ test files).**

**Acceptance criteria for Sprint QF-5:**
- NetpbmExporter has XML doc comment explaining within-family scope
- `_shared/` either deleted or actively inherited from by >=3 format packages
- FODS .NET test files can be navigated by feature (not by sprint number)
- `from fods import FodsDocument` shows type hints in IDE

---

## Fix Sprint Sequencing Summary

```
QF-1 (Release Blockers) — must complete before any commercial release
    └── QF-2 (Packaging) — must complete before PyPI/NuGet publication
        └── QF-3 (API Cleanup) — must complete before developer preview
            └── QF-4 (Examples/Docs) — must complete before public announcement
                └── QF-5 (Deferred P3) — can run in parallel with marketing prep
```

---

## Total Fix Effort Estimate

| Sprint | Effort | Team Size | Calendar Estimate |
|--------|--------|-----------|------------------|
| QF-1 | M-L | 1 agent | 1-2 days |
| QF-2 | L-XL | 1 agent | 3-5 days |
| QF-3 | L | 1 agent | 2-3 days |
| QF-4 | M | 1 agent | 1-2 days |
| QF-5 | XL | 1 agent | 4-7 days |
| **Total** | **XL** | **1 agent** | **~2-3 weeks** |

---

## Fix Sprint Evidence Requirements

Each fix sprint must produce:
1. Changed source files (diff)
2. New or updated test files
3. Test run output showing all passes
4. Updated `product-quality-problem-schema.json` (problem status → RESOLVED)
5. Evidence bundle at `.local/evidences/product-quality-fixes/qf-{N}/`

---

## Unified Fix Plan Success Criteria (ALL SPRINTS COMPLETE)

- All PQ-001 through PQ-009 statuses: RESOLVED
- ZST .NET commercial_readiness_score: >= 3.5 (post ZstWriter addition)
- FODS Python foss_readiness_level: PY-5 (post API cleanup)
- FODS .NET commercial_readiness_score: >= 4.3 (post README + stream load fix)
- FODP Python foss_readiness_level: >= PY-2 (post write stub + honest docs)
- All Python packages: publishable to PyPI (pyproject.toml complete)
- All .NET packages: publishable to NuGet (README.md exists)
- No P0 or P1 OPEN problems remain
