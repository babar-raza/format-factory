// R106 Wave 2: FODS GetColumnValues tests
// Ledger: R106-GOVERNED-DOTNET-FODS-GETCOLUMNVALUES-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR106GetColumnValuesTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void GetColumnValues_FirstColumn_ReturnsValues()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        var vals = doc.GetColumnValues(sheet, 0);
        Assert.NotNull(vals);
        Assert.True(vals.Count > 0);
    }

    [Fact]
    public void GetColumnValues_BeyondCells_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        var vals = doc.GetColumnValues(sheet, 999);
        foreach (var v in vals)
            Assert.Null(v);
    }

    [Fact]
    public void GetColumnValues_NegativeCol_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetColumnValues(sheet, -1));
    }

    [Fact]
    public void GetColumnValues_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.GetColumnValues("NoSheet", 0));
    }

    [Fact]
    public void GetColumnValues_NullSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.GetColumnValues(null!, 0));
    }

    [Fact]
    public void GetColumnValues_EmptySheet_ReturnsEmpty()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("EmptyCol");
        var vals = doc.GetColumnValues("EmptyCol", 0);
        Assert.Empty(vals);
    }

    [Fact]
    public void GetColumnValues_AfterSetCell_ReflectsChange()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "TestColVal");
        var vals = doc.GetColumnValues(sheet, 0);
        Assert.Equal("TestColVal", vals[0]);
    }

    [Fact]
    public void GetColumnValues_CountMatchesRowCount()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        var rowCount = doc.GetRowCount(sheet);
        var vals = doc.GetColumnValues(sheet, 0);
        Assert.Equal(rowCount, vals.Count);
    }
}
