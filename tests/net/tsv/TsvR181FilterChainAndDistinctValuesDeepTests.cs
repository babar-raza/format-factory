// Tests for TsvDocument.Filter chain, GetDistinctValues, GetColumnStats deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R181

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R181: Tests for TsvDocument.Filter chain, GetDistinctValues, GetColumnStats deeper coverage.
/// Filter(predicate): returns new document with only rows matching the predicate.
/// GetDistinctValues(colName): returns distinct values in the named column.
/// GetColumnStats(colName): returns statistics for a numeric column.
/// Covers: Filter by dept correct count; Filter empty result; Filter all match;
/// Filter chain two conditions; Filter then GetDistinctValues one value;
/// Filter then GetColumnValues all match dept;
/// GetDistinctValues non-null; GetDistinctValues count correct; GetDistinctValues contains expected;
/// GetDistinctValues all-same returns one; GetDistinctValues after AddRow includes new;
/// GetColumnStats non-null; GetColumnStats min correct; GetColumnStats max correct;
/// GetColumnStats avg in range; GetColumnStats count matches RowCount;
/// dogfood LoadContent->Filter->GetDistinctValues->GetColumnStats->Verify pipeline.
/// </summary>
public class TsvR181FilterChainAndDistinctValuesDeepTests
{
    private const string Content =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t92\n" +
        "Bob\tFinance\t85\n" +
        "Carol\tEng\t78\n" +
        "Dave\tHR\t91\n" +
        "Eve\tFinance\t88\n" +
        "Frank\tEng\t79";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ByDept_CorrectCount()
    {
        var doc = TsvDocument.LoadContent(Content);
        var eng = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(3, eng.RowCount); // Alice, Carol, Frank
    }

    [Fact]
    public void Filter_EmptyResult()
    {
        var doc = TsvDocument.LoadContent(Content);
        var none = doc.Filter(r => r.GetCellValue("Dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_AllMatch()
    {
        var doc = TsvDocument.LoadContent(Content);
        var all = doc.Filter(r => r.GetCellValue("Name") != null);
        Assert.Equal(doc.RowCount, all.RowCount);
    }

    [Fact]
    public void Filter_ChainTwoConditions()
    {
        var doc = TsvDocument.LoadContent(Content);
        // Eng AND Score > 80
        var engHigh = doc.Filter(r =>
            r.GetCellValue("Dept") == "Eng" &&
            int.TryParse(r.GetCellValue("Score"), out var s) && s > 80);
        // Alice=92, Frank=79 (out), Carol=78 (out) → only Alice
        Assert.Equal(1, engHigh.RowCount);
    }

    [Fact]
    public void Filter_ThenGetDistinctValues_OneValue()
    {
        var doc = TsvDocument.LoadContent(Content);
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        var distinct = engOnly.GetDistinctValues("Dept");
        Assert.Equal(1, distinct.Count);
        Assert.Contains("Eng", distinct);
    }

    [Fact]
    public void Filter_ContainsCorrectRows()
    {
        var doc = TsvDocument.LoadContent(Content);
        var finance = doc.Filter(r => r.GetCellValue("Dept") == "Finance");
        var names = finance.GetColumnValues("Name");
        Assert.Contains("Bob", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Alice", names);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = TsvDocument.LoadContent(Content);
        Assert.NotNull(doc.GetDistinctValues("Dept"));
    }

    [Fact]
    public void GetDistinctValues_CountCorrect()
    {
        var doc = TsvDocument.LoadContent(Content);
        var distinct = doc.GetDistinctValues("Dept");
        Assert.Equal(3, distinct.Count); // Eng, Finance, HR
    }

    [Fact]
    public void GetDistinctValues_ContainsExpected()
    {
        var doc = TsvDocument.LoadContent(Content);
        var distinct = doc.GetDistinctValues("Dept");
        Assert.Contains("Eng", distinct);
        Assert.Contains("Finance", distinct);
        Assert.Contains("HR", distinct);
    }

    [Fact]
    public void GetDistinctValues_AllSameValue_ReturnsOne()
    {
        var content = "Col\nA\nA\nA\nA";
        var doc = TsvDocument.LoadContent(content);
        Assert.Equal(1, doc.GetDistinctValues("Col").Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_IncludesNewValue()
    {
        var doc = TsvDocument.LoadContent(Content);
        doc.AddRow(new[] { "Zara", "Legal", "95" });
        var distinct = doc.GetDistinctValues("Dept");
        Assert.Contains("Legal", distinct);
        Assert.Equal(4, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_NameColumn_AllUnique()
    {
        var doc = TsvDocument.LoadContent(Content);
        var distinct = doc.GetDistinctValues("Name");
        Assert.Equal(6, distinct.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull()
    {
        var doc = TsvDocument.LoadContent(Content);
        Assert.NotNull(doc.GetColumnStats("Score"));
    }

    [Fact]
    public void GetColumnStats_Count_MatchesRowCount()
    {
        var doc = TsvDocument.LoadContent(Content);
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(doc.RowCount, stats.Count);
    }

    [Fact]
    public void GetColumnStats_Min_Correct()
    {
        var doc = TsvDocument.LoadContent(Content);
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(78, stats.Min, 1);
    }

    [Fact]
    public void GetColumnStats_Max_Correct()
    {
        var doc = TsvDocument.LoadContent(Content);
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(92, stats.Max, 1);
    }

    [Fact]
    public void GetColumnStats_Avg_InRange()
    {
        var doc = TsvDocument.LoadContent(Content);
        var stats = doc.GetColumnStats("Score");
        Assert.True(stats.Average >= stats.Min);
        Assert.True(stats.Average <= stats.Max);
    }

    [Fact]
    public void GetColumnStats_MinLessThanOrEqualMax()
    {
        var doc = TsvDocument.LoadContent(Content);
        var stats = doc.GetColumnStats("Score");
        Assert.True(stats.Min <= stats.Max);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Filter_GetDistinctValues_GetColumnStats_Verify_Pipeline()
    {
        var doc = TsvDocument.LoadContent(Content);
        Assert.Equal(6, doc.RowCount);

        // GetDistinctValues
        var depts = doc.GetDistinctValues("Dept");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Eng", depts);

        // GetColumnStats
        var stats = doc.GetColumnStats("Score");
        Assert.NotNull(stats);
        Assert.Equal(6, stats.Count);
        Assert.True(stats.Min <= stats.Max);

        // Filter by Eng
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(3, engOnly.RowCount);
        var engDepts = engOnly.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);

        // Stats on filtered
        var engStats = engOnly.GetColumnStats("Score");
        Assert.Equal(3, engStats.Count);
        Assert.True(engStats.Max <= stats.Max);

        // Filter chain
        var highEngineers = doc.Filter(r =>
            r.GetCellValue("Dept") == "Eng" &&
            int.TryParse(r.GetCellValue("Score"), out var s) && s >= 80);
        Assert.True(highEngineers.RowCount < engOnly.RowCount);

        // AddRow and verify distinct
        doc.AddRow(new[] { "Igor", "Legal", "97" });
        var newDepts = doc.GetDistinctValues("Dept");
        Assert.Equal(4, newDepts.Count);
        Assert.Contains("Legal", newDepts);
    }
}
