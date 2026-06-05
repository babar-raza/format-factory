// R107 Wave 2: FODS InsertRowWithValues tests
// Ledger: R107-FODS-INSERTROWWITHVALUES

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR107InsertRowWithValuesTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void InsertRowWithValues_AtStart_ShiftsExistingRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "A", "B", "C" });
        Assert.Equal(before + 1, doc.GetRowCount(sheet));
    }

    [Fact]
    public void InsertRowWithValues_CellValuesReadable()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "X", "Y", "Z" });
        var col0 = doc.GetColumnValues(sheet, 0);
        Assert.Equal("X", col0[0]);
    }

    [Fact]
    public void InsertRowWithValues_NullValues_CreateEmptyCells()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new string?[] { null, "val", null });
        var col0 = doc.GetColumnValues(sheet, 0);
        Assert.Null(col0[0]);
        var col1 = doc.GetColumnValues(sheet, 1);
        Assert.Equal("val", col1[0]);
    }

    [Fact]
    public void InsertRowWithValues_AtEnd_Appends()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRowWithValues(sheet, before, new[] { "end" });
        Assert.Equal(before + 1, doc.GetRowCount(sheet));
    }

    [Fact]
    public void InsertRowWithValues_InvalidIndex_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.InsertRowWithValues(sheet, -1, new[] { "x" }));
    }

    [Fact]
    public void InsertRowWithValues_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() =>
            doc.InsertRowWithValues("NoSuchSheet", 0, new[] { "x" }));
    }

    [Fact]
    public void InsertRowWithValues_NullValues_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentNullException>(() =>
            doc.InsertRowWithValues(sheet, 0, null!));
    }

    [Fact]
    public void InsertRowWithValues_SurvivesSaveReload()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "saved" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var col = reloaded.GetColumnValues(sheet, 0);
            Assert.Equal("saved", col[0]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
