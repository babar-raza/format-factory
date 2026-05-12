# ODF-Flat Family Reuse Policy
**Sprint:** POST-FODT-GATE10-CONTROLLED-SWARM-001 (Lane C / S-F2F-05)
**Date:** 2026-05-11

---

## 1. Purpose

This document governs how acquisition knowledge can be reused across the ODF flat format family (FODS, FODT, FODP, FODG, FODB).

---

## 2. Absolute Prohibition: No Inherited Gate Approval

**inherited_gate_approval: false**

Gate approval for one format does NOT transfer to any other format. This applies unconditionally:

- FODS Gate 1 PASSED does NOT mean FODT Gate 1 is passed.
- FODS Gates 1-10 PASSED does NOT mean any gate is passed for FODP, FODG, or FODB.
- FODT Gates 1-10 PASSED does NOT mean any gate is passed for FODS, FODP, FODG, or FODB.

Every format must pass every gate independently with:
- DEC-034 independent verification
- Human approval prompt naming the specific format and gate

---

## 3. What Reuse Means

Reuse means one of:
- **reuse_level: guide** — Another format's operation record is a reference point; the new format still creates its own artifacts from scratch.
- **reuse_level: partial** — Some operation artifacts (e.g., tool code, schema structure) can be adapted; the core work is per-format.
- **reuse_level: full** — The artifact is literally shared (e.g., a single ODF 1.3 spec serves all formats); but the acquisition record is still per-format.
- **reuse_level: none** — No reuse applicable; format is entirely independent for this operation.

Reuse never reduces the gate evidence requirement. A full-reuse spec acquisition still requires per-format spec evidence, DEC-034 verification, and gate approval.

---

## 4. Shared Foundation

The following are genuinely shared across all ODF flat formats:

| Item | Shared How | Reuse Level |
|---|---|---|
| ODF 1.3 Part 3 specification | Single spec file serves all formats | full |
| Legal basis (OASIS RF + ISO 26300) | Same patent policy applies | full |
| XML container format (flat, not zipped) | All are single XML files | full |
| soffice.com oracle tool | Same LibreOffice installation | full |
| iterparse streaming parser pattern | Pattern reused; per-format namespaces differ | partial |
| Error hierarchy (FodXError base class) | Naming pattern shared; per-format class names | partial |
| Fuzz categories (4 categories, 18 inputs) | Framework shared; per-format element targets | partial |
| Security threat model (8 categories) | Framework shared; per-format mitigations | partial |
| Tier map framework (T0-T4, first_oss=[0,1,2]) | Framework shared; per-format feature assignment | guide |

---

## 5. Per-Format Differences

| Item | FODS | FODT | FODP | FODG | FODB |
|---|---|---|---|---|---|
| Root content element | office:spreadsheet | office:text | office:presentation | office:drawing | office:database |
| Content namespace | table: | text: | draw: | draw: | db: |
| Neutral model entities | 6 (Row/Cell/etc.) | 7 (Block/List/etc.) | TBD | TBD | TBD |
| IR count | IR-FODS-001..020 | IR-FODT-001..015 | TBD | TBD | TBD |
| Oracle warn type | multi-sheet CSV | word-count tolerance | TBD | TBD | TBD |

---

## 6. Candidate-Only Formats

FODP, FODG, FODB are candidates only. They have not entered the acquisition pipeline. No gate has been started for them.

Per-format playbook.yaml files for FODP, FODG, FODB must NOT be created until:
1. A candidate evaluation sprint is authorized
2. A Gate 1 scoring sprint is explicitly authorized with human prompt naming the format

---

## 7. Per-Format Playbook Authorization

Creating a per-format playbook.yaml file (e.g., acquisition-packs/fods/playbook.yaml) requires:
- Separate human authorization prompt naming the format
- That format must have at least Gate 1 passed
- A dedicated sprint (not part of this family playbook sprint)

This family playbook does NOT authorize creation of per-format playbooks.

---

## 8. Independent DEC-034 Required Everywhere

Even for full-reuse operations (shared spec, shared oracle), DEC-034 independent verification is required for each format at each gate. Sharing an artifact does not share the verification work.
