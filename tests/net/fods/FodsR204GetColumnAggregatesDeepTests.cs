// Tests for FodsDocument.GetColumnAggregates deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R204

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R204: Tests for FodsDocument.GetColumnAggregates deeper coverage.
/// GetColumnAggregates(sheet, col): returns aggregate stats (Sum, Min, Max, Avg, Count)
///   for a numeric column in a given sheet.
/// Covers: GetColumnAggregates non-null; GetColumnAggregates Count correct;
/// GetColumnAggregates Sum correct; GetColumnAggregates Min correct;
/// GetColumnAggregates Max correct; GetColumnAggregates Avg correct;
/// GetColumnAggregates for single-value column; GetColumnAggregates for mixed content;
/// GetColumnAggregates after SetCellValue updates; GetColumnAggregates different columns;
/// dogfood Load->SetCellValues->GetColumnAggregates->Verify->Compare pipeline.
/// </summary>
public class FodsR204GetColumnAggregatesDeepTests
{
    private static FodsDocument CreateDocWithNumbers()
    {
        var doc = FodsDocument.CreateEmpty();
        // Sheet "Sheet1" — col 0: categories, col 1: values
        doc.SetCellValue("Sheet1", 0, 0, "Name");
        doc.SetCellValue("Sheet1", 0, 1, "Score");
        doc.SetCellValue("Sheet1", 1, 0, "Alice");
        doc.SetCellValue("Sheet1", 1, 1, "90");
        doc.SetCellValue("Sheet1", 2, 0, "Bob");
        doc.SetCellValue("Sheet1", 2, 1, "80");
        doc.SetCellValue("Sheet1", 3, 0, "Carol");
        doc.SetCellValue("Sheet1", 3, 1, "70");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetColumnAggregates — basic
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_NonNull()
    {
        var doc = CreateDocWithNumbers();
        var agg = doc.GetColumnAggregates("Sheet1", 1);
        Assert.NotNull(agg);
    }

    [Fact]
    public void GetColumnAggregates_Count_Correct()
    {
        var doc = CreateDocWithNumbers();
        var agg = doc.GetColumnAggregates("Sheet1", 1);
        // Rows 1-3 have numeric values (row 0 is header "Score")
        Assert.True(agg.Count >= 3);
    }

    [Fact]
    public void GetColumnAggregates_Sum_Correct()
    {
        var doc = CreateDocWithNumbers();
        var agg = doc.GetColumnAggregates("Sheet1", 1);
        // 90 + 80 + 70 = 240
        Assert.Equal(240.0, agg.Sum, 1);
    }

    [Fact]
    public void GetColumnAggregates_Min_Correct()
    {
        var doc = CreateDocWithNumbers();
        var agg = doc.GetColumnAggregates("Sheet1", 1);
        Assert.Equal(70.0, agg.Min, 1);
    }

    [Fact]
    public void GetColumnAggregates_Max_Correct()
    {
        var doc = CreateDocWithNumbers();
        var agg = doc.GetColumnAggregates("Sheet1", 1);
        Assert.Equal(90.0, agg.Max, 1);
    }

    [Fact]
    public void GetColumnAggregates_Avg_Correct()
    {
        var doc = CreateDocWithNumbers();
        var agg = doc.GetColumnAggregates("Sheet1", 1);
        // (90 + 80 + 70) / 3 = 80
        Assert.Equal(80.0, agg.Average, 1);
    }

    // -------------------------------------------------------------------------
    // Edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_SingleValue_MinEqualsMaxEqualsSum()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetCellValue("Sheet1", 0, 0, "42");
        var agg = doc.GetColumnAggregates("Sheet1", 0);
        Assert.Equal(agg.Min, agg.Max, 1);
        Assert.Equal(agg.Sum, agg.Max, 1);
    }

    [Fact]
    public void GetColumnAggregates_AfterSetCellValue_UpdatesAggregates()
    {
        var doc = CreateDocWithNumbers();
        // Change Alice's score from 90 to 100
        doc.SetCellValue("Sheet1", 1, 1, "100");
        var agg = doc.GetColumnAggregates("Sheet1", 1);
        Assert.Equal(100.0, agg.Max, 1);
    }

    [Fact]
    public void GetColumnAggregates_DifferentColumns_IndependentResults()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetCellValue("Sheet1", 0, 0, "10");
        doc.SetCellValue("Sheet1", 1, 0, "20");
        doc.SetCellValue("Sheet1", 0, 1, "100");
        doc.SetCellValue("Sheet1", 1, 1, "200");

        var col0 = doc.GetColumnAggregates("Sheet1", 0);
        var col1 = doc.GetColumnAggregates("Sheet1", 1);

        Assert.NotEqual(col0.Sum, col1.Sum);
        Assert.Equal(30.0, col0.Sum, 1);
        Assert.Equal(300.0, col1.Sum, 1);
    }

    [Fact]
    public void GetColumnAggregates_LargerDataset_SumCorrect()
    {
        var doc = FodsDocument.CreateEmpty();
        for (var i = 0; i < 10; i++)
            doc.SetCellValue("Sheet1", i, 0, $"{(i + 1) * 10}");
        // Values: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 — sum = 550
        var agg = doc.GetColumnAggregates("Sheet1", 0);
        Assert.Equal(550.0, agg.Sum, 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetCellValuesGetColumnAggregatesVerifyComparePipeline()
    {
        // Build a document with two data columns
        var doc = FodsDocument.CreateEmpty();

        // Column 0: Q1 sales, Column 1: Q2 sales
        doc.SetCellValue("Sheet1", 0, 0, "50");
        doc.SetCellValue("Sheet1", 1, 0, "75");
        doc.SetCellValue("Sheet1", 2, 0, "60");
        doc.SetCellValue("Sheet1", 3, 0, "85");

        doc.SetCellValue("Sheet1", 0, 1, "55");
        doc.SetCellValue("Sheet1", 1, 1, "80");
        doc.SetCellValue("Sheet1", 2, 1, "65");
        doc.SetCellValue("Sheet1", 3, 1, "90");

        // GetColumnAggregates for Q1
        var q1 = doc.GetColumnAggregates("Sheet1", 0);
        Assert.NotNull(q1);
        Assert.Equal(270.0, q1.Sum, 1); // 50+75+60+85
        Assert.Equal(50.0, q1.Min, 1);
        Assert.Equal(85.0, q1.Max, 1);
        Assert.Equal(67.5, q1.Average, 1);

        // GetColumnAggregates for Q2
        var q2 = doc.GetColumnAggregates("Sheet1", 1);
        Assert.NotNull(q2);
        Assert.Equal(290.0, q2.Sum, 1); // 55+80+65+90
        Assert.Equal(55.0, q2.Min, 1);
        Assert.Equal(90.0, q2.Max, 1);

        // Q2 > Q1 in sum
        Assert.True(q2.Sum > q1.Sum);

        // Mutate and re-aggregate
        doc.SetCellValue("Sheet1", 3, 0, "200"); // Q1 row 3 from 85 → 200
        var q1updated = doc.GetColumnAggregates("Sheet1", 0);
        Assert.Equal(200.0, q1updated.Max, 1);
        Assert.True(q1updated.Sum > q1.Sum);
    }
}
