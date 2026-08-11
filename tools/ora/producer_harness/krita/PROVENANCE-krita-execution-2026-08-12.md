# Real Krita producer-harness execution — provenance record

Base commit this execution was performed against: `e70a35dca` (FF6 Event 518,
the end of the prior session segment — UBL closed, GIMP producer #1 executed).

This is producer #2 (Krita) alongside producer #1 (GIMP,
`../PROVENANCE-gimp-execution-2026-08-11.md`) for 4 obligations compiled
from `POL-LRA-RENDER-01` and siblings. Their release_gates text is
**not identical** — read precisely from `shared/format-contracts/ora.yaml`,
not paraphrased:

- `ORA-RENDER-001`: "Rendering is reproducible and agrees with **at least
  two independent producers/consumers** within declared tolerances." —
  this is the only one of the 4 whose text literally requires two.
- `ORA-COMPOSITE-001`: "All claimed operations match pinned rendering
  references within declared tolerances." — no explicit producer count;
  satisfied by real, independent reference agreement, which two producers
  provide more strongly than one.
- `ORA-ISOLATION-001`: "Isolation semantics agree with independent
  application render**s** for every applicable profile." — plural
  "renders," no explicit "two."
- `ORA-BASELINEASSET-001`: "Generated viewing assets are accepted and
  visually checked by independent **consumers**." — plural "consumers,"
  a distinct CONSUMER-acceptance gate, not a producer-comparison one.

Two full, real, independently-developed producers (GIMP, Krita) is strong
evidence toward all 4 — but only `ORA-RENDER-001`'s own text makes "two" a
literal, checkable requirement. See
`shared/format-contracts/implementation-evidence/ora.yaml`'s own per-obligation
`missing_behavior` entries for the precise, non-conflated disposition of
each.

## Container / image identity

| Field | Value |
|---|---|
| Image tag | `ora-harness-krita:pinned-2026-08-12` |
| Image ID | `sha256:9f07af15684f4f4686f4304c84adaebdc006cc47ca9213d79cc5aae11ba2bdf8` |
| Image created | `2026-08-11T19:32:56.15724762Z` |
| Base image | `ubuntu:22.04` |
| Runtime used | Docker Desktop 28.4.0 (Windows, WSL2 backend) — same runtime already
  detected and used for the GIMP lane; detection order was not re-run since
  Docker was already confirmed working this session |
| Dockerfile | `tools/ora/producer_harness/krita/Dockerfile` (this commit) |
| Entrypoint | `tools/ora/producer_harness/krita/entrypoint.sh` — reused verbatim
  from the GIMP lane's own already-verified manual-Xvfb-plus-`xdpyinfo`-poll
  approach (same host, same root cause for why `xvfb-run` itself is avoided) |
| Automation driver | `tools/ora/producer_harness/krita/pykrita_ext/ora_harness_driver/` —
  a real PyKrita extension (Krita's own documented Python scripting plugin
  mechanism), triggered on `Krita.instance().notifier()`-adjacent
  `createActions(window)`, executing an external, volume-mounted script
  (`tools/ora/producer_harness/krita/scripts/*.py`) via `exec()`, then
  calling `sys.exit(0)` |

## OS / package versions (from a real run, `dpkg -s` + `krita --version` under Xvfb)

```
base_image: ubuntu:22.04
krita_version: krita 5.0.2
krita_package_version: 1:5.0.2+dfsg-1build1
python3_pyqt5_package_version: 5.15.6+dfsg-1ubuntu3
python3_sip_package_version: 4.19.25+dfsg-3build1
xvfb_package_version: 2:21.1.4-2ubuntu1.7~22.04.16
x11_utils_package_version: 7.7+5build2
built_at_utc: 2026-08-11T19:20:24Z
```

(`versions.txt`'s own `krita_version` line, captured at *build* time with no
display available, shows a Qt platform-connection error instead — cosmetic
only; the authoritative real version was captured above from a live,
Xvfb-backed run and matches the apt package version exactly.)

## What building and enabling the plugin actually required (3 wrong guesses, then binary ground truth)

Getting Krita to recognize and load a custom PyKrita extension took 4
distinct attempts at the config format, each ruled out by real evidence
before the next was tried — none guessed twice in a row:

1. **PyQt5 `QSettings`, reasoning "same Qt engine Krita links against"** —
   wrong: Krita's own kritarc reader is KConfig (KDE Frameworks' own config
   system), not plain Qt QSettings. Confirmed by the real error Krita itself
   printed: `kf.config.core: "KConfigIni: In file .../kritarc, line 2: "
   "Invalid escape sequence \"\\0\"."`, repeated for every byte of
   QSettings' own binary `@Variant(...)` blob, which KConfigIni's parser
   does not understand.
2. **Plain KConfig-style comma list, `enable_plugins=ora_harness_driver`** —
   fixed the parse errors (KConfigIni read the file without complaint), but
   Krita's own scripting log then reported the exact root cause directly:
   `krita.scripting: Trying to load plugin "ora_harness_driver" . Enabled:
   false . Broken: false`. The plugin was correctly *discovered* (module
   path resolved, `.desktop` parsed) but not *enabled* — `enable_plugins`
   is not the real per-plugin gate at all.
3. **Per-plugin boolean key, bare module name (`ora_harness_driver=true`)**
   — kritarc byte-for-byte confirmed correct, KConfigIni accepted it, yet
   the identical `Enabled: false` line persisted. Ruled out definitively,
   not by assumption.
4. **Binary ground truth**: extracted printable-ASCII strings directly from
   the compiled `/usr/lib/x86_64-linux-gnu/kritaplugins/kritapykrita.so`
   plugin itself (a plain byte scan, no disassembler) and found the literal
   string `"enable_"` (7 characters, confirmed not truncated by widening
   the scan) — `PythonPluginManager.cpp` builds the real key by string
   concatenation: `"enable_" + moduleName`. Writing `enable_ora_harness_driver=true`
   produced `Enabled: true` on the next run — first attempt at this exact,
   evidence-derived key, not a further guess.

`tools/ora/producer_harness/krita/enable_plugin.py`'s own docstring keeps
this full sequence as a permanent record (all 4 attempts, not just the
final one), matching the same discipline already used for the GIMP lane's
own `generate_scenes.scm` header comments.

## API behavior verified empirically before being relied on (not assumed)

Each of the following was directly confirmed against this real Krita 5.0.2
install via a small, disposable probe script
(`tools/ora/producer_harness/krita/scripts/probe_*.py`) before the real
8-scene matrix (`krita_scenes.py`) was written to depend on it:

- `Krita.instance().createDocument(...)` auto-creates a default
  `"Background"` layer (`opacity="0"`, fully transparent but still an
  extra node) — removed explicitly in every real scene so each has exactly
  the layers it declares.
- `Node.addChildNode(node, None)` inserts the new node as the new TOPMOST
  layer each call (confirmed via the real exported `stack.xml`'s own child
  order) — scenes therefore add children bottom-to-top, matching the
  already-established GIMP-lane convention.
- `Node.setPixelData(bytes, x, y, w, h)` expects **BGRA** byte order per
  pixel (confirmed: colors round-tripped correctly through a real Krita
  export and a fresh-process re-export, decoded by format-factory's own
  PNG decoder).
- `Node.setOpacity()` takes an **integer 0–255**, not a 0–100 percentage or
  a 0.0–1.0 float (confirmed: `setOpacity(128)` exported as
  `opacity="0.501961"`, i.e. exactly `128/255`).
- `Node.setBlendingMode("multiply")` exports as the real, standard
  `composite-op="svg:multiply"` (confirmed by reading the real exported
  XML, not assumed from the string's plausibility).
- Krita's own real `.ora` **group** export always writes
  `isolation="isolate"` literally, regardless of the group's own blend
  mode — confirmed by comparing a default-mode group's export against a
  `"pass through"`-mode group's export: both wrote `isolation="isolate"`;
  `"pass through"` mode instead changes `composite-op` to the
  **non-standard** `"krita:pass through"`, which independently *also*
  forces `is_isolated_group=True` in format-factory's own reader via its
  own composite-op-differs-from-default rule. **Krita's own group
  mechanism therefore cannot produce a genuinely non-isolated group at
  all** — the identical conclusion already reached and fixed for the GIMP
  lane's own `non-isolated-group` scene (see `scene_matrix.py`'s own
  docstring), for a different underlying reason. The fix is the same:
  `non-isolated-group` is scripted with no Krita group node at all (3
  sibling layers), matching the already-verified "equivalent to no group
  at all" principle.

## Exact commands run

Build:

```
docker build --build-arg http_proxy=http://http.docker.internal:3128 \
  --build-arg https_proxy=http://http.docker.internal:3128 \
  -t ora-harness-krita:pinned-2026-08-12 tools/ora/producer_harness/krita
```

Scene generation (all 8 scenes, one Krita process):

```
docker run --rm \
  -v "<repo>/tools/ora/producer_harness/krita/scripts:/scripts:ro" \
  -v "<host-output-dir>:/out" \
  -e ORA_HARNESS_SCRIPT=/scripts/krita_scenes.py \
  -e ORA_HARNESS_LOG=/out/krita-scenes.log \
  -e ORA_HARNESS_SENTINEL=/out/krita-scenes.sentinel \
  -e ORA_HARNESS_OUT=/out \
  ora-harness-krita:pinned-2026-08-12 \
  krita --nosplash
```

Fresh-process re-export (one new Krita process per scene, reopening that
scene's own real `.ora` and exporting via Krita's own native `--export`
CLI — no plugin involved for this step):

```
docker run --rm -v "<host-output-dir>:/out" ora-harness-krita:pinned-2026-08-12 \
  krita --export --export-filename /out/<scene>.png /out/<scene>.ora
```

Consumer-acceptance check (format-factory-generated PNG opened by real
Krita, for `ORA-BASELINEASSET-001`'s own independent-consumer gate):

```
docker run --rm \
  -v "<repo>/tools/ora/producer_harness/krita/scripts:/scripts:ro" \
  -v "<host-output-dir>:/out" \
  -e ORA_HARNESS_SCRIPT=/scripts/consumer_check.py \
  -e ORA_HARNESS_CONSUMER_INPUT=/out/format-factory-generated-mergedimage.png \
  ora-harness-krita:pinned-2026-08-12 \
  krita --nosplash
```

## Exit status

Every real-execution invocation above exited `0`: 1 scene-generation run
(all 8 scenes), 8 fresh-process re-export runs (one per scene), 1
consumer-acceptance run. No hangs, no crashes, no non-zero exits, across
the final, working configuration (earlier plugin-enablement attempts did
not reach this point — see above).

## Output checksums (Krita's own real output, `<host-output-dir>`)

| Scene | `.ora` bytes | `.ora` SHA-256 | `.png` bytes | `.png` SHA-256 |
|---|---|---|---|---|
| `single-opaque-layer` | 1176 | `3f18ad0c00db2aff82b186e2b7cf0267ff4aea09da254d7cad146697f71bb969` | 596 | `71107ea29615314858e42d7fc7498f05299a96e38bf5fa24cbb8bb1c14132bff` |
| `layer-order` | 2459 | `b09fca5073ecbac33a40c65f509f8ccbec8e97263ae4a1f5efe11860781de57c` | 691 | `829fc4e3b198b75ebe4a39b1c8cc6c9eddcb1d94f5bf3fcb69de86785c59697e` |
| `partial-opacity` | 1446 | `1085ebb577b51a2966af37e8281aa3e8906c8d225df25600f31702e6aa513e14` | 595 | `89f85cff3bb474b6005d908ba03706203529cd044503951f2569726f3616abe2` |
| `offset-and-clipping` | 1111 | `c8c0fa3a362500a48065549fecbe14b076eb743eb28fd7838b7c7767173592f8` | 517 | `78ac8d2f1cb7e1085290d841ad1a494c3a263c777dc90f7d83552b454c5fdc56` |
| `hidden-layer` | 1319 | `424a9fe9d79ccdf70a0937e18a5e666ec18e8c2d20542ac51c49acb427c5cbd6` | 506 | `d920ed85ee74cdd67bb6b94c3f74c3bfe9fd1a73653f5cd24863aea5f60dad23` |
| `multiply-blend` | 1342 | `178693301f92e1f588d73bcdf642223cfe63586f09664f5a3db4884ef1d51234` | 513 | `c608fa9ab77b8ef336827fb2bcc722822f37464c5ed3d0117a22aa55e3b74784` |
| `isolated-group-with-opacity` | 1570 | `1e4d71ed57a8fa659ceb76e7db7d8093d46f6c3ce237d9c5e5a19b5b3e11e242` | 508 | `234ec658869ec0b1e1c69cad20eb8938e203d483db42e38fad3292a4d08e17db` |
| `non-isolated-group` | 1579 | `9fd636ccbe8fdf9bd28149e6cdee3a0c00a81ff93bdb8f074e75f3affbef49ab` | 511 | `c14888dfec66bf027767985bda0987320736a8e4230d54da067468fdd8e3be9e` |

These `.ora` files are **real OpenRaster archives serialized entirely by
Krita's own exporter** — no hand-constructed ZIP, no injected `stack.xml`,
no post-hoc repair. `data/*.png` layer members inside each are Krita's own
PNG encoder output; `stack.xml` is Krita's own XML writer output.

All 16 files (8 `.ora` + 8 `.png`) are committed verbatim at
`tools/ora/producer_harness/krita/evidence-2026-08-12/` — the checksums
above were independently re-verified against those committed copies, not
only against this document's own prose claim, so a third party can
reproduce every check in this document (STRICT-mode acceptance, pixel
comparison) directly against real, versioned bytes without re-running
Krita at all.

## Format-factory reader results (STRICT mode, the real `.ora` files above)

All 8: **accepted, zero recovery actions** (`ReadMode.STRICT`, not
`TOLERANT`) — Krita's own OpenRaster export is fully spec-conformant
against this package's own strict reader, unlike the vendored MyPaint
corpus (2 of 3 files need `ReadMode.TOLERANT` for real, disclosed
non-conformances — see that corpus's own `PROVENANCE.md`). This is real,
first-time evidence that a strict conformance implementation and a second
real producer's default export agree without any compatibility allowance.

## Comparison results (Krita vs. format-factory's own renderer)

All 8 scenes, pixel-exact (`tolerance=0`), via
`tools/ora/producer_harness/compare.py::compare_scene`, using the PNG each
scene's own **fresh Krita re-export** produced (not the pre-export
in-memory projection) — this exercises Krita's own OpenRaster
serialization and re-import path, not merely its in-memory compositor:

| scene_id | pixel_exact_match | byte_diff_fraction | max_channel_delta |
|---|---|---|---|
| `single-opaque-layer` | True | 0.0 | 0 |
| `layer-order` | True | 0.0 | 0 |
| `partial-opacity` | True | 0.0 | 0 |
| `offset-and-clipping` | True | 0.0 | 0 |
| `hidden-layer` | True | 0.0 | 0 |
| `multiply-blend` | True | 0.0 | 0 |
| `isolated-group-with-opacity` | True | 0.0 | 0 |
| `non-isolated-group` | True | 0.0 | 0 |

**8/8 exact, first full run** — no scene-level defects were found this
time (contrast with the GIMP lane, which needed 2 defects fixed across 2
full runs). The only real corrections needed were in the *plugin
enablement infrastructure* (documented above), not in the scene
comparisons themselves, once the already-GIMP-verified `non-isolated-group`
redesign and the empirically-confirmed API details (BGRA, 0–255 opacity,
bottom-to-top insertion order) were applied from the start.

## What this evidence does and does not establish

- **Does establish:** Krita, a real, independently-developed OpenRaster
  producer (separate codebase, separate upstream project, separate
  compositing engine — C++/Qt/KDE Frameworks vs. GIMP's own C/GEGL), run
  genuinely independently of format-factory's own code, agrees
  pixel-exactly with format-factory's own renderer across the full 8-scene
  matrix, via real `.ora` files it serialized itself and a fresh process
  reopened and re-exported — proving both compositing agreement AND
  container round-trip fidelity. Krita also successfully opened a
  format-factory-*generated* PNG asset (consumer-acceptance evidence for
  `ORA-BASELINEASSET-001`).
- **Asymmetry with the GIMP lane, disclosed rather than smoothed over:**
  GIMP's own apt package ships no OpenRaster plugin at all (see the GIMP
  PROVENANCE doc), so GIMP's own evidence is real, independent PIXEL
  COMPOSITING agreement (a plain flattened PNG export, compared in the
  same in-process run it was constructed in) — it does **not** include a
  save-as-`.ora`-then-reopen-in-a-fresh-process round trip the way Krita's
  evidence does. Both are genuine, real, independently-produced pixel
  agreement for the render/composite/isolation semantics these 4
  obligations actually name (compositing math, not container framing,
  which is `ORA-CONTAINER-001`'s own separate concern) — but they are not
  evidentially equal in strength, and this document does not claim they
  are.
- **Does not establish:** that every conceivable OpenRaster producer or
  every possible scene/semantic agrees — this is a fixed, deliberately
  small, orthogonal 8-scene matrix (not exhaustive), and MyPaint's own
  real, independently-produced files remain supplementary compatibility
  evidence (structural conformance, not pixel comparison) per their own
  `PROVENANCE.md` — not miscounted toward this specific gate.

## Correction after a second, skeptical review pass (2026-08-12)

A first independent review provisionally accepted `ORA-COMPOSITE-001` as
closed by this evidence. A required second re-review (this session's own
"`ACCEPTED_WITH_CHANGES` must be repaired and re-reviewed" rule) caught a
real overclaim before it was finalized: that obligation's own release gate
says "**all** claimed operations match pinned rendering references," and
its own rule_text names the "**complete** compositing-operation inventory"
— `COMPOSITE_OP_REGISTRY` declares 15 blend functions and 6 Porter-Duff
operators, and this session's own evidence verified exactly 1 of each
(`svg:multiply`, `source-over`) against real producers. `ORA-COMPOSITE-001`
correctly stays `partial` — see `implementation-evidence/ora.yaml`'s own
current entry for the precise remaining gap. `ORA-RENDER-001` and
`ORA-ISOLATION-001` genuinely close: their own rule_text clauses (order,
offsets, clipping, opacity, visibility, isolation) are each directly
exercised by this scene matrix, unlike `ORA-COMPOSITE-001`'s own
much-larger enumerated-inventory requirement. Final ORA reconciliation
after this correction: **2/134 unresolved** (down from 4/134) —
`ORA-COMPOSITE-001` (full-inventory gap, this section) and
`ORA-BASELINEASSET-001` (the "visually checked" gap, above).
