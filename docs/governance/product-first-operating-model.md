# Product-First Operating Model

**Added:** 2026-06-03
**Updated:** 2026-06-04 (external tool architecture, Gnumeric/DIF staging added)
**Authority:** plans/master-plan.md Section 43

## Principle

All project machinery (supervisor, acceleration, skills, autonomous continuation) exists to serve the POC goal. Machinery that audits itself, repairs its own evidence, or generates prompt-quality metrics without producing product output is drift.

## POC Goal

| Track | Products | Required Capability |
|---|---|---|
| Commercial .NET | FODS, FODT, Netpbm | Load/read, editable object model, same-format save, export/conversion, dogfood, tests, examples, package proof, capability matrix |
| Reduced/FOSS (primary) | ZST, Python Netpbm (PBM/PGM/PPM), SYLK/DIF | Honest capability matrix, real parser/writer/export/package/example proof, reproducible tests |
| Reduced/FOSS (staged) | Gnumeric Python | Staged/evaluated — repo source exists, useful as FOSS candidate |

**Important format decisions:**
- Netpbm .NET must be retained. SVG must NOT be substituted (Aspose already supports SVG).
- DIF promoted alongside SYLK: overlap is manageable, DIF is near useful readiness.
- Gnumeric: staged only — no implementation until primary POC targets are green.

## Operating Rules

1. Every sprint must state its product-first purpose.
2. Mainstream must have a hard PASS quota for product output breadth.
3. Machinery sprints must state which product blocker they address.
4. No sprint may pass on evidence repair alone.
5. Cross-stream dependencies must be declared at sprint start.

## Product-Output Floor

No machinery lane may declare clean success unless it either:
- Removes a blocker for Mainstream product work
- Prevents a false PASS or false STOP that affects product velocity
- Creates a reusable accelerator that Mainstream can consume
- Reduces human handoff
- Improves product throughput, safety, or repeatability
