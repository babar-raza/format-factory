# Architecture Gap Decision Record
Lane: D — FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
Date: 2026-06-05
Status: ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP_FOR_THIS_SPRINT

---

## Context

The four gaps below occupy the top 4 positions in the Mainstream gap queue with a priority score of 125 each:

| Gap ID | Format | Capability | Score |
|---|---|---|---|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | FODS .NET | dogfood_status.fods_to_csv_dotnet | 125 |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | FODS .NET | dogfood_status.fods_to_html_dotnet | 125 |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | FODT .NET | dogfood_status.fodt_to_markdown_dotnet | 125 |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | FODT .NET | dogfood_status.fodt_to_txt_dotnet | 125 |

All four are classified `GAP_DOGFOOD_EXTERNAL` and assigned `GOVERNED_SKILL_REQUIRED` (governed-dogfood-export). The current next-sprint.md TASK-009 through TASK-012 instruct agents to invoke `/add-dogfood-export` for each of these gaps. However, invoking that skill against any of these four gaps would immediately trigger the stop condition "A Format Factory target writer does not exist," blocking execution and wasting sprint cycles.

The root cause is an architecture gap: the Format Factory .NET ecosystem does not yet contain the required target writer libraries (`FormatFactory.Csv`, `FormatFactory.Html`, `FormatFactory.Markdown`, `FormatFactory.Txt`). These writer libraries must exist before a governed dogfood export can be implemented.

---

## Evidence

All evidence is from the current investigation sprint. File paths are cited — do not inline content.

- **Lane A — Top-gap confirmation:**
  `reports/dotnet-dogfood-architecture-gap/top-gap-table.json`
  Confirms all 4 gaps at score=125, stream=mainstream, classification=GAP_DOGFOOD_EXTERNAL.

- **Lane B — Target writer library matrix:**
  `reports/dotnet-dogfood-architecture-gap/target-writer-library-matrix.json`
  Confirms all 4 required target writers do not exist in `src/net/`. Product-local stubs exist in
  `FormatFactory.Fods` and `FormatFactory.Fodt` namespaces but are inline serializers, not FF writer
  libraries and carry no `target_ff_library` declaration.

- **Lane C — Stop condition audit:**
  `reports/dotnet-dogfood-architecture-gap/add-dogfood-export-stop-condition-audit.md`
  Confirms stop condition "A Format Factory target writer does not exist." is triggered for all four
  gaps. `/add-dogfood-export` invocation is NOT ALLOWED for any of the four gaps. The
  `latest-next-worker-prompt.md` independently confirms the architecture prerequisite for two of the
  four (Train H: fodt-to-txt, Train I: fodt-to-html).

---

## Decision

**ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP_FOR_THIS_SPRINT**

The four gaps `commercial-net-fods-dogfood-status-fods-to-csv-dotnet`,
`commercial-net-fods-dogfood-status-fods-to-html-dotnet`,
`commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet`, and
`commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet` are hereby accepted as architecture-blocked
in this sprint. The following actions are mandated:

1. **Do NOT invoke `/add-dogfood-export` for any of the four blocked gaps.** The stop condition
   "A Format Factory target writer does not exist." fires immediately and the skill is not allowed.

2. **Reclassify all four gaps** as `GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED` in any downstream
   planning artifacts produced this sprint. The existing `poc-targets.yaml` entry (`GAP_DOGFOOD_EXTERNAL`)
   is NOT modified by this sprint (read-only).

3. **Create a blocked-gap ledger.** Document each gap with its required writer library and the
   sprint/decision required to unblock it (see: CREATE-DOTNET-CSV-WRITER-001 below).

4. **Create a future writer library decision package** (`future-writer-library-options.json`) so the
   architecture team can select the approach for the next implementation sprint.

5. **Escalate to future sprint: CREATE-DOTNET-CSV-WRITER-001.** The first viable unblocking action
   is to build the `FormatFactory.Csv` .NET writer library (Alt-A, recommended). This unblocks
   `fods_to_csv_dotnet` only. Each additional gap requires its own independent writer library.

---

## Blocked-Gap Ledger

| Gap ID | Required Writer Library | Namespace | Sprint to Create | Unblocks |
|---|---|---|---|---|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | format-factory-csv-dotnet | FormatFactory.Csv | CREATE-DOTNET-CSV-WRITER-001 | fods_to_csv_dotnet |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | format-factory-html-dotnet | FormatFactory.Html | CREATE-DOTNET-HTML-WRITER-001 | fods_to_html_dotnet |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | format-factory-markdown-dotnet | FormatFactory.Markdown | CREATE-DOTNET-MARKDOWN-WRITER-001 | fodt_to_markdown_dotnet |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | format-factory-txt-dotnet | FormatFactory.Txt | CREATE-DOTNET-TXT-WRITER-001 | fodt_to_txt_dotnet |

---

## Consequences

**FODS commercial .NET:**
The `dogfood_status.fods_to_csv_dotnet` and `dogfood_status.fods_to_html_dotnet` gaps remain OPEN
until `FormatFactory.Csv` and `FormatFactory.Html` writer libraries are designed and built. No gap
closure can be claimed via `/add-dogfood-export` before that. The existing `FodsCsvExporter.cs` and
`FodsHtmlExporter.cs` stubs (both in `FormatFactory.Fods` namespace) do NOT satisfy the requirement.
All other FODS .NET capabilities (load/parse, edit, save-same-format, roundtrip tests, examples,
object-model features) remain available and unblocked.

**FODT commercial .NET:**
The `dogfood_status.fodt_to_txt_dotnet` and `dogfood_status.fodt_to_markdown_dotnet` gaps remain
OPEN until `FormatFactory.Txt` and `FormatFactory.Markdown` writer libraries are designed and built.
The existing `FodtTxtExporter.cs` and `FodtMarkdownExporter.cs` stubs (both in `FormatFactory.Fodt`
namespace) do NOT satisfy the requirement. All other FODT .NET capabilities remain available and
unblocked.

**Netpbm commercial .NET:**
Unaffected. Dogfood is already `IMPLEMENTED` via `NetpbmExporter.cs` which correctly declares
`target_ff_library: FormatFactory.Netpbm.NetpbmWriter`. No architecture gap exists for Netpbm.

**Mainstream routing — next sprint:**
Mainstream must not route to the four blocked gaps. Safe alternatives exist (see: Product Readiness
Impact Analysis). Recommended routing: SYLK Python installed workflow (score=110), Netpbm FOSS
installed-package proof (score=90), FODS/FODT object-model deepening.

---

## Rejected Alternatives

**Alt-REJECT-A: Use product-local exporters (FodsCsvExporter.cs, etc.) as dogfood**
Status: REJECTED.
Reason: These stubs use inline serialization within the `FormatFactory.Fods`/`FormatFactory.Fodt`
namespaces. They have no `target_ff_library` declaration. The `/add-dogfood-export` stop condition
"External or direct writing remains in the claimed dogfood path" and "A Format Factory target writer
does not exist" both fire. Accepting these stubs as dogfood would silently misrepresent the
architecture and create a false claim that a governed export path is in place.

**Alt-REJECT-B: Substitute Python dogfood for .NET gaps**
Status: REJECTED.
Reason: Python dogfood (`fods_to_csv_python`, `fodt_to_txt_python`) is already `IMPLEMENTED` and
cannot be used to claim .NET gap closure. Doing so would silently misrepresent .NET commercial
product capability and create a capability matrix entry that does not reflect what the .NET library
can actually do.

---

## Viable Alternatives (require future sprint decision)

A human or architecture decision is required to select from the following options before any
implementation sprint is authorized. See `future-writer-library-options.json` for full option set.

**Alt-A (RECOMMENDED): Build format-factory-csv .NET writer first**
Unblocks: `fods_to_csv_dotnet` only.
Risk: LOW. Smallest scope — a single focused sprint to build `FormatFactory.Csv` with a `CsvWriter`
class implementing at minimum `WriteCsv(IEnumerable<string[]> rows, string filePath)`.
Note: `fods_to_html_dotnet` requires a SEPARATE `format-factory-html` .NET writer and is NOT
unblocked by this option.

**Alt-A2: Build format-factory-html .NET writer library**
Unblocks: `fods_to_html_dotnet` only.
Risk: LOW. Independent of CSV writer. Can be done in same sprint as Alt-A or separately.

**Alt-B: Build format-factory-markdown .NET writer library**
Unblocks: `fodt_to_markdown_dotnet` only.
Risk: LOW. Independent.

**Alt-C: Build format-factory-txt .NET writer library**
Unblocks: `fodt_to_txt_dotnet` only.
Risk: LOW. Independent.

**Alt-D: Build all four writers in one sprint**
Unblocks: all four gaps.
Risk: MEDIUM. Higher effort. All four writer libraries plus integration tests in one sprint increases
scope risk and reduces depth of each implementation.

**Alt-E: Defer .NET dogfood, advance safe alternatives**
Unblocks: none of the four blocked gaps.
Risk: LOW. SYLK/Netpbm Python work and object-model deepening advance while the architecture
decision is pending. Appropriate when human authorization for writer library construction is not
yet available.

---

## Future Decision Required

YES — human or architecture team decision required to choose from Alt-A / Alt-A2 / Alt-B / Alt-C /
Alt-D / Alt-E before any implementation sprint begins. No agent may self-authorize construction of a
new FF .NET writer library without this decision.

Suggested escalation ID: CREATE-DOTNET-CSV-WRITER-001 (for Alt-A, the recommended first step).

---

## Lane D Local Verdict

LANE_D_COMPLETE — ISSUE_001_ACCEPTED_AS_ARCHITECTURE_GAP_FOR_THIS_SPRINT

All four gaps are formally accepted as architecture-blocked. Decision record is complete. Blocked-gap
ledger is embedded above. Future writer library options are exported to
`reports/dotnet-dogfood-architecture-gap/future-writer-library-options.json`. Architecture decision
is escalated to human/team under ID CREATE-DOTNET-CSV-WRITER-001.
