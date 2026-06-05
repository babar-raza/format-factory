using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R115 Train B: FilterRows — row filtering for data query pipeline.
/// </summary>
public class FodsR115FilterRowsTests
{
    private static FodsDocument MakeDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.InsertRowWithValues("Data", 0, new[] { "Region", "Product", "Revenue" });
        doc.InsertRowWithValues("Data", 1, new[] { "North", "Widget", "12000" });
        doc.InsertRowWithValues("Data", 2, new[] { "South", "Gadget", "8500" });
        doc.InsertRowWithValues("Data", 3, new[] { "North", "Gadget", "9200" });
        doc.InsertRowWithValues("Data", 4, new[] { "West",  "Widget", "7800" });
        return doc;
    }

    [Fact]
    public void FilterRows_MatchingRows_ReturnedWithHeader()
    {
        var doc = MakeDoc();
        var result = doc.FilterRows("Data", col: 0, value: "North");
        // Header + 2 North rows
        Assert.Equal(3, result.Count);
        Assert.Equal("Region", result[0][0]);
        Assert.Equal("North",  result[1][0]);
        Assert.Equal("North",  result[2][0]);
    }

    [Fact]
    public void FilterRows_NoMatch_ReturnsHeaderOnly()
    {
        var doc = MakeDoc();
        var result = doc.FilterRows("Data", col: 0, value: "East");
        Assert.Equal(1, result.Count); // header only
        Assert.Equal("Region", result[0][0]);
    }

    [Fact]
    public void FilterRows_AllMatch_ReturnsAllWithHeader()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("S");
        doc.InsertRowWithValues("S", 0, new[] { "Type" });
        doc.InsertRowWithValues("S", 1, new[] { "A" });
        doc.InsertRowWithValues("S", 2, new[] { "A" });
        var result = doc.FilterRows("S", col: 0, value: "A");
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void FilterRows_MissingSheet_ReturnsEmpty()
    {
        var doc = MakeDoc();
        var result = doc.FilterRows("NoSuch", col: 0, value: "North");
        Assert.Empty(result);
    }

    [Fact]
    public void FilterRows_ColBeyondRowWidth_NotIncluded()
    {
        var doc = MakeDoc();
        // col 99 — no row has that many cells, so only header is returned
        var result = doc.FilterRows("Data", col: 99, value: "anything");
        Assert.Equal(1, result.Count); // just header
    }

    [Fact]
    public void FilterRows_ThrowsOnNullSheetName()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.FilterRows(null!, col: 0, value: "x"));
    }

    [Fact]
    public void FilterRows_SecondColumn_FiltersCorrectly()
    {
        var doc = MakeDoc();
        var result = doc.FilterRows("Data", col: 1, value: "Widget");
        // Header + North/Widget row + West/Widget row = 3
        Assert.Equal(3, result.Count);
        Assert.Contains(result, r => r[0] == "North");
        Assert.Contains(result, r => r[0] == "West");
    }

    [Fact]
    public void FilterRows_DogfoodPipeline_FilterThenExportCsv()
    {
        var doc = MakeDoc();
        var filtered = doc.FilterRows("Data", col: 0, value: "North");
        // Verify both North rows are there
        Assert.True(filtered.Count >= 3);
        // Build CSV from filtered data (dogfood output)
        var csv = string.Join("\n", filtered.Select(r => string.Join(",", r.Select(v => v ?? ""))));
        Assert.Contains("North", csv);
        Assert.DoesNotContain("South", csv);
        Assert.DoesNotContain("West", csv);
    }
}
