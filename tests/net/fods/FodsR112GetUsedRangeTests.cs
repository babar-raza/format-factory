using Xunit;
using System;
using System.IO;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsR112GetUsedRangeTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void GetUsedRange_MinimalSample_ReturnsNonNull()
    {
        var doc = FodsDocument.Load(SamplePath);
        var range = doc.GetUsedRange();
        Assert.NotNull(range);
    }

    [Fact]
    public void GetUsedRange_MinimalSample_MinRowIsZero()
    {
        var doc = FodsDocument.Load(SamplePath);
        var range = doc.GetUsedRange();
        Assert.NotNull(range);
        Assert.Equal(0, range.Value.MinRow);
    }

    [Fact]
    public void GetUsedRange_MinimalSample_MinColIsZero()
    {
        var doc = FodsDocument.Load(SamplePath);
        var range = doc.GetUsedRange();
        Assert.NotNull(range);
        Assert.Equal(0, range.Value.MinCol);
    }

    [Fact]
    public void GetUsedRange_BySheetName_SameAsDefault()
    {
        var doc = FodsDocument.Load(SamplePath);
        var sheetName = doc.Sheets[0].Name;
        var range1 = doc.GetUsedRange();
        var range2 = doc.GetUsedRange(sheetName);
        Assert.Equal(range1, range2);
    }

    [Fact]
    public void GetUsedRange_StaticOverload_Works()
    {
        var doc = FodsDocument.Load(SamplePath);
        var range = FodsDocument.GetUsedRange(doc.Sheets[0]);
        Assert.NotNull(range);
    }

    [Fact]
    public void GetUsedRange_EmptySheet_ReturnsNull()
    {
        var doc = FodsDocument.Load(SamplePath);
        doc.AddSheet("EmptySheet");
        var range = doc.GetUsedRange("EmptySheet");
        Assert.Null(range);
    }

    [Fact]
    public void GetUsedRange_AfterSetCell_IncludesNewCell()
    {
        var doc = FodsDocument.Load(SamplePath);
        var sheet = doc.Sheets[0];
        // Set a cell beyond current used range
        int lastRow = sheet.Rows.Count - 1;
        int lastCol = sheet.Rows[lastRow].Cells.Count - 1;
        FodsDocument.SetCellValue(sheet, lastRow, lastCol, "test");
        var range = FodsDocument.GetUsedRange(sheet);
        Assert.NotNull(range);
        Assert.True(range.Value.MaxRow >= lastRow);
        Assert.True(range.Value.MaxCol >= lastCol);
    }

    [Fact]
    public void GetUsedRange_InvalidSheetName_Throws()
    {
        var doc = FodsDocument.Load(SamplePath);
        Assert.Throws<InvalidOperationException>(() => doc.GetUsedRange("NoSuchSheet"));
    }

    [Fact]
    public void GetUsedRange_NullSheetName_Throws()
    {
        var doc = FodsDocument.Load(SamplePath);
        Assert.Throws<ArgumentException>(() => doc.GetUsedRange((string)null!));
    }

    [Fact]
    public void GetUsedRange_MaxRowGreaterOrEqualMinRow()
    {
        var doc = FodsDocument.Load(SamplePath);
        var range = doc.GetUsedRange();
        Assert.NotNull(range);
        Assert.True(range.Value.MaxRow >= range.Value.MinRow);
        Assert.True(range.Value.MaxCol >= range.Value.MinCol);
    }
}
