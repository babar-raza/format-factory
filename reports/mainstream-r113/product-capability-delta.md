# R113 Product Capability Delta

## New APIs Added (3)

### FODS .NET: SortRows
- **Symbol:** `FodsDocument.SortRows(string sheetName, int sortColumn, bool ascending = true)`
- **Behavior:** Sorts rows in named sheet by column index; numeric-aware; ascending/descending
- **Source:** src/net/fods/FodsDocument.cs
- **Tests:** 20 (FodsR113SortRowsTests + FodsR113InsertRowDepthTests + FodsR113JsonDogfoodTests)

### FODT .NET: GetDocumentMetadata
- **Symbol:** `FodtDocument.GetDocumentMetadata()`
- **Behavior:** Returns IReadOnlyDictionary<string,string> of ODF metadata fields (title, creator, date, etc.)
- **Source:** src/net/fodt/FodtDocument.cs
- **Tests:** 18 (FodtR113GetDocumentMetadataTests + FodtR113ExportTxtDepthTests + FodtR113TxtDogfoodTests)

### Netpbm .NET: Tile
- **Symbol:** `NetpbmImage.Tile(int tilesX, int tilesY)`
- **Behavior:** Creates tiled image by repeating source tilesX*tilesY times; supports PPM/PGM/PBM
- **Source:** src/net/netpbm/Model/NetpbmImage.cs
- **Tests:** 20 (NetpbmR113TileTests + NetpbmR113CropSaveDepthTests + NetpbmR113TileSaveDogfoodTests)

## FOSS Deepening (4 test suites, 32 tests)
- ZST: Dictionary-mode level variation roundtrips
- PPM: Grayscale conversion roundtrip hardening
- SYLK: CSV export workflow verification
- DIF: Parse hardening and error handling
