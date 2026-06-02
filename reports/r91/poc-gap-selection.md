---
sprint: R91
generated_by: r91-worker
---

# R91 POC Gap Selection

**Source:** `select_poc_gaps.py` run against `product-capability-matrix/poc-targets.yaml`
**Selection date:** 2026-06-02

## Selected Gaps

### Gap 1: FODS .NET — SetCellValue

- **Format:** FODS
- **Track:** .NET (commercial)
- **Capability:** Same-format cell edit
- **POC value:** HIGH (commercial POC)
- **Skill:** `/add-dotnet-api`
- **Rationale:** FODS .NET currently supports read and CSV export. SetCellValue closes the round-trip edit gap, which is the primary commercial value proposition for spreadsheet format support. High-priority for Babar Raza Gate 11 review.

---

### Gap 2: FODT .NET — SaveToFile

- **Format:** FODT
- **Track:** .NET (commercial)
- **Capability:** Same-format save after edit
- **POC value:** HIGH (commercial POC)
- **Skill:** `/add-dotnet-api`
- **Rationale:** FODT .NET currently supports read and text extraction. SaveToFile closes the round-trip edit gap for document format. Paired with SetCellValue as the two highest-value commercial POC APIs in R91.

---

### Gap 3: Netpbm .NET — SetPixelColor

- **Format:** Netpbm (PPM/PGM/PBM)
- **Track:** .NET (commercial)
- **Capability:** Pixel edit API
- **POC value:** MEDIUM (commercial POC)
- **Skill:** `/add-dotnet-api`
- **Rationale:** Netpbm .NET has binary read/write (R86). SetPixelColor adds in-memory pixel editing, completing the image manipulation POC. Medium commercial value — demonstrates image processing capability.

---

### Gap 4: FODT .NET TXT Dogfood Bridge

- **Format:** FODT → TXT
- **Track:** .NET (commercial dogfood)
- **Capability:** Cross-format export from document to text
- **POC value:** HIGH (commercial dogfood)
- **Skill:** `/add-dogfood-export`
- **Rationale:** FODT .NET text extraction exists. A dogfood TXT export completes the commercial dogfood chain for document formats (mirrors PPM→PGM established in R90). Demonstrates cross-format pipeline in .NET.

---

### Gap 5: Python Netpbm PPM — Installed Example

- **Format:** PPM
- **Track:** Python (FOSS)
- **Capability:** Installed package example script
- **POC value:** HIGH (FOSS POC proof)
- **Skill:** `/add-installed-package-example`
- **Rationale:** PPM was added to the package matrix in R86. An installed example demonstrates the FOSS workflow (pip install → import ppm → use). Critical for FOSS publication readiness.

---

## Selection Methodology

Gaps were selected by `select_poc_gaps.py` using the following criteria:
1. Format already has Gate 10 `local_release_candidate_ready`
2. Gap represents a next logical capability step (not a leap)
3. Commercial or FOSS POC value is HIGH or MEDIUM
4. Governed skill exists in `.supervisor/skill-registry.yaml`
5. Not blocked by an unresolved hard-stop

## Not Selected (Deferred)

| Gap | Reason for Deferral |
|-----|---------------------|
| FODP .NET | Overclaim corrected in R78 — format scope not confirmed |
| FODG .NET | Overclaim corrected in R78 — format scope not confirmed |
| ZST publication | Gate 11 G11-G requires human approval (Babar Raza) |
| New format formats | Conway R1-R9 not yet complete — roadmap constraint |

## POC Targets File

Reference: `product-capability-matrix/poc-targets.yaml`

All selected gaps are reflected in `poc-targets.yaml` with `selected: true` and `sprint: R91`.
