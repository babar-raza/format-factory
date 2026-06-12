# Six-Product Selection — Mainstream Mega-Train
# Date: 2026-06-10

## Selection Criteria Applied
1. Must have BOTH Python and .NET tracks (existing or creatable this sprint)
2. Highest existing test coverage and maturity preferred
3. Dual-ecosystem formats (already have .NET project) score highest
4. Must have spec authority basis
5. Must have samples

## Primary 6 Products Selected

### 1. FODS (Flat OpenDocument Spreadsheet)
- Python: 211 tests, production_track_real, read+model, no write
- .NET: 547 tests, full parser+writer+exporters (CSV/HTML/JSON), roundtrip
- Authority: ODF 1.3, OASIS RF, P6
- Selection reason: Highest combined maturity. Needs Python write/export deepening.

### 2. FODT (Flat OpenDocument Text)
- Python: 248 tests, production_track_real, read+model, no write
- .NET: 520 tests, full parser+writer+exporters (HTML/TXT/Markdown), roundtrip
- Authority: ODF 1.3, OASIS RF, P6
- Selection reason: Second highest maturity. Needs Python write/export deepening.

### 3. CSV (Comma-Separated Values)
- Python: 19 tests, read_only_prototype, RFC 4180 parser
- .NET: 15 tests, writer exists
- Authority: RFC 4180, P3
- Selection reason: Universal format. Both tracks exist but need deepening.

### 4. Netpbm Group (PBM/PGM/PPM)
- Python: 144 tests combined, read_only_prototype (all three)
- .NET: 465 tests, parser+writer+exporter, full image pipeline
- Authority: Netpbm spec, P4
- Selection reason: Strong .NET track. Python needs write capability.

### 5. NDJSON (Newline-Delimited JSON)
- Python: 233 tests, roundtrip_capable_library, full read/write/export/roundtrip
- .NET: Does not exist yet — must create
- Authority: ndjson.org informal spec, P0
- Selection reason: Python is most complete. .NET creation is straightforward.

### 6. TSV (Tab-Separated Values)
- Python: 19 tests, read_only_prototype
- .NET: Does not exist yet — must create
- Authority: IANA registration, P0
- Selection reason: Simple format, parallel to CSV. Both tracks achievable.

## Backup Products

### 7. HTML (backup)
- .NET: 12 tests, writer exists
- Python: not tracked in completion matrix
- Reason: .NET exists; Python may need creation

### 8. ZST (backup)
- Python: 62 tests, production_track_real, full codec
- .NET: does not exist
- Reason: Strong Python; .NET creation possible but compression library needed

## Products NOT Selected (with reasons)
- FODG/FODP: probe_only, high overclaim risk, insufficient depth
- ABW/Gnumeric: probe_only per matrix, deep rebuilds needed
- DIF/SYLK: read_only, no .NET, limited commercial value
- ODS/ODT: no .NET, ZIP complexity
- QOI: no .NET, niche image format
- XCF: probe_only, no pixel decode
- TOML: no .NET, Python stdlib overlap
