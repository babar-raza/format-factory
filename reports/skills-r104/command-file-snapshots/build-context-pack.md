---
version: "1.0"
last-updated: "2026-06-03"
created-by: skills-r104
---

# /build-context-pack

Build a machine-readable context pack YAML summarizing current project state for session bootstrap.

## Usage

Generate a context-pack.yaml file that captures the current state of the project including latest sprint, test counts, MCP status, skill registry snapshot, and active work items.

## Required Inputs

- `output_path`: Path for the generated context-pack YAML (default: `.supervisor/context-pack.yaml`)

## What This Skill Does

1. Read the current supervisor state files (session-resume, approval-gates, evidence-review)
2. Read the skill registry for active/draft skill counts
3. Read the POC target matrix for product gap counts
4. Read the product-code change ledger for src file counts
5. Compute MCP status from .vscode/mcp.json presence
6. Write a structured YAML context pack

## Allowed Paths

- `tools/supervisor/build_context_pack.py` (read-only)
- `.supervisor/context-pack.yaml` (write)
- `reports/supervisor/` (read-only)
- `.supervisor/skill-registry.yaml` (read-only)
- `product-capability-matrix/poc-targets.yaml` (read-only)
- `reports/r90/product-code-change-ledger.json` (read-only)
- `.vscode/mcp.json` (read-only)

## Forbidden Paths

- `src/net/**` (no product source)
- `src/python/**` (no product source)
- `registry/format-registry.yaml` (no gate authority)

## Stop Conditions

- Output directory does not exist
- Required input files missing (warn and continue with defaults)

## Evidence Output

The context pack itself at `output_path`.

## Validation

```bash
.local/venv/Scripts/python tools/supervisor/build_context_pack.py
```

## Rollback

Delete the generated context-pack.yaml file.

## Transcript Requirement

Record context pack generation in evidence declaration when part of a sprint.

## Sample Invocation

```bash
.local/venv/Scripts/python tools/supervisor/build_context_pack.py
```

## Changelog

- v1.0 (2026-06-03): Initial command file for promotion from draft to active (Skills R104)
