# Skill Transcript: Netpbm Sharpen

- **Skill:** /add-dotnet-api
- **Sprint:** mainstream-r111
- **Format:** Netpbm
- **API:** Sharpen() → NetpbmImage
- **Behavior:** Apply 3x3 unsharp-mask kernel (center=5, edges=-1). PBM returns clone.
- **Source:** src/net/netpbm/Model/NetpbmImage.cs
- **Pre-SHA:** 323497ab7377d0797cfdb88988f9ed0113c6d16fb77b751a9e2676ecaf3869ba
- **Post-SHA:** 6d1b16be0907f0628fa3ea5bc8ad8abc171fc80ffb966022a9a40bf11b084ba9
- **Tests:** tests/net/netpbm/NetpbmR111SharpenTests.cs (8 tests)
- **Ledger Entry:** R111-GOVERNED-DOTNET-NETPBM-SHARPEN-001
- **Depth Class:** image_processing_depth
