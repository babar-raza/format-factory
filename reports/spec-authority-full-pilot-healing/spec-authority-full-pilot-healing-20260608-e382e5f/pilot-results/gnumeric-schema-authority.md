# Gnumeric Schema Authority — TCA-FULL-011

## Schema Existence Check

- Source type: `xsd_schema` (gnumeric.xsd)
- Retrieval status: `RETRIEVED_VIA_WEBFETCH` (schema metadata retrieved; full XSD not stored locally)
- Namespace: `http://www.gnumeric.org/v10.dtd`
- Root element: `Workbook`
- Full XSD locally cached: **NO** (local_cache_note: "Key schema metadata cached in this spec-index; full XSD not stored locally due to file size")
- Verified facts file: **DOES NOT EXIST** — no verified-facts-review.yaml for Gnumeric

## Classification: schema_authority_available (CORRECT)

Gnumeric has an XSD schema as its primary authority source.
- bypass-ledger: `exception_classification: schema_authority_available` ✓
- This is stronger than `no_public_spec_available` (correct upgrade path applied in repair sprint)

## Is Gnumeric Product-Ready via Schema Authority Alone?

**NO.** Schema authority classification means:
1. Product source work may proceed with `exception_classification: schema_authority_available`
2. This records authority debt (debt-like grade impact for debt-only exceptions)
3. But: schema_authority_available is NOT in DEBT_ONLY_EXCEPTIONS in validate_spec_fact_refs.py
4. schema_authority_available IS in READINESS_ALLOWED_EXCEPTIONS

→ Current code: `schema_authority_available` on READINESS is ACCEPTED (grade_impact: none)
→ This is a GOVERNANCE RISK: schema_authority_available allows readiness without verified facts

## Pilot Declaration Test

A PRODUCT_SOURCE with `exception_classification: schema_authority_available` → ACCEPTED
A READINESS with `exception_classification: schema_authority_available` → ACCEPTED (per READINESS_ALLOWED_EXCEPTIONS)

This means Gnumeric could claim readiness with schema authority alone.
This is a governance debt to document — not a hard block since the XSD provides real schema authority.

## Proof Level Classification

| Component | Present? |
|-----------|----------|
| Schema specification (XSD) | ✓ (retrieved via WebFetch, metadata in spec-index.yaml) |
| Full XSD stored locally | ✗ (size constraint, metadata only) |
| Verified facts file | ✗ (does not exist) |
| Any verified spec fact | ✗ |
| Code/test citations | ✗ |

**Proof Level: P1** — schema exists but not fully cached; no verified facts; no test citations.

## Honest Assessment

Gnumeric is NOT product-ready from schema authority alone.
The `schema_authority_available` exception permits investigation and backfill work but
should not be treated as equivalent to verified spec facts for product readiness claims.
