---
artifact_id: package-install-proof-ndjson-r126
artifact_type: report
path: reports/r126-ndjson-install-proof/package-install-proof.md
format_id: ndjson
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-06-18"
---

# Package Install Proof — ndjson (r126)

**Date:** 2026-06-18
**Skill:** /package-install-proof
**Format:** ndjson

---

## Summary

| Package | Version | Wheel | Import | API Smoke |
|---------|---------|-------|--------|-----------|
| aspose-format-factory-ndjson | 0.1.0.dev0 | aspose_format_factory_ndjson-0.1.0.dev0-py3-none-any.whl | import ndjson: OK | load_ndjson + to_jsonl_str: PASS |

**Verdict: PASS**

---

## Step 1 — Wheel Location

```
.local/package-builds/python-foss/aspose-format-factory-ndjson/dist/
  aspose_format_factory_ndjson-0.1.0.dev0-py3-none-any.whl
  aspose_format_factory_ndjson-0.1.0.dev0.tar.gz
```

---

## Step 2 — Install

```
pip install aspose_format_factory_ndjson-0.1.0.dev0-py3-none-any.whl --user
```

**Result:** Successfully installed aspose-format-factory-ndjson-0.1.0.dev0

Note: system-level install denied (WinError 5); `--user` flag used.
Install location: `C:\Users\prora\AppData\Roaming\Python\Python313\site-packages\ndjson\`

---

## Step 3 — Import Test

```python
import sys
sys.path.insert(0, r'C:\Users\prora\AppData\Roaming\Python\Python313\site-packages')
import ndjson
print(ndjson.__version__)  # → 0.1.0.dev0
```

**Result: OK** — version 0.1.0.dev0 imported successfully.

---

## Step 4 — API Smoke Test

```python
import ndjson, tempfile, os

sample = '{"id":1,"name":"alpha"}\n{"id":2,"name":"beta"}\n'
with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False, encoding='utf-8') as tf:
    tf.write(sample)
    tmp_path = tf.name

records = ndjson.load_ndjson(tmp_path)
# → [{'id': 1, 'name': 'alpha'}, {'id': 2, 'name': 'beta'}]

ndjson.ndjson_record_count(records)      # → 2
ndjson.ndjson_unique_field_names(records) # → ['id', 'name']
ndjson.to_jsonl_str(records)             # → '{"id": 1, ...}\n{"id": 2, ...}'
```

**Result: PASS**

---

## Step 5 — Public API Surface

```
load_ndjson, write_ndjson, probe_ndjson, roundtrip
to_jsonl_str, write_csv, export_to_csv
ndjson_record_count, ndjson_unique_field_names, ndjson_unique_field_count
ndjson_field_count_variance, ndjson_average_record_size, ndjson_max_record_size
ndjson_min_record_size, ndjson_record_size_variance, ndjson_average_field_count
ndjson_schema_consistency, ndjson_is_homogeneous, ndjson_is_empty
ndjson_is_single_record, ndjson_all_records_nonempty, ndjson_has_null_fields
ndjson_has_numeric_fields, ndjson_has_boolean_fields, ndjson_has_string_fields
ndjson_has_lists, ndjson_has_nested_objects, ndjson_max_nesting_depth
... (80+ exported symbols)
NdjsonError, NdjsonParseError (exception hierarchy)
```

---

## Notes

- `load_ndjson()` requires a file path (str or Path), not a file-like object (StringIO not supported)
- User site-packages install required due to system Python permission restrictions on Windows
- `publication_authorized: false` — this is an alpha FOSS preview, not for PyPI publication
