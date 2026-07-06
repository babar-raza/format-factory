# 02-SYSTEM-ARCHITECTURE-AND-DIAGRAMS.md

All diagrams use standard Mermaid syntax. Each diagram has a unique ID, title, purpose statement, and a reference to the claims it represents.

---

## DIAG-001: System Context

**Purpose**: Show Format Factory's position relative to external entities.
**Audience**: Technical managers, new contributors.
**Claims**: CLM-SYS-001, CLM-SYS-002

```mermaid
flowchart TB
    subgraph External["External Inputs"]
        SPECS["File Format Specifications<br/>(ODF, RFC, ISO, etc.)"]
        SAMPLES["Sample Files<br/>(per format)"]
        HUMAN["Human Approver<br/>(Babar Raza — Gate 11)"]
    end

    subgraph FF["Format Factory"]
        MACH["Machinery<br/>(tools/, .supervisor/)"]
        PROD["Products<br/>(src/python/, src/net/)"]
    end

    subgraph Consumers["Consumers"]
        PYDEV["Python Developers<br/>(pip install)"]
        NETDEV[".NET Developers<br/>(NuGet reference)"]
    end

    SPECS --> MACH
    SAMPLES --> MACH
    HUMAN -->|Gate 11 approval| MACH
    MACH -->|generates, tests, governs| PROD
    PROD --> PYDEV
    PROD --> NETDEV
```

**Legend**: Rounded rectangles = systems/entities. Arrows = data/control flow. The machinery produces the products; humans consume the products.

| Node | Description |
|---|---|
| SPECS | Format specifications from standards bodies |
| SAMPLES | Known-good sample files for each format |
| HUMAN | Business approver for commercial release |
| MACH | Development machinery (85K LOC) |
| PROD | Product libraries (77K LOC) |
| PYDEV | End-user Python developers |
| NETDEV | End-user .NET developers |

---

## DIAG-002: Repository and Subsystem Map

**Purpose**: Map the major repository directories to architectural roles.
**Audience**: Contributors, code reviewers.
**Claims**: CLM-ARCH-001

```mermaid
flowchart LR
    subgraph Product["Product Layer (L06)"]
        PY["src/python/<br/>20 formats, 54K LOC"]
        NET["src/net/<br/>10 formats, 22.6K LOC"]
    end

    subgraph Machinery["Machinery"]
        SUP["tools/supervisor/<br/>273 files, 85K LOC"]
        SPEC["tools/spec/ +<br/>tools/specification-authority-layer/"]
        ORC["tools/oracle/"]
        GOV["tools/supervisor/<br/>governance_validators*"]
        AI["tools/ai/"]
    end

    subgraph Evidence["Evidence & State"]
        REG["registry/<br/>format-registry, baselines"]
        QNAME["shared/qname-registry/<br/>21 YAML files"]
        ORA["oracle/formats/<br/>20 format packages"]
        REPORTS["reports/<br/>402 MB sprint history"]
    end

    subgraph Tests["Test Layer (L07)"]
        TESTS["tests/<br/>39,864 tests"]
    end

    SPEC -->|facts| QNAME
    QNAME -->|class mapping| PY
    QNAME -->|class mapping| NET
    SUP -->|orchestrates| PY
    SUP -->|orchestrates| NET
    GOV -->|validates| SUP
    ORC -->|verifies| PY
    TESTS -->|tests| PY
    TESTS -->|tests| NET
```

---

## DIAG-003: End-to-End Specification-to-Source Pipeline

**Purpose**: Trace the complete pipeline from specification input to installable library.
**Audience**: Architects, technical leads.
**Claims**: CLM-PIPE-001

```mermaid
flowchart TB
    S1["1. Format Scoring<br/>(7-factor model)"]
    S2["2. Legal Review<br/>(Gates 1-2)"]
    S3["3. Spec Acquisition<br/>(Gate 2)"]
    S4["4. Prototype<br/>(Gate 4)"]
    S5["5. SAL Fact Extraction<br/>(tools/spec/)"]
    S6["6. QName Mapping<br/>(shared/qname-registry/)"]
    S7["7. Capability Modeling<br/>(reports/capability-layer/)"]
    S8["8. Source Implementation<br/>(src/python/, src/net/)"]
    S9["9. Oracle Verification<br/>(oracle/formats/)"]
    S10["10. Testing<br/>(tests/, 39.8K tests)"]
    S11["11. Governance Validation<br/>(161 validators)"]
    S12["12. Packaging<br/>(packaging/python/)"]
    S13["13. Gate 11 Release<br/>(NOT APPROVED)"]

    S1 --> S2 --> S3 --> S4
    S4 --> S5 --> S6 --> S7
    S7 --> S8 --> S9 --> S10
    S10 --> S11 --> S12 --> S13

    style S13 fill:#f99,stroke:#c00
    style S1 fill:#9f9,stroke:#090
    style S8 fill:#9f9,stroke:#090
    style S10 fill:#9f9,stroke:#090
```

**Legend**: Green = fully operational. Red = blocked/pending. Default = operational.

---

## DIAG-004: Specification Ingestion and Fact Extraction

**Purpose**: Detail how specifications become structured facts.
**Audience**: SAL developers, spec analysts.
**Claims**: CLM-PIPE-002

```mermaid
flowchart TB
    SPECPDF["Specification Document<br/>(PDF, HTML)"]
    CACHE[".local/spec-cache/<br/>(downloaded specs)"]
    SAL["SAL Extractor<br/>(tools/specification-authority-layer/)"]
    AI["AI-Assisted Analysis<br/>(tools/ai/)"]
    FACTS[".local/sal-output/<br/>sal-facts-*.json"]
    PERFORMAT["src/python/{format}/spec/<br/>per-format fact modules"]

    SPECPDF --> CACHE
    CACHE --> SAL
    CACHE --> AI
    SAL --> FACTS
    AI --> FACTS
    FACTS --> PERFORMAT
```

| Node | File Count | Status |
|---|---|---|
| SAL Extractor | 24 .py files | Active |
| AI tools | ~30 .py files | Active |
| Facts output | ~14,719 total facts | 20 formats have facts; 4 have 0 |

---

## DIAG-005: Fact-to-Capability and Capability-to-Feature Flow

**Purpose**: Show how extracted facts become capabilities and work items.
**Audience**: Product planners, capability architects.
**Claims**: CLM-PIPE-003, CLM-PIPE-004

```mermaid
flowchart LR
    FACTS["SAL Facts<br/>(~14.7K facts)"]
    QNAME["QName Registry<br/>(21 YAML files)"]
    CAPS["Capability Model<br/>(reports/capability-layer/)"]
    GAPS["Gap Ledger<br/>(gap-ledger.json)"]
    COMPILER["Feature Compiler<br/>(capability_feature_compiler.py)"]
    WORKITEMS["Next Work Items<br/>(next-work-items.json)"]
    SPRINT["Sprint Execution"]

    FACTS --> QNAME
    QNAME --> CAPS
    CAPS --> GAPS
    GAPS --> COMPILER
    COMPILER --> WORKITEMS
    WORKITEMS --> SPRINT
```

---

## DIAG-006: Source Generation and Object-Model Construction

**Purpose**: Show how source code is structured per format.
**Audience**: Product developers.
**Claims**: CLM-ARCH-002, CLM-ARCH-003

```mermaid
flowchart TB
    subgraph Package["src/python/{format}/"]
        INIT["__init__.py<br/>(public API, __all__)"]
        CODEC["{format}_codec.py<br/>(parse, load, save)"]
        ANALYTICS["{format}_analytics.py<br/>(spec-backed metrics)"]
        MODELS["models.py<br/>(dataclasses)"]
        EXCEPTIONS["exceptions.py"]

        subgraph SpecHier["spec/ (spec-aligned hierarchy)"]
            OFFICE["office/document.py<br/>spec_qname = 'office:document'"]
            TABLE["table/table.py<br/>spec_qname = 'table:table'"]
        end

        subgraph Compat["Compat/ (facades)"]
            FDOC["fods_document.py<br/>FodsDocument"]
            FCELL["fods_cell.py<br/>FodsCell"]
        end
    end

    INIT --> CODEC
    INIT --> ANALYTICS
    INIT --> MODELS
    CODEC --> SpecHier
    SpecHier --> Compat
```

**Key pattern**: Spec QName (e.g., `table:table-cell`) maps to canonical class (`Table.TableCell`) in `spec/`, which is aliased to format-prefixed facade (`FodsCell`) in `Compat/`.

---

## DIAG-007: Product Runtime Architecture

**Purpose**: Show what happens when a user calls `parse_fods("file.fods")`.
**Audience**: API consumers, product developers.
**Claims**: CLM-PROD-001

```mermaid
sequenceDiagram
    participant User
    participant API as fods.__init__
    participant Parser as fods.parser
    participant DefusedXML as defusedxml / xml.etree
    participant Model as Neutral Model Dict

    User->>API: parse_fods("file.fods")
    API->>Parser: parse_fods(file_path)
    Parser->>Parser: Check file size (MAX_FILE_BYTES)
    Parser->>DefusedXML: iterparse(file_path)
    DefusedXML-->>Parser: XML events
    Parser->>Parser: Extract sheets, rows, cells
    Parser->>Parser: Handle types, formulas, styles
    Parser-->>Model: Build workbook dict
    Model-->>User: {sheets: [...], metadata: {...}}
```

---

## DIAG-008: Agent, Skill, Command, and Supervisor Architecture

**Purpose**: Show how AI agents, skills, and the supervisor interact.
**Audience**: Governance architects, contributors.
**Claims**: CLM-GOV-001, CLM-GOV-002, CLM-ARCH-004

```mermaid
flowchart TB
    subgraph Agents["AI Agents"]
        CLAUDE["Claude Code<br/>(primary agent)"]
        CODEX["Codex<br/>(optional secondary)"]
    end

    subgraph Skills["Skills Layer (L13)"]
        REGISTRY[".supervisor/<br/>skill-registry.yaml<br/>(123 skills)"]
        COMMANDS[".claude/commands/<br/>(124 command files)"]
    end

    subgraph Supervisor["Supervisor Layer (L11)"]
        SUPLOOP["supervisor_loop.py<br/>(autonomous-cycle)"]
        AUTOCYCLE["autonomous_cycle.py<br/>(2,651 LOC)"]
        CHECKCONT["check_continuation.py<br/>(continue/stop decision)"]
        PLANLOCK["write_plan_lock.py<br/>(plan enforcement)"]
    end

    subgraph Governance["Governance Layer (L12)"]
        VALIDATORS["161 Governance Validators<br/>(20 modules)"]
        POLICIES[".supervisor/policies.yaml"]
    end

    CLAUDE --> COMMANDS
    COMMANDS --> REGISTRY
    CLAUDE --> SUPLOOP
    SUPLOOP --> AUTOCYCLE
    AUTOCYCLE --> CHECKCONT
    AUTOCYCLE --> VALIDATORS
    CODEX -->|adapter| REGISTRY
    PLANLOCK --> CHECKCONT
```

---

## DIAG-009: Autonomous Execution and Governance Control Loop

**Purpose**: Show the sprint loop lifecycle.
**Audience**: System operators, governance architects.
**Claims**: CLM-GOV-002

```mermaid
stateDiagram-v2
    [*] --> ReadSessionResume: Session Start
    ReadSessionResume --> CheckPlanLock: Read session-resume.md
    CheckPlanLock --> ExecutePlan: Plan loaded
    CheckPlanLock --> ReadNextSprint: No plan
    ReadNextSprint --> ExecuteSprint: Read next-sprint.md

    ExecutePlan --> WriteEvidence: Sprint work done
    ExecuteSprint --> WriteEvidence: Sprint work done

    WriteEvidence --> ValidateDeclaration: Write evidence YAML
    ValidateDeclaration --> AutonomousCycle: Validate declaration
    AutonomousCycle --> CheckContinuation: Grade work items

    CheckContinuation --> ReadNextSprint: CONTINUE (exit 0)
    CheckContinuation --> Stop: STOP (exit 1)
    CheckContinuation --> ResetIterations: MAX_ITERATIONS

    ResetIterations --> ReadNextSprint: Reset to 0

    ExecutePlan --> PlanComplete: All taskcards closed
    PlanComplete --> TerminalStop: write_plan_lock --terminal
    TerminalStop --> [*]: POST_PLAN_TERMINAL
    Stop --> [*]: TRUE_EXTERNAL_GATE
```

---

## DIAG-010: Validation, Evidence, Gap, Rework, and Approval Loop

**Purpose**: Show how governance validators feed rework and gap tracking.
**Audience**: Quality engineers, governance architects.
**Claims**: CLM-GOV-003

```mermaid
flowchart TB
    SPRINT["Sprint Execution"]
    EVIDENCE["Evidence Declaration<br/>(.local/evidences/{run_id}/)"]
    VALIDATE["Sprint Executor Validate<br/>(828 LOC)"]
    GOVVAL["161 Governance Validators"]
    GRADE["Autonomous Cycle Grading"]

    SPRINT --> EVIDENCE
    EVIDENCE --> VALIDATE
    VALIDATE --> GRADE
    GOVVAL --> GRADE

    GRADE -->|ACCEPTED| NEXT["Next Sprint"]
    GRADE -->|REWORK| REWORK["Rework Items"]
    REWORK --> GAPS["Gap Ledger<br/>(gap-ledger.json)"]
    GAPS --> NEXT
    GRADE -->|EXIT 3| NEXT

    style REWORK fill:#ff9,stroke:#cc0
```

---

## DIAG-011: Artifact and Data Lineage

**Purpose**: Trace artifacts from specification to final package.
**Audience**: Traceability auditors.
**Claims**: CLM-PIPE-001

```mermaid
flowchart LR
    subgraph Spec["Specification Inputs"]
        PDF["Spec PDF/HTML"]
        CACHE["Spec Cache<br/>(.local/spec-cache/)"]
    end

    subgraph Facts["Extracted Knowledge"]
        SAL["SAL Facts<br/>(JSON, ~14.7K)"]
        QNAME["QName Registry<br/>(YAML, 21 files)"]
    end

    subgraph Source["Product Source"]
        PYMOD["Python modules<br/>(src/python/)"]
        CSMOD[".NET classes<br/>(src/net/)"]
    end

    subgraph Verify["Verification"]
        ORACLE["Oracle Cases<br/>(oracle/formats/)"]
        TESTS["Tests<br/>(39,864)"]
        EVIDENCE["Evidence Decls<br/>(.local/evidences/)"]
    end

    subgraph Output["Outputs"]
        WHL["Python wheels"]
        NUPKG[".NET packages"]
        REPORTS["Sprint Reports<br/>(402 MB)"]
    end

    PDF --> CACHE --> SAL --> QNAME
    QNAME --> PYMOD
    QNAME --> CSMOD
    PYMOD --> TESTS
    CSMOD --> TESTS
    PYMOD --> ORACLE
    TESTS --> EVIDENCE
    EVIDENCE --> REPORTS
    PYMOD --> WHL
    CSMOD --> NUPKG
```

---

## DIAG-012: Happy-Path Execution Sequence

**Purpose**: Show a successful autonomous sprint from start to finish.
**Audience**: System operators.
**Claims**: CLM-GOV-002

```mermaid
sequenceDiagram
    participant Agent as Claude Code
    participant SR as session-resume.md
    participant NS as next-sprint.md
    participant SRC as src/python/{format}/
    participant TEST as tests/
    participant SUP as supervisor_loop.py
    participant CC as check_continuation.py

    Agent->>SR: Read session resume
    Agent->>NS: Read next sprint tasks
    Agent->>SRC: Implement changes
    Agent->>TEST: Run tests (pytest)
    TEST-->>Agent: All PASS
    Agent->>SUP: autonomous-cycle --declaration evidence.yaml
    SUP-->>Agent: Exit 0 (all accepted)
    Agent->>CC: check_continuation.py
    CC-->>Agent: CONTINUE
    Agent->>NS: Read updated next-sprint.md
    Note over Agent: Loop continues...
```

---

## DIAG-013: Failure and Rework Sequence

**Purpose**: Show what happens when a sprint produces rework items.
**Audience**: System operators.
**Claims**: CLM-GOV-002, CLM-GOV-003

```mermaid
sequenceDiagram
    participant Agent as Claude Code
    participant SUP as supervisor_loop.py
    participant GOV as Governance Validators
    participant CC as check_continuation.py

    Agent->>SUP: autonomous-cycle --declaration evidence.yaml
    SUP->>GOV: Run 161 validators
    GOV-->>SUP: V66 FAIL (monolith detected)
    SUP-->>Agent: Exit 3 (rework items)
    Agent->>CC: check_continuation.py
    CC-->>Agent: STOP (GOV_BLOCK)
    Note over Agent: Agent must fix GOV_BLOCK<br/>before resuming product work
    Agent->>Agent: Analytics separation refactor
    Agent->>SUP: Re-run autonomous-cycle
    SUP-->>Agent: Exit 0 (accepted)
```

---

## DIAG-014: Product Maturity Coverage Map

**Purpose**: Visualize maturity across formats and capabilities.
**Audience**: Product managers, stakeholders.
**Claims**: CLM-PROD-002

```mermaid
flowchart TB
    subgraph Mature["Fully Tested + Oracle Verified"]
        FODS_P["FODS Python<br/>Parse+Write+Export"]
        FODS_N["FODS .NET<br/>Parse+Write+Edit+6 Exports"]
        FODT_P["FODT Python<br/>Parse+Write"]
        FODT_N["FODT .NET<br/>Parse+Write+Edit+3 Exports"]
        ZST_P["ZST Python<br/>Compress+Decompress"]
    end

    subgraph Tested["Tested with Parse + Write"]
        CSV_P["CSV Python"]
        TSV_P["TSV Python"]
        DIF_P["DIF Python"]
        SYLK_P["SYLK Python"]
        NDJSON_P["NDJSON Python"]
        TOML_P["TOML Python"]
        ODS_P["ODS Python"]
        ODT_P["ODT Python"]
        ABW_P["ABW Python"]
        GNUM_P["Gnumeric Python"]
        FODG_P["FODG Python"]
        FODP_P["FODP Python"]
        PBM_P["PBM/PGM/PPM Python"]
    end

    subgraph ParseOnly["Tested with Parse Only (Read-Only)"]
        XCF_P["XCF Python"]
        QOI_P["QOI Python"]
        ZST_RO["ZST Python<br/>(compress/decompress only)"]
    end

    subgraph Scaffolded["Scaffolded / Write-Only"]
        HTML_N["HTML .NET"]
        MD_N["Markdown .NET"]
        TXT_N["TXT .NET"]
    end

    style Mature fill:#9f9,stroke:#090
    style Tested fill:#ff9,stroke:#cc0
    style ParseOnly fill:#fc9,stroke:#c60
    style Scaffolded fill:#f99,stroke:#c00
```

---

## DIAG-015: CI, Packaging, and Release Flow

**Purpose**: Show the CI/CD pipeline from code to potential release.
**Audience**: DevOps engineers.
**Claims**: CLM-ARCH-006

```mermaid
flowchart LR
    PUSH["git push main"]
    LINT["Ruff Lint"]
    SEC["Bandit Security"]
    FAST["Fast Tests (L0-L3)"]
    SKILL["Skill Attribution Check"]
    DOTNETCI[".NET Build + Test<br/>(dotnet restore/build/test)"]
    BUILD["Package Build<br/>(build-local-packages.py)"]
    GATE11["Gate 11 Approval<br/>(NOT APPROVED)"]
    PYPI["PyPI Publish"]
    NUGET["NuGet Publish"]

    PUSH --> LINT
    PUSH --> SEC
    PUSH --> FAST
    PUSH --> SKILL
    PUSH --> DOTNETCI
    LINT --> BUILD
    FAST --> BUILD
    DOTNETCI --> BUILD
    BUILD --> GATE11
    GATE11 -->|Approved| PYPI
    GATE11 -->|Approved| NUGET
    GATE11 -->|Blocked| BLOCKED["Publication Blocked"]

    style GATE11 fill:#f99,stroke:#c00
    style BLOCKED fill:#f99,stroke:#c00
```

---

## DIAG-016: New-Format Extension Workflow

**Purpose**: Show steps to add a new format to the system.
**Audience**: Contributors, format analysts.
**Claims**: CLM-ARCH-005

```mermaid
flowchart TB
    SCORE["/score-format<br/>7-factor evaluation"]
    G1["Gate 1: Human Approval"]
    G2["Gate 2: Legal + Spec Download"]
    G4["Gate 4: Prototype"]
    G5["Gate 5: Requirements"]
    G6["Gate 6: Oracle Comparison"]
    G7["Gate 7: Fuzz Testing"]
    KICK["/new-format-kickstart<br/>Scaffold src/python/{format}/"]
    IMPL["Implement Parser + Writer"]
    TEST["Write Tests + Oracle Cases"]
    PKG["Build Package"]

    SCORE --> G1 --> G2 --> G4
    G4 --> G5 --> G6 --> G7
    G7 --> KICK --> IMPL --> TEST --> PKG
```

---

## DIAG-017: Generated-versus-Manual Ownership Boundary

**Purpose**: Clarify what is generated and what is hand-written.
**Audience**: Architects, code reviewers.
**Claims**: CLM-ARCH-002

```mermaid
flowchart LR
    subgraph Manual["Manually Written"]
        PARSERS["Parsers<br/>(parser.py, *_codec.py)"]
        WRITERS["Writers<br/>(writer.py)"]
        ANALYTICS["Analytics<br/>(*_analytics.py)"]
        MODELS["Models<br/>(models.py)"]
        DOTNET[".NET Classes<br/>(*.cs)"]
        TESTS["Tests<br/>(test_*.py, *Tests.cs)"]
    end

    subgraph Generated["Auto-Generated"]
        STATUS["PROJECT_STATUS.md<br/>(tools/docs/)"]
        NEXTSPRINT["next-sprint.md<br/>(supervisor)"]
        SESSIONRESUME["session-resume.md<br/>(supervisor)"]
        CAPINDEX["Capability Index<br/>(in CLAUDE.md, AGENTS.md)"]
        EVIDENCE["Evidence Reviews<br/>(supervisor)"]
    end

    subgraph Scaffolded["Scaffolded then Manual"]
        SPECDIR["spec/ hierarchy<br/>(kickstart + manual)"]
        COMPATDIR["Compat/ facades<br/>(kickstart + manual)"]
        QNAMEFILES["QName YAML<br/>(seeded + manual)"]
    end

    style Manual fill:#9cf,stroke:#06c
    style Generated fill:#fc9,stroke:#c60
    style Scaffolded fill:#cf9,stroke:#0c6
```

---

## DIAG-018: Current vs Intended Architecture

**Purpose**: Highlight where the current system differs from the documented plan.
**Audience**: Architects, strategic planners.
**Claims**: CLM-SYS-001

```mermaid
flowchart TB
    subgraph Current["Current State"]
        C1["20 Python formats: Parse working"]
        C2["10 .NET formats: Parse working"]
        C3["SAL: Active but AI-assisted"]
        C4["Oracle: 73/73 PASS"]
        C5["Gate 11: NOT approved"]
        C6["No public packages"]
        C7["161 validators"]
        C8["39,864 tests"]
    end

    subgraph Intended["Intended State (from plans)"]
        I1["All formats: Full parse + write + edit + export"]
        I2["Python + .NET parity"]
        I3["SAL: Fully automated extraction"]
        I4["Gate 11: Approved + published"]
        I5["PyPI + NuGet packages live"]
        I6["Continuous code generation from specs"]
        I7["Self-healing autonomous loop"]
    end

    C1 -.->|gap: 3 formats read-only| I1
    C2 -.->|gap: 10 vs 20 formats| I2
    C3 -.->|gap: human/AI hybrid| I3
    C5 -.->|blocked: business decision| I4
    C6 -.->|blocked: Gate 11| I5

    style C5 fill:#f99,stroke:#c00
    style C6 fill:#f99,stroke:#c00
```

**Key gaps**: 3 Python formats remain read-only (QOI, XCF, ZST). .NET covers half the formats Python does. Publication is blocked on Gate 11 business approval. SAL fact extraction involves AI-assisted steps rather than being fully deterministic. Code generation is scaffolding-based, not continuous regeneration.
