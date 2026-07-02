# Plan: Heal README Sync Tooling, Then Regenerate All READMEs

## Reassessment (2026-07-01) — Current State vs Previous Plan

**Nothing from Phase 1 has been implemented.** Verified against current source:

| Plan Item | Status | Evidence |
|-----------|--------|---------|
| Fix 1: dynamic `__all__` | **Unresolved** | `collect_format_state('fodg', 'python')['public_api_exports']` = `['(dynamic)']` at runtime; `collector.py` lines 120–137 unchanged |
| Fix 2: cross-track companion | **Unresolved** | `collect_format_state('fods', 'dotnet')['requires_python']` = `None`; no companion fields in `collect_format_state()` |
| Fix 3: companion in renderer | **Unresolved** | `renderer.py` lines 43–44 still use `state.get("requires_python")` directly |
| Fix 4: grouped Public API | **Unresolved** | `renderer.py` lines 55–62 still dump flat list of up to 80 items |
| Fix 5: new tests | **Partially done** | sys.path prepend added externally (20/20 pass); 3 new test cases from plan not yet added |
| Phase 2: regenerate READMEs | **Blocked** | No `src/*/README.md` changes made; blocked on Phase 1 |

---

## Context

All 30 README.md files under `src/` (20 Python, 10 .NET) are managed by `tools/readme_sync/`. The pipeline has confirmed bugs:

- **`(dynamic)` Public API** — `collector._read_python_exports()` (lines 120–137) uses `ast.literal_eval`, which cannot parse list-comprehension `__all__` definitions. Falls back to `["(dynamic)"]` for all 20 Python packages.
- **`unknown` in .NET Package Info** — `gen_package_info()` shows `License: unknown` and `Python: unknown` because the .NET state dict has no license field and no cross-track Python package reference. Confirmed: `fods dotnet license = None`, `fods dotnet python = None`.
- **Wrong package names in headers** — MAINTAINED sections (preserved byte-for-byte by the tool) say `aspose-format-factory-*`; pyproject.toml says `format-factory-*`.

**Strategy:** Fix the tooling → run one command to regenerate all 30 READMEs → manually fix MAINTAINED-section issues the tool preserves but cannot generate.

---

## Phase 1: Heal the System (tooling fixes)

### Fix 1 — Dynamic `__all__` resolution
**File:** `tools/readme_sync/collector.py`, `_read_python_exports()` (lines 120–137)

Current code tries `ast.literal_eval` on a regex match. All 20 packages use multi-line list comprehensions → `literal_eval` always raises → returns `["(dynamic)"]`.

**Fix:** Add a runtime-import fallback **inside the existing `except Exception` block** (replacing the bare return):

```python
    except Exception:
        # Fallback: import the module at runtime and read __all__ directly
        try:
            import importlib
            mod = importlib.import_module(format_id)
            exports = getattr(mod, "__all__", None)
            if isinstance(exports, list) and exports:
                return [str(v) for v in exports], meta
        except Exception:
            pass
        return ["(dynamic)"], meta
```

This is safe: the sync tool runs in `.venv` where all packages are installed; only reads `__all__`, no side effects.

### Fix 2 — Cross-track companion package lookup
**File:** `tools/readme_sync/collector.py`, `collect_format_state()` (lines 140–172)

Current function assembles and returns a dict literal directly. Need to build it as a local variable, add companion keys, then return.

**Fix:** Change the return statement at line 146 into a `state = {...}` assignment, then append before returning:
```python
    # at bottom of collect_format_state(), before return:
    if trk == "dotnet":
        py_pkg = _read_pyproject(format_id)
        state["companion_python_package"] = py_pkg.get("package_name") if py_pkg else None
    elif trk == "python":
        net_pkg = _read_csproj(format_id)
        state["companion_dotnet_package"] = net_pkg.get("package_name") if net_pkg else None
    return state
```

### Fix 3 — Use companion values in Package Info
**File:** `tools/readme_sync/renderer.py`, `gen_package_info()` (lines 43–44)

**Fix:** Change lines 43–44 from:
```python
        ("Python", _unknown(state.get("requires_python"))),
        (".NET", _unknown(state.get("target_framework"))),
```
to:
```python
        ("Python", _unknown(state.get("requires_python") or state.get("companion_python_package"))),
        (".NET", _unknown(state.get("target_framework") or state.get("companion_dotnet_package"))),
```

### Fix 4 — Group Public API exports by category
**File:** `tools/readme_sync/renderer.py`, `gen_public_api()` (lines 55–62)

**Fix:** Replace the flat-list body with categorized groups:
```python
def gen_public_api(state: dict, timestamp: str | None = None) -> str:
    begin, end = _marker("public_api", "src-python-init", timestamp)
    exports = state.get("public_api_exports") or []
    if not exports or exports == ["(dynamic)"]:
        body = "- No public API exports resolved."
        return f"{begin}\n{body}\n{end}\n"
    fmt = state.get("format_id", "")
    core = sorted(e for e in exports if not e.startswith(f"{fmt}_") and not e[0].isupper())
    classes = sorted(e for e in exports if e[0].isupper())
    analytics = sorted(e for e in exports if e.startswith(f"{fmt}_"))
    lines = [f"**{len(exports)} exports total**\n"]
    if core:
        shown = core[:20]
        extra = f" … and {len(core) - 20} more" if len(core) > 20 else ""
        lines.append(f"**Core API ({len(core)}):** " + ", ".join(f"`{n}`" for n in shown) + extra)
    if classes:
        lines.append(f"**Classes & Exceptions ({len(classes)}):** " + ", ".join(f"`{n}`" for n in classes))
    if analytics:
        shown = analytics[:15]
        extra = f" … and {len(analytics) - 15} more" if len(analytics) > 15 else ""
        lines.append(f"**Analytics ({len(analytics)}):** " + ", ".join(f"`{n}`" for n in shown) + extra)
    return f"{begin}\n" + "\n\n".join(lines) + f"\n{end}\n"
```

### Fix 5 — New tests
**File:** `tests/tools/test_readme_sync.py`

sys.path prepend already added externally; 20/20 existing tests pass. Only add 3 new cases:

```python
def test_collector_resolves_dynamic_all():
    state = collect_format_state("fodg", "python")
    exports = state["public_api_exports"]
    assert exports != ["(dynamic)"]
    assert len(exports) > 10

def test_cross_track_companion_dotnet_has_python_package():
    state = collect_format_state("fods", "dotnet")
    assert state.get("companion_python_package") is not None
    assert "fods" in state["companion_python_package"].lower()

def test_public_api_grouped_rendering():
    from tools.readme_sync.renderer import gen_public_api
    state = collect_format_state("fodg", "python")
    block = gen_public_api(state, "STRIPPED")
    assert "exports total" in block
    assert "(dynamic)" not in block
```

---

## Phase 2: Heal the Content (after Phase 1 complete)

### Step 1 — Regenerate all READMEs
```bash
python tools/readme_sync/run_sync.py --mode full
```
Updates the 4 auto-generated sections (Installation, Package Info, Public API, License) across all 30 files while preserving MAINTAINED sections byte-for-byte.

### Step 2 — Manual fixes to MAINTAINED sections
These cannot be fixed by the sync tool — it preserves them verbatim:

| File | Section | Fix |
|------|---------|-----|
| `src/python/fodg/README.md` | Header | `aspose-format-factory-fodg` → `format-factory-fodg` |
| `src/python/fodg/README.md` | Quick Start | `get_shape_count(doc)` crashes (codec takes path, not model) → use `count_shapes(doc)`; remove non-existent `page_index=` kwarg from `get_page_metadata` |
| `src/python/fodg/README.md` | Package Structure | Expand 4 → 18 source files |
| `src/python/abw/README.md` | Header | `aspose-format-factory-abw` → `format-factory-abw` |
| `src/python/fodp/README.md` | Header | `aspose-format-factory-fodp` → `format-factory-fodp` |
| `src/python/gnumeric/README.md` | Header | `aspose-format-factory-gnumeric` → `format-factory-gnumeric` |
| `src/python/zst/README.md` | Header | `aspose-format-factory-zst` → `format-factory-zst` |
| `src/python/csv/README.md` | Quick Start | Verify `csv_format` import vs actual module name; fix if broken |
| `src/python/fods/README.md` | Package Structure | Expand to actual file count |
| `src/python/fodt/README.md` | Package Structure | Expand to actual file count |

### Step 3 — Verify Quick Start examples
Run each fixed Quick Start snippet to confirm it executes without errors.

---

## Files Modified

### Phase 1 — Tooling (3 files)
- `tools/readme_sync/collector.py` — runtime import fallback (Fix 1) + cross-track companion (Fix 2)
- `tools/readme_sync/renderer.py` — companion in Package Info (Fix 3) + grouped Public API (Fix 4)
- `tests/tools/test_readme_sync.py` — 3 new test cases (Fix 5; sys.path already done)

### Phase 2 — Content (30 + ~10 files)
- All 30 `src/*/README.md` files (via sync tool)
- ~10 files with additional manual edits to MAINTAINED sections

---

## Verification

1. `.venv/Scripts/pytest tests/tools/test_readme_sync.py -v` — all 23 pass (20 existing + 3 new)
2. `python tools/readme_sync/run_sync.py --mode full --dry-run` — shows planned changes across 30 files
3. `python tools/readme_sync/run_sync.py --mode full` — apply all changes
4. `python tools/readme_sync/run_sync.py --mode validate` — all PASS
5. `python tools/readme_sync/run_sync.py --mode drift-only` — NO_DRIFT
6. Spot-check: `python -c "from tools.readme_sync.collector import collect_format_state; s = collect_format_state('fodg', 'python'); print(len(s['public_api_exports']))"` — should be 100+
7. Run Quick Start snippets for fodg and csv to confirm no crashes


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-01T10:07:59.844502+00:00"
  locked_by: "34c4217ef0bd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
