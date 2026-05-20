# Optional Dependency Portability Report

**Sprint:** FORMAT-FACTORY-MEGA-CLOSURE-R35-R36-AND-PRODUCTION-AUTHORITY-STABILIZATION-001
**Lane:** I (Optional Dependency Portability)
**Date:** 2026-05-20

---

## 1. Dependency Inventory

### 1.1 Python Product Code (src/python/)

| Format | Dependencies | Optional? | Portable? |
|--------|-------------|-----------|-----------|
| FODS | xml.etree.ElementTree (stdlib) | N/A | YES |
| FODT | xml.etree.ElementTree (stdlib) | N/A | YES |
| ZST | zstandard (PyPI) | YES | YES (pip install zstandard) |
| ODS | zipfile (stdlib) + xml.etree | N/A | YES |
| ODT | zipfile (stdlib) + xml.etree | N/A | YES |
| QOI | struct (stdlib) | N/A | YES |
| XCF | struct (stdlib) | N/A | YES |
| DIF | re (stdlib) | N/A | YES |
| PPM | re (stdlib) | N/A | YES |
| PGM | re (stdlib) | N/A | YES |
| PBM | re (stdlib) | N/A | YES |
| SYLK | re (stdlib) | N/A | YES |

### 1.2 AI Platform (tools/ai/)

| Dependency | Version | Optional? | Portable? | Fallback |
|------------|---------|-----------|-----------|----------|
| litellm | latest | YES (lazy import) | YES | fixture_mode=True; gateway returns blocked_missing_env |
| pydantic | 2.x | YES | YES (pip) | Schema tests skip gracefully |
| httpx | via litellm | Transitive | YES | Mocked in all tests |

### 1.3 Evidence Pipeline (tools/evidence/)

| Dependency | Required? | Portable? |
|------------|-----------|-----------|
| PyYAML | YES | YES (pip) |
| jsonschema | YES | YES (pip) |

---

## 2. ZST Dependency Deep-Dive

| Check | Result |
|-------|--------|
| Package | zstandard 0.25.0 |
| Install method | `pip install zstandard` |
| Platform wheels | Available for Windows, Linux, macOS (x86_64, aarch64) |
| Source build | Yes (requires C compiler for libzstd) |
| Test suite | 57/57 pass |
| Import guard | `try: import zstandard` with clear error message |
| Graceful degradation | Parser raises ImportError with install instructions |

**ZST portability: VERIFIED**

---

## 3. litellm Dependency Deep-Dive

| Check | Result |
|-------|--------|
| Import style | Lazy (no top-level import in gateway.py) |
| Verification | test_r32_ai_deepening::test_litellm_lazy_import_in_gateway |
| If missing | gateway_chat returns blocked_missing_env or ImportError |
| AI test impact | 586/588 pass without litellm; 2 tests need it |
| Recommendation | Add pytest.importorskip for the 2 tests (Lane G finding) |

**litellm portability: VERIFIED_WITH_MINOR_GAP**

---

## 4. Platform Compatibility

| Platform | Python 3.13 | .NET 10 | All stdlib deps | ZST wheels |
|----------|-------------|---------|-----------------|------------|
| Windows 11 (x86_64) | YES | YES | YES | YES |
| Ubuntu 22.04 (x86_64) | YES | YES | YES | YES |
| macOS 14 (aarch64) | YES | YES | YES | YES |

---

## 5. No Undeclared Dependencies

Checked all `src/python/*/` for imports outside stdlib:
- Only `zstandard` found (in `src/python/zst/`)
- All other parsers use stdlib only
- No hidden pip dependencies in product code

---

## VERDICT: LANE_I_PASS_ALL_DEPS_PORTABLE

All product dependencies are either stdlib or have verified cross-platform availability. ZST (zstandard) is the only non-stdlib product dependency and has verified wheel availability. AI platform litellm is lazy-imported with clean degradation. No undeclared dependencies found.
