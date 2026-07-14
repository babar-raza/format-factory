---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: "Supervisor approval"
skill_type: ATOMIC_SKILL
idempotency: "Same target tool spec (name, description, inputSchema, handler logic) applied against an unchanged tools/supervisor/mcp_bridge.py TOOLS list / handle_call dispatcher produces the same appended TOOLS entry and the same handle_call branch; re-invoking against a tool that has already been added is a no-op (detected by name membership in TOOLS), never a duplicate append"
loc_budget: "0 lines of executable code for this skill itself (prompt-driven 4-phase workflow only; no bundled script) -- guides bounded edits to tools/supervisor/mcp_bridge.py (127 LOC / 3 tools as of this writing); each new tool addition should stay proportional to the existing per-tool footprint (~6-10 LOC TOOLS entry + ~5-10 LOC handle_call branch), matched by an equivalent addition to tests/supervisor/test_mcp_bridge.py"
test_path: "tests/supervisor/test_mcp_bridge.py (existing 4 tests covering the 3 current tools: tools-list membership, one success-path read, one missing-file error-dict case, one unknown-tool-name error-dict case) -- every new tool added via this skill MUST extend this file with an equivalent success-path test and an equivalent error-dict-not-exception test before the invoking taskcard closes"
external_skill_origin: true
external_skill_source: anthropics/skills
external_skill_commit: 9d2f1ae187231d8199c64b5b762e1bdf2244733d
external_skill_license: Apache-2.0
risk_level: MEDIUM
created-by: TC-EXT-026-02
product_track: machinery_governance
---

# /mcp-builder

Formalizes and extends Format Factory's own existing MCP server --
`tools/supervisor/mcp_bridge.py` -- with new tools, using a 4-phase
methodology adapted from anthropics/skills' `mcp-builder`. This is **not**
greenfield scaffolding of a new MCP server project: FF already has exactly
one live MCP server, hand-rolled (no MCP SDK dependency), and this skill's
job is to grow its `TOOLS` list and `handle_call` dispatcher safely, one
bounded tool at a time.

## Attribution

<!--
This skill's 4-phase authoring methodology (Phase 1 Deep Research and
Planning, Phase 2 Implementation, Phase 3 Review and Test, Phase 4 Create
Evaluations) -- including the tool-naming-convention guidance, the
readOnlyHint/destructiveHint/idempotentHint/openWorldHint annotation
concepts, the MCP Inspector (`npx @modelcontextprotocol/inspector`) testing
step, and the 10-question read-only XML-evaluation-pair concept -- is
adapted from the `mcp-builder` skill in `anthropics/skills`, commit
`9d2f1ae187231d8199c64b5b762e1bdf2244733d`. License: Apache-2.0, per the
skill-local `skills/mcp-builder/LICENSE.txt` (confirmed this session under
TC-EXT-026-01 / TC-EXT-001-03; the `anthropics/skills` repository has no
root-level LICENSE file, so this per-skill LICENSE.txt is the operative
grant for the `mcp-builder` directory specifically -- noted explicitly here
because it is easy to assume "no root LICENSE" means "no rights granted,"
which is not the case for this particular skill).

Apache-2.0 requires preservation of copyright/attribution notices in
redistributed/derivative works; it does not require share-alike relicensing
of this derivative file (unlike the CC-BY-SA-4.0 Trail of Bits imports
elsewhere in this family, e.g. `trailmark.md`, `audit-context-building.md`).
This file is a prose adaptation of the upstream skill's documented
methodology, retargeted at FF's actual, real, already-existing
`mcp_bridge.py` implementation -- no upstream code is vendored or executed.
Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule (manual
scan recorded under TC-EXT-026-03, see Governance Note below).
-->

## Purpose

FF has exactly one live MCP server today: `tools/supervisor/mcp_bridge.py`,
registered client-side in `.vscode/mcp.json` under the
`format-factory-supervisor` key (`"command": "python", "args":
["tools/supervisor/mcp_bridge.py"]`). It is a **hand-rolled**, 127-LOC
JSON-RPC 2.0 stdio server -- no MCP SDK dependency -- exposing exactly 3
read-only tools:

- `format_factory__get_sprint_verdict`
- `format_factory__get_next_work_items`
- `format_factory__get_work_item_grade`

This skill governs **adding new tools to that existing server's own `TOOLS`
list and `handle_call` dispatcher**. It does not scaffold a new server
project, does not adopt the official MCP SDK, and does not touch the
client-side server registration (`.vscode/mcp.json`) -- see "Explicit Scope
Exclusion" below.

## `mcp_bridge.py`'s Real Current Structure (read this session, cited by line)

- **No MCP SDK.** Hand-rolled Content-Length / LSP-style stdio framing:
  `_read_message()` (`mcp_bridge.py:67-88`) reads a `Content-Length: <N>\r\n\r\n`
  header then `N` raw bytes; `_send_message()` (`:91-96`) writes the same
  framing back. A naive `for line in sys.stdin` does **not** work against
  this transport -- the module's own docstring calls this out explicitly.
- **`TOOLS`** (`:20-40`) -- a plain Python list of dicts: `name` (always
  `format_factory__`-prefixed), `description`, `inputSchema` (a raw JSON
  Schema dict -- not a Zod or Pydantic model; this server predates and does
  not depend on the official SDK's schema layer).
- **`handle_call(name, args) -> dict`** (`:43-64`) -- an `if`/`elif` chain,
  one branch per tool name. Every existing branch reads exactly one file
  under `reports/supervisor/` (`maturity-signal.json`,
  `next-work-items.json`, `work-item-grades.md`), returns its parsed
  content, and returns `{"error": "not_found", "detail": "..."}` on a
  missing file -- **it never raises**. The final `else` returns
  `{"error": f"unknown_tool: {name}"}`.
- **`main()`** (`:99-124`) -- the stdio loop: reads one message, dispatches
  by `method` (`tools/list` -> `{"tools": TOOLS}`, `tools/call` ->
  `handle_call(...)` wrapped in a JSON-RPC 2.0 `result`/`content` envelope),
  and wraps the whole loop body in `try`/`except Exception` so a bug in a
  handler becomes a JSON-RPC `-32603` error response, never a crashed
  process.
- **Read-only, no state mutation**, by the module's own docstring: "NO
  state mutations -- reads only from `reports/supervisor/*`." All 3 existing
  tools honor this. Adding a mutating tool is a scope change (see Phase 1).
- **Tested** by `tests/supervisor/test_mcp_bridge.py` (4 tests): asserts
  `TOOLS` has exactly 3 entries with the 3 expected names, that
  `get_sprint_verdict` reads `maturity-signal.json` correctly (via
  `monkeypatch.setattr(mb, "_REPO", tmp_path)`), that
  `get_work_item_grade` returns an error dict (not an exception) on a
  missing file, and that an unknown tool name returns an error dict, not a
  raised exception.

## Phase 1 -- Deep Research and Planning (adapted)

- **Coverage tradeoff, retargeted.** Upstream frames this as "full API
  coverage vs. curated workflow tools" for a new external API integration.
  FF's server has no external API -- its "API surface" is FF's own
  `reports/supervisor/*` and `.local/supervisor/*` artifact set. The real
  tradeoff here is: does the new capability belong as **(a)** a new
  read-only tool exposing another local artifact (the pattern all 3
  existing tools follow -- default, low-risk path), or **(b)** a mutating
  tool (a genuinely new capability class the server does not have today --
  any such proposal is a scope change that must be flagged and explicitly
  approved before Phase 2, since it would break the module's own stated
  read-only guarantee)?
- **Tool naming convention.** Preserve the existing
  `format_factory__<verb>_<noun>` prefix (FF's own analogue of upstream's
  `github_create_issue`-style convention) -- e.g. a new tool surfacing
  contradiction state might be named `format_factory__get_contradictions`,
  not `get_contradictions` or `mcp__get_contradictions`.
- **Study the real reference, not the generic spec.** Because this server
  does not use the official SDK, the primary "API to study" is the existing
  3-tool implementation itself (structure above) plus the MCP JSON-RPC 2.0
  message shape it already implements correctly. A live WebFetch against the
  MCP spec or SDK docs is still legitimate here **only** when a proposed new
  tool's shape is not already covered by the existing 3-tool precedent (e.g.
  a genuinely new `inputSchema` shape, or a question about optional
  `annotations` semantics) -- it is not a mandatory step for every addition.

## Phase 2 -- Implementation (adapted)

- **No project-structure scaffolding.** There is exactly one file. This
  phase reduces to two edits: append one entry to `TOOLS` (`mcp_bridge.py`
  lines 20-40) and add one `elif name == "format_factory__<new_tool>":`
  branch to `handle_call` (lines 43-64).
- **No API client / auth / pagination infrastructure** -- this server calls
  no external API and holds no credentials; it only reads local repo files.
  Do not introduce any such infrastructure without a separate, explicitly
  approved architectural change.
- **`inputSchema`**: a raw JSON Schema dict matching the existing 3 tools'
  style (`{"type": "object", "properties": {...}, "required": [...]}`) --
  not Zod, not Pydantic.
- **Annotations
  (`readOnlyHint`/`destructiveHint`/`idempotentHint`/`openWorldHint`)**: the
  existing 3 tools do not wire a formal `annotations` field into their
  `tools/list` entries. Until that field is wired (a separate,
  explicitly-out-of-scope architectural change, tracked here as a known
  gap), every **new** tool added via this skill must at minimum state its
  read-only/idempotent nature in its own `description` string (e.g. "
  Read-only. Idempotent for an unchanged source file.").
- **Error handling**: follow the established pattern exactly -- return
  `{"error": "...", "detail": "..."}` dicts from inside `handle_call`,
  never raise. Only `main()`'s outer `try`/`except` may produce a
  JSON-RPC-level `-32603` error envelope.

## Phase 3 -- Review and Test (adapted)

- **No mandatory MCP Inspector run.** Upstream's `npx
  @modelcontextprotocol/inspector` step targets SDK-based servers
  generically. FF's server is a minimal hand-rolled stdio server already
  covered by a direct pytest suite; an ad hoc manual Inspector session
  remains a legitimate optional debugging aid, but it is not the mandatory
  test gate.
- **Mandatory test gate**: `tests/supervisor/test_mcp_bridge.py`. Every new
  tool must add, at minimum: (a) an update to
  `test_tools_list_returns_three_tools`'s count/name assertions (or a
  renamed equivalent) to reflect the new tool, (b) one success-path test
  (mirroring `test_get_sprint_verdict_reads_signal_file`'s
  `monkeypatch.setattr(mb, "_REPO", tmp_path)` pattern), and (c) one
  error-dict-not-exception test (mirroring
  `test_get_work_item_grade_not_found`).
- **Code-quality pass**: confirm the new branch preserves the file's
  existing invariants -- no new imports beyond stdlib unless justified, no
  network calls, no writes (per the module's own "NO state mutations"
  docstring guarantee) unless the new tool was explicitly approved in Phase
  1 as a scope-changing mutating capability.

## Phase 4 -- Create Evaluations (adapted)

- **Upstream's original design**: 10 read-only, independently verifiable
  Q&A pairs in XML, exercised against the live server via a separate eval
  harness (which, per upstream's own convention, can itself be judged by an
  LLM/Anthropic-API call).
- **FF's adaptation**: this server already has a monitoring counterpart --
  `/check-mcp-status` (`.claude/commands/check-mcp-status.md`, currently
  `status: deferred` pending MCP server integration being active in
  production, per `.supervisor/skill-registry.yaml`). Rather than
  duplicating a separate 10-question XML eval harness, this skill's Phase 4
  is: **(a)** confirm `/check-mcp-status`'s 5-state classification model
  (`CONNECTED`/`DEGRADED`/`TIMEOUT`/`AUTH_FAILED`/`UNREACHABLE`) still
  applies unchanged to the extended server -- it does, since the probe is
  transport-level (can the stdio server be reached and does it respond),
  not tool-specific; and **(b)** once `/check-mcp-status` is activated
  (today: it is not), add the new tool's name to whatever manual
  smoke-test invocation list it references.
- **Cross-reference, explicit**: `/mcp-builder` (this skill) governs
  *adding capability* to `mcp_bridge.py`; `/check-mcp-status` governs
  *verifying the server* (whatever tools it currently exposes) is reachable
  and healthy at runtime. They compose -- build here, monitor there -- and
  neither duplicates the other's job.

## Why `risk_level: MEDIUM` (reconciled explicitly for this adaptation)

Upstream's own risk surface is Phase 1's reference-fetching (WebFetch
against API/SDK docs) and, if a live eval harness were adopted in Phase 4,
Anthropic-API calls to judge eval results. In this FF adaptation, Phase 4's
actual mechanism (the `/check-mcp-status` cross-reference) makes zero
external calls, and Phase 1's WebFetch is now conditional (only needed when
a new tool's shape isn't already covered by the existing 3-tool precedent)
rather than mandatory. `risk_level` is nonetheless kept at `MEDIUM`, not
downgraded to `LOW`, for two reasons: (1) the conditional WebFetch surface
in Phase 1 remains real whenever it is exercised, and (2) if a genuine
eval-harness were ever built out under Phase 4 in the future, it could
reintroduce Anthropic-API calls, and this skill's registration should not
have to be re-graded at that point. The **bounded** scope this skill's
`MEDIUM` rating is measured against is `tools/supervisor/mcp_bridge.py` plus
its own `tests/supervisor/test_mcp_bridge.py` -- not, as in a greenfield
authoring of this skill, "a new, separate server project directory" (there
is no new project here; this is a bounded extension of one existing,
already-reviewed file).

## Explicit Scope Exclusion -- `.vscode/mcp.json`

Confirmed present at `.vscode/mcp.json` this session (gitignored --
`.gitignore:171`), registering 3 servers, including:

```json
"format-factory-supervisor": {
  "type": "stdio",
  "command": "python",
  "args": ["tools/supervisor/mcp_bridge.py"],
  "cwd": "${workspaceFolder}"
}
```

This skill **never** edits `.vscode/mcp.json`. New or extended tools are
added exclusively to `mcp_bridge.py`'s own `TOOLS` list and `handle_call`
dispatcher -- the MCP client discovers tools dynamically at runtime via the
`tools/list` method; it does not enumerate individual tool names in the
config file, so the client-side registration's launch command
(`python tools/supervisor/mcp_bridge.py`) does not change when a tool is
added or removed from the list that command's process exposes. If a task
ever proposes changing `.vscode/mcp.json` itself (a new launch command, a
new server entry, changed `cwd`/`args`), that is out of scope for this
skill and must route through a separate, explicitly authorized change --
not through `/mcp-builder`.

## Allowed Paths

- Read, Grep, Glob -- `tools/supervisor/mcp_bridge.py`,
  `tests/supervisor/test_mcp_bridge.py`,
  `.claude/commands/check-mcp-status.md` (cross-reference only, read-only)
- Edit -- `tools/supervisor/mcp_bridge.py` (bounded: append to `TOOLS` +
  add exactly one new `handle_call` branch per new tool),
  `tests/supervisor/test_mcp_bridge.py` (bounded: add the matching
  success-path + error-dict tests per new tool)
- Bash -- run the project's test binary against the mandatory test gate
  only, e.g. `.venv/Scripts/pytest tests/supervisor/test_mcp_bridge.py`
- WebFetch -- conditional, Phase 1 only, when a proposed new tool's shape
  is not already covered by the existing 3-tool precedent (MCP spec / SDK
  doc lookup); never used to fetch or transmit repository contents to a
  third party

## Forbidden Paths

- **`.vscode/mcp.json`** (FF's live MCP client registration file) -- see
  "Explicit Scope Exclusion" above. Never edited by this skill under any
  circumstance. This is the single most important boundary this skill
  enforces.
- The other two server entries in that same file (`task-master-ai`,
  `claude-flow`) -- untouched, unrelated to this skill regardless.
- `src/python/**`, `src/net/**` -- product source; unrelated to this
  skill's scope.
- Any tool addition that introduces a state-mutating capability without an
  explicit, separately-recorded Phase 1 scope-change approval -- this
  skill's default posture inherits `mcp_bridge.py`'s own "NO state
  mutations -- reads only" docstring guarantee.
- `.supervisor/skill-registry.yaml`, `plans/layers/index.yaml` -- updated
  only via the standard registration pattern (TC-EXT-026-03/04), never
  written ad hoc by this skill during a normal tool-addition invocation.
- Adopting the official MCP SDK as a dependency, or restructuring
  `mcp_bridge.py` into a multi-file project -- both are legitimate future
  architectural changes but are explicitly out of scope for this skill,
  which only grows the existing single-file server incrementally.

## Constraints

- Every new tool must preserve the file's existing invariants: read-only by
  default (mutating tools require an explicit, separately-recorded scope
  change), `format_factory__`-prefixed naming, error-dict-not-exception
  handler behavior, and a matching pytest addition before the invoking
  taskcard closes.
- `.vscode/mcp.json` is never touched, read or written, by this skill's
  Allowed-Paths-governed actions (it may be *read* once, outside this
  skill, to confirm the client registration exists -- see the Purpose
  section above -- but this skill's own Steps never open it).
- No MCP SDK adoption, no multi-file restructuring -- incremental,
  single-file growth only.

## Idempotency Contract

Given an unchanged `tools/supervisor/mcp_bridge.py` and the same proposed
tool spec (name, description, inputSchema, handler logic), this skill's
guided edit produces the same appended `TOOLS` entry and the same
`handle_call` branch. Re-invoking this skill against a tool name that
already exists in `TOOLS` is a no-op (detected by name membership), never a
duplicate append or a second competing branch.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-026 (this import),
this skill was cleared by a manual `/skill-scanner`-equivalent grep-based
review before registration (TC-EXT-026-03 evidence). Its Apache-2.0
attribution is recorded above in both prose and an HTML comment, sourced
from the skill-local `skills/mcp-builder/LICENSE.txt` in `anthropics/skills`
(commit `9d2f1ae187231d8199c64b5b762e1bdf2244733d`) -- confirmed this
session under TC-EXT-026-01 / TC-EXT-001-03, and noted explicitly because
the `anthropics/skills` repository itself carries no root-level LICENSE
file. `/check-mcp-status` (`.claude/commands/check-mcp-status.md`) is this
skill's monitoring counterpart, cross-referenced in Phase 4 above.
