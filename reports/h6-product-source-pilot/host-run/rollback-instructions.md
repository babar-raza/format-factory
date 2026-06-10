# Rollback Instructions — h8-probe-abw-001

## Files Changed

- `src/python/abw/abw_codec.py` — added `probe_abw()` function
- `src/python/abw/__init__.py` — added `probe_abw` to imports and `__all__`

## Rollback Command

```bash
git checkout HEAD -- src/python/abw/abw_codec.py src/python/abw/__init__.py
```

## Verification

After rollback, `probe_abw` should no longer be importable:

```python
python -c "from src.python.abw.abw_codec import probe_abw"  # should ImportError
```

## Notes

- No other files were modified by this task
- The probe_abw change is isolated to the public API
- No external dependencies added
- No tests/ or registry/ files were modified
