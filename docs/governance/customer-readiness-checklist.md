# Customer-Readiness Publication Checklist

**Authority:** This checklist defines the minimum criteria a format must meet before
publication as a customer-facing package (PyPI for Python FOSS, NuGet for .NET).

**Human gates:** `commercial_product_ready=true` requires Babar Raza approval.
PyPI/NuGet publication requires credentials and explicit policy authorization.

---

## Criteria (all 8 must be satisfied)

### 1. Install Proof
- [ ] Wheel builds successfully (`python -m build` or equivalent)
- [ ] Installs in a fresh virtual environment without errors
- [ ] `import {package}` succeeds after install
- [ ] At least 3 public API calls execute correctly post-install

### 2. API Reference
- [ ] `docs/api/{format}.md` exists with all exported functions documented
- [ ] Each function has: signature, parameter descriptions, return type, example
- [ ] No undocumented public functions in `__all__`

### 3. Examples
- [ ] `examples/python/{format}/` exists with 2+ runnable scripts
- [ ] Scripts use only the public API (no internal imports)
- [ ] Scripts include inline comments explaining each step
- [ ] Scripts handle missing sample files gracefully

### 4. Round-Trip Proof
- [ ] 5+ semantic round-trip tests exist (load → edit → write → reload → deep-verify)
- [ ] Tests compare individual field values, not just structure counts
- [ ] Tests cover: string values, numeric values, typed values, empty content
- [ ] At least one test uses a real sample file (not synthetic only)

### 5. Malformed Input Tests
- [ ] 3+ classes of malformed input are tested and rejected gracefully
- [ ] Malformed XML / corrupted headers / truncated files handled
- [ ] No unhandled exceptions on malformed input (returns error or raises documented exception)

### 6. Security Guard Tests
- [ ] File size guard tested (100MB or format-appropriate limit)
- [ ] Injection guard tested (DTD prohibition for XML formats, or equivalent)
- [ ] Both guards have dedicated test functions with assertions

### 7. Release Notes
- [ ] `docs/release/{format}-v{version}.md` exists
- [ ] Contains: version number, date, feature summary, known limitations, breaking changes (if any)

### 8. Version Number
- [ ] `__version__` is set in `__init__.py`
- [ ] Version is not `"0.0.0"` or a placeholder
- [ ] Version follows semver (e.g., `"1.0.0"` for first release)

---

## Verification Process

1. An execution agent fills in the checklist for a specific format
2. All 8 criteria must show evidence (test output, file paths, or screenshots)
3. The agent prepares a Gate 11 readiness packet referencing this checklist
4. Babar Raza reviews the packet and decides on `commercial_product_ready` status
5. Publication proceeds only after explicit authorization + credential availability

---

## Format Readiness Status

| Format | Criteria Met | Blocker |
|--------|-------------|---------|
| ZST | 5-6 of 8 (estimated) | Install proof, examples, release notes |
| FODS | 5-6 of 8 (estimated) | Semantic round-trip, install proof, examples |
| FODT | 5-6 of 8 (estimated) | Semantic round-trip, install proof, examples |

*This table is updated as formats progress toward publication.*
