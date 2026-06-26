# Package Release Layer

```yaml
layer_metadata:
  layer_id: L18
  canonical_name: Package Release Layer
  canonical_slug: package-release-layer
  permanent_plan_path: plans/layers/package-release-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: NOT_ASSESSED
  health: UNKNOWN
  maturity_current: 1
  maturity_target: 3
  current_stage: DISCOVERY
  current_owner: null
  session_id: "923e237958c1"
  dependencies: [L06, L17, L21]
  upstream_layers: [L06, L17, L21]
  downstream_layers: [L19]
  skill_ids: [package-install-proof, check-release-boundary, check-gate]
  command_ids: [package-install-proof, check-release-boundary, check-gate]
  last_updated_at: "2026-06-26"
  next_task_id: TC-PKG-001
  next_action: "BLOCKED_EXTERNAL: Gate 11 execution requires Babar Raza approval before PyPI/NuGet release"
```

## 2. Authority and Purpose

Owns the package release pipeline: PyPI (Python) and NuGet (.NET) publication.
Currently BLOCKED on Gate 11 execution (Babar Raza commercial sign-off).

## 3. Scope

- PyPI publication: `src/python/{format}/setup.py` or `pyproject.toml`
- NuGet publication: `src/net/{format}/*.csproj`
- Release workflow: `.github/workflows/` (if exists)
- Gate authority: `registry/format-registry.yaml` — legal_safety, spec_availability scores

## 9. Current Implementation

- `/package-install-proof` skill registered
- `/check-release-boundary` skill registered
- `/check-gate` skill registered
- Gate 11 G11-G APPROVED by Babar Raza for FODS/FODT/Netpbm
- Gate 11 EXECUTION (commercial release) NOT yet approved

## 14. Gap Register

| Gap ID | Severity | Current | Target | Status |
|--------|----------|---------|--------|--------|
| PKG-GAP-001 | CRITICAL | Gate 11 execution not approved | Babar Raza sign-off received | BLOCKED_EXTERNAL |

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L18-001
  layer_id: L18
  permanent_layer_plan: plans/layers/package-release-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  current_status: NOT_ASSESSED
  maturity_current: 1
  exact_next_task: TC-PKG-001
  why_this_is_next: >
    BLOCKED_EXTERNAL: Gate 11 execution requires Babar Raza commercial sign-off.
    This is a TRUE_EXTERNAL_GATE — agent preparation is done; only human authority needed.
  blocked_tasks: [TC-PKG-001]
  important_decisions:
    - "Gate 11 G11-G is APPROVED for FODS/FODT/Netpbm — but only G11 EXECUTION is gated"
    - "Agent PREPARATION (release packet) is always agent-owned"
    - "Actual PyPI/NuGet registration requires credentials + Babar Raza sign-off"
  resume_instructions: >
    Package release is blocked on Gate 11 execution. Prepare release packets.
    Run /check-gate to verify readiness. Await Babar Raza sign-off for actual publication.
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (stub) |
