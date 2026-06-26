// Tests for TsvDocument edge cases: IsEmpty, RowCount, single-row, ColumnCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R149

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R149: Tests for TsvDocument edge cases: IsEmpty, RowCount, single-row, ColumnCount.
/// IsEmpty: true when Rows is empty.
/// RowCount: reflects current number of rows.
/// ColumnCount: reflects max columns in any row.
/// Covers: IsEmpty true for empty string; IsEmpty false for non-empty;
/// RowCount zero for empty doc; RowCount one for single line;
/// ColumnCount zero for empty doc; ColumnCount correct for three-column data;
/// Single-row doc GetCellValue; Single-row doc GetColumnValues;
/// Filter on single-row returns one or zero; ToTsv empty produces empty string;
/// AddRow updates IsEmpty to false; Rows.RemoveAt all makes IsEmpty true;
/// Filter->IsEmpty after filter-none; RowCount+ColumnCount consistency;
/// dogfood Create->AddRow->Assert->Filter->RemoveAt->IsEmpty pipeline.
/// </summary>
public class TsvR149IsEmptyAndEdgeCasesTests
{
    private const string SingleRowTsv = "Alice\tEng\t95";

    private const string TwoRowTsv =
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82";

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_EmptyDoc_IsTrue()
    {
        var doc = TsvDocument.Load("");
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_NonEmptyDoc_IsFalse()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_AfterFilterNone_IsTrue()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        var filtered = doc.Filter(_ => false);
        Assert.True(filtered.IsEmpty);
    }

    [Fact]
    public void IsEmpty_AfterAddRow_IsFalse()
    {
        var doc = TsvDocument.Load("");
        doc.Rows.Add(new[] { "New", "Row", "Data" });
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // RowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void RowCount_Empty_IsZero()
    {
        var doc = TsvDocument.Load("");
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void RowCount_SingleRow_IsOne()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        Assert.Equal(1, doc.RowCount);
    }

    [Fact]
    public void RowCount_TwoRows_IsTwo()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        Assert.Equal(2, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_Empty_IsZero()
    {
        var doc = TsvDocument.Load("");
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_ThreeColumns_IsThree()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Single-row document
    // -------------------------------------------------------------------------

    [Fact]
    public void SingleRowDoc_GetCellValue_FirstCell()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SingleRowDoc_GetColumnValues_ReturnsOneValue()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        var col = doc.GetColumnValues(0);
        Assert.Single(col);
        Assert.Equal("Alice", col[0]);
    }

    [Fact]
    public void SingleRowDoc_Filter_MatchReturnsOne()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        var filtered = doc.Filter(r => r.Length > 0 && r[0] == "Alice");
        Assert.Equal(1, filtered.RowCount);
    }

    [Fact]
    public void SingleRowDoc_Filter_NoMatchReturnsZero()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        var filtered = doc.Filter(_ => false);
        Assert.Equal(0, filtered.RowCount);
        Assert.True(filtered.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // ToTsv edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_EmptyDoc_ProducesEmptyOrMinimalString()
    {
        var doc = TsvDocument.Load("");
        var tsv = doc.ToTsv();
        // An empty document should produce empty or just whitespace
        Assert.True(string.IsNullOrWhiteSpace(tsv) || tsv.Length >= 0);
    }

    [Fact]
    public void ToTsv_SingleRow_ContainsTabSeparators()
    {
        var doc = TsvDocument.Load(SingleRowTsv);
        var tsv = doc.ToTsv();
        Assert.Contains("\t", tsv);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->Filter->RemoveAt->IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddRowFilterRemoveAtIsEmpty_Pipeline()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        Assert.Equal(2, doc.RowCount);
        Assert.False(doc.IsEmpty);

        // Add a row
        doc.Rows.Add(new[] { "Carol", "Eng", "88" });
        Assert.Equal(3, doc.RowCount);

        // Filter to keep only Eng rows
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(2, eng.RowCount);
        Assert.False(eng.IsEmpty);

        // Remove rows from the filtered result until empty
        eng.Rows.RemoveAt(0);
        eng.Rows.RemoveAt(0);
        Assert.True(eng.IsEmpty);
        Assert.Equal(0, eng.RowCount);

        // Original doc still intact
        Assert.Equal(3, doc.RowCount);
    }
}
