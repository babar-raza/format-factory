// R102 Train A: FODS .NET GetRowValues tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R102-GOVERNED-DOTNET-FODS-GETROWVALUES-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR102GetRowValuesTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void GetRowValues_FirstRow_ReturnsValues()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var values = doc.GetRowValues(0);
        Assert.NotNull(values);
        Assert.True(values.Count > 0);
    }

    [Fact]
    public void GetRowValues_MatchesCellValue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var values = doc.GetRowValues(0);
        var cellVal = doc.GetCellValue(0, 0);
        Assert.Equal(cellVal, values[0]);
    }

    [Fact]
    public void GetRowValues_NegativeRow_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetRowValues(-1));
    }

    [Fact]
    public void GetRowValues_OutOfRange_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int rowCount = doc.GetRowCount();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetRowValues(rowCount));
    }

    [Fact]
    public void GetRowValues_ByName_Works()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheetName = doc.GetSheetNames()[0];
        var values = doc.GetRowValues(sheetName, 0);
        Assert.NotNull(values);
        Assert.True(values.Count > 0);
    }

    [Fact]
    public void GetRowValues_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.GetRowValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetRowValues_StaticOverload_Works()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        var values = FodsDocument.GetRowValues(sheet, 0);
        Assert.NotNull(values);
    }

    [Fact]
    public void GetRowValues_ConsistentWithSetCellValue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.SetCellValue(0, 0, "TestR102");
        var values = doc.GetRowValues(0);
        Assert.Equal("TestR102", values[0]);
    }
}
