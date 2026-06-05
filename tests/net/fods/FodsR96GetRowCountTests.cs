// R96 Train L: FODS .NET GetRowCount Tests
// Governed skill: /add-dotnet-api
// Ledger: R96-GOVERNED-DOTNET-FODS-GETROWCOUNT-001
// Sprint: FORMAT-FACTORY-R96-AUTONOMOUS-CONTINUATION-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR96GetRowCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private static string MultiSheetFodsPath =>
        Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    [Fact]
    public void GetRowCount_ReturnsNonNegative()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.True(doc.GetRowCount() >= 0);
    }

    [Fact]
    public void GetRowCount_HasRows()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.True(doc.GetRowCount() > 0, "Sample document should have rows");
    }

    [Fact]
    public void GetRowCount_ByName_Works()
    {
        var doc = FodsDocument.Load(MultiSheetFodsPath);
        var names = doc.GetSheetNames();
        Assert.True(names.Count > 0);
        var count = doc.GetRowCount(names[0]);
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRowCount_InvalidSheet_Throws()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.Throws<ArgumentException>(() => doc.GetRowCount("NoSuchSheet"));
    }

    [Fact]
    public void GetRowCount_ConsistentWithSheets()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheets = doc.Sheets;
        if (sheets.Count > 0)
        {
            Assert.Equal(sheets[0].Rows.Count, doc.GetRowCount());
        }
    }

    [Fact]
    public void GetRowCount_Consistent()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.Equal(doc.GetRowCount(), doc.GetRowCount());
    }

    [Fact]
    public void GetRowCount_ReturnsInt()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        int count = doc.GetRowCount();
        Assert.IsType<int>(count);
    }

    [Fact]
    public void GetRowCount_MultiSheet_AllPositive()
    {
        var doc = FodsDocument.Load(MultiSheetFodsPath);
        foreach (var name in doc.GetSheetNames())
        {
            Assert.True(doc.GetRowCount(name) >= 0, $"Sheet '{name}' should have non-negative row count");
        }
    }
}
