# Skill Transcript: Netpbm BlurBox

- **Skill:** /add-dotnet-api
- **Sprint:** mainstream-r111
- **Format:** Netpbm
- **API:** BlurBox(radius) → NetpbmImage
- **Behavior:** Apply NxN box blur (kernel = (2*radius+1)^2). PBM returns clone. Clamps to max.
- **Source:** src/net/netpbm/Model/NetpbmImage.cs
- **Pre-SHA:** 323497ab7377d0797cfdb88988f9ed0113c6d16fb77b751a9e2676ecaf3869ba
- **Post-SHA:** 6d1b16be0907f0628fa3ea5bc8ad8abc171fc80ffb966022a9a40bf11b084ba9
- **Tests:** tests/net/netpbm/NetpbmR111BlurBoxTests.cs (10 tests)
- **Ledger Entry:** R111-GOVERNED-DOTNET-NETPBM-BLURBOX-001
- **Depth Class:** image_processing_depth
