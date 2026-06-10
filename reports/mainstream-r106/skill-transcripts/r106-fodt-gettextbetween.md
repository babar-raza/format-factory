# Skill Transcript: FODT GetTextBetweenParagraphs

- **Skill:** /add-dotnet-api
- **Format:** FODT
- **API:** GetTextBetweenParagraphs(int startIndex, int endIndex)
- **Sprint:** mainstream-r106
- **Source:** src/net/fodt/FodtDocument.cs
- **Tests:** tests/net/fodt/FodtR106GetTextBetweenTests.cs (8 tests, all pass)
- **Ledger entry:** reports/r90/product-code-change-ledger.json (R106-FODT-GETTEXTBETWEEN)
- **Behavior:** Returns concatenated text of paragraphs from startIndex (inclusive) to endIndex (exclusive), joined by newlines. Returns null if indices out of range or start >= end.
- **SHA-256:** 985aef9f96f48738cf095fe9ab64f5e96a3dde3c025cba60ecf24945f348aa26
