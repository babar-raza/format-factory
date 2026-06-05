// R108 Lane C: FODS GetColumnCount tests
// Ledger: R108-GOVERNED-DOTNET-FODS-GETCOLUMNCOUNT-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR108GetColumnCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void GetColumnCount_DefaultSheet_ReturnsPositive()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int cols = doc.GetColumnCount();
        Assert.True(cols >= 0);
    }

    [Fact]
    public void GetColumnCount_NamedSheet_ReturnsPositive()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int cols = doc.GetColumnCount(sheet);
        Assert.True(cols >= 0);
    }

    [Fact]
    public void GetColumnCount_AfterInsertRow_MatchesValues()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "a", "b", "c", "d" });
        Assert.Equal(4, doc.GetColumnCount(sheet));
    }

    [Fact]
    public void GetColumnCount_EmptySheet_ReturnsZero()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetColumnCount(sheet));
    }

    [Fact]
    public void GetColumnCount_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.GetColumnCount("NONEXISTENT"));
    }

    [Fact]
    public void GetColumnCount_MultipleRows_ReturnsMax()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "a", "b" });
        doc.InsertRowWithValues(sheet, 1, new[] { "x", "y", "z" });
        Assert.Equal(3, doc.GetColumnCount(sheet));
    }

    [Fact]
    public void GetColumnCount_ConsistentWithGetRowValues()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "1", "2", "3" });
        var rowValues = doc.GetRowValues(sheet, 0);
        Assert.Equal(rowValues.Count, doc.GetColumnCount(sheet));
    }

    [Fact]
    public void GetColumnCount_SaveReload_Preserved()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.InsertRowWithValues(sheet, 0, new[] { "a", "b", "c" });
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal(3, reloaded.GetColumnCount(sheet));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
