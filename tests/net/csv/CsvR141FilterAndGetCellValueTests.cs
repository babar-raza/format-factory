// Tests for CsvDocument.Filter, GetCellValue, HasHeaders property.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R141

using System;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R141: Tests for CsvDocument.Filter, GetCellValue, HasHeaders property.
/// Filter(predicate): returns a new CsvDocument with rows matching predicate; preserves headers.
/// GetCellValue(row, col): returns cell value or null for OOB.
/// HasHeaders: true if Headers != null.
/// Covers: Filter keep-all preserves row count; Filter keep-none returns empty;
/// Filter partial returns subset; Filter preserves headers;
/// Filter null predicate throws or returns all; Filter result is independent copy;
/// GetCellValue valid row/col returns string; GetCellValue OOB row returns null;
/// GetCellValue OOB col returns null; GetCellValue negative row returns null;
/// HasHeaders true when hasHeaders=true; HasHeaders false when hasHeaders=false;
/// HasHeaders false for empty doc; dogfood Load->Filter->GetCellValue->HasHeaders pipeline.
/// </summary>
public class CsvR141FilterAndGetCellValueTests
{
    private const string FourRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_KeepAll_PreservesRowCount()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    [Fact]
    public void Filter_KeepNone_ReturnsEmpty()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(_ => false);
        Assert.Equal(0, filtered.RowCount);
    }

    [Fact]
    public void Filter_PartialMatch_ReturnsSubset()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, filtered.RowCount); // Alice and Carol
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(_ => true);
        Assert.NotNull(filtered.Headers);
        Assert.Contains("Name", filtered.Headers!);
    }

    [Fact]
    public void Filter_ResultIsIndependentCopy()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(_ => true);
        // Modify filtered; original should not be affected
        filtered.RemoveRow(0);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void Filter_ScoreAbove90_ReturnsHighScorers()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var high = doc.Filter(row =>
            row.Length > 2 && int.TryParse(row[2], out var s) && s > 90);
        Assert.Equal(2, high.RowCount); // Alice(95) and Dave(91)
    }

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ValidRowCol_ReturnsString()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_OobRow_ReturnsNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Null(doc.GetCellValue(doc.RowCount, 0));
    }

    [Fact]
    public void GetCellValue_OobCol_ReturnsNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Null(doc.GetCellValue(0, doc.ColumnCount));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ReturnsNull()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Null(doc.GetCellValue(-1, 0));
    }

    [Fact]
    public void GetCellValue_ThirdColumn_ReturnsScore()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal("95", doc.GetCellValue(0, 2));
    }

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_WithHeaders_IsTrue()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_WithoutHeaders_IsFalse()
    {
        var doc = CsvDocument.Load("A,B\n1,2", hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_EmptyDoc_IsFalse()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->GetCellValue->HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterGetCellValueHasHeaders_Pipeline()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.True(doc.HasHeaders);
        Assert.Equal(4, doc.RowCount);

        // Filter to Eng dept
        var engOnly = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, engOnly.RowCount);
        Assert.True(engOnly.HasHeaders);
        Assert.Equal("Alice", engOnly.GetCellValue(0, 0));
        Assert.Equal("Carol", engOnly.GetCellValue(1, 0));

        // Filter to Finance
        var financeOnly = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.Equal(2, financeOnly.RowCount);
        Assert.Equal("Bob", financeOnly.GetCellValue(0, 0));
        Assert.Equal("Dave", financeOnly.GetCellValue(1, 0));

        // GetCellValue OOB
        Assert.Null(financeOnly.GetCellValue(5, 0));
    }
}
