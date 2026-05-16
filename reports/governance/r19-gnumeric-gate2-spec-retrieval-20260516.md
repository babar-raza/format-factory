# R19 Gnumeric Gate 2 Spec Retrieval
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 11 (R19) — Gnumeric Gate 2 Spec Retrieval

## Retrieval Summary

| Item | Status |
|------|--------|
| XSD schema at GNOME GitLab | RETRIEVED |
| Namespace identified | http://www.gnumeric.org/v10.dtd |
| Root element | Workbook |
| Key elements documented | YES |
| Legal analysis | COMPLETE (Category 2, minor gap) |

## Spec Retrieved

**Source:** https://gitlab.gnome.org/GNOME/gnumeric/-/raw/master/gnumeric.xsd
**Type:** XML Schema Definition (XSD)
**Version:** v10 (for Gnumeric 1.2.2+, last updated 1.12.21, Feb 2015)

### Key Schema Facts

Namespace: `http://www.gnumeric.org/v10.dtd`
Root element: `<Workbook>`
Major sub-elements: Version, Sheets/Sheet, Cells, Styles/StyleRegion, PrintInformation, Objects
Cell value types: empty, boolean, integer, float, error, string, cellrange, array

### File Format Technical Facts

- File encoding: gzip-compressed XML
- MIME type: application/x-gnumeric
- Extensions: .gnumeric, .gnm
- XML prefix: `gnm:` (Gnumeric namespace)

## Legal Analysis

- Application license: GPL-2.0
- Format license: None (open XML — no restriction on parsing)
- Legal category: 2 (permissive OSS, minor gap)
- Legal gap: GPL application license; no formal spec body
- Classification: MINOR gap, no blocker

## Gate 2 Decision

Status: **PASSED**
Method: Agent retrieval via WebFetch (R19 internet authorization)
Approved by: delegated_agent_execution_under_r19_prompt

## Registry Updates

- gnumeric.gates.gate_2.status: not_started → passed

GATE_11_R19_GNUMERIC_GATE2: PASSED
