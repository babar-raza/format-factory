---
artifact_id: TC-FF6-UBL-TYPING-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-PROGRAM-CAPABILITIES-001
status: WORK_IN_PROGRESS
format_id: ubl
skill_ids:
  - research-format-contract-sources
  - ingest-spec-sal
  - sal-pipeline-heal
  - create-format-family-pack
  - compile-format-contract
  - compile-production-capability-universe
  - create-taskcard
  - plan-control
---

# Compile the Complete UBL 2.3 Schema-Typed Surface

## Boundary

This is authority, schema-graph, naming, obligation, family, contract, and
capability-policy work. It prepares the exact denominator needed to generate a
production UBL library. It does not authorize product-source generation,
product tests, package mutation, certification, promotion, release, or gates.

The task is `WORK_IN_PROGRESS`, but it is not the controller-selected active
task. Native Event 27 serializes verified completion of UBL-01 and UBL-02 as a
parallel-safe checkpoint. XLIFF remains the canonical active task at
XLF-04-BATCH-005. UBL may continue only as a disjoint, separately leased lane
when coordination permits it. It must never mutate XLIFF paths or rewrite the
native event head without serialized plan-control ownership.

## Current checkpoint

Detailed substate: `PACKAGE_CENSUS_COMPLETE`.

Completed:

- `UBL-01`: all three pinned UBL authority records are current matches and all
  34 canonical UBL SAL facts verify.
- `UBL-02`: the deterministic package census contains 890 members and exactly
  91 document roots.

First unmet step: `UBL-03`.

Resume evidence:

- native event: `FF6-EVENT-000027`;
- implementation ancestors: `7b5cce4f`, `7fc49c29`;
- package/root census:
  `reports/ff6/ubl-package-root-census.yaml`;
- census SHA-256:
  `787c8d9258dc25a8662ee934b9b0b14096de790db87826dab970792b9494976d`;
- SAL receipt: `reports/sal-verification/ubl.json`;
- SAL receipt SHA-256:
  `2cc0f2cac163b7f42ab18bbe5220837d1f49a808904ac964c536085ca6d111a0`.

This checkpoint proves authority closure and the package/root denominator. It
does not prove the reachable schema graph, deterministic naming contract,
complete obligation denominator, reconciled ProductContract, product source,
certification, promotion, release, or any gate.

## Objective

Compile an exact, authority-bound UBL 2.3 schema and product-obligation
universe that is complete enough to drive deterministic generation of:

- distinct typed Python roots for all 91 UBL 2.3 maindoc schemas;
- every reachable common aggregate component, common basic component,
  unqualified data type, extension type, signature structure, attribute, and
  namespace;
- exact sequence, choice, cardinality, inheritance, restriction,
  substitution, wildcard, and QName behavior;
- typed parsing, authoring, schema-order serialization, validation,
  preservation, streaming, security, signature, and code-list hooks;
- hand-curated Invoice, CreditNote, and Order workflows without making the
  other 88 roots generic or untyped.

National invoicing rules, jurisdiction-specific profiles, and business-network
policy are explicitly separate future packages. The UBL core library must not
claim them implicitly.

## Verified starting boundary

The current compiled planning projection contains:

- one stable profile, `ubl_2.3`;
- 18 broad capabilities;
- 194 generated obligations;
- 34 canonical UBL SAL facts;
- three declared authorities, including the official UBL 2.3 prose/package
  and a separately classified product-requirement source;
- a `DRAFT` ProductContract;
- a current source package containing 91 named root subclasses.

These numbers do not prove complete typing:

- A root subclass containing only `ROOT_NAME` is a named facade, not a
  schema-derived typed document model.
- A broad capability referencing the 91-root fact does not prove that each
  root, type, element, attribute, choice, and cardinality is represented.
- A generated class count is not a schema denominator.
- XSD validity does not prove signature lifecycle, extension preservation,
  external-resource security, streaming limits, or developer workflow depth.
- Existing UBL 2.1 wording in historical rules cannot stand in for the pinned
  UBL 2.3 authority.

## Required authority

The task must use and independently revalidate:

1. `SRC-UBL-001`: official UBL 2.3 Standard prose.
2. `SRC-UBL-002`: official UBL 2.3 release package.
3. `SRC-UBL-003`: Format Factory product requirements, classified as product
   policy rather than OASIS normative authority.

All schema and example members must be inventoried from the digest-pinned
release package. No network result, installed third-party library, current
source class, or generated report may replace the pinned package.

## State machine

```text
READY
-> AUTHORITY_REVALIDATED
-> PACKAGE_CENSUS_COMPLETE
-> SCHEMA_GRAPH_COMPLETE
-> NAMING_CONTRACT_COMPLETE
-> OBLIGATION_DENOMINATOR_COMPLETE
-> CONTRACT_RECONCILED
-> VERIFIED
-> PASS
```

Each transition requires a native FF6 event or an explicitly journaled
parallel-lane checkpoint. A partial task remains `WORK_IN_PROGRESS` with the
first unmet step and exact evidence boundary.

## UBL-01 — Revalidate the predecessor and authority closure

1. Fetch GitLab `origin/main` and verify the current FF6 journal/controller.
2. Confirm UBL is a disjoint lane and no live lease owns the intended UBL
   contract, report, generator, or task paths.
3. Recompute all UBL authority package and member digests.
4. Prove clean offline reconstruction from content-addressed inputs.
5. Verify legal/redistribution classification.
6. Record exact current counts for roots, schemas, examples, code-list
   resources, signatures, and auxiliary artifacts.
7. Treat every current product class, test, and capability as
   characterization input only.

Exit evidence:

- every UBL authority record is `MATCH`;
- no undeclared authority byte was consumed;
- package inventory reproduces byte-identically;
- current source/test breadth is recorded without promotion.

## UBL-02 — Compile the complete package and root census

Produce a deterministic package inventory with:

- every package member, byte size, SHA-256, legal role, and normative status;
- exactly 91 maindoc XSD files and 91 root QNames;
- each root element, declared complex type, target namespace, schema file,
  import closure, and official examples;
- all common-library, extension, signature, datatype, and auxiliary schemas;
- duplicate, missing, ambiguous, and foreign-namespace detection;
- schema catalog/import resolution without network access.

Negative controls must prove failure on:

- 90 or 92 maindoc roots;
- duplicate root QName;
- two files claiming one root;
- root element with missing declared type;
- undeclared import or remote import;
- member digest drift;
- path traversal, duplicate ZIP member, symlink, oversize member, or
  decompression-limit violation.

The 91-root total is an authority denominator, not a completion claim for the
schema type graph.

## UBL-03 — Compile the complete reachable schema graph

Build a content-addressed graph containing every reachable:

- global element and attribute;
- complex and simple type;
- anonymous type with a stable synthesized identity;
- sequence, choice, all-group, group reference, and attribute group;
- extension and restriction edge;
- substitution group and abstract declaration;
- element/type reference;
- `minOccurs`, `maxOccurs`, nillability, default, fixed, and form rule;
- simple-content and complex-content base;
- enumeration, pattern, length, numeric, whitespace, and union/list facet;
- wildcard and `processContents` rule;
- namespace prefix policy and canonical QName;
- documentation annotation used for generated API documentation.

The graph must distinguish:

- a document root from its document complex type;
- common aggregate components from common basic components;
- UBL unqualified data types from XML Schema primitives;
- extension wildcards from semantically supported core content;
- signature structures from cryptographic verification support.

Exit evidence:

- every root reaches one declared content type;
- every reference resolves exactly once;
- every occurrence/order rule is retained;
- no schema surface is omitted because the current source lacks a model.

## UBL-04 — Lock deterministic Python naming and generation contracts

Define a checked-in naming manifest before generating product code:

- QName to canonical Python class/type/member name;
- root QName to root class and module;
- stable module partitioning for roots, common aggregate components, common
  basic components, datatypes, extensions, and signatures;
- keyword, acronym, digit, punctuation, singular/plural, and case handling;
- deterministic collision suffixes based on semantic identity rather than
  discovery order;
- anonymous-type naming from stable owner/path identity;
- public facade aliases separated from canonical generated names;
- compatibility policy for generator naming changes.

Required negative controls:

- reordered schema discovery produces identical names and bytes;
- two QNames normalizing to the same identifier fail unless the collision
  manifest resolves them;
- changing a naming rule invalidates every affected generated descendant;
- duplicate or orphan naming entries fail closed;
- no generated file exceeds architecture limits or becomes a monolithic
  all-schema mega-file.

## UBL-05 — Compile the complete obligation denominator

Build an explicit expected-ID inventory independently from current generated
classes and current broad capabilities.

Every mandatory schema item must own obligations for the applicable behavior:

- typed construction;
- typed parse;
- schema-order write;
- cardinality and choice enforcement;
- value/facet validation;
- namespace and QName correctness;
- semantic roundtrip;
- unknown extension preservation where permitted;
- positive and rejection evidence;
- documentation and public symbol ownership.

Every one of the 91 roots must have separate expected IDs for root detection,
typed construction, parse, write, validation, and installed-package exposure.
The denominator must also cover all reachable shared types and attributes.

Completion is forbidden when:

- the denominator was derived from existing source classes or test names;
- an expected ID is missing, duplicated, ambiguous, or unowned;
- a generated root is only a generic property bag;
- percentage coverage hides any mandatory missing root or type;
- schema-component presence is substituted for executed behavior.

## UBL-06 — Separate normative rules from production policies

OASIS schema/prose requirements and library product policies must have distinct
authority classes and conformance effects.

Production-policy obligations include:

- deterministic canonical serialization;
- secure XML parsing with DTD/entity/network resolution disabled by default;
- configurable byte, depth, element, attribute, text, binary, and diagnostic
  limits;
- bounded streaming parsing and writing;
- code-list provider hooks and offline cache policy;
- extension preservation and typed extension adapters;
- signature invalidation whenever signed content changes;
- optional cryptographic verification/signing adapters;
- safe external-document and attachment resolution;
- resource-limit diagnostics and fail-closed behavior;
- hand-curated builders/workflows for Invoice, CreditNote, and Order.

These may be release-mandatory without being misreported as OASIS normative
conformance rules.

## UBL-07 — Reconcile SAL, family, contract, and capability ownership

1. Replace broad or mixed-authority facts with exact stable facts.
2. Give every live UBL fact one canonical owner.
3. Split broad capabilities when roots/types have different proof strategies.
4. Recompile the XML-business family pack with explicit-complete ownership.
5. Assign `ubl_2.3` to every stable capability and obligation.
6. Keep national profiles outside the stable UBL-core projection.
7. Preserve optional cryptography and ecosystem dependencies in adapters.
8. Regenerate all six-format projections without altering other format
   semantics.

## UBL-08 — Verify and checkpoint

Required verification:

- exact package and 91-root census;
- complete schema-graph integrity;
- independent expected-ID denominator;
- zero missing, duplicate, dangling, ambiguous, or foreign-format edges;
- deterministic naming and collision tests;
- three byte-identical clean graph, naming, contract, and capability runs;
- strict ProductContract compilation;
- all UBL authorities still `MATCH`;
- focused and affected pytest;
- Ruff, Pyright 1.1.411, and strict Mypy for touched typed machinery;
- negative controls for malformed schemas, imports, QNames, order,
  cardinality, wildcards, signatures, and product-policy authority;
- no product-source, package, certification, promotion, release, or gate
  mutation.

Checkpoint through the native FF6 journal, controller projections, task index,
current gaps, and provider-neutral handover. Push only to GitLab `main` and
verify the remote.

## Acceptance criteria

- The official UBL 2.3 package is independently digest-verified and clean
  offline reconstructible.
- Exactly 91 maindoc roots have unique, authority-located QNames and declared
  content types.
- Every reachable schema item and semantic edge is present in the canonical
  schema graph.
- Naming and collision behavior is deterministic and checked in.
- The expected obligation denominator is independent of current source and
  enumerates every mandatory root/type behavior.
- Every root is required to become genuinely typed; hollow subclasses and a
  generic property bag cannot satisfy completion.
- OASIS conformance and production-library policy are separately classified.
- Signature structures are typed; cryptographic behavior remains optional and
  explicit.
- Invoice, CreditNote, and Order receive curated developer workflows without
  reducing the other 88 roots to generic XML.
- National/jurisdictional profiles remain explicit future packages.
- Three identical compilations and all focused/affected/static gates pass.
- No product implementation or certification is claimed by this task.

## Expected successor

After this task and the parent capability universe pass, create a separate
obligation-driven UBL generator/product-source task. That successor must
generate checked-in reproducible Python source, then prove all 91 roots through
built-wheel tests, official examples, generated schema-valid minimal
instances, and an independent schema engine.

## Truth boundary

`PASS` on this task proves a complete, deterministic work denominator and
generation contract. It does not prove that the existing UBL package is
production-ready. Production readiness still requires generated source,
installed-package behavior, independent interoperability, security,
performance, documentation, reproducible packages, SBOM, provenance,
signatures, repository extraction, and technical certification.
