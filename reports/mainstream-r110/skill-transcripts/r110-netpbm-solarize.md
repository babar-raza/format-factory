# Skill Transcript: Netpbm Solarize

- **Skill:** /add-dotnet-api
- **Sprint:** mainstream-r110
- **Format:** Netpbm
- **API:** Solarize(byte threshold) → NetpbmImage
- **Behavior:** Create solarized copy. Pixels above threshold are inverted (MaxValue - pixel). PBM returns clone. PPM applies per-channel.
- **Source:** src/net/netpbm/Model/NetpbmImage.cs
- **Pre-SHA:** 99f60913e9adc0c677b8c253ba6b9df1074e918532aadfbaeef9aa2a9b44deb7
- **Post-SHA:** 323497ab7377d0797cfdb88988f9ed0113c6d16fb77b751a9e2676ecaf3869ba
- **Tests:** tests/net/netpbm/NetpbmR110SolarizeTests.cs (8 tests)
- **Ledger Entry:** R110-GOVERNED-DOTNET-NETPBM-SOLARIZE-001
- **Depth Class:** image_processing_depth
