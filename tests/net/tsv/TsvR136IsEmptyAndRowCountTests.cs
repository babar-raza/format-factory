// Tests for TsvDocument.IsEmpty and RowCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R136

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R136: Tests for TsvDocument.IsEmpty and RowCount.
/// IsEmpty returns true when Rows.Count == 0; false otherwise.
/// RowCount returns Rows.Count (data rows only, not the header row).
/// Covers: IsEmpty empty Load returns true; IsEmpty with data returns false;
/// IsEmpty after Filter-all returns false; IsEmpty after Filter-none returns true;
/// RowCount empty doc is 0; RowCount with data equals row count;
/// RowCount with hasHeaders=true excludes header from Rows;
/// RowCount with hasHeaders=false includes all rows in Rows;
/// ColumnCount from headers length; ColumnCount no headers from first row;
/// dogfood Load->Filter->IsEmpty->RowCount pipeline.
/// </summary>
public class TsvR136IsEmptyAndRowCountTests
{
    private const string ThreeRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_EmptyLoad_IsTrue()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_LoadWithContent_IsFalse()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_FilterAll_IsFalse()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var filtered = doc.Filter(_ => true);
        Assert.False(filtered.IsEmpty);
    }

    [Fact]
    public void IsEmpty_FilterNone_IsTrue()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var filtered = doc.Filter(_ => false);
        Assert.True(filtered.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // RowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void RowCount_EmptyDoc_IsZero()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void RowCount_WithHeaders_ExcludesHeaderRow()
    {
        // ThreeRowTsv has 1 header + 3 data rows = RowCount should be 3
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void RowCount_WithoutHeaders_IncludesAllRows()
    {
        var content = "A\tB\n1\t2\n3\t4";
        var doc = TsvDocument.Load(content, hasHeaders: false);
        Assert.Equal(3, doc.RowCount); // all rows are data rows
    }

    [Fact]
    public void RowCount_SingleDataRow_IsOne()
    {
        var doc = TsvDocument.Load("H1\tH2\nX\tY");
        Assert.Equal(1, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_FromHeaders_EqualsHeaderLength()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_NoHeaders_EqualsFirstRowLength()
    {
        var content = "A\tB\tC\tD\n1\t2\t3\t4";
        var doc = TsvDocument.Load(content, hasHeaders: false);
        Assert.Equal(4, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_EmptyDoc_IsZero()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Equal(0, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: combined pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterIsEmptyRowCount_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.False(doc.IsEmpty);
        Assert.Equal(3, doc.RowCount);

        // Filter to Eng only
        var engOnly = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.False(engOnly.IsEmpty);
        Assert.Equal(2, engOnly.RowCount);

        // Filter to Finance only
        var financeOnly = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.False(financeOnly.IsEmpty);
        Assert.Equal(1, financeOnly.RowCount);

        // Filter nothing
        var empty = doc.Filter(_ => false);
        Assert.True(empty.IsEmpty);
        Assert.Equal(0, empty.RowCount);
    }
}
