using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R116 Train A: GetColumnAggregates — numeric aggregate query pipeline.
/// </summary>
public class FodsR116ColumnAggregatesTests
{
    private static FodsDocument MakeDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.InsertRowWithValues("Sales", 0, new[] { "Product", "Revenue", "Units" });
        doc.InsertRowWithValues("Sales", 1, new[] { "Widget", "12000", "100" });
        doc.InsertRowWithValues("Sales", 2, new[] { "Gadget", "8500",  "75" });
        doc.InsertRowWithValues("Sales", 3, new[] { "Thingamajig", "3200", "40" });
        doc.InsertRowWithValues("Sales", 4, new[] { "Doohickey", "15600", "130" });
        return doc;
    }

    [Fact]
    public void GetColumnAggregates_Sum_IsCorrect()
    {
        var doc = MakeDoc();
        var (_, _, sum, _) = doc.GetColumnAggregates("Sales", col: 1);
        Assert.Equal(39300.0, sum, precision: 2);
    }

    [Fact]
    public void GetColumnAggregates_Min_IsCorrect()
    {
        var doc = MakeDoc();
        var (min, _, _, _) = doc.GetColumnAggregates("Sales", col: 1);
        Assert.Equal(3200.0, min, precision: 2);
    }

    [Fact]
    public void GetColumnAggregates_Max_IsCorrect()
    {
        var doc = MakeDoc();
        var (_, max, _, _) = doc.GetColumnAggregates("Sales", col: 1);
        Assert.Equal(15600.0, max, precision: 2);
    }

    [Fact]
    public void GetColumnAggregates_Count_IsCorrect()
    {
        var doc = MakeDoc();
        var (_, _, _, count) = doc.GetColumnAggregates("Sales", col: 1);
        Assert.Equal(4, count);
    }

    [Fact]
    public void GetColumnAggregates_HeaderSkipped()
    {
        // Column 0 is "Product" — all strings, count should be 0
        var doc = MakeDoc();
        var (_, _, _, count) = doc.GetColumnAggregates("Sales", col: 0);
        Assert.Equal(0, count);
    }

    [Fact]
    public void GetColumnAggregates_MissingSheet_ReturnsZero()
    {
        var doc = MakeDoc();
        var result = doc.GetColumnAggregates("NoSuch", col: 1);
        Assert.Equal(0, result.Count);
        Assert.Equal(0.0, result.Sum);
    }

    [Fact]
    public void GetColumnAggregates_ThrowsOnNullSheetName()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.GetColumnAggregates(null!, col: 1));
    }

    [Fact]
    public void GetColumnAggregates_DogfoodPipeline_FilterThenAggregate()
    {
        // Dogfood: filter North rows → aggregate revenue
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.InsertRowWithValues("Data", 0, new[] { "Region", "Revenue" });
        doc.InsertRowWithValues("Data", 1, new[] { "North", "5000" });
        doc.InsertRowWithValues("Data", 2, new[] { "South", "3000" });
        doc.InsertRowWithValues("Data", 3, new[] { "North", "4500" });

        var filtered = doc.FilterRows("Data", col: 0, value: "North");
        Assert.Equal(3, filtered.Count); // header + 2 north rows

        // Manual aggregate from filtered rows (header at index 0, skip it)
        double sum = 0;
        for (int i = 1; i < filtered.Count; i++)
        {
            if (double.TryParse(filtered[i][1], out double v))
                sum += v;
        }
        Assert.Equal(9500.0, sum, precision: 2);
    }
}
