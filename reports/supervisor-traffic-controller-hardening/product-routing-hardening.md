# Product Routing Hardening — Lane D

## Sprint
`FORMAT-FACTORY-SUPERVISOR-TRAFFIC-CONTROLLER-HARDENING-IV-001`

## Purpose
Verify that the Supervisor traffic controller correctly routes based on product family breadth,
rejects SVG as a replacement for Netpbm, retains Netpbm, and enforces the 3-family CLEAN_PASS threshold.

## Product Family Breadth Verification

### Confirmed Active Families (from mainstream replay)
| Family | Stream | Status | Source diffs |
|--------|--------|--------|-------------|
| FODS (.NET) | mainstream | ACTIVE | src/net/fods/FodsDocument.cs |
| FODT (.NET) | mainstream | ACTIVE | src/net/fodt/FodtDocument.cs |
| Netpbm (.NET) | mainstream | ACTIVE | src/net/netpbm/Model/NetpbmImage.cs |
| SYLK (Python) | mainstream | ACTIVE | src/python/sylk/sylk_parser.py |

Confirmed breadth: **4 families** with actual source diffs in git status.

### CLEAN_PASS Threshold
- Minimum required: 3 families with source diffs
- Current: 4 families
- Verdict: **BREADTH_THRESHOLD_MET**

## SVG Replacement Rejection

### Scenario
A routing proposal could incorrectly suggest replacing Netpbm with SVG (a vector format)
because both involve image-adjacent capabilities. This must be rejected.

### Why SVG Cannot Replace Netpbm
1. Netpbm = raster pixel format (P1-P6 binary/ASCII bitmaps)
2. SVG = XML-based vector format — entirely different capability class
3. Netpbm has confirmed source diffs in current sprint (NetpbmImage.cs modified)
4. Replacing Netpbm with SVG would reduce breadth by removing a raster format family
5. SVG is not in poc-targets.yaml as an active target

### Routing Rule Applied
```
IF proposed_replacement.format_class != current_family.format_class:
    REJECT replacement
IF current_family has source_diffs in git_status:
    RETAIN current_family
```

### Verdict: **SVG_REPLACEMENT_REJECTED — NETPBM_RETAINED**

## 3-Family Routing Enforcement

### Mainstream routing packet requirements for CLEAN_PASS
- `families_touched >= 3` — PASS (4 families)
- `source_diffs >= 3` — PASS (4 files: FodsDocument.cs, FodtDocument.cs, NetpbmImage.cs, sylk_parser.py)
- `governed_transcripts >= 3` — tracked in declaration, PARTIAL (3 declared)
- `raw_logs >= 3` — PARTIAL (raw-logs/ directory has 3 files)
- `capability_matrix_deltas >= 3` — tracked in evidence, PARTIAL

### PARTIAL Assessment
Mainstream sprint R113 does not yet meet all CLEAN_PASS conditions.
Current classification: **PARTIAL_GOVERNED_TRANSCRIPTS_NEEDED**

Required action: Mainstream must produce 3+ governed transcripts with raw CLI proof.

## False-Pass Prevention

### Scenario: Evidence-only sprint claiming CLEAN_PASS
If a sprint produces only docs/evidence and no source diffs, it cannot claim CLEAN_PASS.
The traffic controller must route this back to Supervisor for rework.

### Routing result for evidence-only sprint:
- `source_diffs = 0` → classify_mainstream_package returns `PARTIAL_ONE_SOURCE`
- `product_output_floor_met = False` → continuation state = `NO_PRODUCT_OUTPUT_FLOOR`
- Route: REWORK_REQUIRED

### Verified by fixture: `product-family-breadth-proof.json`

## Conclusion

| Check | Result |
|-------|--------|
| 4 families confirmed | PASS |
| Netpbm retained | PASS |
| SVG replacement rejected | PASS |
| 3-family breadth threshold met | PASS |
| False-pass for evidence-only blocked | PASS |

**Lane D Verdict: PRODUCT_ROUTING_HARDENED**
