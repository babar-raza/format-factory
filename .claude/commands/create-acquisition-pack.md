# /create-acquisition-pack

Initialize a format acquisition pack from the standard template.

## Usage

```
/create-acquisition-pack <format_id>
```

Example: `/create-acquisition-pack fods`

## What This Command Does

1. **Validate format exists** — Confirm `<format_id>` is in `registry/format-registry.yaml`
2. **Create acquisition directory** — `acquisitions/<format_id>/`
3. **Scaffold required files** from template:
   - `acquisitions/<format_id>/acquisition-plan.md` — Discovery + implementation plan
   - `acquisitions/<format_id>/spec-inventory.yaml` — Spec document registry
   - `acquisitions/<format_id>/gap-ledger.yaml` — Capability gap tracker
   - `acquisitions/<format_id>/evidence-log.md` — Sprint evidence log
4. **Pre-populate from registry** — Fill format name, family, tier, primary spec URL

## Required Inputs

- `format_id` — The format identifier as it appears in `registry/format-registry.yaml`

## Steps

```
1. Read registry/format-registry.yaml → validate format exists
2. Create directory: acquisitions/<format_id>/
3. Create acquisition-plan.md from template (see template section below)
4. Create spec-inventory.yaml with format metadata
5. Create gap-ledger.yaml with empty capability ledger
6. Create evidence-log.md with sprint header
7. Update registry/format-registry.yaml: set acquisition_status = "IN_PROGRESS"
```

## Template: acquisition-plan.md

```markdown
# Acquisition Plan: <FORMAT_NAME>
**Format ID:** <format_id>
**Tier:** <tier>
**Created:** <date>
**Status:** IN_PROGRESS

## Phase 1: Discovery
- [ ] Locate primary spec document
- [ ] Identify OSS reference implementations
- [ ] Enumerate core capabilities for POC

## Phase 2: POC Implementation
- [ ] Implement read/probe
- [ ] Implement write (if applicable)
- [ ] Add tests for each capability
- [ ] Run Gate 4 checklist

## Phase 3: Commercial Product
- [ ] Validate spec parity
- [ ] Commercial API design
- [ ] Gate 8 / Gate 11 preparation
```

## Validation

Complete when:
- `acquisitions/<format_id>/` directory exists with all 4 required files
- `registry/format-registry.yaml` shows `acquisition_status: IN_PROGRESS`

## Allowed Paths

- `registry/ — format registry (read-only unless updating registry)`
- `reports/ — acquisition reports (write)`
- `plans/ — acquisition plans (read/write)`

## Forbidden Paths

- `src/net/**` — no product source mutation during acquisition
- `src/python/**` — no product source mutation during acquisition
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
