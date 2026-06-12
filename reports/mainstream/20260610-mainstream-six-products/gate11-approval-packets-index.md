# Gate 11 Approval Packets Index
# Date: 2026-06-10

## Gate 11 Status (AUTHORITATIVE — from registry/format-registry.yaml)
**Gate 11 is NOT approved for ANY format.**

## Products with Sufficient Capability for Gate 11 Packet Preparation

### FODS (.NET)
- Capability: Read, Write, Roundtrip, Export (CSV/HTML/JSON)
- Tests: 547 .NET + 211 Python
- Package: FormatFactory.Fods.0.1.0-tier0.nupkg
- Packet status: AGENT-PREPARABLE (capability sufficient)
- Approval status: NOT APPROVED (approved_by: null)
- Blocker: TRUE_HUMAN_GATE — requires formal approval from Babar Raza

### FODT (.NET)
- Capability: Read, Write, Roundtrip, Export (HTML/TXT/Markdown)
- Tests: 520 .NET + 248 Python
- Package: FormatFactory.Fodt.0.1.0-tier0.nupkg
- Packet status: AGENT-PREPARABLE (capability sufficient)
- Approval status: NOT APPROVED (approved_by: null)
- Blocker: TRUE_HUMAN_GATE — requires formal approval from Babar Raza

### Netpbm (.NET)
- Capability: Read, Write, Export, Image Model
- Tests: 465 .NET + 144 Python
- Package: FormatFactory.Netpbm.0.1.0-r85-poc.nupkg
- Packet status: AGENT-PREPARABLE
- Approval status: NOT APPROVED
- Blocker: TRUE_HUMAN_GATE

### CSV (.NET)
- Capability: Read, Write, Document Model, Roundtrip
- Tests: 36 .NET + 38 Python
- Package: FormatFactory.Csv.0.1.0-mwp.nupkg
- Packet status: NEEDS-DEEPENING (test count low for commercial)
- Approval status: NOT APPROVED

### NDJSON (.NET)
- Capability: Read, Write, Document Model, CSV Export
- Tests: 29 .NET
- Package: FormatFactory.Ndjson.0.1.0-mwp.nupkg
- Packet status: NEEDS-DEEPENING (new project, needs more tests)
- Approval status: NOT APPROVED

### TSV (.NET)
- Capability: Read, Write, Document Model, CSV Export
- Tests: 38 .NET
- Package: FormatFactory.Tsv.0.1.0-mwp.nupkg
- Packet status: NEEDS-DEEPENING (new project, needs more tests)
- Approval status: NOT APPROVED

## Gate 11 Rules (from AGENTS.md + CLAUDE.md)
- Agent may prepare all evidence and recommend approval
- Agent may NOT self-approve
- Registry approval fields MUST NOT be updated without formal approval
- Formal approval requires human authorization from Babar Raza
