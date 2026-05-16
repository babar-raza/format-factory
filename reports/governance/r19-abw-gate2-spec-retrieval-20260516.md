# R19 ABW Gate 2 Spec Retrieval
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 12 (R19) — ABW Gate 2 Spec Retrieval

## Retrieval Summary

| Item | Status |
|------|--------|
| AWML 1.0 DTD at abisource.com | FAILED (ECONNREFUSED) |
| Public identifier documented | YES |
| Spec understanding from secondary | ADEQUATE |
| Legal analysis | COMPLETE (Category 2, minor gap) |

## Spec Retrieval Attempt

**Attempted URL:** http://www.abisource.com/awml.dtd
**Public identifier:** `-//ABISOURCE//DTD AWML 1.0 Strict//EN`
**Result:** Connection refused — abisource.com appears to be offline as of 2026-05-16

## Spec Understanding from Secondary Sources

Secondary sources consulted:
1. MobileRead Wiki — ABW format technical details (RETRIEVED)
2. AbiWord GitHub repository — source code reference (ACCESSIBLE)
3. XML Matters article on AWML format (RETRIEVED)

### Key Format Structure Documented

**Root element:** `<abiword>` with `version="1.0"` and `fileformat="1.0"`
**Namespaces:** fo (XSL-FO), math (MathML), svg, dc (Dublin Core), xlink
**Key elements:** section, p, c, image, table, cell, styles, metadata, pagesize
**Props pattern:** CSS-style `props` attribute for formatting
**Image encoding:** Base64 inline

### File Variants

- `.abw` — plain XML
- `.abw.gz` / `.zabw` — gzip-compressed XML (magic: 1F 8B 08...)

## Legal Analysis

- Application license: GPL-2.0 (AbiWord)
- Format license: None (AWML XML is open)
- Legal category: 2 (same as Gnumeric)
- Legal gap: Minor — DTD not cached due to server down; format open
- Classification: MINOR gap, no blocker

## Gate 2 Decision

Status: **PASSED_WITH_NOTES**
Method: Secondary source documentation (primary DTD unreachable)
Approved by: delegated_agent_execution_under_r19_prompt

Note: `passed_with_notes` is appropriate because:
1. The format structure is well-understood from secondary sources
2. AbiWord source code provides authoritative implementation reference
3. The AWML DTD itself is acknowledged to be "out-of-date" even when available
4. Gate 4 prototype can proceed using AbiWord source + secondary docs

## Registry Updates

- abw.gates.gate_2.status: not_started → passed_with_notes

GATE_12_R19_ABW_GATE2: PASSED_WITH_NOTES
