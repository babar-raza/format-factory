// Tests for TsvDocument.GetColumnValues dedicated coverage.
// Sprint: ff-sprint-s147-dotnet-deepening-20260628
// Ledger: PC-TSV-R135

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R135: Dedicated tests for TsvDocument.GetColumnValues.
/// GetColumnValues(int colIndex) returns all values from the given column across all data rows.
/// Rows shorter than colIndex return null for the missing cell.
/// Throws ArgumentOutOfRangeException for negative column index.
/// Covers: negative index throws; first column values correct; second column values correct;
/// short rows return null for missing cells; empty document returns empty list;
/// column count matches row count; single-row single-column returns one value;
/// multiple rows all values returned; colIndex beyond all rows returns all nulls;
/// dogfood Load->GetColumnValues matches expected; dogfood with headers GetColumnValues data rows.
/// </summary>
public class TsvR135GetColumnValuesDedicatedTests
{
    private static TsvDocument BuildDoc()
    {
        const string tsv = "Name\tScore\tPass\nAlice\t95\ttrue\nBob\t82\ttrue\nCarol\t45\tfalse\n";
        return TsvDocument.Load(tsv, hasHeaders: true);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = BuildDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetColumnValues(-1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_FirstColumn_ReturnsAllFirstColumnValues()
    {
        var doc = BuildDoc();
        var values = doc.GetColumnValues(0);
        Assert.Equal(3, values.Count);
        Assert.Equal("Alice", values[0]);
        Assert.Equal("Bob", values[1]);
        Assert.Equal("Carol", values[2]);
    }

    [Fact]
    public void GetColumnValues_SecondColumn_ReturnsScores()
    {
        var doc = BuildDoc();
        var values = doc.GetColumnValues(1);
        Assert.Equal("95", values[0]);
        Assert.Equal("82", values[1]);
        Assert.Equal("45", values[2]);
    }

    [Fact]
    public void GetColumnValues_EmptyDocument_ReturnsEmptyList()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        var values = doc.GetColumnValues(0);
        Assert.Empty(values);
    }

    [Fact]
    public void GetColumnValues_ColumnCountMatchesRowCount()
    {
        var doc = BuildDoc();
        var values = doc.GetColumnValues(0);
        Assert.Equal(doc.RowCount, values.Count);
    }

    [Fact]
    public void GetColumnValues_SingleRow_SingleColumn_ReturnsOneValue()
    {
        var doc = TsvDocument.Load("Alpha\n", hasHeaders: false);
        var values = doc.GetColumnValues(0);
        Assert.Single(values);
        Assert.Equal("Alpha", values[0]);
    }

    [Fact]
    public void GetColumnValues_ShortRow_ReturnNullForMissingCell()
    {
        // First row has 3 cols, second has 1 col — second row col[2] should be null
        const string tsv = "A\tB\tC\nX\n";
        var doc = TsvDocument.Load(tsv, hasHeaders: false);
        var values = doc.GetColumnValues(2);
        Assert.Equal("C", values[0]);
        Assert.Null(values[1]);
    }

    [Fact]
    public void GetColumnValues_IndexBeyondAllRows_ReturnsAllNulls()
    {
        var doc = BuildDoc(); // 3 rows, 3 cols
        var values = doc.GetColumnValues(10); // col 10 doesn't exist
        Assert.Equal(3, values.Count);
        Assert.All(values, v => Assert.Null(v));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Load_GetColumnValues_MatchesExpected()
    {
        const string tsv = "Header1\tHeader2\nVal1A\tVal1B\nVal2A\tVal2B\n";
        var doc = TsvDocument.Load(tsv, hasHeaders: true);
        var col0 = doc.GetColumnValues(0);
        var col1 = doc.GetColumnValues(1);
        Assert.Equal(new[] { "Val1A", "Val2A" }, col0);
        Assert.Equal(new[] { "Val1B", "Val2B" }, col1);
    }

    [Fact]
    public void DogfoodPipeline_WithHeaders_GetColumnValues_DataRowsOnly()
    {
        var doc = BuildDoc(); // has headers: Name, Score, Pass
        // GetColumnValues operates on data rows (not headers)
        var names = doc.GetColumnValues(0);
        Assert.DoesNotContain("Name", names); // header not included
        Assert.Contains("Alice", names);
    }
}
