# Commercial Product Current Source Audit
# Sprint: COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001
# Lane A — Evidence and Source Audit
# Date: 2026-05-13
# Auditor: Coordinator Agent

## 1. Audit Scope

This report audits the current state of all product source trees against the commercial product
requirements stated by the human:
1. Load the supported format
2. Build an in-memory document object model for manipulation
3. Allow editing of format-specific entities in that object model
4. Save back to the same supported format, with or without edits
5. Export/convert to other formats (PDF, PNG, HTML, related family formats)

Evidence bundle referenced: `gate11-approval-release-readiness-swarm-20260513.zip`
Bundle status: DOES NOT EXIST in `.local/evidence-bundles/`
Note: Sprint proceeds on direct source inspection per sprint instructions.

Latest available bundle: `dec033-option-b-gate11-commercial-swarm-20260512.zip`

---

## 2. Source Tree Inspection

### 2.1 src/net/fods/

**Tracked files:**
- `FodsParser.cs` — 287 lines
- `FormatFactory.Fods.csproj` — project definition
- `README.md` — documentation

**Local (gitignored) artifacts:**
- `bin/` — gitignored, present locally
- `obj/` — gitignored, present locally

**FodsParser.cs analysis:**
- Class: `FodsParser` (sealed)
- Method: `Parse(string filePath) -> FodsParseResult`
- Method: `GetSheetNames(string filePath) -> IReadOnlyList<string>`
- Implementation: Streaming XmlReader — reads document once, counts elements
- Capabilities:
  - Reads FODS file from path
  - Extracts `mimetype`, `version` from `office:document`
  - Extracts `dc:title`, `dc:creator`, `dc:subject`, `meta:initial-creator`
  - Enumerates `table:table` elements → `FodsSheetInfo` (name, row count, cell count)
  - Security: DTD prohibited, XmlResolver disabled, 50 MB size guard

**FodsParseResult:** mimetype, OdfVersion, Title, Creator, Subject, InitialCreator, FileSizeBytes, Sheets[], Errors[], Warnings[]
**FodsSheetInfo:** Name, RowCount, CellCount

### 2.2 src/net/fodt/

**Tracked files:**
- `FodtParser.cs` — 321 lines
- `FormatFactory.Fodt.csproj` — project definition
- `README.md` — documentation

**Local (gitignored) artifacts:**
- `bin/` — gitignored, present locally
- `obj/` — gitignored, present locally

**FodtParser.cs analysis:**
- Class: `FodtParser` (sealed)
- Method: `Parse(string filePath) -> FodtParseResult`
- Method: `GetParagraphCount(string filePath) -> int`
- Implementation: Streaming XmlReader — reads document once, counts elements
- Capabilities:
  - Reads FODT file from path
  - Extracts `mimetype`, `version` from `office:document`
  - Extracts `dc:title`, `dc:creator`, `dc:subject`, `meta:initial-creator`
  - Counts `text:p` and `text:h` → ParagraphCount and HeadingCount
  - Counts `text:list` → ListCount
  - Enumerates `table:table` → `FodtTableInfo` (name, row count, cell count)
  - Security: DTD prohibited, XmlResolver disabled, 50 MB size guard

**FodtParseResult:** mimetype, OdfVersion, Title, Creator, Subject, InitialCreator, FileSizeBytes,
ParagraphCount, HeadingCount, ListCount, Tables[], Errors[], Warnings[]
**FodtTableInfo:** Name, RowCount, CellCount

### 2.3 src/python/fods/

**Tracked files:**
- `__init__.py`, `parser.py`, `constants.py`, `exceptions.py`, `neutral_model.py`, `README.md`
- Local: `__pycache__/` (gitignored)

**Implementation:** Iterparse-based streaming parser returning neutral model dict.
Returns: `{mime_type, version, sheets[{name, rows[{cells[{value_type, value, formula}]}]}], errors}`
**Track:** Python FOSS (Apache-2.0, DEC-033 confirmed)

### 2.4 src/python/fodt/

**Tracked files:**
- `__init__.py`, `parser.py`, `constants.py`, `exceptions.py`, `neutral_model.py`, `list_traversal.py`, `README.md`
- Local: `__pycache__/` (gitignored)

**Implementation:** Iterparse-based streaming parser returning neutral model dict.
Returns: `{mime_type, version, paragraphs, lists, tables, word_count, errors}`
**Track:** Python FOSS (Apache-2.0, DEC-033 confirmed)

---

## 3. Commercial Product Capability Classification

### 3.1 src/net/fods — FODS .NET Commercial

| Capability | Status | Evidence |
|---|---|---|
| CURRENTLY_TIER0_READONLY_EXTRACTOR | YES | Streaming parser, count-only output |
| HAS_LOAD_OBJECT_MODEL | NO | No Document/Workbook/Worksheet/Row/Cell object hierarchy |
| HAS_EDIT_MODEL | NO | No mutation API; result objects are data bags only |
| HAS_SAVE_SAME_FORMAT | NO | No serialization/write path at all |
| HAS_ROUNDTRIP_PRESERVATION | NO | No roundtrip tested or possible |
| HAS_EXPORT_HTML | NO | Not implemented |
| HAS_EXPORT_PDF | NO | Not implemented |
| HAS_EXPORT_PNG | NO | Not implemented |
| HAS_FAMILY_CONVERSION | NO | Not implemented |
| HAS_COMMERCIAL_RELEASE_ARCHITECTURE | NO | Single-class extractor; not a product architecture |

**Verdict: CURRENTLY_TIER0_READONLY_EXTRACTOR. Not a commercial product.**

### 3.2 src/net/fodt — FODT .NET Commercial

| Capability | Status | Evidence |
|---|---|---|
| CURRENTLY_TIER0_READONLY_EXTRACTOR | YES | Streaming parser, count-only output |
| HAS_LOAD_OBJECT_MODEL | NO | No Document/Section/Paragraph/Run object hierarchy |
| HAS_EDIT_MODEL | NO | No mutation API; result objects are data bags only |
| HAS_SAVE_SAME_FORMAT | NO | No serialization/write path at all |
| HAS_ROUNDTRIP_PRESERVATION | NO | No roundtrip tested or possible |
| HAS_EXPORT_HTML | NO | Not implemented |
| HAS_EXPORT_PDF | NO | Not implemented |
| HAS_EXPORT_PNG | NO | Not implemented |
| HAS_FAMILY_CONVERSION | NO | Not implemented |
| HAS_COMMERCIAL_RELEASE_ARCHITECTURE | NO | Single-class extractor; not a product architecture |

**Verdict: CURRENTLY_TIER0_READONLY_EXTRACTOR. Not a commercial product.**

### 3.3 src/python/fods and src/python/fodt

**Track:** Python FOSS — intentionally scoped to parse/extract per DEC-033.
These are correct for their stated scope. No commercial capability mismatch.

---

## 4. Source Package Hygiene

### Repo hygiene
- Repository tracked files: CLEAN (only .cs, .csproj, README.md in src/net/)
- bin/, obj/, __pycache__ excluded via .gitignore: CONFIRMED
- .nupkg, .snupkg excluded via .gitignore: CONFIRMED
- No build artifacts committed to repository

### User-supplied ZIP (src/src.zip — untracked)
- File: `src/src.zip` (untracked, not committed)
- Build artifacts in ZIP: 117 entries including:
  - `net/fods/bin/Debug/net10.0/FormatFactory.Fods.dll`
  - `net/fods/bin/Release/net10.0/FormatFactory.Fods.dll`
  - `net/fods/obj/...` (full MSBuild intermediate outputs)
  - Same pattern for net/fodt/
- Classification: **REPO_CLEAN_BUT_USER_ZIP_DIRTY**
- Action required: When creating source review packages, exclude bin/, obj/, __pycache__, .pyc
- The repository itself is clean; this is a review/packaging process gap, not a repo corruption

---

## 5. Gate 11 Status

### FODS Gate 11
- Current recorded status: `commercial_readiness_in_progress`
- DEC-033 resolved: Option B (.NET Commercial Only)
- Tier 0 implementation: EXISTS (FodsParser.cs — streaming extractor)
- Gate 11 APPROVED: NO — explicitly deferred in commit c7ee7ab
- Commercial product complete: NO — Tier 0 only, missing all C2-C10 capabilities

### FODT Gate 11
- Current recorded status: `commercial_readiness_in_progress`
- DEC-033 resolved: Option B (.NET Commercial Only)
- Tier 0 implementation: EXISTS (FodtParser.cs — streaming extractor)
- Gate 11 APPROVED: NO — explicitly deferred in commit c7ee7ab
- Commercial product complete: NO — Tier 0 only, missing all C2-C10 capabilities

---

## 6. Master Plan and Registry Status

- master-plan.md: v2.47 (from memory)
- FODS Gate 11: commercial_readiness_in_progress
- FODT Gate 11: commercial_readiness_in_progress
- Both gates: approval deferred as of c7ee7ab

---

## 7. Product Direction Drift Assessment

**Drift detected:** Prior sprints created and labeled Tier 0 streaming parsers as
"commercial readiness in progress" — which implies forward progress toward commercial product.
However, the code produced does NOT satisfy any of the five commercial requirements:
load → object model → edit → save → convert.

The risk is that future agents treat Tier 0 parser tests passing as "commercial readiness"
and proceed toward Gate 11 approval with an extractor, not a product.

**This sprint's role:** Correct the trajectory by:
1. Explicitly documenting what Tier 0 is and is not
2. Creating a capability model that defines the actual commercial product requirements
3. Creating a roadmap from Tier 0 to commercial product
4. Rebaselining Gate 11 so it cannot be approved with Tier 0 code

---

## 8. Lane A Verdict

```
LANE_A_VERDICT: LANE_A_PASS_SOURCE_GAP_CONFIRMED

files_read:
  - src/net/fods/FodsParser.cs
  - src/net/fodt/FodtParser.cs
  - src/python/fods/ (directory listing)
  - src/python/fodt/ (directory listing)
  - .gitignore
  - git status (including --ignored)
  - src/src.zip (artifact scan)

files_changed: none (audit only)

conflicts_found: none

validation_run: direct source inspection

stop_conditions_checked: YES — no UNKNOWN_REQUIRES_STOP items

lane_verdict: LANE_A_PASS_SOURCE_GAP_CONFIRMED

recommended_integration_action:
  - Proceed to Lane B capability model
  - Ensure master-plan and registry note current .NET code is Tier 0 extractor only
  - Source package hygiene: document src.zip creation policy in Lane G
  - Gate 11 rebaseline: ensure Gate 11 cannot be approved with Tier 0 code alone (Lane D)
```
