// Tests for TsvDocument.GetColumnStatistics, GetColumnValues chain deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R178

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R178: Tests for TsvDocument.GetColumnStatistics, GetColumnValues chain deeper.
/// GetColumnStatistics(colName): returns statistics for a numeric column (min/max/avg/count).
/// GetColumnValues(colName): returns all values in the named column.
/// Covers: GetColumnStatistics non-null for numeric column; GetColumnStatistics count correct;
/// GetColumnStatistics Min <= Max; GetColumnStatistics Avg between min and max;
/// GetColumnValues all values present; GetColumnValues count equals RowCount;
/// GetColumnValues after SetCellValue reflects change; GetColumnValues after AddRow includes new;
/// GetColumnValues chain on filtered result; GetColumnStatistics on single row;
/// dogfood CreateEmpty->AddRows->GetColumnStatistics->GetColumnValues->Filter->verify pipeline.
/// </summary>
public class TsvR178GetColumnStatisticsDeepTests
{
    private static TsvDocument CreateWithNumericData()
    {
        var doc = TsvDocument.CreateEmpty(new List<string> { "Name", "Score", "Age" });
        doc.AddRow(new List<string> { "Alice", "92", "30" });
        doc.AddRow(new List<string> { "Bob", "85", "25" });
        doc.AddRow(new List<string> { "Carol", "78", "35" });
        doc.AddRow(new List<string> { "Dave", "91", "28" });
        doc.AddRow(new List<string> { "Eve", "88", "32" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetColumnStatistics
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStatistics_NonNull_ForNumericColumn()
    {
        var doc = CreateWithNumericData();
        Assert.NotNull(doc.GetColumnStatistics("Score"));
    }

    [Fact]
    public void GetColumnStatistics_Count_EqualsRowCount()
    {
        var doc = CreateWithNumericData();
        var stats = doc.GetColumnStatistics("Score");
        Assert.Equal(doc.RowCount, stats.Count);
    }

    [Fact]
    public void GetColumnStatistics_Min_LessThanOrEqualMax()
    {
        var doc = CreateWithNumericData();
        var stats = doc.GetColumnStatistics("Score");
        Assert.True(stats.Min <= stats.Max);
    }

    [Fact]
    public void GetColumnStatistics_Avg_BetweenMinAndMax()
    {
        var doc = CreateWithNumericData();
        var stats = doc.GetColumnStatistics("Score");
        Assert.True(stats.Average >= stats.Min);
        Assert.True(stats.Average <= stats.Max);
    }

    [Fact]
    public void GetColumnStatistics_Min_CorrectValue()
    {
        var doc = CreateWithNumericData();
        var stats = doc.GetColumnStatistics("Score");
        // Min score should be 78 (Carol)
        Assert.Equal(78, stats.Min);
    }

    [Fact]
    public void GetColumnStatistics_Max_CorrectValue()
    {
        var doc = CreateWithNumericData();
        var stats = doc.GetColumnStatistics("Score");
        // Max score should be 92 (Alice)
        Assert.Equal(92, stats.Max);
    }

    [Fact]
    public void GetColumnStatistics_SingleRow_MinEqualsMax()
    {
        var doc = TsvDocument.CreateEmpty(new List<string> { "Val" });
        doc.AddRow(new List<string> { "42" });
        var stats = doc.GetColumnStatistics("Val");
        Assert.Equal(stats.Min, stats.Max);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_AllValuesPresent()
    {
        var doc = CreateWithNumericData();
        var vals = doc.GetColumnValues("Name");
        Assert.Contains("Alice", vals);
        Assert.Contains("Bob", vals);
        Assert.Contains("Carol", vals);
        Assert.Contains("Dave", vals);
        Assert.Contains("Eve", vals);
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = CreateWithNumericData();
        var vals = doc.GetColumnValues("Score");
        Assert.Equal(doc.RowCount, vals.Count);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_ReflectsChange()
    {
        var doc = CreateWithNumericData();
        doc.SetCellValue(0, "Name", "Alicia");
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alicia", names);
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_IncludesNew()
    {
        var doc = CreateWithNumericData();
        doc.AddRow(new List<string> { "Frank", "95", "27" });
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Frank", names);
        Assert.Equal(6, names.Count);
    }

    [Fact]
    public void GetColumnValues_OnFiltered_CorrectCount()
    {
        var doc = CreateWithNumericData();
        var high = doc.Filter(r => r.GetCell("Score") != null &&
                                   int.TryParse(r.GetCell("Score"), out var s) && s >= 90);
        var names = high.GetColumnValues("Name");
        Assert.Equal(2, names.Count); // Alice(92) and Dave(91)
    }

    [Fact]
    public void GetColumnValues_ScoreColumn_NumericallyCorrect()
    {
        var doc = CreateWithNumericData();
        var scores = doc.GetColumnValues("Score");
        Assert.Contains("92", scores);
        Assert.Contains("78", scores);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddRows_GetColumnStatistics_GetColumnValues_Filter_Verify_Pipeline()
    {
        // Create with data
        var doc = CreateWithNumericData();
        Assert.Equal(5, doc.RowCount);

        // GetColumnStatistics
        var stats = doc.GetColumnStatistics("Score");
        Assert.NotNull(stats);
        Assert.Equal(5, stats.Count);
        Assert.Equal(78, stats.Min);
        Assert.Equal(92, stats.Max);
        Assert.True(stats.Average > 78 && stats.Average < 92);

        // GetColumnValues
        var names = doc.GetColumnValues("Name");
        Assert.Equal(5, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);

        var scores = doc.GetColumnValues("Score");
        Assert.Equal(5, scores.Count);

        // Filter high scorers (>=90)
        var highScorers = doc.Filter(r =>
        {
            var s = r.GetCell("Score");
            return int.TryParse(s, out var score) && score >= 90;
        });
        Assert.Equal(2, highScorers.RowCount);

        // GetColumnValues on filtered
        var highNames = highScorers.GetColumnValues("Name");
        Assert.Contains("Alice", highNames);
        Assert.Contains("Dave", highNames);

        // GetColumnStatistics on filtered
        var highStats = highScorers.GetColumnStatistics("Score");
        Assert.Equal(2, highStats.Count);
        Assert.Equal(91, highStats.Min);
        Assert.Equal(92, highStats.Max);

        // After AddRow, statistics change
        doc.AddRow(new List<string> { "Grace", "99", "24" });
        var updatedStats = doc.GetColumnStatistics("Score");
        Assert.Equal(6, updatedStats.Count);
        Assert.Equal(99, updatedStats.Max);
    }
}
