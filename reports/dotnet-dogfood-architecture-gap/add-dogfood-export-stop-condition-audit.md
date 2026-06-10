# /add-dogfood-export Stop Condition Audit
Lane: C — FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
Date: 2026-06-05

---

## Stop Condition (verbatim)

Source file: `.claude/commands/add-dogfood-export.md`, section **Stop Conditions** (lines 62-68):

```
## Stop Conditions

- The ledger or validator is missing.
- A Format Factory target writer does not exist.
- Paths exceed the explicit handoff.
- External or direct writing remains in the claimed dogfood path.
- Reload or focused tests fail.
```

The directly applicable stop condition for all four blocked gaps is:

> "A Format Factory target writer does not exist."

---

## Trigger Analysis

For each gap, the stop condition "A Format Factory target writer does not exist." is triggered because
the required target FF writer library has not been built anywhere in the repository.

| Gap ID | Required Target Writer | Writer Exists | Stop Condition Triggered |
|---|---|---|---|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | format-factory-csv-dotnet | NO | YES |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | format-factory-html-dotnet | NO | YES |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | format-factory-markdown-dotnet | NO | YES |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | format-factory-txt-dotnet | NO | YES |

### Per-Gap Analysis

**Gap 1: fods-to-csv-dotnet**

Required writer: `format-factory-csv-dotnet` (a FF-produced .NET CSV write library).

Status: No such library exists in `src/net/`. The existing stub `src/net/fods/FodsCsvExporter.cs`
implements RFC 4180 CSV escaping inline within the `FormatFactory.Fods` namespace. This constitutes
"raw serialization that bypasses an available Format Factory target writer" — an explicitly forbidden
export backend in /add-dogfood-export. No `target_ff_library` declaration is present in the file.

Stop condition: TRIGGERED.
/add-dogfood-export invocation: NOT ALLOWED.
Expected action: ARCHITECTURE_DECISION_REQUIRED — build FormatFactory.Csv .NET library first.

**Gap 2: fods-to-html-dotnet**

Required writer: `format-factory-html-dotnet` (a FF-produced .NET HTML write library).

Status: No such library exists in `src/net/`. The existing stub `src/net/fods/FodsHtmlExporter.cs`
uses `System.Net.WebUtility.HtmlEncode` (BCL) and StringBuilder inline within `FormatFactory.Fods`.
No `target_ff_library` declaration is present. latest-next-worker-prompt.md Train I states explicitly:
"No FF .NET HTML write library. Prerequisite: Build FormatFactory.Html .NET library."

Stop condition: TRIGGERED.
/add-dogfood-export invocation: NOT ALLOWED.
Expected action: ARCHITECTURE_DECISION_REQUIRED — build FormatFactory.Html .NET library first.

**Gap 3: fodt-to-markdown-dotnet**

Required writer: `format-factory-markdown-dotnet` (a FF-produced .NET Markdown write library).

Status: No such library exists in `src/net/`. The existing stub `src/net/fodt/FodtMarkdownExporter.cs`
generates ATX Markdown headings inline (`new string('#', level)`) within `FormatFactory.Fodt`. No
`target_ff_library` declaration is present in the file. No FormatFactory.Markdown namespace exists
anywhere in `src/net/`.

Stop condition: TRIGGERED.
/add-dogfood-export invocation: NOT ALLOWED.
Expected action: ARCHITECTURE_DECISION_REQUIRED — build FormatFactory.Markdown .NET library first.

**Gap 4: fodt-to-txt-dotnet**

Required writer: `format-factory-txt-dotnet` (a FF-produced .NET plain-text write library).

Status: No such library exists in `src/net/`. The existing stub `src/net/fodt/FodtTxtExporter.cs`
joins paragraph texts via `string.Join("\n", lines)` and `File.WriteAllText` inline within
`FormatFactory.Fodt`. No `target_ff_library` declaration is present. latest-next-worker-prompt.md
Train H states explicitly: "No FF .NET text write library. Prerequisite: Build FormatFactory.Text
.NET library with write_text()."

Stop condition: TRIGGERED.
/add-dogfood-export invocation: NOT ALLOWED.
Expected action: ARCHITECTURE_DECISION_REQUIRED — build FormatFactory.Text .NET library first.

---

## Latest-Next-Worker-Prompt References

File checked: `reports/supervisor/latest-next-worker-prompt.md`
Sprint ID from file: FORMAT-FACTORY-R2-MEGA-TRAIN-001
Generated: 2026-06-05T07:37:35.020289

The prompt contains Group G5 (Dogfood Exports) with Train H and Train I, which reference two of the
four blocked gaps directly:

**Train H: Dogfood: fodt -> txt** (verbatim, lines 212-218):
```
### Train H: Dogfood: fodt -> txt

No FF .NET text write library. Prerequisite: Build FormatFactory.Text .NET library with write_text().

**Acceptance Criteria:**
- Export test passes using FF library
- Dogfood status updated in poc-targets.yaml
```

**Train I: Dogfood: fodt -> html** (verbatim, lines 220-226):
```
### Train I: Dogfood: fodt -> html

No FF .NET HTML write library. Prerequisite: Build FormatFactory.Html .NET library.

**Acceptance Criteria:**
- Export test passes using FF library
- Dogfood status updated in poc-targets.yaml
```

Observation: The prompt correctly identifies the architecture prerequisite for Train H (fodt-to-txt)
and Train I (fodt-to-html) and does NOT invoke /add-dogfood-export for either. The skill is deferred
pending library construction. The other two gaps (fods-to-csv, fodt-to-markdown) are not named in
Group G5 but are structurally blocked by the same stop condition — no FF .NET writer library exists
for CSV or Markdown.

---

## Routing Matrix

| Gap ID | Required Target Writer | Writer Exists | Skill Allowed | Expected Action |
|---|---|---|---|---|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | format-factory-csv-dotnet | NO | NO | ARCHITECTURE_DECISION_REQUIRED |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | format-factory-html-dotnet | NO | NO | ARCHITECTURE_DECISION_REQUIRED |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | format-factory-markdown-dotnet | NO | NO | ARCHITECTURE_DECISION_REQUIRED |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | format-factory-txt-dotnet | NO | NO | ARCHITECTURE_DECISION_REQUIRED |

---

## Local Verdict

STOP_CONDITION_CONFIRMED — all 4 gaps blocked

All four .NET dogfood export gaps trigger the /add-dogfood-export stop condition "A Format Factory
target writer does not exist." The skill MUST NOT be invoked for any of these gaps. The correct
action for all four is ARCHITECTURE_DECISION_REQUIRED: each gap requires a corresponding FF-produced
.NET writer library to be designed and built before a governed dogfood export can be claimed as
IMPLEMENTED.

The latest-next-worker-prompt.md confirms this finding explicitly for fodt-to-txt (Train H) and
fodt-to-html (Train I), and the same structural diagnosis applies to fods-to-csv and fodt-to-markdown,
where no FormatFactory.Csv or FormatFactory.Markdown library exists anywhere in src/net/.
