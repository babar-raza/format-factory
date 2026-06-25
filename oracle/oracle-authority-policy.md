# Oracle Authority Policy — Format Factory

**Document type:** Governing Policy
**Mission:** FORMAT-FACTORY-ORACLE-LAYER-HARDENING-001
**Created:** 2026-06-25
**Authority:** Format Factory project lead (Babar Raza)

---

## 1. Non-Negotiable Oracle Principles

Every oracle case expected value must be classified with an authority class.
Every oracle authority class must map to a specification, an authorized fact, a
product contract, or explicitly classified empirical evidence.

### 1.1 Authority Classification Scale

| Class | Description | Can Produce PASS? |
|---|---|---|
| `SPEC_NORMATIVE` | Derived from spec normative text (RFC/OASIS/ISO) | YES |
| `SPEC_INFORMATIVE` | Derived from spec informative text | YES |
| `SCHEMA_DERIVED` | Derived from spec schema/grammar | YES |
| `AUTHORITATIVE_REFERENCE_VECTOR` | Authoritative reference corpus (e.g. facebook/zstd golden) | YES |
| `VERIFIED_INTEROPERABILITY` | Cross-tool verified (e.g. LibreOffice + FODS prototype) | YES |
| `ACCEPTED_EMPIRICAL` | Empirical — documented, justified, not contradicted by spec | YES (with declaration) |
| `GENERATED_FROM_NEUTRAL_MODEL` | Generated from Gate 5 neutral model — reviewed | YES (with review) |
| `PRODUCT_CONTRACT` | Explicit product API contract | YES |
| `AI_DRAFT_UNVERIFIED` | AI-generated, not reviewed | **NO — BLOCKED** |
| `IMPLEMENTATION_OBSERVED` | Observed from current implementation (circular) | **NO — BLOCKED** |
| `REJECTED` | Explicitly rejected | **NO — BLOCKED** |
| `UNKNOWN` | No authority established | **NO — BLOCKED** |

### 1.2 Self-Approval Prohibition

A product implementation **may not** use its own output to derive oracle expectations.

| Prohibited Pattern | Why |
|---|---|
| Run parser → capture output → call it the expected result | `IMPLEMENTATION_OBSERVED` — circular |
| Generate file with writer → call it a valid golden file | Self-approval without independent validation |
| Use AI to invent expected bytes | `AI_DRAFT_UNVERIFIED` |
| Update golden file automatically after test failure | Snapshot approval without authority review |

---

## 2. Valid Authority Derivation Paths

Acceptable paths for establishing oracle expectations:

1. **RFC / OASIS / ISO normative text** → `SPEC_NORMATIVE`
2. **Spec schema/grammar derivation** → `SCHEMA_DERIVED`
3. **Independent reference implementation** (LibreOffice, pyzstd, etc.) → `VERIFIED_INTEROPERABILITY`
4. **Authoritative reference corpus** (facebook/zstd golden, IETF test vectors) → `AUTHORITATIVE_REFERENCE_VECTOR`
5. **Manually constructed and independently reviewed** → `GENERATED_FROM_NEUTRAL_MODEL`
6. **Documented empirical behavior, not contradicted by spec** → `ACCEPTED_EMPIRICAL`
7. **Explicit public API contract** → `PRODUCT_CONTRACT`

---

## 3. Oracle Case Requirements

Every oracle case must:

1. Have a unique `case_id` (format: `{format_id}-{type}-{NNN}`)
2. Declare `authority_class` (one of the 12 classes above)
3. Provide at least one `authority_refs` entry (spec section, fact ref, or corpus ref)
4. Declare `applicable_profiles` (at least one)
5. For valid cases: declare `expected_model_properties` with at least one property
6. For invalid cases: declare `expected_failure_stage`

---

## 4. Roundtrip Equality Rules

| Equality Mode | Condition | Permitted Tolerance |
|---|---|---|
| `BYTE_IDENTICAL` | Lossless formats (ZST, PBM/PGM/PPM decompressed) | None |
| `STRUCTURALLY_EQUIVALENT` | Same logical structure, possibly different bytes | XML whitespace, namespace prefixes |
| `SEMANTICALLY_EQUIVALENT` | Same data, may differ in representation | Declared in tolerance_policy |
| `EQUIVALENT_WITH_ALLOWED_NORMALIZATION` | Known normalization applied | Explicitly declared fields |
| `INTENTIONALLY_LOSSY_WITH_DECLARED_LOSS` | Lossy export | All lost fields declared |

---

## 5. Stale Oracle Detection Rules

An oracle package becomes **STALE** when any of these change:

- Specification version changes (e.g., ODF 1.3 → ODF 2.0)
- SAL authorized fact set changes (new facts added for format)
- Corpus sample hash changes (file modified)
- Comparator implementation changes
- Tolerance policy changes
- Product API changes (method renamed, behavior changed)
- Package version bump with behavior change

Stale oracles must be regenerated before they can produce `PASS` verdicts.

---

## 6. Product Advancement Gates

| Gate | Oracle Requirement |
|---|---|
| Gate 4 (Prototype Parser) | No oracle requirement |
| Gate 5 (Neutral Model) | OBLIGATION_CREATED in registry |
| Gate 6 (Acquisition Oracle) | Acquisition oracle (LibreOffice/reference) PASS for ODF formats |
| Gate 7 (Fuzz) | INVALID_INPUT_REJECTION cases defined |
| Gate 8 (Security) | SECURITY_ROBUSTNESS cases defined and passing |
| Gate 9 (Product Mapping) | DOMAIN_MODEL_MAPPING cases defined |
| Gate 10 (OSS Release) | CASES_DEFINED status, PARSE_VALIDITY passing |
| Gate 11 (Commercial) | VERIFIED status, PACKAGE_CONSUMER passing |

---

## 7. Governance Integration

The oracle obligation validator (`tools/oracle/validate_oracle_obligations.py`) must:
- Pass (exit 0) for all registered formats before Gate 10 advancement
- Be run as part of sprint closeout when new formats are registered
- Be run when oracle packages are modified

The onboarding gate check (`--check-new-format {format_id}`) must PASS before any
product source may be committed for a new format.

---

## 8. Prohibited Oracle Patterns

These patterns are explicitly prohibited:

1. **Test-only expectations**: expected values defined only in test code (no oracle package)
2. **Implicit tolerance**: comparison without declared tolerance policy
3. **Auto-snapshot refresh**: test runner updating expected output on failure
4. **Format-counting coverage**: passing = "N tests ran" (not "N oracle cases passed")
5. **Empty validation**: `assert result is not None` without property checks
6. **Circular golden files**: product generates → commits → approves
7. **Unbounded numeric tolerance**: `abs(a - b) < 1000` without spec justification
