using FormatFactory.Fods;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R114 Train A: GetSheetStats — aggregate sheet statistics for data analysis.
/// </summary>
public class FodsR114GetSheetStatsTests
{
    private static FodsDocument MakeDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.InsertRowWithValues("Data", 0, new[] { "Name", "Score", "Grade" });
        doc.InsertRowWithValues("Data", 1, new[] { "Alice", "95", "A" });
        doc.InsertRowWithValues("Data", 2, new string?[] { "Bob", "82", null });
        return doc;
    }

    [Fact]
    public void GetSheetStats_ReturnsCorrectRowCount()
    {
        var doc = MakeDoc();
        var (rows, _, _, _) = doc.GetSheetStats("Data");
        Assert.Equal(3, rows);
    }

    [Fact]
    public void GetSheetStats_ReturnsCorrectColCount()
    {
        var doc = MakeDoc();
        var (_, cols, _, _) = doc.GetSheetStats("Data");
        Assert.True(cols >= 2);
    }

    [Fact]
    public void GetSheetStats_CountsNonEmptyCells()
    {
        var doc = MakeDoc();
        var (_, _, _, nonEmpty) = doc.GetSheetStats("Data");
        Assert.Equal(8, nonEmpty); // 3+3+2
    }

    [Fact]
    public void GetSheetStats_MissingSheet_ReturnsZeros()
    {
        var doc = MakeDoc();
        var (rows, cols, cells, nonEmpty) = doc.GetSheetStats("NoSuch");
        Assert.Equal(0, rows);
        Assert.Equal(0, cols);
        Assert.Equal(0, cells);
        Assert.Equal(0, nonEmpty);
    }

    [Fact]
    public void GetSheetStats_EmptySheet_ReturnsZeros()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        var (rows, cols, cells, nonEmpty) = doc.GetSheetStats("Empty");
        Assert.Equal(0, rows);
        Assert.Equal(0, cells);
        Assert.Equal(0, nonEmpty);
    }

    [Fact]
    public void GetSheetStats_ThrowsOnNullSheetName()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.GetSheetStats(null!));
    }

    [Fact]
    public void GetSheetStats_ThrowsOnEmptySheetName()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.GetSheetStats(""));
    }

    [Fact]
    public void GetSheetStats_CellCountEqualsRowTimesMaxCols()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("S");
        doc.InsertRowWithValues("S", 0, new[] { "A", "B" });
        doc.InsertRowWithValues("S", 1, new[] { "C", "D" });
        var (rows, cols, cells, _) = doc.GetSheetStats("S");
        Assert.Equal(2, rows);
        Assert.Equal(2, cols);
        Assert.True(cells > 0);
    }
}
