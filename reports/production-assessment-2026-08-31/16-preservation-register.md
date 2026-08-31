# 16 — Preservation Register

**Baseline commit:** dd909cf3a
**Criterion:** Runtime proof that the component produces correct output from real input under current conditions. Historical transcript claims are not proof.

## PRESERVE (proven working, valuable responsibility)

### P1: FF6 Obligation Registers
- **Location:** `plans/strategic/ff6/obligations/{format}.yaml`
- **Proof:** All 6 files parseable, obligation IDs stable, reconciler consumes them correctly
- **Proof boundary:** Structural validity and reconciler compatibility. Does NOT prove obligations are complete or current against latest spec
- **Preserve:** The register structure and obligation identity scheme
- **Risk:** Obligation set may need expansion when evidence freshness is enforced

### P2: Format Contracts
- **Location:** `shared/format-contracts/{format}.yaml`
- **Proof:** Contracts parsed by reconciler, digest-bound to SAL facts
- **Proof boundary:** Structural validity and digest binding. Contract content accuracy depends on SAL fact accuracy
- **Preserve:** Contract compilation pipeline and digest binding mechanism

### P3: Append-Only Event Journal
- **Location:** `plans/strategic/ff6/events.jsonl` (522 events)
- **Proof:** Hash chain verified (PASS). Structural integrity proven.
- **Proof boundary:** Chain integrity only. Projection semantics are NOT derivable from events (sync_projection_head is "deliberately narrow")
- **Preserve:** The append-only journal concept and hash chain integrity mechanism
- **Do NOT preserve:** The assumption that valid chain implies valid projection

### P4: Installed Package Implementations
- **Location:** `src/python/{format}/` (7 packages: core + 6 FF6)
- **Proof:** 5/6 formats demonstrate real product behavior from installed packages. 4916+ tests pass across all formats.
- **Proof boundary:** Individual package behavior. Does NOT prove certification-grade completeness.
- **Preserve:** All source code, package structure, namespace scheme (`format_factory.*`)

### P5: Contract Reconciler (structural checking only)
- **Location:** `tools/format_contract/contract_reconciler.py`
- **Proof:** Deterministic output from identical inputs. Correct structural validation (AST symbol existence, file presence, schema validation)
- **Proof boundary:** File/symbol existence checking. Does NOT verify test execution or evidence freshness.
- **Preserve:** The structural checking capability
- **Must repair:** Add test execution or hash-based freshness validation (R6)

### P6: SAL Facts Store
- **Location:** `shared/sal-facts/{format}.yaml` (14 manually-seeded formats)
- **Proof:** 14,441 facts compiled successfully. Reconciler references them via digest binding.
- **Proof boundary:** Fact compilation. Does NOT prove completeness against latest specs.
- **Preserve:** The SAL fact store and compilation pipeline

### P7: Oracle Verification Layer
- **Location:** `oracle/` (20 formats VERIFIED, 73/73 PASS)
- **Proof:** All 20 Python FOSS formats verified. Execute_oracle.py produces deterministic verdicts.
- **Proof boundary:** Gen-1 formats only. FF6 oracle coverage varies per format.
- **Preserve:** Oracle execution engine and verified test cases

### P8: Governance Validator Framework
- **Location:** `tools/governance/`, `tools/supervisor/governance_validator_runner.py`
- **Proof:** 211 validators executed, 164 PASS, 9 FAIL (real problems detected), 38 WARN
- **Proof boundary:** Detection capability proven. Enforcement NOT proven (bypass rules override blocks)
- **Preserve:** The validator framework and individual validators
- **Must repair:** Make validators fail-closed pre-execution gates (R16)

### P9: Package Build/Install Infrastructure
- **Location:** `packaging/python/package-matrix.yaml`, `src/python/*/pyproject.toml`
- **Proof:** All 7 packages install successfully via `pip install -e`
- **Proof boundary:** Editable install only. Wheel build and PyPI publication not tested.
- **Preserve:** Package metadata and build configuration

### P10: Action Queue Locking
- **Location:** `tools/supervisor/action_queue.py`
- **Proof:** Lease-based claim mechanism exists with coordination DB
- **Proof boundary:** Mechanism exists. Concurrent claim behavior under load not tested.
- **Preserve:** The locking concept for task claims

## REPAIR (proven partially, needs specific fixes)

### P11: Goal Driver
- **Location:** `tools/ff6/goal_driver.py`
- **What works:** Deterministic state reading, format enumeration, next-task computation
- **What's broken:** Reads promotion label instead of computing certification from proof (R4, R5)
- **Preserve:** State-derived (not signal-derived) architecture
- **Repair:** Replace promotion-label reading with proof-chain computation

### P12: Controller Events (sync_projection_head)
- **Location:** `tools/ff6/controller_events.py`
- **What works:** Hash chain append, integrity verification
- **What's broken:** Projection sync only covers sequence/id/hash — promotion and semantic state are manual
- **Preserve:** Append-only journal mechanism
- **Repair:** Either derive projection fully from journal or separate journal from projection authority

### P13: Evidence Store
- **Location:** `shared/format-contracts/implementation-evidence/{format}.yaml`
- **What works:** Evidence record structure, citation of test selectors
- **What's broken:** No source/test/corpus file hashing, no invalidation on change (R6)
- **Preserve:** Evidence record structure
- **Repair:** Add hash-based freshness tracking

## UNKNOWN (cannot determine from current evidence)

### P14: Plan Control Journal/Projection Concepts
- **Location:** `tools/plan_control/` (12 modules)
- **Status:** Bootstrapped but completely inert (0 plans, 0 tasks, 0 journal entries)
- **Unknown:** Whether the concepts (journal-driven projection, task coordination) are better than FF6's approach
- **Decision deferred to:** R14 (integrate or retire)

## Evidence Classification
- P1-P10: PROVEN working within stated boundaries
- P11-P13: PROVEN partially working; specific repair needed
- P14: UNKNOWN — no runtime proof available
