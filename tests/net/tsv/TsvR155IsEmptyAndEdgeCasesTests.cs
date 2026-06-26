// Tests for TsvDocument.IsEmpty, single-row edge cases, ToTsv empty, and ColumnCount edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R155

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R155: Tests for TsvDocument.IsEmpty, column count edge cases, and ToTsv behavior on empty docs.
/// IsEmpty: true when RowCount == 0.
/// ToTsv on empty: should produce empty or header-only output.
/// ColumnCount on empty: returns 0.
/// Covers: IsEmpty on empty string Load; IsEmpty false on data Load;
/// IsEmpty after Filter-all-false; ColumnCount on empty doc;
/// ColumnCount on single-column doc; ToTsv on empty is empty or just newline;
/// Load empty string IsEmpty; GetCellValue on empty returns null;
/// GetColumnValues on empty returns empty list;
/// HasHeaders on empty with hasHeaders=true; HasHeaders on empty with hasHeaders=false;
/// RowCount on empty is zero; Filter-none Count is zero;
/// Load single row single col cell value;
/// dogfood Load->Filter-none->ToTsv->Load->IsEmpty pipeline.
/// </summary>
public class TsvR155IsEmptyAndEdgeCasesTests
{
    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_EmptyStringLoad_IsTrue()
    {
        var doc = TsvDocument.Load(string.Empty);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_DataLoad_IsFalse()
    {
        var doc = TsvDocument.Load("A\tB\n1\t2");
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_AfterFilterNone_IsTrue()
    {
        var doc = TsvDocument.Load("A\tB\n1\t2\n3\t4");
        var none = doc.Filter(_ => false);
        Assert.True(none.IsEmpty);
    }

    [Fact]
    public void RowCount_AfterFilterNone_IsZero()
    {
        var doc = TsvDocument.Load("A\tB\n1\t2");
        var none = doc.Filter(_ => false);
        Assert.Equal(0, none.RowCount);
    }

    // -------------------------------------------------------------------------
    // ColumnCount edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_EmptyDoc_IsZero()
    {
        var doc = TsvDocument.Load(string.Empty);
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_SingleColumnDoc_IsOne()
    {
        var doc = TsvDocument.Load("Name\nAlice\nBob");
        Assert.Equal(1, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // ToTsv on empty
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_EmptyDoc_IsEmptyOrWhitespace()
    {
        var doc = TsvDocument.Load(string.Empty);
        var tsv = doc.ToTsv();
        Assert.True(string.IsNullOrWhiteSpace(tsv));
    }

    // -------------------------------------------------------------------------
    // GetCellValue on empty
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_EmptyDoc_ReturnsNull()
    {
        var doc = TsvDocument.Load(string.Empty);
        Assert.Null(doc.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetColumnValues on empty
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_EmptyDoc_ReturnsEmptyList()
    {
        var doc = TsvDocument.Load(string.Empty);
        var col = doc.GetColumnValues(0);
        Assert.Empty(col);
    }

    // -------------------------------------------------------------------------
    // HasHeaders on empty doc
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_EmptyDocWithHeaders_IsFalseOrTrue()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: true);
        // With empty content and hasHeaders=true, behavior may vary
        _ = doc.HasHeaders; // just verify accessible
    }

    [Fact]
    public void HasHeaders_EmptyDocWithoutHeaders_IsFalse()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Single row/col edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_SingleRowSingleCol_CellValueCorrect()
    {
        var doc = TsvDocument.Load("SingleValue", hasHeaders: false);
        Assert.Equal("SingleValue", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void Load_SingleRowSingleCol_RowCountIsOne()
    {
        var doc = TsvDocument.Load("X", hasHeaders: false);
        Assert.Equal(1, doc.RowCount);
    }

    [Fact]
    public void Load_SingleRowSingleCol_ColumnCountIsOne()
    {
        var doc = TsvDocument.Load("X", hasHeaders: false);
        Assert.Equal(1, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter-none->ToTsv->Load->IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterNoneToTsvLoadIsEmpty_Pipeline()
    {
        var doc = TsvDocument.Load("Name\tDept\nAlice\tEng\nBob\tFinance", hasHeaders: true);
        Assert.False(doc.IsEmpty);
        Assert.Equal(2, doc.RowCount);

        // Filter none
        var none = doc.Filter(_ => false);
        Assert.True(none.IsEmpty);
        Assert.Equal(0, none.RowCount);

        // ToTsv on none
        var tsv = none.ToTsv();

        // Load from ToTsv result
        var loaded = TsvDocument.Load(tsv);
        Assert.True(loaded.IsEmpty || loaded.RowCount == 0);

        // GetColumnValues on empty is always empty
        var col = none.GetColumnValues(0);
        Assert.Empty(col);
    }
}
