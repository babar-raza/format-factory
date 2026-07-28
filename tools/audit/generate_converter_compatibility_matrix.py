"""generate_converter_compatibility_matrix.py — emit registry/converter-compatibility-matrix.yaml.

TC-PA-008 / V251 (mission PORTFOLIO-AUDIT-2026-07-16). Regenerates the information-model
compatibility classification for every *_to_*.py converter under src/python/ from the
format-domain model below. Re-run after adding or removing a converter; V251 FAILs on any
converter module with no entry.

The domain map and pair rules ARE the substance of the gate: they encode what kind of
information each format can represent, and therefore whether a given conversion can carry
meaning at all. Changing a classification is a governance decision, not a formatting change.

Usage: python tools/audit/generate_converter_compatibility_matrix.py
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools" / "supervisor"))
import yaml
from governance_validators_converter_compat import discover_converters

# Information model of each format. This is the substance of the gate: what KIND of
# information the format can represent.
DOMAIN = {
    # grid of addressable cells
    "csv": "TABULAR", "tsv": "TABULAR", "dif": "TABULAR", "sylk": "TABULAR",
    "gnumeric": "TABULAR", "ods": "TABULAR", "fods": "TABULAR",
    # flowed, styled text
    "abw": "DOCUMENT", "fodt": "DOCUMENT", "odt": "DOCUMENT",
    # slide sequence
    "fodp": "PRESENTATION",
    # vector geometry
    "fodg": "DRAWING",
    # pixel grid
    "pbm": "RASTER", "pgm": "RASTER", "ppm": "RASTER", "qoi": "RASTER", "xcf": "RASTER",
    # tree / record structures
    "ndjson": "STRUCTURED_DATA", "toml": "STRUCTURED_DATA", "ipynb": "STRUCTURED_DATA",
    "ubl": "STRUCTURED_DATA", "xliff": "STRUCTURED_DATA", "mtlx": "STRUCTURED_DATA",
    "abw_typed_children": "DOCUMENT",  # abw sub-model extractor
    # n-dimensional numeric arrays
    "safetensors": "TENSOR", "nrrd": "TENSOR",
    # byte container
    "zst": "CONTAINER",
}

# Pair rules, most specific first. (source_domain, target_domain) -> (category, rationale)
RULES = {
    ("TABULAR", "RASTER"): ("INCOMPATIBLE",
        "A cell grid's payload (typed values, text, formulas) has no representation in a "
        "pixel raster. Every observed implementation reduces each cell to ONE trivial scalar "
        "and writes it as a pixel — measured 2026-07-17: *_to_pbm emits an occupancy bit "
        "(1 if v.strip() else 0), *_to_pgm emits min(255, len(v)) as grey, *_to_ppm emits "
        "ord(v[0:1]) as colour. None preserves any cell's value; none is round-trippable. "
        "These are sparsity/length visualisations mislabelled as format conversions."),
    ("DOCUMENT", "RASTER"): ("INCOMPATIBLE",
        "Flowed, styled text has no pixel representation absent a layout+font rasteriser, "
        "and none is present. The implementations reduce each text run to one scalar per "
        "pixel (occupancy / length / first-char code — measured 2026-07-17), discarding the "
        "prose entirely."),
    ("STRUCTURED_DATA", "RASTER"): ("INCOMPATIBLE",
        "A record/tree structure has no pixel representation; the implementations encode a "
        "single scalar per field (occupancy / length / first-char code) and lose the data."),
    ("PRESENTATION", "RASTER"): ("INCOMPATIBLE",
        "Slide content requires a layout renderer to rasterise; none is present, so the "
        "implementations fall back to the same one-scalar-per-pixel reduction."),
    ("TENSOR", "RASTER"): ("PROJECTION",
        "A 2-D/3-D numeric array maps onto a pixel grid directly when shape and dtype "
        "permit; lossy in dtype range and channel semantics."),
    ("DRAWING", "RASTER"): ("PROJECTION",
        "Rasterising vector geometry is a legitimate, standard operation; lossy (resolution, "
        "editability). NOTE: V251 gates the declared relationship only — it does not verify "
        "that the implementation actually rasterises."),
    ("RASTER", "TABULAR"): ("PROJECTION",
        "A pixel grid IS a numeric grid; emitting it as rows/columns is faithful and "
        "reversible for the sample values, losing only image metadata."),
    ("RASTER", "STRUCTURED_DATA"): ("PROJECTION",
        "Pixel samples plus header fields serialise to records; loses image semantics."),
    ("RASTER", "TENSOR"): ("PROJECTION", "A pixel grid is a typed n-d array; near-lossless."),
    ("TENSOR", "TABULAR"): ("PROJECTION", "A 2-D slice of an array is a cell grid; loses rank>2 and dtype."),
    ("TENSOR", "STRUCTURED_DATA"): ("PROJECTION", "Array header/values serialise to records; loses layout."),
    ("DOCUMENT", "TABULAR"): ("PROJECTION",
        "Extracting each paragraph as a row is documented and useful; loses styling, "
        "structure, and inline objects."),
    ("TABULAR", "DOCUMENT"): ("PROJECTION",
        "Rendering a grid as a document table or paragraph run; loses formulas and cell typing."),
    ("PRESENTATION", "TABULAR"): ("PROJECTION", "Slide text extracted as rows; loses layout and media."),
    ("PRESENTATION", "DOCUMENT"): ("PROJECTION", "Slide text as flowed paragraphs; loses slide structure."),
    ("DRAWING", "TABULAR"): ("PROJECTION", "Shape properties as rows; loses geometry and rendering."),
    ("DRAWING", "DOCUMENT"): ("PROJECTION", "Text elements extracted from the canvas; loses geometry."),
    ("TABULAR", "DRAWING"): ("PROJECTION", "Cells laid out as positioned shapes; loses cell semantics."),
    ("DOCUMENT", "DRAWING"): ("PROJECTION", "Paragraphs as positioned text shapes; loses flow."),
    ("STRUCTURED_DATA", "TABULAR"): ("PROJECTION", "Records flatten to rows; loses nesting."),
    ("TABULAR", "STRUCTURED_DATA"): ("PROJECTION", "Rows serialise to records; loses cell typing/formulas."),
    ("DOCUMENT", "STRUCTURED_DATA"): ("PROJECTION", "Document tree serialises to records; loses styling."),
    ("STRUCTURED_DATA", "DOCUMENT"): ("PROJECTION", "Records rendered as paragraphs; loses type info."),
    ("STRUCTURED_DATA", "DRAWING"): ("PROJECTION", "Records as positioned shapes; loses structure."),
    ("TENSOR", "DOCUMENT"): ("PROJECTION", "Array summary as prose/table; heavily lossy."),
    ("TENSOR", "DRAWING"): ("PROJECTION", "Array values plotted as geometry; heavily lossy."),
    ("RASTER", "DOCUMENT"): ("PROJECTION", "Image embedded/described in a document; loses pixels unless embedded."),
    ("RASTER", "DRAWING"): ("PROJECTION", "Image embedded as a canvas object; no vectorisation implied."),
    ("PRESENTATION", "STRUCTURED_DATA"): ("PROJECTION", "Slide tree serialises to records; loses layout."),
    ("PRESENTATION", "DRAWING"): ("PROJECTION", "Slide shapes onto a canvas; loses slide sequencing."),
    ("DRAWING", "STRUCTURED_DATA"): ("PROJECTION", "Shape tree serialises to records; loses rendering."),
    ("DOCUMENT", "PRESENTATION"): ("PROJECTION", "Sections become slides; loses flow."),
    ("TABULAR", "PRESENTATION"): ("PROJECTION", "Rows become slide content; loses cell semantics."),
}

repo = REPO
convs = discover_converters(repo / "src" / "python", repo)

entries = {}
unknown = []
for c in convs:
    s, t = c["source"], c["target"]
    ds, dt = DOMAIN.get(s), DOMAIN.get(t)
    if ds is None or dt is None:
        unknown.append((s, t))
        continue
    if ds == dt:
        cat = "COMPATIBLE"
        rat = (f"Both {s} and {t} are {ds}: they share an information model, so the mapping "
               f"is structure-preserving and round-trippable modulo format-specific features.")
    else:
        cat, rat = RULES.get((ds, dt), (None, None))
        if cat is None:
            unknown.append((s, t))
            continue
    entries[c["path"]] = {
        "pair": c["pair"],
        "source_domain": ds,
        "target_domain": dt,
        "category": cat,
        "rationale": rat,
        **({"disposition": "PENDING"} if cat == "INCOMPATIBLE" else {}),
    }

if unknown:
    print("UNCLASSIFIED PAIRS (must be resolved):", sorted(set(unknown)))
    raise SystemExit(1)

from collections import Counter
counts = Counter(e["category"] for e in entries.values())
doc = {
    "schema_version": "1.0",
    "taskcard": "TC-PA-008",
    "validator": "V251",
    "mission_id": "PORTFOLIO-AUDIT-2026-07-16",
    "authority": (
        "Information-model compatibility classification for every converter module under "
        "src/python/. V251 FAILs on any *_to_*.py module with no entry here. This registry is "
        "the gate /add-dogfood-export never had: it forces the question 'does this conversion "
        "carry meaning?' to be answered before code is generated (TC-PA-009 wires it in)."
    ),
    "categories": {
        "COMPATIBLE": "Source and target share an information model. Structure-preserving.",
        "PROJECTION": "Different models, defensible documented mapping, known loss.",
        "INCOMPATIBLE": ("No semantic relationship; the implementation must invent structure "
                          "absent from the source. Should not exist — TC-PA-015 disposition."),
    },
    "scope_limit": (
        "V251 gates the DECLARED relationship of a format pair, derived from format domains. "
        "It does NOT read converter bodies: a faithful PROJECTION and a lazy one are "
        "indistinguishable to it. Implementation semantics remain ungated (TC-PA-016)."
    ),
    "format_domains": dict(sorted(DOMAIN.items())),
    "totals": {"converters": len(entries), **{k: counts[k] for k in sorted(counts)}},
    "converters": dict(sorted(entries.items())),
}
out = repo / "registry" / "converter-compatibility-matrix.yaml"
out.write_text(yaml.safe_dump(doc, sort_keys=False, width=100), encoding="utf-8")
print(f"wrote {out.relative_to(repo).as_posix()}: {len(entries)} converters -> {dict(counts)}")
inc = sorted(p for p, e in entries.items() if e["category"] == "INCOMPATIBLE")
print(f"\nINCOMPATIBLE ({len(inc)}):")
for p in inc[:50]:
    print("   ", p)
