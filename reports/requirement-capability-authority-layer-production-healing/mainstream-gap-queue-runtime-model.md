# Mainstream Gap Queue Runtime Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane D

## 11-Step Algorithm

**Step 1:** Load the POC target model from poc-targets.yaml (read-only). For each target product,
identify: capability families required, proof sufficiency level required, dogfood_required, and
accepted_with_limitations policy.

**Step 2:** Load the current proof graph (capability-graph-nodes.jsonl + capability-graph-edges.jsonl).
Compute the source_graph_hash for this snapshot.

**Step 3:** Compute claim coverage for every CapabilityClaim node in the graph. For each claim:
run CapabilityCoverageEvaluator; record CoverageRecord status (clean, partial, or blocked_{reason}).

**Step 4:** Identify blocked claims. A claim is blocked if its CoverageRecord is any blocked_* state
or if the claim status is stale, rejected, or blocked. For each blocked claim: record which proof
types are missing (missing_proof_types list).

**Step 5:** Group blocked claims by product_id and capability_family. For each POC target:
which capability families have blocked claims? Which are fully coverage_validated?

**Step 6:** Rank by POC impact. Claims in capability families that are required_for_poc (per
poc-targets.yaml) rank higher than stretch claims. Claims where the POC target is not yet
accepted_for_poc rank higher than targets already at accepted_with_limitations.

**Step 7:** Rank by smallest missing proof count. Within the same POC impact group, claims with
fewer missing_proof_types rank higher. A claim missing only DogfoodProof ranks above a claim
missing ImplementationProof + TestProof + DogfoodProof.

**Step 8:** Apply product preference. Prefer required commercial targets (FODS, FODT, Netpbm .NET)
and required FOSS targets (ZST, Python Netpbm, SYLK). Include DIF and Gnumeric only if their gap
closure is faster than the remaining required targets' gaps.

**Step 9:** Generate lane-specific gap entries. For each ranked gap, determine: recommended_lane
(LaneA/B/C based on complexity), expected_files (which source files to add or modify),
expected_tests (which test file pattern to add), expected_dogfood (which dogfood output to produce).

**Step 10:** Apply stop conditions. Some gaps have stop_conditions that prevent automation:
"cannot continue until ProductPolicyDecision is recorded", "cannot continue until UnsupportedFeature
severity is classified". Flag these as REQUIRES_HUMAN_DECISION in the queue.

**Step 11:** Emit mainstream-gap-queue.json. The file contains: queue_generated_at, source_graph_hash,
queue_entries (sorted list), and per-entry all 15 gap entry fields (see below).

## 10 Priority Scoring Fields

1. **poc_required_weight** — 1.0 if claim is in a required POC target family; 0.5 for stretch; 0.0 for not_applicable
2. **product_family_weight** — 1.0 for commercial required targets; 0.8 for FOSS required; 0.5 for stretch targets
3. **missing_proof_count** — Integer: number of missing proof types. Lower is better (closer to acceptance)
4. **dogfood_unlock_score** — 1.0 if adding DogfoodProof unlocks accepted_for_poc for this claim; 0.0 otherwise
5. **implementation_present_bonus** — +0.2 if ImplementationArtifact already linked; reduces risk
6. **tests_present_bonus** — +0.2 if TestArtifact already linked; reduces risk
7. **overclaim_penalty** — −0.3 if claim has an active overclaim flag; requires decomposition before gap is workable
8. **stale_penalty** — −0.5 if claim is in stale state; revalidation required before gap can close
9. **cross_stream_packet_bonus** — +0.1 if gap closure will produce a StreamHandoff for Skills lane
10. **risk_penalty** — −0.2 for gaps requiring external dependency resolution; −0.4 for gaps requiring policy decision

## 15 Queue Entry Fields

1. **gap_id** — Unique identifier for this gap entry (format: gap-{product_id}-{family}-{missing_proof})
2. **target_product** — Which POC target this gap blocks (e.g., fods, fodt, netpbm-net, zst)
3. **format_id** — Format family (e.g., fods, fodt, ppm, sylk, dif)
4. **claim_id** — The CapabilityClaim this gap belongs to
5. **missing_proof_type** — Which proof class is missing (RequirementProof, TestProof, DogfoodProof, etc.)
6. **next_action** — Specific action Mainstream must take (e.g., "add TestArtifact for claim-fods-export-001")
7. **expected_files** — List of source file paths expected to be created or modified
8. **expected_tests** — List of test file paths expected to be added or updated
9. **expected_dogfood** — Path and format of DogfoodArtifact expected to be produced (null if not required)
10. **recommended_lane** — Which Mainstream lane should work this gap (complexity-based)
11. **validation_command** — Command to run after work is done to validate gap closure
12. **estimated_unlock** — Which other claims or POC targets this gap closure unblocks
13. **dependencies** — List of other gap_ids that must be closed before this one
14. **stop_conditions** — Conditions under which Mainstream must pause and await human decision
15. **priority_score** — Computed float score from priority scoring fields (higher = work first)

## Product Examples (6)

**FODS gap entry:**
```json
{
  "gap_id": "gap-fods-cell_write-dogfood",
  "target_product": "fods",
  "format_id": "fods",
  "claim_id": "claim-fods-cell_write-save",
  "missing_proof_type": "DogfoodProof",
  "next_action": "Produce a .fods output file by running the save operation on a real FODS document",
  "expected_files": ["src/net/fods/FodsDocument.cs"],
  "expected_tests": ["tests/net/fods/FodsR*SaveRoundtrip*.cs"],
  "expected_dogfood": "examples/net/fods/dogfood-output.fods",
  "recommended_lane": "LaneA",
  "validation_command": "python tools/requirements_authority/run_coverage_evaluator.py --claim claim-fods-cell_write-save",
  "estimated_unlock": ["accepted_for_poc: fods cell_write family"],
  "dependencies": [],
  "stop_conditions": [],
  "priority_score": 0.92,
  "dogfood_unlock_score": 1.0
}
```

**FODT gap entry:**
```json
{
  "gap_id": "gap-fodt-paragraph_write-test",
  "target_product": "fodt",
  "format_id": "fodt",
  "claim_id": "claim-fodt-paragraph_write-save",
  "missing_proof_type": "TestProof",
  "next_action": "Add roundtrip test: load FODT → append paragraph → write_fodt → reload → verify paragraph count",
  "expected_files": [],
  "expected_tests": ["tests/net/fodt/FodtR*ReplaceTextSaveRoundtrip*.cs"],
  "expected_dogfood": null,
  "recommended_lane": "LaneA",
  "validation_command": "dotnet test tests/net/fodt/",
  "estimated_unlock": ["tests_present: fodt paragraph_write"],
  "dependencies": [],
  "stop_conditions": [],
  "priority_score": 0.85,
  "dogfood_unlock_score": 0.0
}
```

**Netpbm gap entry:**
```json
{
  "gap_id": "gap-netpbm-net-P6-test",
  "target_product": "netpbm-net",
  "format_id": "ppm",
  "claim_id": "claim-netpbm-net-image_save-P6",
  "missing_proof_type": "TestProof",
  "next_action": "Add P6 binary write test and produce a valid P6 binary PPM output file",
  "expected_files": ["src/net/netpbm/Model/NetpbmImage.cs"],
  "expected_tests": ["tests/net/netpbm/NetpbmR*P6*.cs"],
  "expected_dogfood": "examples/net/netpbm/dogfood-P6-output.ppm",
  "recommended_lane": "LaneB",
  "validation_command": "dotnet test tests/net/netpbm/",
  "estimated_unlock": ["variant=P6 accepted: netpbm-net image_save family"],
  "dependencies": [],
  "stop_conditions": [],
  "priority_score": 0.82,
  "dogfood_unlock_score": 0.8
}
```

**ZST gap entry:**
```json
{
  "gap_id": "gap-zst-py-streaming-dogfood",
  "target_product": "zst",
  "format_id": "zst",
  "claim_id": "claim-zst-py-streaming-roundtrip",
  "missing_proof_type": "DogfoodProof",
  "next_action": "Stream compress a file and decompress it; verify output bytes are identical to input",
  "expected_files": [],
  "expected_tests": ["tests/python/zst/test_r*_zst_streaming*.py"],
  "expected_dogfood": "examples/python/zst/dogfood-roundtrip.zst",
  "recommended_lane": "LaneC",
  "validation_command": "python -m pytest tests/python/zst/",
  "estimated_unlock": ["dogfood_present: zst streaming roundtrip"],
  "dependencies": [],
  "stop_conditions": [],
  "priority_score": 0.79,
  "dogfood_unlock_score": 1.0
}
```

**SYLK gap entry:**
```json
{
  "gap_id": "gap-sylk-py-write-test",
  "target_product": "sylk",
  "format_id": "sylk",
  "claim_id": "claim-sylk-py-sylk_write-save",
  "missing_proof_type": "TestProof",
  "next_action": "Add write_sylk test that serializes a grid and re-parses to verify round-trip",
  "expected_files": ["src/python/sylk/sylk_parser.py"],
  "expected_tests": ["tests/python/sylk/test_r*_sylk_write_roundtrip*.py"],
  "expected_dogfood": "examples/python/sylk/dogfood-output.slk",
  "recommended_lane": "LaneC",
  "validation_command": "python -m pytest tests/python/sylk/",
  "estimated_unlock": ["tests_present: sylk write family"],
  "dependencies": [],
  "stop_conditions": [],
  "priority_score": 0.74,
  "dogfood_unlock_score": 0.7
}
```

**DIF gap entry:**
```json
{
  "gap_id": "gap-dif-py-write-implementation",
  "target_product": "dif",
  "format_id": "dif",
  "claim_id": "claim-dif-py-dif_write-save",
  "missing_proof_type": "ImplementationProof",
  "next_action": "Implement DIF write (serialize grid to .dif format); add tests and dogfood output",
  "expected_files": ["src/python/dif/dif_writer.py"],
  "expected_tests": ["tests/python/dif/test_r*_dif_write*.py"],
  "expected_dogfood": "examples/python/dif/dogfood-output.dif",
  "recommended_lane": "LaneD",
  "validation_command": "python -m pytest tests/python/dif/",
  "estimated_unlock": ["implementation_present: dif write family"],
  "dependencies": ["gap-dif-py-parse-test"],
  "stop_conditions": ["stop if DIF write is slower to implement than SYLK write"],
  "priority_score": 0.65,
  "dogfood_unlock_score": 0.7
}
```
