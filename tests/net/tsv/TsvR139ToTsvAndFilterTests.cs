// Tests for TsvDocument.ToTsv, Filter, ColumnCount, IsEmpty.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R139

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R139: Tests for TsvDocument.ToTsv, Filter, ColumnCount, IsEmpty.
/// ToTsv(): serializes document to TSV string with tab separators.
/// Filter(predicate): returns new TsvDocument with rows matching predicate.
/// ColumnCount: inferred from first row when no headers.
/// IsEmpty: true when Rows.Count == 0.
/// Covers: ToTsv contains tab characters; ToTsv includes all rows;
/// ToTsv round-trip via Load; Filter keep-all preserves count;
/// Filter partial match returns subset; Filter keep-none returns empty;
/// Filter result is independent copy; ColumnCount from headers;
/// ColumnCount from first row when no headers; IsEmpty for empty doc;
/// IsEmpty false for non-empty; dogfood Load->Filter->ToTsv->Load pipeline.
/// </summary>
public class TsvR139ToTsvAndFilterTests
{
    private const string FourRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88\n" +
        "Dave\tFinance\t91";

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_ContainsTabCharacters()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var tsv = doc.ToTsv();
        Assert.Contains("\t", tsv);
    }

    [Fact]
    public void ToTsv_IncludesAllRows()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var tsv = doc.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Bob", tsv);
        Assert.Contains("Carol", tsv);
        Assert.Contains("Dave", tsv);
    }

    [Fact]
    public void ToTsv_RoundTrip_PreservesRowCount()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void ToTsv_RoundTrip_PreservesCellValues()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
    }

    [Fact]
    public void ToTsv_EmptyDoc_ReturnsEmptyOrNewline()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        var tsv = doc.ToTsv();
        Assert.True(string.IsNullOrEmpty(tsv) || tsv == "\n");
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_KeepAll_PreservesCount()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    [Fact]
    public void Filter_PartialMatch_ReturnsSubset()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var filtered = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, filtered.RowCount); // Alice and Carol
    }

    [Fact]
    public void Filter_KeepNone_ReturnsEmpty()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var filtered = doc.Filter(_ => false);
        Assert.Equal(0, filtered.RowCount);
    }

    [Fact]
    public void Filter_ResultIsIndependentCopy()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var filtered = doc.Filter(_ => true);
        // Remove a row from filtered; original should be unchanged
        filtered.Rows.RemoveAt(0);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void Filter_ScoreAbove85_ReturnsHighScorers()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var high = doc.Filter(row =>
            row.Length > 2 && int.TryParse(row[2], out var s) && s > 85);
        Assert.Equal(3, high.RowCount); // Alice(95), Carol(88), Dave(91)
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_FromHeaders_IsCorrect()
    {
        var doc = TsvDocument.Load(FourRowTsv, hasHeaders: true);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_NoHeaders_FromFirstRow()
    {
        var doc = TsvDocument.Load("A\tB\tC\t D\n1\t2\t3\t4", hasHeaders: false);
        Assert.Equal(4, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_EmptyDoc_IsTrue()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_NonEmpty_IsFalse()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->ToTsv->Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterToTsvLoad_Pipeline()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.False(doc.IsEmpty);
        Assert.Equal(4, doc.RowCount);

        // Filter Finance dept
        var finance = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.Equal(2, finance.RowCount);
        Assert.False(finance.IsEmpty);

        // Serialize and reload
        var tsv = finance.ToTsv();
        Assert.Contains("\t", tsv);
        var reloaded = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal(2, reloaded.RowCount);
        Assert.Contains("Bob", reloaded.GetCellValue(0, 0) ?? "");
    }
}
