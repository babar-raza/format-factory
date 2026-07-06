# PyPI Name Availability Report

**Source task:** TC-H2-001 (FF-XPLAN-001 healed plan)
**Generated:** 2026-07-06
**Method:** HTTP GET to `https://pypi.org/pypi/{package}/json` — 404 = AVAILABLE, 200 = TAKEN

## Summary

- **Preferred naming convention:** `format-factory-{format}-python`
- **All 24 preferred names:** AVAILABLE (no conflicts)
- **Bare names (just `{format}`):** 15 TAKEN by other packages — do NOT use bare names

## Results Table

| Format | Preferred Name (`format-factory-{fmt}-python`) | Status | Bare Name (`{fmt}`) | Bare Status | Recommendation |
|--------|-----------------------------------------------|--------|---------------------|-------------|----------------|
| fods | format-factory-fods-python | AVAILABLE | fods | AVAILABLE | Use preferred |
| fodt | format-factory-fodt-python | AVAILABLE | fodt | AVAILABLE | Use preferred |
| zst | format-factory-zst-python | AVAILABLE | zst | TAKEN | Use preferred |
| fodp | format-factory-fodp-python | AVAILABLE | fodp | AVAILABLE | Use preferred |
| fodg | format-factory-fodg-python | AVAILABLE | fodg | AVAILABLE | Use preferred |
| gnumeric | format-factory-gnumeric-python | AVAILABLE | gnumeric | AVAILABLE | Use preferred |
| abw | format-factory-abw-python | AVAILABLE | abw | AVAILABLE | Use preferred |
| ora | format-factory-ora-python | AVAILABLE | ora | TAKEN | Use preferred |
| ods | format-factory-ods-python | AVAILABLE | ods | TAKEN | Use preferred |
| odt | format-factory-odt-python | AVAILABLE | odt | AVAILABLE | Use preferred |
| qoi | format-factory-qoi-python | AVAILABLE | qoi | TAKEN | Use preferred |
| xcf | format-factory-xcf-python | AVAILABLE | xcf | AVAILABLE | Use preferred |
| zpaq | format-factory-zpaq-python | AVAILABLE | zpaq | TAKEN | Use preferred |
| dif | format-factory-dif-python | AVAILABLE | dif | TAKEN | Use preferred |
| ppm | format-factory-ppm-python | AVAILABLE | ppm | TAKEN | Use preferred |
| pgm | format-factory-pgm-python | AVAILABLE | pgm | TAKEN | Use preferred |
| pbm | format-factory-pbm-python | AVAILABLE | pbm | TAKEN | Use preferred |
| sylk | format-factory-sylk-python | AVAILABLE | sylk | TAKEN | Use preferred |
| csv | format-factory-csv-python | AVAILABLE | csv | TAKEN | Use preferred |
| tsv | format-factory-tsv-python | AVAILABLE | tsv | TAKEN | Use preferred |
| xpm | format-factory-xpm-python | AVAILABLE | xpm | TAKEN | Use preferred |
| pam | format-factory-pam-python | AVAILABLE | pam | TAKEN | Use preferred |
| ndjson | format-factory-ndjson-python | AVAILABLE | ndjson | TAKEN | Use preferred |
| toml | format-factory-toml-python | AVAILABLE | toml | TAKEN | Use preferred |

## Conclusion

The `format-factory-{format}-python` naming pattern is clear for all 24 formats checked. This pattern should be used as the canonical PyPI package name for all Format Factory Python packages.

Bare names like `csv`, `toml`, `tsv`, `ods`, `zst`, etc. are taken by other ecosystem packages and must NOT be used.
