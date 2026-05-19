# R30 Lane F: Retrieval Namespace Path-Safety Hardening
# Date: 2026-05-19

## Defects Fixed
1. **No format_id validation:** `format_id` was used directly in filesystem paths (`self._store_root / format_id`) with no sanitization. Path traversal via `../etc` or `/abs/path` was possible.
2. **Dead `authorized_cross_format` parameter:** `query()` accepted `authorized_cross_format` bool but never used it, creating a false sense of cross-format authorization capability.

## Fix
1. Added `validate_format_id()` function with regex `^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$`. Rejects empty, `..`, `/`, `\`, and special characters. Called from `get_namespace_path()` which gates all namespace operations.
2. Removed `authorized_cross_format` parameter from `query()`. Cross-format retrieval is always forbidden (use `reject_cross_namespace_query()`).

## Tests Added (Lane F in test_r30_ai_defect_closure.py)
- `test_traversal_dots_rejected`
- `test_traversal_slash_rejected`
- `test_traversal_backslash_rejected`
- `test_empty_rejected`
- `test_special_chars_rejected`
- `test_valid_format_id_accepted`
- `test_namespace_manager_rejects_traversal`
- `test_cross_namespace_rejected`
- `test_stale_detection_no_manifest`
- `test_create_and_load_manifest`
- `test_query_without_cross_format_param` — verifies parameter removed from signature

## Status: CLOSED_VERIFIED
