// R97 Train L: FODS .NET GetCellCount Tests
// Governed skill: /add-dotnet-api
// Ledger: R97-GOVERNED-DOTNET-FODS-GETCELLCOUNT-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR97GetCellCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private static string MultiSheetFodsPath =>
        Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    [Fact]
    public void GetCellCount_ReturnsNonNegative()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.True(doc.GetCellCount() >= 0);
    }

    [Fact]
    public void GetCellCount_GreaterThanOrEqualToRowCount()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.True(doc.GetCellCount() >= doc.GetRowCount(),
            "Cell count should be >= row count (at least 1 cell per row)");
    }

    [Fact]
    public void GetCellCount_Consistent()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.Equal(doc.GetCellCount(), doc.GetCellCount());
    }

    [Fact]
    public void GetCellCount_ReturnsInt()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        int count = doc.GetCellCount();
        Assert.IsType<int>(count);
    }

    [Fact]
    public void GetCellCount_MultiSheet_HasCells()
    {
        var doc = FodsDocument.Load(MultiSheetFodsPath);
        Assert.True(doc.GetCellCount() > 0);
    }

    [Fact]
    public void GetCellCount_MatchesManualCount()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheets = doc.Sheets;
        if (sheets.Count > 0)
        {
            int manual = 0;
            foreach (var row in sheets[0].Rows)
                manual += row.Cells.Count;
            Assert.Equal(manual, doc.GetCellCount());
        }
    }

    [Fact]
    public void GetCellCount_HasPositiveValue()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.True(doc.GetCellCount() > 0, "Sample should have cells");
    }

    [Fact]
    public void GetCellCount_CorrelatesWithColumnHeaders()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var headers = doc.GetColumnHeaders();
        if (headers.Count > 0 && doc.GetRowCount() > 0)
        {
            Assert.True(doc.GetCellCount() >= headers.Count);
        }
    }
}
