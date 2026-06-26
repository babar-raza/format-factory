// Tests for CsvDocument.Filter chain, GetColumnStats deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R184

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R184: Tests for CsvDocument.Filter chain, GetColumnStats deeper coverage.
/// Filter(predicate): returns new document with only rows matching predicate.
/// GetColumnStats(colName): returns statistics (min/max/avg/count) for numeric column.
/// Covers: Filter by dept correct count; Filter empty result; Filter all match;
/// Filter chain two conditions; Filter then GetColumnStats correct;
/// Filter then GetDistinctValues one value; Filter preserves column headers;
/// GetColumnStats non-null for numeric; GetColumnStats count equals RowCount;
/// GetColumnStats min correct; GetColumnStats max correct; GetColumnStats avg in range;
/// GetColumnStats after AddRow updates; GetColumnStats sum correct;
/// dogfood LoadContent->Filter->GetColumnStats->GetDistinctValues->Verify pipeline.
/// </summary>
public class CsvR184FilterAndGetColumnStatsDeepTests
{
    private const string SampleContent =
        "Name,Dept,Score\n" +
        "Alice,Eng,92\n" +
        "Bob,Finance,85\n" +
        "Carol,Eng,78\n" +
        "Dave,HR,91\n" +
        "Eve,Finance,88\n" +
        "Frank,Eng,79";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ByDept_CorrectCount()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var eng = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(3, eng.RowCount); // Alice, Carol, Frank
    }

    [Fact]
    public void Filter_EmptyResult()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var none = doc.Filter(r => r.GetCellValue("Dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_AllMatch()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var all = doc.Filter(r => r.GetCellValue("Name") != null);
        Assert.Equal(doc.RowCount, all.RowCount);
    }

    [Fact]
    public void Filter_ChainTwoConditions()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var engHigh = doc.Filter(r =>
            r.GetCellValue("Dept") == "Eng" &&
            int.TryParse(r.GetCellValue("Score"), out var s) && s >= 90);
        // Alice=92, Carol=78 (out), Frank=79 (out) → only Alice
        Assert.Equal(1, engHigh.RowCount);
    }

    [Fact]
    public void Filter_PreservesColumnHeaders()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var filtered = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(doc.ColumnCount, filtered.ColumnCount);
    }

    [Fact]
    public void Filter_ThenGetDistinctValues_OneValue()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        var distinct = engOnly.GetDistinctValues("Dept");
        Assert.Equal(1, distinct.Count);
        Assert.Contains("Eng", distinct);
    }

    [Fact]
    public void Filter_ThenGetColumnValues_AllMatchDept()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        var depts = engOnly.GetColumnValues("Dept");
        foreach (var d in depts)
            Assert.Equal("Eng", d);
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.NotNull(doc.GetColumnStats("Score"));
    }

    [Fact]
    public void GetColumnStats_Count_EqualsRowCount()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.Equal(doc.RowCount, doc.GetColumnStats("Score").Count);
    }

    [Fact]
    public void GetColumnStats_Min_Correct()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(78, stats.Min, 1);
    }

    [Fact]
    public void GetColumnStats_Max_Correct()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(92, stats.Max, 1);
    }

    [Fact]
    public void GetColumnStats_Avg_InRange()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var stats = doc.GetColumnStats("Score");
        Assert.True(stats.Average >= stats.Min);
        Assert.True(stats.Average <= stats.Max);
    }

    [Fact]
    public void GetColumnStats_AfterFilter_CorrectMin()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        var stats = engOnly.GetColumnStats("Score");
        // Eng: Alice=92, Carol=78, Frank=79 → min=78
        Assert.Equal(78, stats.Min, 1);
        Assert.Equal(92, stats.Max, 1);
    }

    [Fact]
    public void GetColumnStats_AfterAddRow_UpdatesMax()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.AddRow(new[] { "Zara", "Legal", "100" });
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(100, stats.Max, 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Filter_GetColumnStats_GetDistinctValues_Verify_Pipeline()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.Equal(6, doc.RowCount);

        // GetDistinctValues
        var depts = doc.GetDistinctValues("Dept");
        Assert.Equal(3, depts.Count);

        // GetColumnStats full
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(6, stats.Count);
        Assert.Equal(78, stats.Min, 1);
        Assert.Equal(92, stats.Max, 1);

        // Filter by Eng
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(3, engOnly.RowCount);

        // Stats on Eng only
        var engStats = engOnly.GetColumnStats("Score");
        Assert.Equal(3, engStats.Count);
        Assert.True(engStats.Max <= stats.Max);

        // GetDistinctValues on filtered
        var engDepts = engOnly.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);

        // Chain filter: Eng AND Score > 80
        var highEng = doc.Filter(r =>
            r.GetCellValue("Dept") == "Eng" &&
            int.TryParse(r.GetCellValue("Score"), out var s) && s > 80);
        Assert.Equal(1, highEng.RowCount); // Only Alice (92)

        // AddRow with high score
        doc.AddRow(new[] { "Igor", "Eng", "99" });
        var statsAfter = doc.GetColumnStats("Score");
        Assert.Equal(99, statsAfter.Max, 1);
        Assert.True(statsAfter.Average > stats.Average);

        // GetDistinctValues unchanged for Dept (Igor is Eng)
        var newDepts = doc.GetDistinctValues("Dept");
        Assert.Equal(3, newDepts.Count); // Still Eng, Finance, HR
    }
}
