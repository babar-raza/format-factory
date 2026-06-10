# Deep Reverse Engineering Assessment: refdev
## Capability-Catalog-Driven Body Generator
**Date:** 2026-06-10 | **Repository:** `refdev` (GitHub)
**Review type:** Deep reverse engineering — code-first, evidence-based
**Authored by:** Claude Code agent (Opus 4.6) at operator request
**Source of truth:** Codebase at `c:\Users\prora\OneDrive\Documents\GitHub\refdev` (commit `413c9ae`, branch `main`, clean)

---

## 1. Executive Verdict

**refdev** is a Python 3.11 CLI tool that uses LLMs (primarily self-hosted Qwen, optionally Anthropic Claude) to generate target-language implementation files ("bodies") for public API classes. It takes a YAML capability catalog describing a class's shape, an idiomatic header authored by a human, and foundation primitive sources, then asks an LLM to write the glue code that binds the header to the foundation. It compile-checks the result, retries on failure with error feedback, and optionally runs hand-authored smoke tests.

The project is **real, coherent, and well-engineered** for a v0.1.0 tool by a single author. It solves a genuine problem — automating the tedious body-file authoring step in a multi-language FOSS library pipeline (specifically Aspose.PDF FOSS across C++, C#, TypeScript, Python, Java). The architecture is clean: a deterministic orchestrator drives a single LLM-calling agent, with compile-check and verify stages as quality gates. The code quality is above average — good separation of concerns, defensive error handling, thorough docstrings, and ~60 real tests covering the pure-function layer.

**However**, it is tightly coupled to one product (Aspose.PDF FOSS), uses `requests` for raw HTTP LLM calls rather than official SDKs, hardcodes macOS Homebrew paths for C++ linker flags, has no packaging (`setup.py`/`pyproject.toml`), and cannot be pip-installed. It's a single-author internal tool at v0.1.0 — not a general-purpose library. **You should care about it** if you operate in a similar methodology (catalog-driven code generation with LLM + compile gates), but adoption requires understanding its specific Aspose.PDF/LibForge assumptions.

---

## 2. Project Identity

| Aspect | Detail |
|--------|--------|
| **Project type** | CLI automation tool (LLM-assisted code generator) |
| **Intended users** | A single operator (Dmitry Letuchy) running body composition for Aspose.PDF FOSS libraries |
| **Core problem** | Automate writing implementation files that bridge idiomatic public headers to frozen foundation primitives across 5 target languages |
| **Real maturity** | v0.1.0, single author, active development (commits through June 2026), pre-1.0 |
| **Operational shape** | Local CLI or Docker container; depends on external LLM endpoint + external project repos mounted at runtime |
| **Primary language** | Python 3.11+ |
| **Dependencies** | PyYAML, python-dotenv, requests, pytest |
| **Target languages** | C++, C#, TypeScript, Python, Java (5 plugins) |
| **Total source** | ~4,700 LOC (refdev/), ~1,790 LOC (tests/) |

---

## 3. What the Project Actually Does

### Plain English
refdev takes a YAML description of a class (what methods it has, what types they use) and a hand-authored header file for that class, then asks an LLM to write the implementation file that makes the header work by calling "foundation" primitives (lower-level building blocks). If the generated code doesn't compile, it shows the compiler errors to the LLM and asks again. If the compiled code fails its smoke test, it feeds the test output back and retries again.

### Main Capabilities
1. **`compose`**: Generate a body file for a capability. Retry up to N times on compile failure with error feedback.
2. **`verify`**: Compose + build a full executable linking body + foundation + test, run it, report pass/fail. Retry with runtime feedback.
3. **Multi-target**: Supports C++, C#, TypeScript, Python, Java through a plugin system.
4. **Metrics reporting**: Optional POST to an org dashboard with token usage and success/failure stats.

### Main Outputs
- `<lib>/src/public/<name>.<ext>` — the composed body file (persistent, committed to lib repo)
- `<name>.FAILED.txt` — raw LLM response on exhaustion (for operator inspection)
- `<lib>/build/<target>/<name>_test` — verifier-built test executable (transient)
- Metrics events (HTTP POST, optional)

### What It Does NOT Do
- Does NOT generate foundation primitives (that's SpecDev)
- Does NOT author headers/surfaces (those are hand-authored)
- Does NOT write tests (those are hand-authored alongside headers)
- Does NOT manage dependencies or build systems for the target libraries
- Does NOT work without an external LLM endpoint
- Does NOT work without the external Feedstock/API project repos

---

## 4. How It Actually Works

### True Entrypoints

| Entrypoint | File | Line | Context |
|-----------|------|------|---------|
| Primary CLI | `refdev/cli.py` | `main()` at L232 | `python3 -m refdev.cli` |
| Docker | `Dockerfile` | L31 | `ENTRYPOINT ["python3", "-m", "refdev.cli"]` |
| Shell wrappers | `scripts/compose.sh`, `scripts/verify.sh` | — | Read `REFDEV_PROJECT` env var |
| Tests | `tests/` | — | `python3 -m pytest tests/` |

### End-to-End Flow: `refdev verify document --target cpp --project /path/to/api`

```
CLI (cli.py:main, L232)
  |-- build_parser().parse_args()
  |-- load_config(tool_config, project_config, "cpp", llm_name)
  |     |-- Read targets/cpp.yaml (LLM tuning: max_tokens=16384, temp=0.2, retries=5)
  |     |-- Read <project>/.refdev/cpp.yaml (output, foundation_src paths)
  |     |-- Read <project>/targets/cpp.yaml (header subdir, compiler flags)
  |     '-- load_dotenv(llm/qwen.env) -> TOKEN, LLM, MODEL
  |-- RunStats context set (metrics accumulator)
  '-- _verify_one_with_feedback_loop(cfg, "document", args) (cli.py:96)
        |-- Check if body_file exists on disk -> reuse or compose
        |-- compose_capability(cfg, "document") (orchestrator.py:56)
        |     |-- _load_inputs(): read capability.yaml, manifest.yaml, header, foundation headers
        |     '-- LOOP (up to max_retries=5):
        |           |-- compose_attempt() (agent_composer.py:74)
        |           |     |-- _build_system_prompt(): load composer-system.md + optional adapter
        |           |     |-- _build_user_prompt(): template with class, methods, deps, feedback
        |           |     |-- call_llm() (llm.py:22): HTTP POST to LLM endpoint
        |           |     |-- _parse_files(): regex extract ```lang:filename blocks
        |           |     '-- _compile_check(): target plugin runs clang++ -fsyntax-only
        |           |-- If ok -> _persist() -> write body file -> return ComposeResult
        |           '-- If fail -> carry stderr as retry_feedback -> next attempt
        |-- verify_capability(cfg, "document", body_file) (verifier.py:37)
        |     |-- Plugin dispatch -> _verify_capability_cpp()
        |     |-- Load capability + manifest, walk transitive deps
        |     |-- Collect foundation .cpp files (transitive include walk)
        |     |-- Collect sibling bodies
        |     |-- _warn_missing_capability_deps() (pre-flight check)
        |     |-- Build: clang++ body + siblings + foundation + test -> executable
        |     '-- Run: execute binary, capture stdout/stderr
        |-- If verify passes -> return (True, False)
        '-- If verify fails -> LOOP (verify_retries=2):
              |-- compose_capability(cfg, "document", verify_feedback=v.output)
              |-- verify_capability(cfg, "document", new_body)
              '-- If passes -> return (True, False)
```

### Component Map

| Module | LOC | Responsibility | Key Functions |
|--------|-----|---------------|---------------|
| `refdev/agent_composer.py` | ~1423 | LLM prompt assembly, call, response parsing, compile-check dispatch (5 targets) | `compose_attempt()` L74, `_build_system_prompt()` L151, `_build_user_prompt()` L167, `_parse_files()` L106, `_compile_check()` L115 |
| `refdev/verifier.py` | 1071 | Build + run smoke tests per target | `verify_capability()` L37, `_verify_capability_cpp()` L50, `_verify_capability_csharp()` L462, `_verify_capability_typescript()` L727, `_verify_capability_python()` L843, `_verify_capability_java()` L970 |
| `refdev/targets.py` | 432 | Plugin registry | `TargetPlugin` dataclass L32, `register()` L144, `get()` L150, `_register_builtins()` L419 |
| `refdev/config.py` | 374 | Config loading — tool/project/target YAML merge, path resolution, env loading | `Config` dataclass L37, `load_config()` L277, `body_file()` L253 |
| `refdev/api_targets.py` | 387 | Canonical .NET FQN -> target type translation + drops | `ApiTargetPlugin` L97, `translate()` L116, `is_dropped()` L193 |
| `refdev/cli.py` | 246 | Argparse CLI, command dispatch, metrics lifecycle | `main()` L232, `cmd_compose()` L28, `cmd_verify()` L55, `_verify_one_with_feedback_loop()` L96 |
| `refdev/metrics.py` | 174 | Agent Metrics v1 HTTP POST (optional) | `RunStats` L71, `report()` L96, `CURRENT_RUN_STATS` ContextVar L90 |
| `refdev/orchestrator.py` | 164 | Deterministic retry loop, input loading, persistence | `compose_capability()` L56, `_load_inputs()` L99, `_persist()` L145 |
| `refdev/manifest.py` | 140 | Manifest YAML loader | `Manifest` L63, `MethodKey` L43, `load_manifest()` L84 |
| `refdev/capability.py` | 144 | Capability YAML loader | `Capability` L65, `CapabilityMember` L43, `load_capability()` L77 |
| `refdev/llm.py` | 119 | Raw HTTP client for Anthropic + OpenAI-compatible endpoints | `call_llm()` L22, `_clean_response()` L113 |
| `refdev/prompts.py` | 15 | Simple file loader from `prompts/` dir | `load_prompt()` L7 |
| `refdev/__init__.py` | 14 | Package marker, registers built-in plugins | `_targets._register_builtins()` L13 |

### Data Flow
```
YAML files (capability, manifest, config) -> Python dataclasses
  + Header text (read from disk)
  + Foundation headers (read from disk)
  -> Prompt assembly (template + rendered members/deps/feedback)
  -> LLM HTTP POST -> raw text response
  -> Regex parse -> {filename: contents} dict
  -> Compile-check (subprocess: clang++/dotnet/tsc/mypy/javac)
  -> Body file written to disk
  -> Verify (subprocess: build + run test executable)
  -> VerifyResult (ok, output text)
  -> Metrics HTTP POST (optional)
```

### State and Persistence
- **No database, no cache, no queue.** Pure file I/O + HTTP.
- Body files are persistent (committed to target lib repo).
- FAILED.txt files are persistent (operator inspection).
- Build artifacts in `build/<target>/` (transient, not committed).
- Config is read-only. Capability/manifest YAMLs are read-only.
- RunStats accumulated in ContextVar (thread-local, per-process).

### External Integrations
1. **LLM endpoint** (required): Anthropic API or OpenAI-compatible (Qwen). Raw `requests.post` — see `refdev/llm.py:37-74`.
2. **Metrics endpoint** (optional): HTTP POST to org dashboard — see `refdev/metrics.py:139-145`. Silent skip if `METRICS_URL` unset.
3. **Compiler toolchains** (required per target): clang++, dotnet, tsc, mypy, pytest, gradle/javac.
4. **External project repos** (required): Feedstock/PDF/API (capability catalog) + FOSS lib repos (headers, foundation, tests).

---

## 5. Architecture Judgment

### Actual Architecture Style
**Pipeline with plugin dispatch.** Three clean stages (orchestrate -> compose -> verify) with a target-plugin registry that avoids if/else chains on language strings. The only LLM-calling module is clearly marked (`agent_composer.py`). Everything else is deterministic.

### Strong Patterns

1. **Single LLM boundary** (`refdev/agent_composer.py`): Only module that calls the LLM via `llm.py`. All other modules are deterministic. This is the most important architectural decision and it's done correctly.

2. **Feedback loop design** (`orchestrator.py:80-96`, `cli.py:142-158`): Compile errors -> retry prompt, verify failures -> compose-with-feedback. Clean channel design.

3. **Plugin system** (`refdev/targets.py`): `TargetPlugin` frozen dataclass with callable fields avoids inheritance complexity. Adding a target is one plugin + one YAML.

4. **Config separation** (`refdev/config.py:277-373`): Tool config (LLM tuning) vs project config (paths) prevents cross-contamination.

5. **Soft-skip pattern** (verifiers): When toolchain is missing, verifiers return `ok=True` with a message (e.g., `verifier.py:470-472` for dotnet, `verifier.py:765-771` for tsc/vitest). Compose-gate hard-fails (catches real errors).

6. **ContextVar for metrics** (`refdev/metrics.py:90-91`): Avoids threading stats through every function signature. `llm.py:103-108` reads and increments it.

7. **Defensive metrics** (`refdev/metrics.py:139-158`): Network failure logged but never raised into pipeline.

### Weak Patterns

1. **Giant modules**: `agent_composer.py` at ~1423 LOC contains compile-check implementations for all 5 targets, prompt rendering, response parsing, and the attempt logic. `verifier.py` at 1071 LOC has five language-specific verify implementations.

2. **Private function imports across modules**: `orchestrator.py:38-39` imports `_output_filename` and uses `_collect_foundation_deps` (private by convention) from `agent_composer.py`. `targets.py:169-175` imports private functions like `_compile_check_cpp`, `_verify_capability_cpp`, etc.

3. **Duplicate `_to_pascal` lambdas**: Defined independently in `targets.py:209`, `targets.py:258`, and `targets.py:376`. Should be a shared utility.

### Coupling Analysis
- **Loose coupling between stages**: Orchestrator <-> Composer communicate via `AttemptResult` dataclass (`agent_composer.py:59-66`). Orchestrator <-> Verifier communicate via `VerifyResult` (`verifier.py:32-34`). Clean.
- **Tight coupling to Aspose.PDF**: Hardcoded in `metrics.py:126` (`"Aspose.PDF FOSS for {lang}"`), in Python test path conventions (`targets.py:332`: `aspose_pdf_foss/_public/test_{c}`), and in the Java package path (`verifier.py:1019`: `"com" / "aspose" / "pdf" / "foss" / "_public"`).
- **Tight coupling to macOS/Homebrew**: `_LINK_LIB_FLAGS` in `verifier.py:366-379` hardcodes `/opt/homebrew/` paths for OpenSSL, libjpeg, openjpeg, libtiff.

### Fragility Points

1. **Regex-based response parsing** (`agent_composer.py:52-55`, `_FENCE_RE`): If the LLM omits the `:filename` tag or uses an unlisted language tag, the body silently fails to parse.

2. **`load_dotenv(override=True)`** in `config.py:368`: Overrides ALL env vars from the .env file, including any `PATH` or `HOME` the process inherited. Global side effect.

3. **Attribute name bug** in `verifier.py:266`: References `cfg.capabilities_dir` but `Config` (config.py:42) only has `capability_dir` (no trailing 's'). Falls back to hardcoded `cfg.capability_file("document").parent` at line 270.

### Dead/Suspicious Zones

| Item | Location | Issue |
|------|----------|-------|
| `llm/` directory | Referenced in config YAMLs | Empty in repo (expected — holds .env files at runtime) |
| No packaging | Root directory | No `setup.py`, `pyproject.toml`, or `setup.cfg` |
| `SECURITY.md` | Root directory | Placeholder disclosure policy, not security analysis |
| `__init__.py` docstring | `refdev/__init__.py:4` | Says "cpp, csharp" but 5 targets exist |
| `rust` and `go` | `metrics.py:58-59`, `agent_composer.py:53` | In `_LANG_DISPLAY` dict and `_FENCE_RE` pattern but have no registered plugins |

---

## 6. Code and Engineering Assessment

### What Is Well Written

- **Docstrings**: Every module, class, and significant function has thorough docstrings explaining not just what but *why*. Examples: `orchestrator.py:1-29`, `cli.py:55-77`, `verifier.py:190-248`. These are among the best docstrings I've seen in a project this size.

- **Data models**: `Config` (`config.py:37`), `Capability` (`capability.py:65`), `Manifest` (`manifest.py:63`), `AttemptResult` (`agent_composer.py:59`), `ComposeResult` (`orchestrator.py:48`), `VerifyResult` (`verifier.py:32`), `TargetPlugin` (`targets.py:32`) — well-chosen dataclasses with clear fields.

- **Error messages**: Every error path includes the file path, the expected state, and a hint. E.g., `capability.py:90`: `"capability {path} missing required key {key!r} (v2 schema -- re-seed via apidev seed --force)"`.

- **Test architecture** (`tests/`): Tests are well-organized — pure helper tests (no LLM, no toolchain) cover the critical logic. Integration test for C# verify (`test_pipeline_csharp.py`) uses a synthetic workspace with `_make_workspace()`. Tests are properly skipped when toolchain is missing (`test_pipeline_csharp.py:31-33`).

- **Manifest design** (`manifest.py:43-58`): The `MethodKey(name, params_tuple)` approach for overload disambiguation is clever and correct.

- **ContextVar metrics** (`metrics.py:90-91`): Clean alternative to threading stats through every function call.

### What Is Badly Written

- **Global side effect in config** (`config.py:368`): `load_dotenv(cfg.env_file, override=True)` followed by `os.getenv("TOKEN")` (`config.py:369`) mutates the global process environment. If you load two different configs in one process, the second's env vars override the first's.

- **No type hints on callables in TargetPlugin** (`targets.py:55-88`): The `compile_check`, `verify_capability` etc. use `Callable[..., ...]` with `object` placeholders rather than proper types.

- **Hardcoded Homebrew paths** (`verifier.py:366-379`): `_LINK_LIB_FLAGS` hardcodes `/opt/homebrew/opt/openssl/`, `/opt/homebrew/include/`, `/opt/homebrew/lib/` — only works on macOS with Homebrew. Linux, Windows, and even macOS without Homebrew will fail.

- **Hardcoded csharp xUnit environment PATH** (`verifier.py:623-628`): Sets `PATH` to `"/usr/bin:/bin"` — will fail on Windows or any non-standard Linux layout. Same issue in TypeScript verifier (`verifier.py:780-787`) and Python verifier (`verifier.py:899-903`).

### What Is Risky

1. **No input sanitization on subprocess calls**: Capability names, file paths, and foundation dep names flow into `subprocess.run()` argument lists. While using list-form args (not `shell=True`) mitigates command injection, malicious YAML file paths could still cause issues.

2. **LLM token exposed in plaintext**: Token is read from `.env` file (`config.py:369`) and passed in HTTP headers (`llm.py:51`, `llm.py:70`). No encryption, no credential manager.

3. **No rate limiting**: The retry loop (`orchestrator.py:80`) can fire up to `max_retries` compose attempts in rapid succession with no backoff.

4. **`sys.stdout.reconfigure(line_buffering=True)`** called at module import time in `orchestrator.py:44`, `agent_composer.py:45`, `verifier.py:28`. Global side effect affecting any code importing these modules.

### What Is Deceptive or Unclear

- The README's "three-layer picture" sounds like three independent tools, but refdev can't function without SpecDev and ApiDev output files on disk. It's not standalone — it's part of a larger pipeline.

- "project-agnostic" claim in docs: while the Config split is clean, the Java verifier hardcodes `com/aspose/pdf/foss/_public/` (`verifier.py:1019`), the Python test paths hardcode `aspose_pdf_foss/_public/` (`targets.py:332`), and metrics hardcode "Aspose.PDF FOSS" (`metrics.py:126`). The architecture is project-agnostic but the implementation is Aspose-specific.

### What Will Become Expensive to Maintain

- **`agent_composer.py` at ~1423 LOC**: Contains per-target compile-check, copy, render, and scan functions for 5 languages. Each new target adds ~100-150 LOC to this file.
- **`verifier.py` at 1071 LOC**: Same issue — each new target adds a full verify function (~100 LOC).
- **The prompt templates** (`prompts/`): Any change to the LLM contract (output format, fencing convention) requires updating 7 prompt files + the regex + per-target adapters.

---

## 7. Reality vs Claims

### Verified Truths

| Claim | Evidence |
|-------|----------|
| "Only the composer calls the LLM" | Verified: only `agent_composer.py` calls `call_llm()`, only `llm.py` makes HTTP requests to LLM endpoint |
| "Two commands: compose and verify" | Verified: `build_parser()` in `cli.py:165-216` registers exactly these two subcommands |
| "Retry loop with compile-error feedback" | Verified: `orchestrator.py:80-96` loops, `retry_feedback=last_error` at L84 |
| "5 target languages" | Verified: `_register_builtins()` in `targets.py:419-431` registers cpp, csharp, typescript, python, java |
| "Missing manifest -> empty manifest" | Verified: `manifest.py:87-88`, `if not path.exists(): return empty_manifest()` |
| "Metrics are optional and defensive" | Verified: `metrics.py:108` checks `METRICS_URL`, `metrics.py:153` catches all `RequestException` |
| "Bodies are persistent artifacts" | Verified: `_persist()` at `orchestrator.py:145-152` writes to `cfg.body_output_dir`, reused on next verify run |

### Partially True Claims

| Claim | Reality |
|-------|---------|
| "project-agnostic" | Architecture is, but implementation has Aspose.PDF-specific paths hardcoded in Java/Python verifiers and metrics |
| "Cpp + csharp plugins ship in-tree" | `__init__.py` docstring says this, but actually all 5 plugins ship in-tree (typescript, python, java too) |
| "Adding a new target is a single plugin entry" | True for the plugin, but you also need: adapter prompt, target YAML, project-side config, API translation YAML + drops YAML, and the external lib repo with headers/tests |

### False or Misleading Claims

None found. Documentation is unusually honest and accurate.

### Important Undocumented Realities

1. **Bug**: `verifier.py:266` references `cfg.capabilities_dir` but Config has `capability_dir` (no 's'). The fallback at L270 (`cfg.capability_file("document").parent`) hardcodes "document".
2. **macOS-only C++ linking**: `_LINK_LIB_FLAGS` at `verifier.py:366-379` hardcodes Homebrew paths. Undocumented.
3. **C#/TS/Python verifier PATH restriction**: Sets PATH to `/usr/bin:/bin` (Unix-only) at `verifier.py:624`, `verifier.py:785`, `verifier.py:899`. Undocumented.
4. **`load_dotenv(override=True)`** at `config.py:368` has process-global side effects. Undocumented.
5. **rust/go in metrics `_LANG_DISPLAY`** (`metrics.py:58-59`) and fence regex: Placeholder for future targets that don't exist. May confuse adopters.

---

## 8. Operational Readiness

### Run Requirements
- **Python 3.11+** (uses `|` union types throughout)
- **PyYAML, python-dotenv, requests** (`requirements.txt`)
- **LLM endpoint** with TOKEN/URL/MODEL in a `.env` file under `llm/`
- **Target toolchain**: clang++ (cpp), dotnet SDK 8.0 (csharp), node+npm (typescript), Python venv with mypy+pytest (python), JDK 17 + Gradle (java)
- **External repos**: Feedstock/PDF/API tree + target library repos, mounted or on filesystem

### Deployment Assumptions
- Single operator, local machine or Docker
- LLM endpoint accessible over HTTPS
- macOS with Homebrew (for C++ external lib linking)
- GitLab CI for lint + unit tests only (no integration tests in CI)

### Failure Behavior

| Failure | Handling | Location |
|---------|----------|----------|
| LLM timeout/error | Returns None, attempt fails, retries continue | `llm.py:75-77` |
| Compile failure | Captured stderr feeds into next retry prompt | `orchestrator.py:84` |
| Toolchain missing | Compile-check hard-fails; verifier soft-skips | Various per-target |
| Metrics failure | Logged to stderr, never raises | `metrics.py:153-156` |
| Config file missing | Hard exit with `sys.exit(1)` | `config.py:292-296` |
| No crash-recovery | Each run is stateless | N/A |

### Observability
- **Stdout**: Progress messages (`print()` calls throughout)
- **Stderr**: Warnings (missing capability deps), metrics errors
- **Metrics**: Optional HTTP POST with token usage, duration, success/failure
- **No structured logging**: All output is `print()` calls
- **No log levels**: Can't increase/decrease verbosity

### Reliability
- **Idempotent**: Re-running compose on the same inputs produces same output (modulo LLM variance)
- **No partial-write protection**: Body file written directly at `orchestrator.py:150`, not via atomic rename
- **No lock files**: Two concurrent refdev processes could overwrite each other's body files

### Security
- **LLM token in plaintext `.env` files**: No credential management
- **subprocess calls**: List-form (not `shell=True`) — mitigates command injection
- **No user-supplied code execution**: LLM output is written to disk and compiled, not eval'd
- **YAML `safe_load` used consistently**: No YAML deserialization attacks (e.g., `config.py:298`, `capability.py:82`, `manifest.py:90`)
- **Metrics token passed as query parameter** (`metrics.py:142`): Visible in server logs

### Scalability
- **Single-threaded, single-process**: No parallelism
- **One LLM call per attempt**: Sequential, blocking
- **Scales by target x capability count**: For N capabilities x 5 targets, that's 5N sequential LLM calls minimum

---

## 9. Workflow-Fit Analysis

### Best-Fit Uses
- **Identical methodology**: If you use the same LibForge approach (capability catalog -> header -> body generation), this is purpose-built for it.
- **LLM-assisted code generation with compile gates**: The compose -> compile-check -> retry loop is a well-proven pattern reusable in other code generation scenarios.
- **Study as reference architecture**: The feedback loop design (LLM -> compile -> error feedback -> retry) is worth studying for any LLM code generation project.

### Moderate-Fit Uses
- **Different product, same methodology**: Refactoring out Aspose-specific hardcodings would make it usable for other products.
- **Different LLM provider**: The dual Anthropic/OpenAI-compatible client (`llm.py:35-74`) handles most providers.

### Poor-Fit Uses
- **General-purpose code generation**: This is not Copilot or aider. It generates one specific type of code (body files binding headers to foundation).
- **Non-YAML-catalog workflows**: If your API shape isn't described in a capability catalog, the input pipeline doesn't fit.
- **Windows-native development**: PATH restrictions, Homebrew paths, and Unix assumptions throughout the verifiers make Windows a poor fit.

### Prerequisites for Adoption
1. Adopt or adapt the LibForge methodology (capability catalog + manifests + idiomatic headers)
2. Have a working LLM endpoint (Qwen self-hosted or Anthropic API key)
3. Have target toolchains installed (per target language)
4. Create project-side config files (`.refdev/<target>.yaml`)
5. Create API target translation files (`translations.yaml` + `drops.yaml`)

---

## 10. Adoption Recommendation

### Adopt only selected parts

**Justification:**

The project is tightly coupled to the Aspose.PDF FOSS pipeline. Adopting it wholesale means inheriting:
- Aspose-specific hardcodings in metrics, paths, and package conventions
- macOS/Homebrew-only C++ linking
- A single-author codebase with no packaging or installation mechanism
- A methodology dependency (LibForge/SpecDev/ApiDev) that you may not use

**What to adopt:**

1. **The architecture pattern** (orchestrator -> LLM agent -> verifier with compile-gate feedback loop). This is the highest-value intellectual property in the project.
2. **The plugin system design** (`TargetPlugin` dataclass with callable dispatch at `targets.py:32-138`). Clean and extensible.
3. **The prompt engineering approach** (base system prompt + per-target adapter, structured user prompt with capability/header/deps/feedback sections — see `prompts/`).
4. **The retry-with-feedback pattern** (compile stderr -> prompt at `orchestrator.py:84`, test output -> prompt at `cli.py:146`).

**What to leave behind:**
- The Aspose.PDF-specific implementations
- The raw `requests` HTTP client (use official SDKs)
- The macOS-only link flags
- The `load_dotenv(override=True)` pattern

---

## 11. Top Gaps and Fixes

### Most Important Fixes Before Serious Use

| Priority | Issue | Location | Fix |
|----------|-------|----------|-----|
| **P0** | `capabilities_dir` attribute bug | `verifier.py:266` | Change to `cfg.capability_dir` (the actual attribute on `Config` at `config.py:42`) |
| **P0** | macOS Homebrew hardcoded paths | `verifier.py:366-379` | Use `pkg-config` or config-driven approach; currently breaks on Linux/Windows |
| **P1** | Unix-only PATH in verifiers | `verifier.py:624`, `verifier.py:785`, `verifier.py:899` | Add Windows support or document Unix-only requirement |
| **P1** | No atomic file writes | `orchestrator.py:150` | Use write-to-temp + `os.rename()` to prevent partial writes |
| **P1** | `load_dotenv(override=True)` global side effect | `config.py:368` | Read .env file manually, pass values to Config directly |

### Highest-Value Refactors

| Refactor | Impact | Effort |
|----------|--------|--------|
| Split `agent_composer.py` (~1423 LOC) | Per-target compile-check/render functions into plugin modules | Medium |
| Split `verifier.py` (1071 LOC) | Per-target verify functions into separate files | Medium |
| Add `pyproject.toml` | Enable pip install, entry point scripts, dependency management | Low |
| Replace raw `requests` with Anthropic SDK | Better error handling, streaming support, API compatibility | Low |
| Extract shared `_to_pascal()` utility | Remove duplicate lambda definitions at `targets.py:209,258,376` | Trivial |

### Fastest Path to a Safe Pilot

1. Fix the `capabilities_dir` bug (5 minutes)
2. Document the macOS-only requirement for C++ linking OR add pkg-config fallback
3. Set up your Feedstock directory structure with one test capability
4. Create `.refdev/<target>.yaml` for your project
5. Point at an LLM endpoint via `llm/<profile>.env`
6. Run `python3 -m refdev.cli --target <lang> --project <path> compose <capability>`

### Highest-Risk Assumptions to Verify First

1. **LLM quality**: The entire system depends on the LLM generating compilable code. Test with your specific LLM endpoint/model before committing to the approach.
2. **Foundation primitives exist and are frozen**: refdev assumes foundation code is stable and correct. If it's not, the generated bodies will be wrong.
3. **Smoke tests are meaningful**: refdev treats "test passes" as "body is correct". The quality of the output is only as good as the smoke tests.

---

## 12. Evidence Appendix

### Major Conclusions with Evidence

| Conclusion | Evidence | File:Line | Status |
|-----------|----------|-----------|--------|
| Only one module calls LLM | `agent_composer.py` imports `call_llm`, no other module does | `agent_composer.py:42` | **Verified** |
| Retry loop carries compile errors forward | `retry_feedback=last_error` | `orchestrator.py:84` | **Verified** |
| 5 target plugins registered | `_register_builtins()` registers cpp, csharp, typescript, python, java | `targets.py:419-431` | **Verified** |
| macOS-only C++ linking | Hardcoded `/opt/homebrew/` paths | `verifier.py:366-379` | **Verified** |
| `capabilities_dir` attribute bug | `cfg.capabilities_dir` used but Config only has `capability_dir` | `verifier.py:266` vs `config.py:42` | **Verified** |
| `load_dotenv(override=True)` global side effect | Mutates `os.environ` | `config.py:368` | **Verified** |
| No packaging mechanism | No `setup.py`, `pyproject.toml`, or `setup.cfg` in repo root | — | **Verified** |
| Tests cover pure helpers, not LLM calls | All 8 test files test parsers, renderers, loaders; none call `call_llm` | `tests/` | **Verified** |
| Single author | `CODEOWNERS` file | `CODEOWNERS`: all `@dmitry.letuchy` | **Verified** |
| Metrics hardcode Aspose.PDF | String literal in report payload | `metrics.py:126` | **Verified** |
| Java verifier hardcodes package path | Hardcoded directory segments | `verifier.py:1019` | **Verified** |
| Response parsing is regex-based | `_FENCE_RE` regex pattern | `agent_composer.py:52-55` | **Verified** |
| Manifest missing -> empty manifest | `if not path.exists(): return empty_manifest()` | `manifest.py:87-88` | **Verified** |
| ContextVar for metrics accumulation | `CURRENT_RUN_STATS` ContextVar read in `call_llm` | `metrics.py:90`, `llm.py:103-108` | **Verified** |
| YAML safe_load used everywhere | `yaml.safe_load()` in all loaders | `config.py:298`, `capability.py:82`, `manifest.py:90`, `api_targets.py:286` | **Verified** |

---

## Mandatory Grading

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Functional clarity** | 8/10 | Clear what it does, how it works, and what the boundaries are. Every module has good docstrings. Minor unclear areas around multi-project use. |
| **Architectural quality** | 8/10 | Clean pipeline, single LLM boundary, good plugin system, feedback loop design. Loses points for giant modules (`agent_composer.py` 1423 LOC, `verifier.py` 1071 LOC). |
| **Code quality** | 7/10 | Good naming, good error messages, defensive patterns. Loses points for global side effects (`load_dotenv`, `stdout.reconfigure`), private cross-module imports, duplicate `_to_pascal`, and the `capabilities_dir` bug. |
| **Operational maturity** | 4/10 | No packaging, no structured logging, no parallelism, no atomic writes, no lock files, no rate limiting. Single-threaded, single-operator tool. macOS-only for C++ linking. |
| **Test confidence** | 6/10 | ~60 tests covering pure helpers and one integration test (C# pipeline). No tests for the LLM call path. No tests for cpp/typescript/python/java verify paths. |
| **Documentation trustworthiness** | 9/10 | Unusually honest and accurate. `docs/architecture.md` matches code. README matches CLI. Only minor discrepancy (`__init__.py` says "cpp, csharp" when 5 targets exist). |
| **Security confidence** | 5/10 | No credential management, plaintext tokens in .env files, metrics token as query param. Subprocess calls use list-form (good). YAML uses `safe_load` (good). No user input reaches exec/eval. |
| **Integration fitness** | 4/10 | Tightly coupled to Aspose.PDF FOSS methodology. No packaging. macOS-only for some paths. Would require significant adaptation for other workflows. High value as reference architecture. |
| **Maintainability** | 7/10 | Good structure, good docs, good tests for a solo project. Plugin system makes adding targets mechanical. Giant modules and private cross-module imports are the main maintenance risks. |
| **Overall adoption confidence** | 5/10 | Excellent as reference architecture and for understanding the methodology. Would require significant hardening for different contexts. For its intended single-operator use case, it works well. |

---

## File Inventory

### Source Modules (refdev/)

| File | Lines | Purpose |
|------|-------|---------|
| `refdev/__init__.py` | 14 | Package marker, registers built-in plugins |
| `refdev/agent_composer.py` | ~1423 | LLM agent: prompt assembly, LLM call, response parsing, compile-check dispatch |
| `refdev/api_targets.py` | 387 | Canonical FQN -> target type translation + member drops |
| `refdev/capability.py` | 144 | Capability YAML loader (v2 canonical-faithful schema) |
| `refdev/cli.py` | 246 | Argparse CLI, command dispatch, metrics lifecycle |
| `refdev/config.py` | 374 | Config loading: tool/project/target YAML merge, path resolution |
| `refdev/llm.py` | 119 | Shared LLM HTTP client (Anthropic + OpenAI-compatible) |
| `refdev/manifest.py` | 140 | Manifest YAML loader (capability_deps, link_libs, foundation_deps) |
| `refdev/metrics.py` | 174 | Agent Metrics v1 reporter (optional HTTP POST) |
| `refdev/orchestrator.py` | 164 | Deterministic retry loop, input loading, persistence |
| `refdev/prompts.py` | 15 | Prompt file loader |
| `refdev/targets.py` | 432 | Target-language plugin registry (TargetPlugin dataclass) |
| `refdev/verifier.py` | 1071 | Build + run smoke tests per target language |

### Test Modules (tests/)

| File | Lines | Coverage |
|------|-------|---------|
| `tests/test_capability.py` | 96 | Capability YAML loading, v2 schema validation |
| `tests/test_cli_parse.py` | 79 | Argparse CLI shape, mandatory flags |
| `tests/test_composer_helpers.py` | 373 | Fenced-block parser, foundation-dep collection, member rendering, sibling scanning |
| `tests/test_config.py` | 290 | Config loading, path resolution, per-target body filenames |
| `tests/test_manifest.py` | 149 | Manifest loader, method-key overloads, missing-file handling |
| `tests/test_metrics.py` | 184 | Metrics v1 payload shape, status mapping, defensive failure |
| `tests/test_pipeline_csharp.py` | 295 | End-to-end C# verify pipeline (xUnit happy path, failures, legacy rejection) |
| `tests/test_verifier_helpers.py` | 330 | Transitive-dep walker, link-flag picker, sibling-reference pre-flight |

### Configuration

| File | Purpose |
|------|---------|
| `targets/cpp.yaml` | C++ LLM tuning (qwen, 16384 tokens, 0.2 temp, 300s timeout, 5 retries) |
| `targets/csharp.yaml` | C# LLM tuning (qwen, 16384 tokens, 0.2 temp, 600s timeout, 3 retries) |
| `targets/typescript.yaml` | TypeScript LLM tuning |
| `targets/python.yaml` | Python LLM tuning |
| `targets/java.yaml` | Java LLM tuning |
| `.env.example` | Template for METRICS_URL, METRICS_TOKEN, AGENT_OWNER |
| `.gitlab-ci.yml` | Two-stage CI: lint (compileall) + test (pytest) |
| `Dockerfile` | Python 3.11-slim + g++/cmake/make/git; ENTRYPOINT is refdev CLI |

### Prompt Templates (prompts/)

| File | Purpose |
|------|---------|
| `composer-system.md` | Base system prompt (C++-flavoured baseline) |
| `composer-system-csharp-adapter.md` | C# adapter (prepended for csharp target) |
| `composer-system-typescript-adapter.md` | TypeScript adapter |
| `composer-system-python-adapter.md` | Python adapter |
| `composer-user.md` | User prompt template (capability/header/deps/feedback placeholders) |
| `composer-retry-verify.md` | Smoke-test feedback block template |
| `composer-objects-consumer.md` | Foundation objects/content_stream invariants block |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview, three-layer picture, commands, config |
| `AGENTS.md` | Three-stage pipeline: orchestrator/composer/verifier |
| `CHANGELOG.md` | Version history |
| `CODEOWNERS` | All code owned by @dmitry.letuchy |
| `SECURITY.md` | Security disclosure policy |
| `docs/architecture.md` | System layers, config split, target plugins, pipeline flow |
| `docs/methodology.md` | LibForge positioning, two-tier LLM workflow |
