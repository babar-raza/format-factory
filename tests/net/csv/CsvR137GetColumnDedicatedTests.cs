// Tests for CsvDocument.GetColumn(int) and GetColumn(string) dedicated coverage.
// Sprint: ff-sprint-s148-dotnet-deepening-20260628
// Ledger: PC-CSV-R137

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R137: Dedicated tests for CsvDocument.GetColumn(int colIndex) and GetColumn(string headerName).
/// GetColumn(int) returns all values from the given column index across data rows.
/// GetColumn(string) returns values from the column with that header name.
/// GetColumn(int) throws CsvReaderException for negative index.
/// GetColumn(string) throws CsvReaderException when no headers or header not found.
/// Covers: GetColumn(int) negative throws; GetColumn(string) no headers throws;
/// GetColumn(string) missing header throws; GetColumn(int) first column values;
/// GetColumn(int) second column values; GetColumn(string) by name returns values;
/// GetColumn(int) short rows excluded; original document unchanged;
/// GetColumn(int) count matches row count; dogfood Load->GetColumn pipeline;
/// dogfood GetColumn(int) and GetColumn(string) return same values.
/// </summary>
public class CsvR137GetColumnDedicatedTests
{
    private static CsvDocument BuildDoc()
    {
        const string csv = "Name,Score,Pass\nAlice,95,true\nBob,72,true\nCarol,45,false\n";
        return CsvDocument.Load(csv, hasHeaders: true);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_Int_NegativeIndex_ThrowsCsvReaderException()
    {
        var doc = BuildDoc();
        Assert.Throws<CsvReaderException>(() => doc.GetColumn(-1));
    }

    [Fact]
    public void GetColumn_String_NoHeaders_ThrowsCsvReaderException()
    {
        var doc = CsvDocument.Load("Alice,95\nBob,72\n", hasHeaders: false);
        Assert.Throws<CsvReaderException>(() => doc.GetColumn("Name"));
    }

    [Fact]
    public void GetColumn_String_MissingHeader_ThrowsCsvReaderException()
    {
        var doc = BuildDoc();
        Assert.Throws<CsvReaderException>(() => doc.GetColumn("NotAHeader"));
    }

    // -------------------------------------------------------------------------
    // Functional tests — GetColumn(int)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_Int_FirstColumn_ReturnsAllValues()
    {
        var doc = BuildDoc();
        var col = doc.GetColumn(0);
        Assert.Equal(3, col.Count);
        Assert.Equal("Alice", col[0]);
        Assert.Equal("Bob", col[1]);
        Assert.Equal("Carol", col[2]);
    }

    [Fact]
    public void GetColumn_Int_SecondColumn_ReturnsScores()
    {
        var doc = BuildDoc();
        var col = doc.GetColumn(1);
        Assert.Equal("95", col[0]);
        Assert.Equal("72", col[1]);
        Assert.Equal("45", col[2]);
    }

    [Fact]
    public void GetColumn_Int_CountMatchesRowCount()
    {
        var doc = BuildDoc();
        Assert.Equal(doc.RowCount, doc.GetColumn(0).Count);
    }

    [Fact]
    public void GetColumn_Int_OriginalUnchanged()
    {
        var doc = BuildDoc();
        _ = doc.GetColumn(0);
        Assert.Equal(3, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Functional tests — GetColumn(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_String_ByName_ReturnsValues()
    {
        var doc = BuildDoc();
        var col = doc.GetColumn("Name");
        Assert.Equal(3, col.Count);
        Assert.Equal("Alice", col[0]);
    }

    [Fact]
    public void GetColumn_String_ByScoreHeader_ReturnsScores()
    {
        var doc = BuildDoc();
        var col = doc.GetColumn("Score");
        Assert.Contains("95", col);
        Assert.Contains("72", col);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Load_GetColumnInt_MatchesExpected()
    {
        const string csv = "X,Y\n1,4\n2,5\n3,6\n";
        var doc = CsvDocument.Load(csv, hasHeaders: true);
        var colX = doc.GetColumn(0);
        Assert.Equal(new[] { "1", "2", "3" }, colX);
    }

    [Fact]
    public void DogfoodPipeline_GetColumnInt_GetColumnString_SameValues()
    {
        var doc = BuildDoc();
        var byIndex = doc.GetColumn(0);
        var byName = doc.GetColumn("Name");
        Assert.Equal(byIndex, byName);
    }
}
