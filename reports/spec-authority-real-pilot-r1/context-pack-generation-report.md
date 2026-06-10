# Context Pack Generation Report — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Lane: E

---

## Context Packs Generated

3 context packs generated (minimum requirement: ZST and Netpbm). FODS/FODT not packaged (stretch pilot; full extraction deferred).

| Format | Context Pack ID | Manifest SHA-256 | Requirements | Output Path |
|---|---|---|---|---|
| zst | CP-ZST-a1269259b41f | `a1269259b41fd61cc613ecccdfb23354a5d58a749670beb89d7ecf3da3cafcdc` | 17 | `.local/evidences/spec-authority-real-pilot-r1/context-packs/zst-context-pack.json` |
| netpbm | CP-NETPBM-d746e21cf23d | `d746e21cf23d4ab761a1bf478928de83fee476adf474f2cde7b3deef5585b55f` | 13 | `.local/evidences/spec-authority-real-pilot-r1/context-packs/netpbm-context-pack.json` |
| dif | CP-DIF-fde58d1d14fc | `fde58d1d14fc2fc95cfb21c00b3b67c13eec693ca2b587da8baf783b2eb7ef04` | 8 | `.local/evidences/spec-authority-real-pilot-r1/context-packs/dif-context-pack.json` |

---

## Determinism Test — Run 1 vs Run 2

Context pack generation run twice from identical inputs (same normalized artifacts, same source records).

| Format | Run 1 manifest_sha256 | Run 2 manifest_sha256 | Deterministic |
|---|---|---|---|
| zst | `a1269259b41fd61c...` | `a1269259b41fd61c...` | **PASS** |
| netpbm | `d746e21cf23d4ab7...` | `d746e21cf23d4ab7...` | **PASS** |
| dif | `fde58d1d14fc2fc9...` | `fde58d1d14fc2fc9...` | **PASS** |

**Determinism result: PASS for all 3 context packs.**

Determinism mechanism: `_compute_manifest_sha256()` in `context_pack_builder.py` uses:
```python
sorted(sources, key=lambda x: x.get("source_id", ""))
# parts: "{source_id}:{sha256}:{sections_count}"
# sha256(join(parts))
```
Timestamps (`created_at`) are present in the pack JSON but excluded from the canonical hash.
Same canonical inputs → same `manifest.sha256`.

---

## Context Pack Verification

All 3 context packs passed `verify_context_pack()`:
- `manifest.sha256` present: YES
- `format_id` present: YES
- `context_pack_id` present: YES
- Recomputed SHA matches stored SHA: YES (all 3)

| Format | valid | reason |
|---|---|---|
| zst | True | CP-ZST-a1269259b41f verified |
| netpbm | True | CP-NETPBM-d746e21cf23d verified |
| dif | True | CP-DIF-fde58d1d14fc verified |

---

## FODS/FODT Context Pack

Not built in this pilot. Reason: stretch target; fixture extraction is partial (structural only); full ODF 1.3 context pack deferred to Pilot R2.
Artifact evidence: normalized + indexed artifacts exist for `src-fods-oasis` but no context pack output.
Recommendation: Pilot R2 should fetch full ODF 1.3, extract comprehensive requirements, then build FODS context pack.

---

## Defects

None discovered. All 3 context packs built, verified, and deterministic.
