# FODS Oracle Provider Options

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 6
**Created:** run037 (2026-05-07)
**Status:** LibreOffice is the sole approved provider. See below for alternatives considered.

---

## 1. Summary

FODS Gate 6 requires an oracle provider capable of authoritatively reading and
exporting FODS files for comparison against our parser output. This document
evaluates all candidate providers and explains why LibreOffice was selected as
the sole approved provider.

---

## 2. Provider Evaluation

### 2.1 LibreOffice (APPROVED)

| Property | Value |
|---|---|
| Type | Desktop application |
| License | MPL-2.0 (open source) |
| Format support | FODS native (ODF is its primary format) |
| Headless mode | YES — `--headless --convert-to` |
| Version available | 7.0+ (24.2 recommended) |
| Platform | Windows, Linux, macOS |
| Authoritative for ODF | YES — LibreOffice co-developed ODF with OASIS |
| Installation | libreoffice.org (free, no account required) |
| Acquisition pack | acquisition-packs/fods/oracle-installation-checklist.md |
| Status | **APPROVED** |

**Rationale:** LibreOffice is the reference implementation for ODF formats. It was
co-developed by the same organization (Document Foundation) that maintains the
ODF specification. Its FODS export is the most faithful available outside of a
specification-conformant test suite. No other provider meets this standard.

### 2.2 Apache OpenOffice (REJECTED)

| Property | Value |
|---|---|
| License | Apache 2.0 |
| Headless mode | YES |
| Last release | 4.1.15 (2023) — minimal maintenance since 2014 |
| Status | **REJECTED** |

**Reason rejected:** Apache OpenOffice forked from LibreOffice in 2011 and has
received minimal ODF compatibility updates since. Its FODS support is behind
LibreOffice's. Using it would reduce oracle fidelity relative to the current ODF 1.3
specification. LibreOffice is strictly preferred.

### 2.3 Microsoft Excel via COM Automation (REJECTED)

| Property | Value |
|---|---|
| License | Commercial |
| Platform | Windows only |
| ODF support | Partial — known issues with ODF flat-XML format |
| Headless mode | Possible via COM; not reliable |
| Status | **REJECTED** |

**Reason rejected:** Microsoft Excel's ODF implementation is not conformant with
ODF 1.3 for all features. Using it as an oracle for FODS would produce comparison
results that reflect Microsoft's interpretation, not the specification's. Additionally,
Excel is a commercial dependency that would not be appropriate for an open-source
pipeline. Commercial dependency is also gated by DEC-010/DEC-013.

### 2.4 Python odfpy (REJECTED FOR ORACLE ROLE)

| Property | Value |
|---|---|
| License | Apache 2.0 |
| Platform | Cross-platform |
| Role | Useful for reading ODF structure; not suitable as oracle |
| Status | **REJECTED for oracle role** |

**Reason rejected as oracle:** odfpy is a Python library for reading and writing
ODF files. It does not perform format conversion and does not model the full ODF
semantic interpretation. It is potentially useful as a secondary verification tool
(checking that our parser produces structurally valid ODF output) but cannot replace
LibreOffice as the authoritative conversion oracle.

### 2.5 Calligra Suite (DEFERRED)

| Property | Value |
|---|---|
| License | LGPL/GPL |
| Platform | Linux primary |
| ODF support | High (KDE-based, uses odf format natively) |
| Headless mode | Limited |
| Status | **DEFERRED** |

**Reason deferred:** Calligra Suite supports ODF natively but has limited headless
conversion capability. It could be added as a secondary oracle for cross-validation
in future runs if LibreOffice results are disputed. Adding it now is not required.
See `tools/oracle/provider_registry.yaml` for how to add it when needed.

---

## 3. Decision

**LibreOffice is the sole approved oracle provider for FODS Gate 6.**

This is recorded in `tools/oracle/provider_registry.yaml` under
`format_provider_assignments.fods.approved_providers: [libreoffice]`.

No other provider may be used for FODS Gate 6 oracle comparison without:
1. A new entry in the provider registry with `status: approved`.
2. An updated format assignment in the registry.
3. A gate documentation update in `docs/gates.md`.
4. A master plan decision record (DEC-XXX).

---

## 4. Current Blocker

LibreOffice is not installed on the development machine. This is confirmed by three
consecutive oracle preflight runs (run035, run036, run037) all returning:

```
ORACLE_PREFLIGHT: FAIL
Reasons:
  LibreOffice (soffice) not found
```

See `acquisition-packs/fods/oracle-installation-checklist.md` for installation steps.
See `acquisition-packs/fods/gate6-oracle-blocker-report.md` for full diagnostic evidence.

---

## 5. References

- `tools/oracle/provider_registry.yaml` — canonical provider registry
- `docs/ai/oracle-provider-strategy.md` — oracle provider architecture
- `acquisition-packs/fods/oracle-installation-checklist.md` — installation guide
- `acquisition-packs/fods/gate6-oracle-blocker-report.md` — diagnostic evidence
- `taskcards/TC-0026-fods-gate6-oracle-execution.md` — execution taskcard (blocked)
