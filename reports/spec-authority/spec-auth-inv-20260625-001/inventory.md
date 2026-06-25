# SAL Investigation Inventory
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25
**Investigator:** autonomous_cycle (woolly-yawning-stream)

## SAL Fact Inventory by Format

| Format | Spec Body | Spec Version | Fact Count | Real Facts? |
|--------|-----------|--------------|-----------|-------------|
| fods | OASIS | ODF 1.3 | 4987 | YES |
| fodt | OASIS | ODF 1.3 | 4933 | YES |
| zst | IETF | RFC 8878 | 94 | YES |
| fodp | OASIS | ODF 1.3 | 1066 | YES |
| fodg | OASIS | ODF 1.3 | 1066 | YES |
| ods | OASIS ODF TC | ODF 1.3 (ISO/IEC 26300-3:2021) | 1066 | YES |
| odt | OASIS ODF TC | ODF 1.3 (ISO/IEC 26300-3:2021) | 1066 | YES |
| csv | IETF | RFC 4180 | 2 | PARTIAL |
| ndjson | Community | NDJSON spec (informal) | 2 | PARTIAL |
| pbm | Portable Bitmap | Netpbm 1.0 | 2 | PARTIAL |
| pgm | Portable Graymap | Netpbm 1.0 | 2 | PARTIAL |
| ppm | Portable Pixmap | Netpbm 1.0 | 2 | PARTIAL |
| tsv | IANA/informal | IANA text/tab-separated-values | 2 | PARTIAL |
| gnumeric | GNOME Project | Gnumeric XML | 0 | NO |
| abw | AbiSource | AWML 1.0 | 0 | NO |
| qoi | phoboslab | QOI 1.0 | 0 | NO |
| xcf | GIMP | XCF v011 | 0 | NO |
| dif | VisiCalc | DIF 1.0 (informal) | 0 | NO |
| sylk | Microsoft | SYLK (symbolic link) | 0 | NO |
| toml | Tom Preston-Werner | TOML v1.0 | 0 | NO |

## Summary

- **Total facts in system:** 14,315
- **Formats with rich facts (>3):** 7 (all ODF/IETF structured formats)
- **Formats with partial facts (2-3):** 6 (NetPBM, CSV, NDJSON, TSV)
- **Formats with no facts (0):** 7 (Gnumeric, ABW, QOI, XCF, DIF, SYLK, TOML)
- **SAL parser coverage:** ODF formats (FODS/FODT/FODP/FODG/ODS/ODT) have workbench-verified facts. Non-ODF formats rely on manual stubs only.
