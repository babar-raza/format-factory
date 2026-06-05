# Information Architecture Proposal

## Proposed Tree
```
docs/
  README.md
  overview/
  getting-started/
  guides/
  reference/
  architecture/
  operations/
  development/
  _audit/
  _archive/
```

## Personas and Their Needs

### User
- **Who**: End-user of the format-factory tools (e.g., someone using the parsed output or converters).
- **Needs**: 
  - High-level overview of what format-factory does.
  - Getting started guides for using the output (if applicable).
  - Reference for supported formats and their capabilities.
  - Not concerned with internal development or contribution.

### Operator
- **Who**: Person responsible for running format-factory in a CI/CD pipeline or production environment (e.g., setting up spec acquisition, running validation, managing evidence bundles).
- **Needs**:
  - Overview of the acquisition pipeline and gates.
  - Getting started guides for setting up the environment, acquiring specifications, running validation.
  - Guides for common operations: running evidence bundles, updating spec cache, running oracle comparisons.
  - Reference for CLI tools, configuration files, environment variables, and exit codes.
  - Operations runbooks for troubleshooting common issues.
  - Reference for file contracts (e.g., evidence bundle structure, spec cache layout).

### Contributor
- **Who**: Developer contributing to format-factory (adding new formats, improving tools, updating documentation).
- **Needs**:
  - Overview of the project structure, coding conventions, and agent methodology.
  - Getting started guides for setting up the development environment, running tests.
  - Guides for contributing: adding a new format, updating gates, modifying tools.
  - Reference for API internals (if any), tool contracts, and data flow.
  - Architecture documentation for understanding system design decisions.
  - Development guidelines for testing, linting, and committing.
  - Reference for agent commands and skills.

## “Where Does This Go?” Rules

### Guides vs Reference
- **Guides** are scenario-driven, step-by-step instructions aimed at helping a persona accomplish a specific task. They are task-oriented and often follow a "how to" structure. Examples: "How to acquire a new specification", "How to run an evidence bundle validation", "How to add a new format to the registry".
- **Reference** is canonical, exhaustive, and structured for lookup. It provides detailed information about a subject without assuming a specific task. Examples: "CLI tool reference", "Environment variable reference", "Evidence bundle file contract", "Gate definitions and rules".

### Specific Mapping
- **overview/**: High-level concepts, what format-factory is, the acquisition pipeline, gate model, product tracks. Intended for all personas to get a foundational understanding.
- **getting-started/**: Quickstart guides tailored to each persona (User, Operator, Contributor). Short, actionable steps to get started with the relevant activities.
- **guides/**: Detailed, step-by-step instructions for common tasks and scenarios. Examples: running a spec acquisition, building evidence bundles, contributing a new format, running tests.
- **reference/**: Authoritative, exhaustive documentation for reference. Includes:
  - CLI tool reference (if any)
  - Configuration reference (environment variables, kilo.json if existed, .claude/settings.json)
  - File contracts (evidence bundle metadata, spec cache structure, acquisition pack structure)
  - API reference (for internal Python/.NET APIs if exposed)
  - Gate model details (from gates.md)
  - Visibility classification rules (from release-control.md)
  - Legal categories (from legal-and-licensing.md)
- **architecture/**: System design documents, diagrams (in markdown), architectural decisions, and design rationales. Examples: Format Understanding Layer, AI platform operating model, evidence bundle contract rules.
- **operations/**: Runbooks, troubleshooting guides, telemetry configuration, deployment considerations. Focus on keeping the system running smoothly.
- **development/**: Contributing guidelines, testing procedures, repository structure, coding standards, and guidance for contributing code and documentation.
- **_audit/**: Internal audit outputs (like this file). Not for general consumption.
- **_archive/**: Archived old documentation with notes on why it was moved or deprecated.

## Docs Root Allowed Items Rule
- The `docs/` root directory SHALL contain only:
  - `README.md` (the documentation home and navigation hub)
  - Meta folders: `_audit/` and `_archive/` (and any other internal/admin folders like `_templates/` if needed, but not for general documentation)
- NO other files (e.g., `.md`, `.yaml`, `.txt`) are permitted directly in the `docs/` root.
- This rule ensures a clean entry point and prevents scatter of orphaned documentation files.

## Navigation
The `README.md` at the root of `docs/` should serve as a navigation hub, providing links to each of the top-level sections (overview, getting-started, guides, etc.) with brief descriptions of what each section contains.
