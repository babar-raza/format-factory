# Skill Transcript: Netpbm Sepia

- **Skill:** /add-dotnet-api
- **Sprint:** mainstream-r110
- **Format:** Netpbm
- **API:** Sepia() → NetpbmImage
- **Behavior:** Create sepia-toned copy. PPM: converts to luminance then tints (R*1.0, G*0.8, B*0.6). PBM/PGM: returns clone.
- **Source:** src/net/netpbm/Model/NetpbmImage.cs
- **Pre-SHA:** 99f60913e9adc0c677b8c253ba6b9df1074e918532aadfbaeef9aa2a9b44deb7
- **Post-SHA:** 323497ab7377d0797cfdb88988f9ed0113c6d16fb77b751a9e2676ecaf3869ba
- **Tests:** tests/net/netpbm/NetpbmR110SepiaTests.cs (10 tests)
- **Ledger Entry:** R110-GOVERNED-DOTNET-NETPBM-SEPIA-001
- **Depth Class:** image_processing_depth
