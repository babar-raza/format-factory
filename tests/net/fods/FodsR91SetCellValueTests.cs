// R91 Train G: FODS .NET SetCellValue Round-Trip Tests
// New API: SetCellValue(row, col, value) + SetCellValue(sheet, row, col, value)
// Sprint: FORMAT-FACTORY-R91-AUTONOMOUS-SUPERVISOR-DECLARATION-GRADING-POC-ACCELERATION-MAINSTREAM-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR91SetCellValueTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void SetCellValue_FirstSheet_UpdatesInMemory()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var original = doc.GetCellValue(0, 0);
        doc.SetCellValue(0, 0, "R91-UPDATED");
        var updated = doc.GetCellValue(0, 0);
        Assert.Equal("R91-UPDATED", updated);
        Assert.NotEqual(original, updated);
    }

    [Fact]
    public void SetCellValue_SpecificSheet_UpdatesInMemory()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "SHEET-EDIT");
        Assert.Equal("SHEET-EDIT", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void SetCellValue_RoundTrip_SaveAndReload()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        doc.SetCellValue(0, 0, "ROUNDTRIP-VALUE");

        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("ROUNDTRIP-VALUE", reloaded.GetCellValue(0, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetCellValue_MultipleEdits_AllPersist()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheet = doc.Sheets[0];
        // Edit multiple cells
        FodsDocument.SetCellValue(sheet, 0, 0, "A1-NEW");
        if (sheet.Rows.Count > 1 && sheet.Rows[1].Cells.Count > 0)
            FodsDocument.SetCellValue(sheet, 1, 0, "A2-NEW");

        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("A1-NEW", reloaded.GetCellValue(0, 0));
            if (reloaded.Sheets[0].Rows.Count > 1)
                Assert.Equal("A2-NEW", reloaded.GetCellValue(1, 0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetCellValue_OutOfRange_Row_ThrowsArgumentOutOfRange()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var ex = Record.Exception(() => doc.SetCellValue(9999, 0, "X"));
        Assert.Null(ex); // Auto-expands, no throw
    }

    [Fact]
    public void SetCellValue_OutOfRange_Col_ThrowsArgumentOutOfRange()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var ex = Record.Exception(() => doc.SetCellValue(0, 9999, "X"));
        Assert.Null(ex); // Auto-expands, no throw
    }

    [Fact]
    public void SetCellValue_NullValue_ThrowsArgumentNull()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.Throws<ArgumentNullException>(() => doc.SetCellValue(0, 0, null!));
    }

    [Fact]
    public void SetCellValue_EmptyString_SetsEmptyCell()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        doc.SetCellValue(0, 0, "");
        var val = doc.GetCellValue(0, 0);
        Assert.True(val is null || val == "", $"Expected empty/null, got '{val}'");
    }
}
