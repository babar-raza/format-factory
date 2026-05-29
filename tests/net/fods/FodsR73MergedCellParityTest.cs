// FodsR73MergedCellParityTest.cs
// R73 Train D: .NET parity test for merged-cell parsing
// Verifies that the .NET FODS parser can load a FODS file with merged cells
// (table:number-columns-spanned) without errors. Parity with R73 Python
// improvement: merged cell span metadata preservation.
//
// Note: The .NET model does not yet expose col_span/row_span in the cell
// object model (Python was updated in R73). This test proves the parser
// handles merged-cell fixtures without failure — foundation for future
// span exposure in the .NET object model.
//
// Gate 11 status: commercial_readiness_in_progress (NOT approved).

using System;
using System.IO;
using Xunit;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsR73MergedCellParityTest
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    // ------------------------------------------------------------------
    // R73-PARITY-01: Load FODS with merged cells — no parse errors
    // ------------------------------------------------------------------
    [Fact]
    public void Load_FodsWithMergedCells_Succeeds()
    {
        var path = Path.Combine(FixturesDir, "fods-merged-cells.fods");
        var doc = FodsDocument.Load(path);

        Assert.NotNull(doc);
        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet-flat-xml",
                     doc.MimeType);
    }

    // ------------------------------------------------------------------
    // R73-PARITY-02: Sheet name preserved from merged-cell FODS
    // ------------------------------------------------------------------
    [Fact]
    public void Load_FodsWithMergedCells_PreservesSheetName()
    {
        var path = Path.Combine(FixturesDir, "fods-merged-cells.fods");
        var doc = FodsDocument.Load(path);

        Assert.Single(doc.Sheets);
        Assert.Equal("MergedSheet", doc.Sheets[0].Name);
    }

    // ------------------------------------------------------------------
    // R73-PARITY-03: Row count correct from merged-cell FODS
    // ------------------------------------------------------------------
    [Fact]
    public void Load_FodsWithMergedCells_CorrectRowCount()
    {
        var path = Path.Combine(FixturesDir, "fods-merged-cells.fods");
        var doc = FodsDocument.Load(path);

        // 2 rows: header row + data row
        Assert.Equal(2, doc.Sheets[0].Rows.Count);
    }

    // ------------------------------------------------------------------
    // R73-PARITY-04: Merged cell FODS can be saved (roundtrip stability)
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_FodsWithMergedCells_Stable()
    {
        var path = Path.Combine(FixturesDir, "fods-merged-cells.fods");
        var doc = FodsDocument.Load(path);

        var tempPath = Path.Combine(Path.GetTempPath(), $"r73-merged-parity-{Guid.NewGuid()}.fods");
        try
        {
            doc.Save(tempPath);
            Assert.True(File.Exists(tempPath), "Saved file must exist");
            var fileSize = new FileInfo(tempPath).Length;
            Assert.True(fileSize > 100, $"Saved file must be > 100 bytes, got {fileSize}");

            // Reload and verify structure preserved
            var reloaded = FodsDocument.Load(tempPath);
            Assert.Equal(doc.Sheets.Count, reloaded.Sheets.Count);
            Assert.Equal(doc.Sheets[0].Name, reloaded.Sheets[0].Name);
        }
        finally
        {
            if (File.Exists(tempPath)) File.Delete(tempPath);
        }
    }
}
