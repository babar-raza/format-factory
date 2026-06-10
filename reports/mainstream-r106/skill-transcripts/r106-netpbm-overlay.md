# Skill Transcript: Netpbm Overlay

- **Skill:** /add-dotnet-api
- **Format:** Netpbm
- **API:** Overlay(NetpbmImage overlay, int topOffset, int leftOffset)
- **Sprint:** mainstream-r106
- **Source:** src/net/netpbm/Model/NetpbmImage.cs
- **Tests:** tests/net/netpbm/NetpbmR106OverlayTests.cs (10 tests, all pass)
- **Ledger entry:** reports/r90/product-code-change-ledger.json (R106-NETPBM-OVERLAY)
- **Behavior:** Creates a new image by cloning the base and copying overlay pixels onto it at the specified offset. Validates format match. Throws on negative offsets. Non-mutating.
- **SHA-256:** 4d36d30dcd40d65ad7f7a5cde92b91feabf9d03cef0aec13e673d7e6c0e930f7
