# Code Quality Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores the internal quality of product source code — independent of API surface or feature set.
High code quality correlates with maintainability, correctness, and developer confidence.

---

## Scoring Scale

0 = Absent or non-functional
1 = Weak / prototype / proof-of-concept
2 = Basic but functional
3 = Acceptable for internal use
4 = Strong professional quality
5 = Exemplary / publication-grade

---

## Code Quality Dimensions

### CQ-1: Code Clarity

Does the code communicate intent clearly? Are variable names, method names, and type names
expressive and domain-specific?

| Score | Criteria |
|-------|---------|
| 0 | No meaningful naming; variable names are `a`, `b`, `x`, `tmp` |
| 1 | Some names are clear; many are single-character or opaque |
| 2 | Domain concepts visible but inconsistently named |
| 3 | Most names are expressive; occasional shortcuts acceptable |
| 4 | All public names are expressive; internal names clear with context |
| 5 | Names read like natural language; intent is unambiguous without comments |

### CQ-2: Code Modularity

Is the code divided into focused, single-responsibility units?

| Score | Criteria |
|-------|---------|
| 0 | Single monolithic file; all logic in one class/function |
| 1 | Some separation but classes have multiple unrelated concerns |
| 2 | Basic separation (parser + model + writer) but boundaries unclear |
| 3 | Clear separation; each class has a primary responsibility |
| 4 | Components are independently testable; no cross-cutting concerns |
| 5 | Perfect separation; each component replaceable without ripple effects |

### CQ-3: Error Handling

Are failure modes handled explicitly? Are exceptions typed and meaningful?

| Score | Criteria |
|-------|---------|
| 0 | No error handling; exceptions propagate raw from framework |
| 1 | Try/catch around broad areas; swallows exceptions without logging |
| 2 | Some errors caught; generic exception types used |
| 3 | Custom exception hierarchy; most failure paths handled |
| 4 | All failure paths handled; custom exceptions carry meaningful messages |
| 5 | Exceptions carry full diagnostic context; stack trace + cause + recovery hint |

### CQ-4: Input Validation

Are user-provided inputs validated at boundaries?

| Score | Criteria |
|-------|---------|
| 0 | No validation; null inputs cause NullReferenceException / AttributeError |
| 1 | Some validation; inconsistently applied |
| 2 | Basic null/empty checks; no semantic validation |
| 3 | File existence, type constraints, range checks present |
| 4 | Comprehensive validation at all public entry points |
| 5 | Validation is its own testable layer; failure messages are actionable |

### CQ-5: Testability

Can the code be tested without external dependencies, file I/O, or complex setup?

| Score | Criteria |
|-------|---------|
| 0 | Hardcoded file paths; no DI; impossible to unit test |
| 1 | Some unit tests exist but require real file system |
| 2 | Most tests use real files but in predictable locations |
| 3 | Core logic testable in isolation; some I/O wrapped behind interfaces |
| 4 | All I/O injectable; memory streams usable for most tests |
| 5 | Pure functions for core logic; I/O is thin adapter layer; 100% unit testable |

### CQ-6: Internal Consistency

Do similar operations follow the same pattern across the codebase?

| Score | Criteria |
|-------|---------|
| 0 | No consistency; each method uses different patterns |
| 1 | Some shared patterns but frequently broken |
| 2 | Patterns visible but not enforced |
| 3 | Most operations follow a consistent pattern |
| 4 | All operations follow common patterns; deviations are documented |
| 5 | Enforced via base classes, interfaces, or source generation |

---

## Format Factory Code Quality Scores (Preliminary)

| Product | CQ-1 | CQ-2 | CQ-3 | CQ-4 | CQ-5 | CQ-6 | Avg |
|---------|------|------|------|------|------|------|-----|
| FODS .NET | 4 | 4 | 4 | 4 | 3 | 4 | 3.8 |
| FODT .NET | 4 | 4 | 4 | 3 | 3 | 4 | 3.7 |
| NetPBM .NET | 4 | 5 | 4 | 4 | 4 | 4 | 4.2 |
| NDJSON .NET | 3 | 3 | 3 | 3 | 3 | 3 | 3.0 |
| CSV .NET | 3 | 3 | 2 | 2 | 3 | 3 | 2.7 |
| TSV .NET | 3 | 3 | 3 | 2 | 3 | 3 | 2.8 |
| ZST .NET | 3 | 3 | 3 | 3 | 3 | 2 | 2.8 |
| HTML .NET | 2 | 2 | 1 | 1 | 2 | 2 | 1.7 |
| FODS Python | 3 | 3 | 3 | 3 | 3 | 2 | 2.8 |
| FODT Python | 3 | 3 | 3 | 3 | 3 | 2 | 2.8 |
| PBM Python | 4 | 4 | 4 | 4 | 4 | 4 | 4.0 |
| ZST Python | 3 | 3 | 2 | 3 | 3 | 3 | 2.8 |

---

## Code Quality Bands

| Score | Band |
|-------|------|
| 0.0 – 1.4 | Not production-ready |
| 1.5 – 2.4 | Prototype quality |
| 2.5 – 3.4 | Acceptable internal tool |
| 3.5 – 4.2 | Professional quality |
| 4.3 – 5.0 | Publication-grade |
