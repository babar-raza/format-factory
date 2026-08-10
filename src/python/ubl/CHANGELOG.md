---
visibility: generated
generated_by: codex
---

# Changelog

## 0.2.0.dev0

- Add the collision-safe `format_factory.ubl` namespace.
- Add bounded secure XML parsing and deterministic semantic serialization.
- Add the generated, authority-pinned inventory and typed root classes for all
  91 UBL 2.3 document roots.
- Preserve the existing top-level `ubl` source only as migration input; it is
  intentionally excluded from the production wheel.
- Add an official UBL 2.3 code list registry and deterministic offline code
  validation (`official_code_list_registry`, `validate_code`,
  `CodeListRegistry`, `parse_genericode`).
- Add document indexing and business-role queries (`DocumentIndex`,
  `business_role`) that work identically across all 91 supported document
  roots.
- Add opt-in digital signature presence tracking (`SignatureBackendRegistry`,
  `sign_document`, `verify_signature`) with passive preservation of signed
  content; this package tracks signature presence, it does not ship a
  cryptographic implementation.
- Vendor the official OASIS UBL 2.3 sample corpus (55 real example instance
  documents) with a round-trip manifest.
- Add CRUD editing for lines and other repeating core business components
  (`add_line`, `remove_line`, `move_line`, `renumber_lines`, `replace_party`,
  `update_component`, `add_component`, `remove_component`) with
  schema-order-preserving inserts and validation-preserving refusal.
- Add cross-field arithmetic reconciliation (`reconcile_invoice`) checking
  invoice-line-sum, tax-subtotal-sum, and allowance/charge totals against
  their declared `LegalMonetaryTotal`/`TaxTotal` values -- checks the XSD
  structurally cannot express.
- Add opt-in extension content decoding (`ExtensionAdapterRegistry`,
  `decode_extension`) for foreign-namespace `ExtensionContent` payloads,
  with an explicit unknown-adapter state rather than a guess.
- Add opt-in profile-specific validation (`ProfileValidatorRegistry`,
  `validate_profile`) keyed by `cbc:CustomizationID`, with an immutable
  registry and a `None` result that is never mistaken for a passing report.
- Add UBL 2.0-to-2.3, 2.1-to-2.3, and 2.2-to-2.3 version migration
  (`migrate_document`, `MigrationReport`) for the 31, 65, and 81 (of 91)
  document roots respectively whose older schema differs from 2.3 only by
  optional additions and cardinality widenings, gated on re-validation
  against the stable 2.3 profile before relabeling.
