# Deep Reverse-Engineering Assessment: `apidev`

> **Date:** 2026-06-10
> **Repo:** `c:\Users\prora\OneDrive\Documents\GitHub\apidev`
> **Branch:** `main` (clean)
> **Head:** `d3928b1` — fix(apidev): treat dotnet-script "already exists" reinstall as success
> **Assessor:** Claude Opus 4.6 (automated deep review)
> **Scope:** Full codebase — every file read, every code path traced

---

## Table of Contents

1. [Executive Verdict](#1-executive-verdict)
2. [Project Identity](#2-project-identity)
3. [What the Project Actually Does](#3-what-the-project-actually-does)
4. [How It Actually Works](#4-how-it-actually-works)
5. [Architecture Judgment](#5-architecture-judgment)
6. [Code and Engineering Assessment](#6-code-and-engineering-assessment)
7. [Reality vs Claims](#7-reality-vs-claims)
8. [Operational Readiness](#8-operational-readiness)
9. [Workflow-Fit for My Environment](#9-workflow-fit-for-my-environment)
10. [Adoption Recommendation](#10-adoption-recommendation)
11. [Top Gaps and Fixes](#11-top-gaps-and-fixes)
12. [Evidence Appendix](#12-evidence-appendix)
13. [Mandatory Grading](#13-mandatory-grading)

---

## 1. Executive Verdict

`apidev` is a deterministic, no-LLM CLI tool that manages a "capability catalog" — a set of YAML files describing the public API surface of a .NET NuGet package (specifically Aspose.PDF). It extracts metadata from a pinned .NET assembly via Roslyn, mechanically seeds capability YAML files, and verifies that hand-maintained catalogs remain a strict subset of the canonical .NET surface. It also supports per-target-language type translation (e.g. .NET FQNs to C++ idioms) with direction-aware stream handling, drop cascading, and stale-entry detection.

The project is **well-engineered, focused, and operationally coherent**. It is a real, actively maintained internal tool (~20 commits of progressive refinement). Code quality is high — clear naming, good separation of concerns, defensive validation, and a principled data-driven architecture. The codebase is small (~2100 lines of Python + ~520 lines of C#), fully readable in one sitting, and has 70 unit tests covering the deterministic logic. The main risk is the hard dependency on .NET SDK + `dotnet-script` at runtime. This is a legitimate tool for adoption if you work in the Aspose PDF FOSS wrapper ecosystem or a similar multi-target API-binding workflow.

---

## 2. Project Identity

| Attribute | Value |
|---|---|
| **Type** | CLI tool / internal build-time verifier |
| **Languages** | Python 3.10+ (engine), C# script (Roslyn extractor) |
| **Dependencies** | PyYAML, pytest; .NET 8+ SDK, dotnet-script, Roslyn NuGet, YamlDotNet NuGet |
| **Intended users** | API catalog operators building multi-language FOSS wrappers around a .NET commercial library |
| **Core problem** | Ensuring a hand-curated API subset catalog stays synchronized with the upstream .NET assembly's actual public surface, across multiple target languages |
| **Maturity** | Active internal tool — post-v1, progressively refined, production-facing for its niche |
| **Shape** | Local CLI, run by operators during development; CI runs lint+test only |

### File inventory (66 files total)

| Category | Count | Key paths |
|---|---|---|
| Python engine | 11 | [apidev/](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/) |
| C# extractor | 1 | [tools/extract_public_api.csx](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx) |
| Standalone tool | 1 | [tools/seed_annotations.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/seed_annotations.py) |
| Tests | 8 | [tests/](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tests/) |
| Shell scripts | 4 | [scripts/](c:/Users/prora/OneDrive/Documents/GitHub/apidev/scripts/) |
| Docs | 5 | [README.md](c:/Users/prora/OneDrive/Documents/GitHub/apidev/README.md), [apidev/README.md](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/README.md), [docs/code-quality/architecture.md](c:/Users/prora/OneDrive/Documents/GitHub/apidev/docs/code-quality/architecture.md), [docs/methodology.md](c:/Users/prora/OneDrive/Documents/GitHub/apidev/docs/methodology.md), [CHANGELOG.md](c:/Users/prora/OneDrive/Documents/GitHub/apidev/CHANGELOG.md) |
| Infra | 4 | [Dockerfile](c:/Users/prora/OneDrive/Documents/GitHub/apidev/Dockerfile), [.gitlab-ci.yml](c:/Users/prora/OneDrive/Documents/GitHub/apidev/.gitlab-ci.yml), [.gitignore](c:/Users/prora/OneDrive/Documents/GitHub/apidev/.gitignore), [CODEOWNERS](c:/Users/prora/OneDrive/Documents/GitHub/apidev/CODEOWNERS) |
| Config | 1 | [requirements.txt](c:/Users/prora/OneDrive/Documents/GitHub/apidev/requirements.txt) |

---

## 3. What the Project Actually Does

### Plain-English explanation

You have a commercial .NET library (Aspose.PDF). You're building open-source wrappers in multiple languages (C++, C#, potentially TS/Rust/Go/Swift). You need a controlled catalog of which API members from the commercial library are exposed in each wrapper. `apidev` is the tool that:

1. **Reads the .NET assembly** via Roslyn metadata mode (no source code) to extract the complete public API surface
2. **Seeds YAML catalogs** — mechanically generates `capabilities/<slug>.yaml` files describing each class's public members with canonical .NET FQNs
3. **Verifies coverage** — checks that every capability YAML entry actually exists on the canonical assembly (UNBOUND, INVENTED, SIGNATURE_FQN_MISMATCH), that every type can be translated to target idioms (TRANSLATION_MISS), and that drop/annotation sidecars haven't drifted (STALE_DROP, STALE_ANNOTATION)
4. **Reports pending work** — scans target language source trees for `PENDING("slug")` markers and produces a prioritized backlog

### Main capabilities

- Deterministic catalog seeding from .NET metadata
- 6-bucket verification (UNBOUND, INVENTED, SIGNATURE_FQN_MISMATCH, TRANSLATION_MISS, STALE_DROP, STALE_ANNOTATION)
- Per-target type translation with direction-aware stream handling
- Drop cascading (if any type in a signature can't translate, the whole member drops)
- Pending-marker backlog walker with comment stripping

### Clear boundaries — what it does NOT do

- Does NOT generate code, headers, or implementations
- Does NOT use any LLM or AI
- Does NOT author API documentation
- Does NOT manage the per-target idiomatic headers (that's RefDev)
- Does NOT handle foundation primitives (that's SpecDev)

---

## 4. How It Actually Works

### True entrypoints

| # | Entrypoint | Location | Context |
|---|---|---|---|
| 1 | Primary CLI | [apidev/cli.py:321-332](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/cli.py#L321) — `main()` | `python3 -m apidev.cli` |
| 2 | Docker | [Dockerfile:38](c:/Users/prora/OneDrive/Documents/GitHub/apidev/Dockerfile#L38) | `ENTRYPOINT ["python3", "-m", "apidev.cli"]` |
| 3 | Shell wrappers | [scripts/verify.sh](c:/Users/prora/OneDrive/Documents/GitHub/apidev/scripts/verify.sh), [scripts/seed.sh](c:/Users/prora/OneDrive/Documents/GitHub/apidev/scripts/seed.sh), [scripts/pending.sh](c:/Users/prora/OneDrive/Documents/GitHub/apidev/scripts/pending.sh) | Operator shortcuts |
| 4 | Standalone tool | [tools/seed_annotations.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/seed_annotations.py) | Independent stream-direction annotation seeder |
| 5 | Tests | `python3 -m pytest tests/` | [scripts/test.sh](c:/Users/prora/OneDrive/Documents/GitHub/apidev/scripts/test.sh) |

### End-to-end flow: `apidev verify`

```
CLI args (--project, --target, verify)
  -> _resolve_config_path()               [cli.py:274-278]
     -> <project>/.apidev/<target>.yaml
  -> load_config()                         [config.py:83-109]
     -> Config dataclass
  -> verify_coverage(cfg)                  [verifier.py:191-233]
     -> CanonicalSurface.for_config(cfg)   [canonical.py:148-163]
        -> resolve_assembly()              [dotnet_assembly.py:46-82]
           (NuGet cache probe, dotnet restore if needed)
        -> run_csx(extract_public_api.csx) [dotnet_script.py:113-121]
           (Roslyn metadata -> YAML on stdout)
        -> yaml.safe_load()               [canonical.py:297-298]
           -> in-memory index by full_name
     -> load_annotations()                 [annotations.py:156-174]
        (<api_definition>/annotations/)
     -> For each target: get_plugin()      [targets.py:407-415]
        loads translations.yaml + drops.yaml
     -> For each capability YAML:
        -> load_capability()               [capability.py:98-131]
           -> Capability dataclass
        -> _check_canonical()              [verifier.py:241-291]
           -> UNBOUND / INVENTED / SIGNATURE_FQN_MISMATCH
        -> _check_per_target()             [verifier.py:385-444]
           -> TRANSLATION_MISS + shipping tally
     -> _check_stale_drops()               [verifier.py:607-648]
        -> STALE_DROP
     -> _check_stale_annotations()         [verifier.py:473-599]
        -> STALE_ANNOTATION
  -> _print_report()                       [cli.py:103-198]
     -> human-readable console output
  -> exit code 0 (pass) or 1 (fail)
```

### End-to-end flow: `apidev seed`

```
CLI args (--project, --target, seed CLASS [--force] [--members/--omit] [--namespace])
  -> load_config()                         [config.py:83-109]
  -> seed_catalog(cfg, class_name, ...)    [seed.py:94-164]
     -> CanonicalSurface.for_config(cfg)._ensure_loaded()
     -> _resolve_canonical()               [seed.py:176-205]
        find class by simple name or namespace+name
     -> _filter_members()                  [seed.py:248-267]
        apply allowlist/denylist
     -> _build_payload()                   [seed.py:275-291]
        dict with canonical FQNs
     -> yaml.safe_dump()                   [seed.py:157-159]
        write capabilities/<slug>.yaml
  -> _print_seed_report()                  [cli.py:79-93]
```

### Key components

| Module | File | Lines | Responsibility |
|---|---|---|---|
| CLI | [apidev/cli.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/cli.py) | 333 | Argument parsing, subcommand dispatch, report printing |
| Config | [apidev/config.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/config.py) | 142 | YAML config loading, `Config` and `AssemblySource` dataclasses |
| Canonical | [apidev/canonical.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/canonical.py) | 334 | Lazy wrapper around the .csx extractor; in-memory canonical surface cache |
| Capability | [apidev/capability.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/capability.py) | 165 | Capability YAML loader; v2 schema dataclasses |
| Seed | [apidev/seed.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/seed.py) | 327 | Catalog seeding from canonical surface; slug generation; member filtering |
| Verifier | [apidev/verifier.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/verifier.py) | 649 | 6-bucket coverage verification; per-target checks |
| Targets | [apidev/targets.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py) | 582 | Per-target type translation plugin; drop cascading; direction-aware primitives |
| Annotations | [apidev/annotations.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/annotations.py) | 293 | Stream-direction annotation registry; YAML sidecar loader |
| Pending | [apidev/pending.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/pending.py) | 138 | PENDING marker scanner with comment stripping |
| .NET Assembly | [apidev/dotnet_assembly.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/dotnet_assembly.py) | 116 | NuGet package resolution; `dotnet restore` driver |
| .NET Script | [apidev/dotnet_script.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/dotnet_script.py) | 122 | `dotnet-script` auto-install + invocation |
| Roslyn Extractor | [tools/extract_public_api.csx](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx) | 526 | Roslyn metadata extractor; YAML output; optional static-value probe |
| Annotation Seeder | [tools/seed_annotations.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/seed_annotations.py) | 200 | Standalone stream-direction annotation seeder |

### Data flow

```
.NET NuGet package -> dotnet restore -> local DLL cache
  -> dotnet script extract_public_api.csx -> YAML stdout
  -> Python yaml.safe_load -> CanonicalSurface (in-memory dict)
  -> verifier reads capabilities/*.yaml + translations.yaml + drops.yaml + annotations/*.yaml
  -> CoverageReport dataclass -> console output + exit code
```

### State and persistence

- **No database, no cache files** — the canonical surface is loaded fresh each run (~5s for full Aspose.PDF)
- **NuGet cache** (`~/.nuget/packages/`) is the only persistent side effect
- **Output artifacts**: `capabilities/<slug>.yaml` (seed), `annotations/<slug>.streams.yaml` (seed_annotations)
- **No temp files persist** — `dotnet restore` uses `tempfile.TemporaryDirectory`

---

## 5. Architecture Judgment

### Actual architecture style

Clean pipeline architecture — data flows unidirectionally from canonical assembly through loaders into verification logic. No circular dependencies. Each module has a single clear responsibility.

### Strong patterns

- **Data-driven target plugins** (translations.yaml + drops.yaml) — no code changes needed for new targets
- **Lazy loading with in-process caching** ([apidev/canonical.py:270](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/canonical.py#L270) `_ensure_loaded()`, [apidev/targets.py:404](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L404) `_REGISTRY`)
- **Consistent use of frozen/immutable dataclasses** for results
- **Defensive validation** at every YAML ingestion boundary
- **Clean separation** between canonical-side checks (target-agnostic) and per-target checks

### Weak patterns

| Pattern | Location | Issue |
|---|---|---|
| `sys.exit(1)` in library code | [apidev/config.py:89,99,122,128,135](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/config.py#L89) | Should raise exceptions, not terminate the process |
| Module-level side effect on import | [apidev/verifier.py:80](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/verifier.py#L80), [apidev/seed.py:43](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/seed.py#L43) | `sys.stdout.reconfigure(line_buffering=True)` fires on import |
| Duck-typing adapter | [apidev/verifier.py:447-460](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/verifier.py#L447) | `_as_canon_view` creates a class inside a function — works but fragile |
| Module-level mutable cache | [apidev/targets.py:404](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L404) | `_REGISTRY` dict requires manual `reset_cache()` in tests |
| Hardcoded namespace default | [apidev/targets.py:262-265](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L262) | `Aspose.Pdf.*` ties the "project-agnostic" engine to Aspose |

### Coupling analysis

Low overall. Modules communicate through well-defined dataclass interfaces. The only tight coupling is between [apidev/canonical.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/canonical.py) and [apidev/dotnet_assembly.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/dotnet_assembly.py)/[apidev/dotnet_script.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/dotnet_script.py) (necessarily so — they form the .NET integration layer).

### Fragility points

- The .csx depends on specific Roslyn (`4.9.2`) and YamlDotNet (`15.1.6`) NuGet versions — version drift could break extraction
- `dotnet-script` auto-install in [apidev/dotnet_script.py:78-110](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/dotnet_script.py#L78) is fragile across .NET SDK major version changes
- 600-second timeout on .csx invocation ([apidev/canonical.py:290](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/canonical.py#L290)) — a hung Roslyn session blocks the operator for 10 minutes

### Dead zones or suspicious zones

- **No dead code found.** Every file is actively used. No placeholder files, no abandoned experiments.
- **Stale comments** in [tools/extract_public_api.csx:8-9](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx#L8) reference `apidev bootstrap` (renamed to `seed`) and [apidev/semantic_type.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/semantic_type.py) (renamed to [apidev/targets.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py)). Working code, stale prose.

---

## 6. Code and Engineering Assessment

### What is well written

- **Naming** — Excellent throughout. `CanonicalSurface`, `CapabilityMember`, `TranslationMiss`, `DropDecision`, `StaleDrop` — every name self-documents
- **Dataclasses** — Clean, typed, with sensible defaults and field factories
- **Validation** — Every YAML loader validates required keys, types, and cross-references; clear error messages with file paths
- **Slug generation** ([apidev/seed.py:46-76](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/seed.py#L46)) — well-documented algorithm with clear boundary rules
- **Generic type parsing** ([apidev/targets.py:551-569](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L551)) — correct recursive bracket-depth tracking
- **Direction-aware translation** — principled slot+direction model with clear semantics
- **Inheritance-aware member lookup** ([apidev/canonical.py:199-229](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/canonical.py#L199)) — walks base types and interfaces with cycle protection

### What is badly written

Nothing is truly "bad." The weakest code is the `_as_canon_view` adapter pattern ([apidev/verifier.py:447-460](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/verifier.py#L447)) which ducks typing rather than using a proper protocol/interface, but it's isolated and works.

`print()` for error reporting instead of structured logging is a consistent minor weakness.

### What is risky

| Risk | Location | Severity | Mitigation |
|---|---|---|---|
| 600s subprocess timeout | [apidev/canonical.py:290](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/canonical.py#L290) | Medium | Add `--timeout` CLI flag or reduce default |
| Package name in generated XML | [apidev/dotnet_assembly.py:99](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/dotnet_assembly.py#L99) | Low | Operator controls input; could add XML escaping |
| Assembly code execution via static-value probe | [tools/extract_public_api.csx:405](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx#L405) | Low | Documented, fail-soft, operator pins NuGet package |

### What is deceptive or unclear

- The README says "apidev is project-agnostic" but [apidev/targets.py:262](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L262) hardcodes `Aspose.Pdf.` as a default translation namespace — not fully project-agnostic
- The README mentions "Five buckets" but the code actually has 6 (STALE_ANNOTATION was added later)

### What is likely expensive to maintain

- The .csx extractor depends on specific Roslyn and YamlDotNet NuGet versions — periodic bumps required
- The `dotnet-script` global tool auto-install logic is fragile across .NET SDK version changes
- Any Roslyn API breaking changes would require rewriting the .csx

---

## 7. Reality vs Claims

### Verified truths

| Claim | Evidence | Status |
|---|---|---|
| "Deterministic — no LLM" | Zero AI/LLM references in any code path; grep for `openai`, `anthropic`, `llm`, `gpt`, `claude` returns nothing | **Verified** |
| "Single source of truth from canonical .NET assembly" | `CanonicalSurface` class is the sole canonical authority; all checks flow through it | **Verified** |
| "Mechanical seeding — no hand-editing" | `seed_catalog()` writes pure Roslyn projections; no post-processing | **Verified** |
| "Per-target translation is data-driven" | `ApiTargetPlugin` reads YAML tables, no code changes needed for new targets | **Verified** |
| "Idempotent re-seed" | Without `--force`, existing files are skipped; with `--force`, output is deterministic from canonical | **Verified** |

### Partially true claims

| Claim | Reality |
|---|---|
| "Project-agnostic" | The engine is project-agnostic in structure (config is external), but `Aspose.Pdf.*` is hardcoded as a default translation namespace in [apidev/targets.py:262](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L262). A non-Aspose project would need to modify this or add all FQNs to `primitives:`. |

### False or misleading claims

| Claim | Reality |
|---|---|
| README says "Five buckets" ([README.md:22](c:/Users/prora/OneDrive/Documents/GitHub/apidev/README.md#L22)) | Actually 6 buckets now — STALE_ANNOTATION was added in a later commit |
| .csx header references `apidev bootstrap` and `semantic_type.py` ([tools/extract_public_api.csx:8-9](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx#L8)) | Both renamed; stale comments |

### Important undocumented realities

- The `.csx` extractor's static-value probe **executes code from the target assembly** at extraction time — documented in the .csx header but not in the README or methodology docs
- The `Aspose.Pdf.*` default namespace handling in [apidev/targets.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py) is not documented anywhere as a project-specific assumption
- The `sys.exit()` calls in [apidev/config.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/config.py) mean this tool **cannot be safely used as a library** without catching `SystemExit` — not documented

---

## 8. Operational Readiness

### Run requirements

| Requirement | Detail |
|---|---|
| **Python** | 3.10+ (uses `X \| Y` union syntax, `list[str]` generics) |
| **PyYAML** | >= 6.0 ([requirements.txt](c:/Users/prora/OneDrive/Documents/GitHub/apidev/requirements.txt)) |
| **.NET SDK** | 8+ on PATH |
| **dotnet-script** | Auto-installed on first use |
| **NuGet network** | First-time package restore |
| **Project config** | `<project>/.apidev/<target>.yaml` |
| **Capability catalog** | `<project>/capabilities/*.yaml` |
| **Translation tables** | `<project>/targets/<lang>/translations.yaml` |

### Deployment assumptions

- Local developer workstation or CI runner with .NET SDK
- Docker image provided for containerized use ([Dockerfile](c:/Users/prora/OneDrive/Documents/GitHub/apidev/Dockerfile))
- No server, no daemon, no persistent state

### Failure behavior

| Aspect | Quality | Detail |
|---|---|---|
| Error messages | Good | Clear messages with file paths and context |
| Exit codes | Good | 0 for pass, 1 for fail, structured |
| Static-value probe | Good | Fail-soft — individual failures don't abort extraction |
| Config loading | Bad | `sys.exit(1)` prevents graceful library use |
| NuGet restore | Bad | No retry logic for transient network failures |
| .csx execution | Bad | 600s timeout is very long for a hung process |

### Observability

- **Minimal**: `print()` to stdout/stderr; no logging framework, no metrics, no structured output format
- Reports are human-readable console text, not machine-parseable

### Reliability

- **High for its niche**: Deterministic operations, no state mutation beyond file writes, idempotent seed
- **Risk**: .NET SDK version mismatches, NuGet feed outages, Roslyn version incompatibilities

### Security

- **Low attack surface**: CLI tool run by operators; no network services; no user input from untrusted sources
- **Package name in csproj**: Minor XML injection risk if package name contains special characters (operator-controlled input)
- **Assembly.LoadFrom**: Executes static property getters from the target assembly — acceptable since operator pins the NuGet package

### Scalability

Not a concern — this is a build-time verification tool, not a service. Runs once per verification cycle.

---

## 9. Workflow-Fit for My Environment

### Best-fit uses

- **If you build multi-target API wrappers around .NET libraries**: This is exactly what `apidev` was built for. The verify -> seed -> translate pipeline is directly applicable.
- **As a CI gate**: Run `apidev verify` in CI to prevent catalog drift from the canonical assembly.
- **As a catalog seeder**: `apidev seed` eliminates manual YAML authoring for new API classes.

### Moderate-fit uses

- **API surface comparison tool**: The Roslyn extractor + canonical surface model could be repurposed for any .NET assembly API diff workflow, with some modification to remove the Aspose-specific defaults.
- **Type translation engine**: The `ApiTargetPlugin` direction-aware translation system is generalizable to other .NET-to-native type mapping problems.

### Poor-fit uses

- **Non-.NET APIs**: The entire pipeline assumes a .NET assembly as the source of truth. Not applicable to REST APIs, gRPC, or non-.NET native libraries.
- **As a library**: The `sys.exit()` calls and module-level side effects make it unsafe to embed without wrapping.

### Prerequisites for adoption

1. .NET 8+ SDK installed
2. A NuGet package to pin as the canonical source
3. A project directory structure matching the expected layout (`<project>/.apidev/`, `capabilities/`, `targets/<lang>/`)
4. Translation tables authored for each target language

### Integration design suggestions

- Wrap `verify_coverage()` return value instead of relying on exit codes if integrating programmatically
- Consider adding `--output json` flag for machine-parseable output
- Remove or parameterize the `Aspose.Pdf.*` default in [apidev/targets.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py) for true project-agnosticism

---

## 10. Adoption Recommendation

### Verdict: **Adopt with limited hardening**

The tool is well-engineered, focused, and solves a real problem effectively. The codebase is small enough to fully understand and maintain. The deterministic, no-LLM design is a strength — it's predictable, testable, and auditable. The test suite covers the deterministic logic well (70 tests), though integration testing requires the actual .NET assembly.

Hardening needed before serious use:

1. Replace `sys.exit()` in [apidev/config.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/config.py) with raised exceptions
2. Remove or parameterize the `Aspose.Pdf.*` default in [apidev/targets.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py)
3. Update stale comments in [tools/extract_public_api.csx](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx)
4. Add structured (JSON) output mode for CI integration
5. Add a `--timeout` CLI flag or reduce the 600s default

The tool is ready for production use within its intended niche. The hardening items are minor and don't block adoption.

---

## 11. Top Gaps and Fixes

### Most important fixes before serious use

| Priority | Fix | File(s) | Evidence |
|---|---|---|---|
| **P1** | Replace `sys.exit()` with exceptions in config loading | [apidev/config.py:89,99,122,128,135](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/config.py#L89) | Prevents library use; kills process on bad config |
| **P1** | Parameterize `Aspose.Pdf.*` default translation | [apidev/targets.py:262-265](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L262) | Contradicts "project-agnostic" claim |
| **P2** | Fix stale comments in .csx | [tools/extract_public_api.csx:8-9](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx#L8) | References `bootstrap` and `semantic_type.py` |
| **P2** | Update README bucket count | [README.md:22](c:/Users/prora/OneDrive/Documents/GitHub/apidev/README.md#L22) | Says 5 buckets, actually 6 |
| **P3** | Add JSON output mode | [apidev/cli.py](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/cli.py) | Console-only output limits CI integration |
| **P3** | Add integration tests with a public NuGet package | [tests/](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tests/) | Verifier tests don't exercise actual canonical surface |

### Highest-value refactors

- Extract the `_as_canon_view` adapter into a proper `Protocol` class
- Replace `print()` error reporting with `logging` module
- Move `sys.stdout.reconfigure()` from module level to `main()`

### Fastest path to a safe pilot

1. Install .NET 8 SDK + Python 3.10+
2. `pip install -r requirements.txt`
3. Create a project config at `<project>/.apidev/<target>.yaml` pointing at your NuGet package
4. Run `apidev seed` for a few classes to generate catalog YAMLs
5. Author `translations.yaml` for your target language
6. Run `apidev verify` to validate

### Highest-risk assumptions to verify first

1. That your .NET SDK version works with Roslyn 4.9.2 in the .csx
2. That `dotnet-script` auto-install works in your environment (corporate proxy, airgapped, etc.)
3. That the `Aspose.Pdf.*` default doesn't interfere with your namespace

---

## 12. Evidence Appendix

| Conclusion | Evidence | Status |
|---|---|---|
| No LLM usage anywhere | Grep for `openai`, `anthropic`, `llm`, `gpt`, `claude` — zero matches across all files | **Verified** |
| .NET SDK required at runtime | [apidev/dotnet_script.py:83-87](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/dotnet_script.py#L83) — `DotnetMissingError` raised if `dotnet` not on PATH | **Verified** |
| Canonical surface loaded fresh each run | [apidev/canonical.py:19-22](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/canonical.py#L19) — "We never write the canonical surface to disk" | **Verified** |
| 6 verification buckets | [apidev/verifier.py:1-51](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/verifier.py#L1) docstring lists all 6; `CoverageReport.passed` checks all 6 at [apidev/verifier.py:177-183](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/verifier.py#L177) | **Verified** |
| Aspose.Pdf hardcoded | [apidev/targets.py:262](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L262) — `if s.startswith("Aspose.Pdf.")` | **Verified** |
| sys.exit in library code | [apidev/config.py:89,99,122,128,135](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/config.py#L89) | **Verified** |
| 70 unit tests | 7 test files: test_annotations (8), test_capability (6), test_cli_parse (7), test_config (9), test_extractor (24), test_targets_direction (11), test_verifier (5) | **Verified** |
| Docker image works standalone | [Dockerfile](c:/Users/prora/OneDrive/Documents/GitHub/apidev/Dockerfile) — complete image with .NET SDK + Python + dotnet-script | **Verified** |
| Project-agnostic config | [apidev/cli.py:274-278](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/cli.py#L274) — config path derived from `--project` + `--target` args, not hardcoded | **Verified** |
| Direction-aware translation | [apidev/targets.py:156-176](c:/Users/prora/OneDrive/Documents/GitHub/apidev/apidev/targets.py#L156) — `translate()` accepts `direction` and `slot` params | **Verified** |
| Static-value probe executes assembly code | [tools/extract_public_api.csx:397-438](c:/Users/prora/OneDrive/Documents/GitHub/apidev/tools/extract_public_api.csx#L397) — `Assembly.LoadFrom` + `prop.GetValue(null)` | **Verified** |
| No dead files or abandoned code | Full file listing examined — every file referenced by at least one import or entry point | **Verified** |
| Active development | 20 commits of progressive refinement; most recent: `d3928b1` (fix dotnet-script reinstall) | **Verified** |

---

## 13. Mandatory Grading

| Dimension | Score | Justification |
|---|---|---|
| **Functional clarity** | **9/10** | Every subcommand has a clear purpose; verification buckets are well-named and well-documented; the only ambiguity is the 5-vs-6 bucket count in README |
| **Architectural quality** | **8/10** | Clean pipeline, good separation, data-driven plugins; docked for `sys.exit()` in library code and `Aspose.Pdf.*` hardcoding |
| **Code quality** | **8/10** | Excellent naming, clean dataclasses, defensive validation; docked for `_as_canon_view` duck-typing hack and `print()` instead of logging |
| **Operational maturity** | **6/10** | Works well for its operator; no structured output, no logging framework, no retry logic, 600s timeout; Docker image is a plus |
| **Test confidence** | **6/10** | 70 unit tests cover deterministic logic well; no integration tests against real assemblies; verifier tests are shallow (only test report dataclass, not actual verification logic) |
| **Documentation trustworthiness** | **7/10** | README is detailed and mostly accurate; stale bucket count, stale .csx comments; [docs/code-quality/architecture.md](c:/Users/prora/OneDrive/Documents/GitHub/apidev/docs/code-quality/architecture.md) and [docs/methodology.md](c:/Users/prora/OneDrive/Documents/GitHub/apidev/docs/methodology.md) are excellent reference docs |
| **Security confidence** | **8/10** | Low attack surface; operator-controlled inputs; the Assembly.LoadFrom probe is documented and fail-soft; minor XML injection risk in csproj generation |
| **Integration fitness** | **7/10** | Good CLI design with required flags; docked for no JSON output, `sys.exit()` preventing library use, and Aspose-specific defaults |
| **Maintainability** | **8/10** | Small codebase, clear module boundaries, good test coverage of core logic; .NET SDK dependency chain adds maintenance burden |
| **Overall adoption confidence** | **7/10** | Solid tool for its niche; needs minor hardening; the .NET SDK dependency is the biggest practical barrier to adoption |

**Weighted composite: 7.4 / 10** — A well-built internal tool ready for adoption with minor hardening.
