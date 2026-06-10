# Product Readiness Impact Analysis
Lane: E — FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
Date: 2026-06-05

---

## Summary

The architecture gap investigation (Lanes A–D) confirmed that four .NET dogfood export capabilities
are blocked because the required Format Factory writer libraries do not exist. This analysis assesses
the product-readiness impact per product and identifies safe alternative work lanes that Mainstream
can route to immediately, without waiting for the architecture decision.

Two of the three commercial .NET products (FODS and FODT) have blocked dogfood capabilities. The
third (Netpbm) is unaffected — dogfood is already `IMPLEMENTED`. The blocking capabilities represent
a small subset of each product's total capability surface; the majority of FODS and FODT .NET work
remains available and unblocked.

---

## Product Matrix

| Product | Approximate Test Count | Blocked Capabilities | Blocked Count | Available Work |
|---|---|---|---|---|
| FODS .NET | ~507 (R114 sprint data) | fods_to_csv_dotnet, fods_to_html_dotnet | 2 of 40+ | load/parse, edit, save-same-format, roundtrip, examples, all object-model features |
| FODT .NET | ~493 (R114 sprint data) | fodt_to_markdown_dotnet, fodt_to_txt_dotnet | 2 of 40+ | load/parse, edit, save-same-format, roundtrip, examples, all object-model features |
| Netpbm .NET | ~423 (R114 sprint data) | none | 0 | all capabilities available; additional image processing features |

### FODS .NET — Detail

- **Status in poc-targets.yaml:** `dotnet_tests: 507`, 40+ dotnet_status capabilities all `PASS`
- **Blocked:** `dogfood_status.fods_to_csv_dotnet` (GAP_DOGFOOD_EXTERNAL) and
  `dogfood_status.fods_to_html_dotnet` (GAP_DOGFOOD_EXTERNAL)
- **Blocker root cause:** `FormatFactory.Csv` and `FormatFactory.Html` .NET writer libraries do not
  exist. Product-local stubs `FodsCsvExporter.cs` and `FodsHtmlExporter.cs` use inline serialization
  within `FormatFactory.Fods` namespace — these do NOT satisfy the governed dogfood requirement.
- **Unblocked work:** All dotnet_status capabilities remain available. Object-model deepening
  (additional features, examples, roundtrip hardening) can continue without restriction.
- **Stop condition:** Do not claim dogfood IMPLEMENTED for fods_to_csv_dotnet or fods_to_html_dotnet
  without the corresponding FF writer library in place.

### FODT .NET — Detail

- **Status in poc-targets.yaml:** `dotnet_tests: 493`, 40+ dotnet_status capabilities all `PASS`
- **Blocked:** `dogfood_status.fodt_to_txt_dotnet` (GAP_DOGFOOD_EXTERNAL) and
  `dogfood_status.fodt_to_markdown_dotnet` (GAP_DOGFOOD_EXTERNAL)
- **Blocker root cause:** `FormatFactory.Txt` and `FormatFactory.Markdown` .NET writer libraries do
  not exist. Product-local stubs `FodtTxtExporter.cs` and `FodtMarkdownExporter.cs` use inline
  serialization within `FormatFactory.Fodt` namespace — these do NOT satisfy the requirement.
  `latest-next-worker-prompt.md` explicitly states the prerequisite for Train H and Train I.
- **Unblocked work:** All dotnet_status capabilities remain available. Object-model deepening,
  additional paragraph/heading features, examples, and roundtrip hardening can continue.
- **Stop condition:** Do not claim dogfood IMPLEMENTED for fodt_to_txt_dotnet or
  fodt_to_markdown_dotnet without the corresponding FF writer library in place.

### Netpbm .NET — Detail

- **Status in poc-targets.yaml:** `dotnet_tests: 423`, 40+ dotnet_status capabilities all `PASS`
- **Blocked:** none
- **Dogfood:** `dotnet_family_export: IMPLEMENTED` via `NetpbmExporter.cs` with
  `target_ff_library: FormatFactory.Netpbm.NetpbmWriter` — the correct pattern.
- **Available work:** All capabilities open. Additional image processing features (draw, median
  filter, create canvas, etc.) can be added. Installed-package proof refresh is the next blocker
  (score=90, gap_id: `foss-reduced-netpbm-blockers-1`).
- **Stop condition:** none — architecture is correct.

---

## Safe Alternative Lanes

The following gaps are unblocked and can be executed by Mainstream immediately. All are from
`reports/dotnet-dogfood-architecture-gap/selected-product-gaps.json` (source:
`.local/supervisor/selected-product-gaps.json`).

| Rank | Gap ID | Format | Score | Skill | Notes |
|---|---|---|---|---|---|
| 1 | foss-reduced-sylk-python-status-installed-workflow | SYLK Python | 110 | governed-installed-workflow-verification | PARTIAL → can advance to PASS |
| 2 | foss-reduced-netpbm-blockers-1 | Netpbm Python FOSS | 90 | governed-dogfood-export | Installed-package proof refresh |
| 3 | foss-reduced-sylk-blockers-1 | SYLK Python | 90 | governed-dogfood-export | SYLK writer not implemented; read+export-only scope |
| 4 | foss-reduced-zst-blockers-1 | ZST Python | 90 | governed-dependency-resolution-review | zstandard PyPI offline resolution |
| 5 | (FODS/FODT object-model deepening) | FODS .NET / FODT .NET | — | governed dotnet API skill | Additional API features; no dogfood requirement |

Note: Gaps 9–11 (`commercial-net-fods-blockers-1`, `commercial-net-fodt-blockers-1`,
`commercial-net-netpbm-blockers-1`) are Gate 11 G11-G escalations (score=70) requiring Babar Raza
written approval — not autonomous.

---

## Recommendation

**Immediate routing for Mainstream next sprint:**

1. **Primary lane:** `foss-reduced-sylk-python-status-installed-workflow` (score=110) — highest
   unblocked score, governed skill available, no architecture prerequisite.

2. **Secondary lane:** `foss-reduced-netpbm-blockers-1` (score=90) — installed-package proof
   refresh for Python Netpbm export family.

3. **Tertiary lane:** FODS .NET and/or FODT .NET object-model feature deepening — add new API
   capabilities (sort_rows, filter_rows, column aggregates, etc.) to increase dotnet_tests count and
   expand the capability surface, without touching the blocked dogfood capabilities.

4. **Do NOT route to** the four blocked gaps (`fods_to_csv_dotnet`, `fods_to_html_dotnet`,
   `fodt_to_markdown_dotnet`, `fodt_to_txt_dotnet`) until the architecture decision
   (CREATE-DOTNET-CSV-WRITER-001 or equivalent) is made and the writer library sprint is complete.

**Architecture decision required (human):** Choose from Alt-A through Alt-E in
`reports/dotnet-dogfood-architecture-gap/future-writer-library-options.json` before any
implementation sprint for the blocked gaps is authorized.

---

## Lane E Local Verdict

LANE_E_COMPLETE — PRODUCT_READINESS_IMPACT_ANALYSIS_COMPLETE

Product impact confirmed: 2 blocked capabilities in FODS .NET, 2 in FODT .NET, 0 in Netpbm .NET.
Majority of each product's capability surface remains available. Five safe alternative lanes
identified. Recommendation: route Mainstream to SYLK Python installed-workflow (score=110) and
Netpbm FOSS installed-package proof (score=90) immediately; defer blocked gaps pending architecture
decision.
