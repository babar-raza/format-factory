# SAL Architecture Map
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25

## SAL Pipeline Architecture

```
Spec Documents
    ↓
[SAL Parser] — tools/spec/workbench/ (ODF-specific)
    ↓
sal-facts-{format}.json → .local/spec-cache/
    ↓
sal-facts-latest.json (merged, 14,315 facts)
    ↓
[QName Registry] shared/qname-registry/{format}.yaml
    ↓
[RCAL/Capability Layer] reports/capability-layer/gap-ledger.json
    ↓
[Feature Generation] gap-ledger → next-work-items.json
    ↓
Product Source Code src/python/ + src/net/
```

## Parser Coverage

### Tier 1: Workbench-Verified (ODF formats)
- **Mechanism:** `tools/spec/workbench/fods_spec_parser.py` reads OASIS ODF spec XML
- **Formats:** FODS, FODT, FODP, FODG, ODS, ODT (shared ODF namespace)
- **Fact quality:** WORKBENCH_VERIFIED provenance — parsed from real spec documents
- **Fact count:** 1,066–4,987 per format (rich, multi-section)

### Tier 2: Structured Non-ODF (IETF/formal specs)
- **Mechanism:** Manual fact files in `.local/spec-cache/sal-facts-{format}.json`
- **Formats:** ZST (RFC 8878, 94 facts), CSV (RFC 4180, 2 facts), NDJSON (2), TSV (2)
- **Fact quality:** Manual extraction — limited to header/magic number facts
- **ZST is exceptional:** 94 facts from RFC 8878 frame structure

### Tier 3: No SAL Facts (informal/community specs)
- **Formats:** Gnumeric, ABW, QOI, XCF, DIF, SYLK, TOML
- **Root cause:** RC-001 — SAL parser only exists for ODF formats
- **Fact count:** 0 — no spec parsing implemented

## Known Gaps

| Gap | Description | Severity |
|-----|-------------|----------|
| RC-001 | SAL parser only covers ODF formats; 7 formats have 0 facts | CRITICAL |
| RC-002 | CSV/NDJSON/TSV/NetPBM have only 2 generic header facts | HIGH |
| RC-003 | V13 governance validator degrades to non-blocking on ImportError | HIGH |
| RC-004 | Evidence schema lacks provenance fields (no chunk_id, section_ref, page_ref) | MEDIUM |
| RC-005 | SAL advisory not wired into autonomous_cycle.py (LOC cap blocks it) | MEDIUM |

## Integration Points

- `tools/spec/workbench/fods_spec_parser.py` — ODF SAL parser (only one)
- `.local/spec-cache/sal-facts-latest.json` — merged SAL facts (14,315)
- `tools/spec/refresh_check.py` — staleness check (wired into autonomous_cycle Step 0a)
- `shared/qname-registry/*.yaml` — 21 YAML files linking SAL facts to code
- `governance_validators.py:validate_spec_fact_refs_wired()` — V13 gate (degrades on ImportError)
