# Code Quality Rubric
# Format Factory — Expert Manual System Review
# Phase 9 output — Generated: 2026-06-25

## Overview

This rubric applies to ALL source files in src/net/ and src/python/.
It defines the minimum code quality expectations for commercial (.NET) and FOSS (Python) products.

---

## General Code Quality Dimensions (0–5)

### CQ-1: Naming and Readability

| Score | Criteria |
|-------|---------|
| 0 | Meaningless names (a, b, x, tmp) throughout |
| 1 | Single-letter variables; unclear method names |
| 2 | Adequate names; some abbreviations that need context |
| 3 | Clear names; self-documenting code in most places |
| 4 | Professional naming; consistent naming conventions throughout |
| 5 | Naming so clear that comments are rarely needed |

### CQ-2: Structure and Organization

| Score | Criteria |
|-------|---------|
| 0 | All logic in one file; no separation of concerns |
| 1 | Minimal structure; partial separation |
| 2 | Files separated by function; some large files |
| 3 | Clear separation; each file has one purpose |
| 4 | Parser/model/writer/exporter clearly separated; no circular imports |
| 5 | Injectable layers; interfaces defined; plugin-ready |

### CQ-3: Error Handling

| Score | Criteria |
|-------|---------|
| 0 | No error handling; exceptions propagate raw |
| 1 | Basic try/catch; catches all Exception generically |
| 2 | Format-specific exceptions; not consistently applied |
| 3 | Custom exception hierarchy; applied consistently |
| 4 | Meaningful exceptions with error codes; null-safe throughout |
| 5 | Exception hierarchy + documentation + recovery suggestions |

### CQ-4: Security

| Score | Criteria |
|-------|---------|
| 0 | No security guards; vulnerable to malformed input |
| 1 | Basic validation; some guards missing |
| 2 | File size guard; basic format validation |
| 3 | File size + DTD disabled + no XXE + input sanitization |
| 4 | Full defense: all of above + streaming (no full-load OOM) |
| 5 | Full defense + fuzzing tests + CVE-resistant design |

### CQ-5: Test Coverage Quality

| Score | Criteria |
|-------|---------|
| 0 | No tests or 1 trivial smoke test |
| 1 | Smoke tests only (non-null returns) |
| 2 | Unit tests for primary path |
| 3 | Unit + edge cases (empty, malformed, Unicode) |
| 4 | Unit + edge + roundtrip + malformed input |
| 5 | Full spec coverage + property-based tests |

---

## .NET-Specific Additions

### CQ-6: XML Documentation

| Score | Criteria |
|-------|---------|
| 0 | No XML comments |
| 1 | Some XML comments on public API |
| 2 | All public methods have summary |
| 3 | All public members have summary + param/returns |
| 4 | Full XML docs; examples where applicable |
| 5 | Full XML docs + remarks + exception documentation |

### CQ-7: Culture and Encoding Safety

| Score | Criteria |
|-------|---------|
| 0 | Culture-sensitive parsing (decimal separator issues) |
| 1 | Some culture-invariant methods used |
| 2 | Most parsing uses InvariantCulture |
| 3 | All number/date parsing is culture-invariant |
| 4 | Full culture-invariant + UTF-8 throughout + stream APIs |
| 5 | Full culture + encoding safety + BOM handling |

---

## Python-Specific Additions

### CQ-8: Python Packaging Quality

| Score | Criteria |
|-------|---------|
| 0 | No setup.py/pyproject.toml |
| 1 | Minimal setup.py (name and version only) |
| 2 | Complete setup.py with dependencies |
| 3 | Complete pyproject.toml + wheel builds |
| 4 | Wheel + installed workflow verified |
| 5 | Wheel + README + CHANGELOG + pinned deps |

---

## Minimum Quality Gates

### For .NET commercial publication:
- CQ-3 >= 3 (meaningful exception hierarchy)
- CQ-4 >= 3 (security guards in place)
- CQ-5 >= 3 (unit + edge cases)
- CQ-6 >= 2 (all public methods documented)
- CQ-7 >= 3 (culture-invariant parsing)

### For Python FOSS release:
- CQ-3 >= 2 (custom exceptions for key failures)
- CQ-4 >= 2 (basic security guards)
- CQ-5 >= 2 (unit tests for primary path)
- CQ-8 >= 3 (wheel builds successfully)
