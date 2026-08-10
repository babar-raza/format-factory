# Independent Python Format Library Extraction Standard

**Version:** 1.0  
**Purpose:** Common engineering contract for extracting any format-specific Python implementation from a larger monorepo into a standalone professional library.

---

## 1. Scope

This standard applies whenever a format-specific implementation is moved from a shared repository into its own independently reusable Python library.

It governs:

- repository structure;
- migration sequence;
- donor parity;
- dependency removal;
- public API design;
- source organization;
- error/diagnostic conventions;
- testing;
- security;
- interoperability;
- packaging;
- documentation;
- CI;
- Git discipline;
- autonomous agent execution;
- release-readiness evidence.

Format-specific behavior may differ. Engineering conventions should not.

---

## 2. Non-Negotiable Product Outcome

Every extracted library must be:

- independently versioned;
- independently buildable;
- independently installable;
- independently testable;
- independently documented;
- independently releasable;
- independently maintainable;
- free of sibling-format imports;
- free of donor-framework runtime dependencies;
- usable without the donor monorepo on `PYTHONPATH`;
- suitable for internal reuse and future public publication.

A library is not standalone merely because it has a new package name.

---

## 3. Canonical Repository Identity

Each library must define one canonical set of identifiers:

- repository name;
- distribution name;
- Python import namespace;
- central public document/model type;
- CLI executable name if retained.

These identifiers must be consistent across:

- `pyproject.toml`;
- source imports;
- documentation;
- examples;
- CI;
- package metadata;
- console entry points.

Do not preserve donor-framework identity in the final product.

Legally required copyright, license, attribution, or third-party notices must be retained.

---

## 4. Required Migration Lifecycle

Every extraction follows this order.

### Stage 1 — Donor Truth

Record the exact donor baseline before changing anything:

- donor commit SHA;
- production source manifest;
- public API manifest;
- production test manifest;
- package metadata;
- direct runtime dependencies;
- shared-core imports;
- fixtures/corpus and provenance;
- known review findings;
- legacy/shadow implementation paths;
- current test results;
- interoperability evidence;
- security/resource behavior.

The donor is read-only.

### Stage 2 — Repository Bootstrap

Create or clone the real destination repository.

Use a conventional standalone Python package layout.

Do not migrate generic supervisor, FF6, task, event, or cross-format machinery.

### Stage 3 — Mechanical Source Extraction

Copy the current production implementation with the minimum changes necessary to run under the new namespace.

Do not redesign public APIs here.

Do not delete donor behavior here.

### Stage 4 — One-for-One Production Test Migration

Migrate production tests with traceability.

Do not merge/reorganize them before parity.

Legacy/shadow tests must be individually classified as:

- already covered;
- unique useful behavior to port;
- obsolete implementation-specific behavior.

### Stage 5 — Extraction Parity Gate

Prove that the independently located package preserves donor production behavior.

This gate is about behavior, not independence from shared core.

### Stage 6 — Independence Gate

Remove:

- donor-framework imports;
- generic shared-core dependency;
- sibling-format dependency;
- donor path assumptions.

Re-run parity.

### Stage 7 — Source/API Normalization

Only after parity and independence:

- normalize internal layout;
- flatten unnecessary nested codec folders;
- curate public exports;
- rename donor-specific classes;
- establish final document-centric API;
- remove temporary compatibility aliases.

### Stage 8 — Format-Specific Professional Depth

Build the real differentiated product capabilities required by that format.

### Stage 9 — Evidence, Security, Interoperability, Docs

Add professional external evidence.

### Stage 10 — CI, Packaging, Release Candidate

Verify from a clean clone.

---

## 5. No Broken Checkpoints

Every committed checkpoint must be usable and testable for its declared scope.

Do not commit a state that intentionally imports an unavailable donor package.

If a temporary compatibility bridge is necessary:

- keep it private;
- keep it local to the new repository;
- copy only the minimum donor behavior needed for parity;
- do not require the donor package at runtime;
- remove it at the independence gate.

A compatibility bridge is migration scaffolding, not architecture.

---

## 6. Standard Repository Structure

Use this as the default shape:

```text
<repo>/
  pyproject.toml
  README.md
  CHANGELOG.md
  SECURITY.md
  CONTRIBUTING.md
  LICENSE
  THIRD_PARTY_NOTICES.md       # when required
  .gitignore
  .gitlab-ci.yml

  src/
    <package>/
      __init__.py
      py.typed
      errors.py
      diagnostics.py

      model/
      codec/
        reader.py
        writer.py

      validation/
      security/
        limits.py

      cli/
        __init__.py
        main.py

      _internal/

  tests/
    unit/
    integration/
    interoperability/
    security/
    package/
    fixtures/
      valid/
      invalid/
      adversarial/

  docs/
  examples/
```

Add format-specific directories only when justified, such as:

- `adapters/`;
- `modules/`;
- `benchmarks/`;
- `analytics/`;
- `merge.py`.

Equivalent concepts should live in equivalent locations across libraries.

Do not recreate a generic `_core` package inside every product.

`_internal/` is only for genuinely private implementation helpers.

---

## 7. Common Coding Conventions

All libraries must use:

- `from __future__ import annotations`;
- Python 3.11+ baseline unless deliberately revised for all libraries;
- PEP 8 naming;
- Ruff formatting/checking;
- line length 100;
- mypy strict;
- typed public APIs;
- explicit exports;
- no wildcard imports;
- no import-time optional heavyweight dependencies;
- no hidden mutable global state.

Use:

- `slots=True` dataclasses where beneficial;
- `frozen=True` for immutable value types where appropriate;
- `StrEnum` where appropriate.

Review hand-written files approaching 800 LOC.

Decompose by responsibility, not arbitrary line limits.

The root `__init__.py` is a facade, not an implementation module.

---

## 8. Common Public API Philosophy

Every format should expose one obvious central domain object.

Examples:

- `NotebookDocument`
- `XliffDocument`
- `SafeTensorsDocument`
- `UblDocument`
- `NrrdDocument`

Primary consumer pattern:

```python
document = FormatDocument.load("input")
result = document.validate()
document.save("output")
```

Use typed child collections.

Known domain entities should not require raw dictionary/XML/binary traversal.

Unknown or extension data must remain preservable when the format requires forward compatibility.

Module-level `load`, `loads`, `dump`, `dumps`, and `probe` may remain where useful, but the document/model object is the primary documented experience.

### Options

Create `LoadOptions`, `SaveOptions`, `ValidationOptions`, etc. only when an operation has meaningful configuration.

Do not create empty boilerplate option classes merely for visual symmetry.

### Root namespace

Keep the root small and intentional.

Aim roughly for the common 80% consumer workflow.

Advanced APIs belong in submodules.

---

## 9. Public Errors

Each library owns its error hierarchy.

Pattern:

```text
<Product>Error
<Product>ParseError
<Product>ValidationError
<Product>WriteError
<Product>SecurityError
<Product>ResourceLimitError
```

Add format-specific errors only when real product behavior requires them.

Every public domain error should consistently support:

- `message`;
- `code`;
- `context`.

Use stable dotted product-specific error codes for new/final codes, e.g.:

- `xliff.security.doctype`
- `ipynb.parse.invalid_version`
- `safetensors.layout.overlap`

Internal implementation errors must not leak across the public boundary.

---

## 10. Public Diagnostics

All libraries use the same vocabulary:

- `DiagnosticSeverity`
- `SourceLocation` where meaningful
- `Diagnostic`
- `ValidationResult`

A diagnostic should provide:

- code;
- message;
- severity;
- optional location;
- structured details/context where appropriate.

`ValidationResult` should provide at minimum:

- diagnostics;
- `is_valid`;
- filtered errors;
- iteration/access semantics.

Temporary parity aliases are acceptable during extraction but should be removed before the first non-development release unless real external compatibility requires them.

---

## 11. Resource Limits

Every product uses a format-specific resource-limit class:

- `NotebookResourceLimits`
- `XliffResourceLimits`
- `SafeTensorsResourceLimits`
- etc.

Use:

```python
DEFAULT_RESOURCE_LIMITS
```

as the primary public default.

Do not invent final defaults during planning.

Required process:

1. record donor defaults;
2. trace every field to actual use;
3. preserve donor behavior for parity where necessary;
4. study realistic workloads;
5. study hostile workloads;
6. test memory/runtime implications;
7. choose final defaults with evidence;
8. document them in `SECURITY.md`;
9. regression-test enforcement.

Remove unused generic fields.

Different access modes may legitimately enforce different limits.

---

## 12. Dependency Policy

Standalone does not mean zero third-party dependencies.

Allowed runtime dependencies must be:

- public;
- maintained;
- justified by real product value;
- minimal.

Forbidden runtime dependencies:

- donor framework;
- sibling format libraries;
- unpublished internal umbrella packages.

If a mature third-party parser/security library materially improves correctness, prefer it over fragile home-grown machinery.

Optional ecosystem integrations belong in extras.

---

## 13. Security Standard

Every parser treats input as hostile.

Security gates must be format-specific.

Typical classes include:

- resource exhaustion;
- integer overflow;
- malformed lengths/offsets;
- path traversal;
- decompression bombs;
- XML entities/DTD;
- active embedded content;
- unsafe temporary files;
- unbounded recursion;
- encoding confusion;
- malicious metadata.

Security protections must act early enough to prevent expensive/dangerous work.

Every demonstrated defect receives a regression test.

Security claims must be supported by adversarial execution, not source inspection alone.

---

## 14. Test Taxonomy

Final test layout:

```text
tests/
  unit/
  integration/
  interoperability/
  security/
  package/
  fixtures/
    valid/
    invalid/
    adversarial/
```

### Unit

Single components.

### Integration

Complete multi-component workflows.

### Interoperability

Independent reference implementations, validators, or ecosystem tools.

### Security

Adversarial input and resource-limit behavior.

### Package

Built wheel/sdist behavior from outside the source checkout.

No test counts as professional package evidence if it imports the source tree accidentally.

---

## 15. Corpus and Provenance

Synthetic fixtures and real corpus serve different purposes.

### Synthetic/spec fixtures

Use for:

- exact edge cases;
- malformed inputs;
- adversarial payloads;
- specification boundaries.

### Real/independent corpus

Use for:

- producer diversity;
- ecosystem interoperability;
- realistic metadata/content;
- large/complex documents.

Every third-party fixture needs provenance and licensing information.

Normal CI must not depend on downloading live public-network fixtures.

---

## 16. Interoperability

Self-roundtrip is not independent interoperability.

Where reference implementations or validators exist:

- test both directions when meaningful;
- pin known reference versions;
- also test the supported current range when practical;
- document intentional differences;
- never turn the reference implementation into a runtime dependency.

A skipped interoperability suite is not a passing release gate.

---

## 17. Property, Fuzz, and Mutation Testing

Every library must include risk-based advanced testing.

Use property/fuzz tests where the format has combinatorial structures.

Use mutation testing on critical logic such as:

- parsers;
- writers;
- validation;
- security boundaries;
- version conversion;
- binary arithmetic;
- merge/diff;
- state transitions.

Do not use a vanity global mutation percentage.

Review surviving mutations by risk.

---

## 18. CLI Standard

CLI is optional and secondary to the Python API.

Retain it only if it exposes mature product workflows.

Use:

- `argparse` unless a clear reason justifies another dependency;
- lowercase kebab-case commands;
- predictable machine-friendly exit codes;
- installed-entry-point tests;
- README documentation.

Do not build a CLI merely to increase feature count.

---

## 19. Versioning

All new extraction repositories begin at:

```text
0.1.0.dev0
```

unless there is an explicit release policy saying otherwise.

Do not mark Alpha/Beta/Stable inconsistently during extraction.

At the final release-ready gate, deliberately decide the first non-development version, normally `0.1.0` unless evidence supports another value.

Do not jump mechanically to `1.0.0`.

---

## 20. Git and GitLab Discipline

Use Conventional Commits:

```text
chore(repo):
feat(...):
fix(...):
refactor(...):
test(...):
docs(...):
ci:
```

Rules:

- exact-path staging;
- no `git add .`;
- no `git add -A`;
- inspect every diff;
- no force push;
- every commit leaves its scope testable;
- checkpoint frequently;
- do not leave hours of useful work only in the working tree;
- push accepted checkpoints.

### GitLab Authentication

When `gl_token` is provided through the environment:

- never print it;
- never log it;
- never commit it;
- never embed it in `origin`;
- use transient credential/askpass handling;
- remove temporary helper files;
- keep `origin` as the clean HTTPS URL.

Respect protected branches.

---

## 21. CI Standard

Use these conceptual GitLab stages:

```text
quality
test
interop
package
```

### quality

- Ruff;
- mypy;
- metadata/static checks.

### test

- supported Python matrix;
- unit;
- integration;
- security.

### interop

- official/reference implementation;
- schema/external validation;
- real corpus where appropriate;
- required optional adapter jobs for claimed capabilities.

### package

- wheel build;
- sdist build;
- clean wheel install;
- clean sdist install;
- import from outside checkout;
- installed CLI if retained;
- package-content check;
- metadata validation.

Required release capabilities must not be `allow_failure`.

---

## 22. Documentation Standard

Every library needs:

- README;
- CHANGELOG;
- SECURITY;
- CONTRIBUTING;
- license;
- third-party notices where required;
- `py.typed`.

README should cover:

- what the library does;
- supported format versions/profiles;
- installation;
- quick start;
- document/model API;
- major workflows;
- validation;
- security/resource limits;
- interoperability status;
- optional integrations;
- CLI if retained;
- known limitations.

Examples should execute in CI.

---

## 23. Release Candidate Gate

A product is release-ready only when:

- repository is independent;
- no donor-framework runtime dependency;
- no sibling-format dependency;
- no shadow/legacy implementation;
- donor production parity proven;
- independence parity proven;
- final API intentionally reviewed;
- wheel builds;
- sdist builds;
- clean installed-wheel test passes;
- clean installed-sdist test passes;
- security gate passes;
- interoperability gate passes where applicable;
- real corpus exists where applicable;
- property/fuzz/mutation work is satisfactory for critical logic;
- documentation examples execute;
- GitLab CI is green;
- metadata/version reflect actual readiness;
- clean clone builds/tests/packages without donor repository.

Do not publish externally merely because this gate passes.

Publication is a separate explicit action.

---

## 24. Autonomous Agent Execution

A `/goal` remains active until the final product gate passes.

A worker must not interpret any of the following as mission completion:

- subplan completion;
- one feature completion;
- one commit;
- test pass;
- evidence creation;
- context exhaustion.

After every accepted product slice:

1. inspect changes;
2. run acceptance checks;
3. run relevant regression;
4. review evidence;
5. repair failures;
6. commit;
7. push;
8. choose the next highest-value unblocked item;
9. continue.

If a worker stops unexpectedly:

- preserve useful work;
- inspect git status/commits;
- run acceptance checks independently;
- resume the same goal.

A worker exit is not a product blocker.

---

## 25. Product-First Rule

Do not rebuild generic governance or supervisor machinery inside product repositories.

New machinery is justified only when:

1. a demonstrated repeated failure exists;
2. existing product tests/CI cannot prevent it;
3. the machinery directly reduces product risk.

The majority of effort after extraction/independence must go into:

- format knowledge;
- API depth;
- interoperability;
- validation;
- security;
- documentation;
- performance where relevant.

---

## 26. Future Extraction Checklist

Before starting any future format extraction, answer:

1. What is the exact production donor source?
2. Which code is legacy/shadow?
3. What is the donor public API?
4. Which donor tests exercise production code?
5. Which shared-core symbols are actually used?
6. Which of those should become format-specific internals?
7. What is the canonical new repository/distribution/namespace?
8. What is the central document/model type?
9. What independent reference implementation or validator exists?
10. What real corpus is available?
11. What are the format-specific security threats?
12. What professional workflows would make developers choose this library?

Only after these answers are recorded should extraction begin.
