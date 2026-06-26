// Tests for CsvDocument.Filter dedicated coverage.
// Sprint: ff-sprint-s146-dotnet-deepening-20260628
// Ledger: PC-CSV-R136

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R136: Dedicated tests for CsvDocument.Filter.
/// Filter returns a new CsvDocument containing only rows matching a predicate.
/// Headers are preserved unchanged. Throws ArgumentNullException for null predicate.
/// Covers: null predicate throws; all rows match returns all; no rows match returns empty;
/// single-column filter returns matching rows; numeric column filter; original document unchanged;
/// filtered doc preserves headers; filtered doc has correct row count;
/// dogfood Filter->ToCsv round-trip contains only matching rows;
/// dogfood Filter chain (two filters applied sequentially).
/// </summary>
public class CsvR136FilterDedicatedTests
{
    private static CsvDocument BuildDoc()
    {
        const string csv = "Name,Score,Pass\nAlice,95,true\nBob,72,true\nCarol,45,false\nDave,88,true\n";
        return CsvDocument.Load(csv, hasHeaders: true);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NullPredicate_ThrowsArgumentNullException()
    {
        var doc = BuildDoc();
        Assert.Throws<ArgumentNullException>(() => doc.Filter(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_AllRowsMatch_ReturnsAllRows()
    {
        var doc = BuildDoc();
        var result = doc.Filter(_ => true);
        Assert.Equal(doc.RowCount, result.RowCount);
    }

    [Fact]
    public void Filter_NoRowsMatch_ReturnsEmptyDocument()
    {
        var doc = BuildDoc();
        var result = doc.Filter(_ => false);
        Assert.Equal(0, result.RowCount);
    }

    [Fact]
    public void Filter_ByFirstColumn_ReturnsMatchingRows()
    {
        var doc = BuildDoc();
        var result = doc.Filter(row => row.Length > 0 && row[0] == "Alice");
        Assert.Equal(1, result.RowCount);
    }

    [Fact]
    public void Filter_ByThirdColumn_ReturnsMatchingRows()
    {
        var doc = BuildDoc();
        var result = doc.Filter(row => row.Length > 2 && row[2] == "true");
        Assert.Equal(3, result.RowCount); // Alice, Bob, Dave
    }

    [Fact]
    public void Filter_OriginalDocumentUnchanged()
    {
        var doc = BuildDoc();
        _ = doc.Filter(_ => false);
        Assert.Equal(4, doc.RowCount); // original still has 4 rows
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = BuildDoc();
        var result = doc.Filter(row => row.Length > 0 && row[0] == "Alice");
        Assert.Equal(doc.Headers, result.Headers);
    }

    [Fact]
    public void Filter_ByNumericScore_ReturnsHighScorers()
    {
        var doc = BuildDoc();
        var result = doc.Filter(row =>
            row.Length > 1 && int.TryParse(row[1], out int score) && score >= 80);
        Assert.Equal(2, result.RowCount); // Alice=95, Dave=88
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Filter_ToCsv_ContainsOnlyMatchingRows()
    {
        var doc = BuildDoc();
        var result = doc.Filter(row => row.Length > 2 && row[2] == "false");
        var csv = result.ToCsv();
        Assert.Contains("Carol", csv);
        Assert.DoesNotContain("Alice", csv);
        Assert.DoesNotContain("Bob", csv);
    }

    [Fact]
    public void DogfoodPipeline_ChainedFilters_AppliedSequentially()
    {
        var doc = BuildDoc();
        // First filter: Pass == true (3 rows: Alice, Bob, Dave)
        var passing = doc.Filter(row => row.Length > 2 && row[2] == "true");
        // Second filter: Score >= 80 (2 rows: Alice=95, Dave=88)
        var highScoring = passing.Filter(row =>
            row.Length > 1 && int.TryParse(row[1], out int score) && score >= 80);
        Assert.Equal(2, highScoring.RowCount);
    }
}
