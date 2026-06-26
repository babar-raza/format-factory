// Tests for TsvDocument.GetColumnValues, Filter preserving headers, Headers property.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R142

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R142: Tests for TsvDocument.GetColumnValues, Filter preserving headers, Headers.
/// GetColumnValues(colIndex): returns all values in column.
/// Filter(predicate): returns filtered document; headers are NOT included in predicate rows.
/// Headers: string array from first row when hasHeaders=true.
/// Covers: GetColumnValues count equals RowCount; GetColumnValues contains expected values;
/// GetColumnValues OOB index returns empty/nulls; Filter preserves HasHeaders;
/// Filter on first column; Filter on numeric column; Headers not null with hasHeaders;
/// Headers count equals ColumnCount; ColumnCount consistent with headers;
/// GetColumnValues after Filter returns subset; dogfood Load->GetColumnValues->Filter pipeline.
/// </summary>
public class TsvR142GetColumnValuesAndFilterTests
{
    private const string FourRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88\n" +
        "Dave\tFinance\t91";

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var vals = doc.GetColumnValues(0);
        Assert.Equal(doc.RowCount, vals.Count);
    }

    [Fact]
    public void GetColumnValues_FirstColumn_ContainsNames()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var names = doc.GetColumnValues(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetColumnValues_SecondColumn_ContainsDepts()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var depts = doc.GetColumnValues(1);
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
    }

    [Fact]
    public void GetColumnValues_ThirdColumn_ContainsScores()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var scores = doc.GetColumnValues(2);
        Assert.Contains("95", scores);
        Assert.Contains("82", scores);
        Assert.Contains("88", scores);
    }

    [Fact]
    public void GetColumnValues_OobIndex_ReturnsAllNullsOrEmpty()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var vals = doc.GetColumnValues(999);
        // OOB: all nulls or empty list
        Assert.True(vals.Count == 0 || vals.All(v => v == null));
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_PreservesHasHeaders()
    {
        var doc = TsvDocument.Load(FourRowTsv, hasHeaders: true);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.HasHeaders, filtered.HasHeaders);
    }

    [Fact]
    public void Filter_OnFirstColumn_ReturnsMatchingRows()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var filtered = doc.Filter(row => row.Length > 0 && row[0] == "Alice");
        Assert.Equal(1, filtered.RowCount);
        Assert.Equal("Alice", filtered.GetCellValue(0, 0));
    }

    [Fact]
    public void Filter_OnNumericColumn_HighScores()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var high = doc.Filter(row =>
            row.Length > 2 && int.TryParse(row[2], out var s) && s > 88);
        Assert.Equal(2, high.RowCount); // Alice(95), Dave(91)
    }

    [Fact]
    public void Filter_GetColumnValuesAfterFilter_SubsetReturned()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        var engNames = eng.GetColumnValues(0);
        Assert.Equal(2, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_WithHeaders_IsNotNull()
    {
        var doc = TsvDocument.Load(FourRowTsv, hasHeaders: true);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_CountEqualsColumnCount()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal(doc.ColumnCount, doc.Headers!.Length);
    }

    [Fact]
    public void Headers_ContainsExpectedNames()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Contains("Name", doc.Headers!);
        Assert.Contains("Dept", doc.Headers!);
        Assert.Contains("Score", doc.Headers!);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->GetColumnValues->Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnValuesFilterPipeline()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);

        // Get all departments
        var allDepts = doc.GetColumnValues(1);
        Assert.Equal(4, allDepts.Count);
        Assert.True(allDepts.Contains("Eng") && allDepts.Contains("Finance"));

        // Filter Eng dept
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // GetColumnValues on filtered
        var engNames = eng.GetColumnValues(0);
        Assert.Equal(2, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // Filter Finance and check score
        var finance = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        var finScores = finance.GetColumnValues(2);
        Assert.Contains("82", finScores);
        Assert.Contains("91", finScores);
    }
}
