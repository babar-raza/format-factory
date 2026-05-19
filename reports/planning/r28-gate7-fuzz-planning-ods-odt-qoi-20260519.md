# Gate 7 Security/Fuzz Planning — ODS/ODT/QOI
# Sprint: FORMAT-FACTORY-R28-GATE5-GATE7-ORACLE-FUZZ-XCF-ZPAQ-G11-C9-PUBLICATION-HARDENING-001
# Date: 2026-05-19

## Strategy: Deterministic Malformed Input Guards

All fuzz tests are deterministic — no randomized fuzzing, no heavy fuzzing framework.
Each test creates a specific malformed input and verifies the parser rejects it safely.

## ODS Fuzz Guards (7 tests)
- Not-a-ZIP file
- Empty file
- ZIP bomb (>1000 entries)
- Malformed XML in content.xml
- Binary garbage in content.xml
- Dict API never-raises guarantee
- Extremely nested XML (100 levels)

## ODT Fuzz Guards (7 tests)
- Not-a-ZIP file
- Empty file
- ZIP bomb (>1000 entries)
- Malformed XML in content.xml
- Binary garbage in content.xml
- Dict API never-raises guarantee
- Extremely nested XML (100 levels)

## QOI Fuzz Guards (9 tests)
- Empty file
- Random bytes (seed=42, deterministic)
- Wrong magic bytes
- Truncated header
- Huge dimensions (99999x99999)
- Truncated pixel data
- Dict API never-raises guarantee
- All-zeros file
- Missing end marker

## Results
- Total: 23/23 PASS
- No heavy fuzzing — all tests are fast, deterministic
- No Gate 7 overclaim — initial fuzz guards only
