// Tests for CsvDocument.CreateEmpty and IsEmpty deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R173

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R173: Tests for CsvDocument.CreateEmpty and IsEmpty deeper coverage.
/// CreateEmpty(): creates an empty CsvDocument with no rows and no headers.
/// CreateEmpty(headers[]): creates a CsvDocument with headers but no data rows.
/// IsEmpty: true when RowCount is zero.
/// Covers: CreateEmpty() RowCount is zero; CreateEmpty() IsEmpty is true;
/// CreateEmpty() HasHeaders is false; CreateEmpty(headers) RowCount is zero;
/// CreateEmpty(headers) HasHeaders is true; CreateEmpty(headers) Headers correct;
/// CreateEmpty(headers) IsEmpty is true; IsEmpty false after AddRow;
/// IsEmpty false after Load with data; IsEmpty true after removing all rows;
/// IsEmpty true for zero-row filter result; CreateEmpty->AddRow->Filter->IsEmpty;
/// dogfood CreateEmpty->AddRows->IsEmpty->Filter->IsEmpty->Clear->IsEmpty verify.
/// </summary>
public class CsvR173CreateEmptyAndIsEmptyDeepTests
{
    // -------------------------------------------------------------------------
    // CreateEmpty()
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateEmpty_RowCount_IsZero()
    {
        var doc = CsvDocument.CreateEmpty();
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void CreateEmpty_IsEmpty_True()
    {
        var doc = CsvDocument.CreateEmpty();
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void CreateEmpty_HasHeaders_False()
    {
        var doc = CsvDocument.CreateEmpty();
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // CreateEmpty(headers)
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateEmpty_WithHeaders_RowCount_IsZero()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "id", "name", "dept" });
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void CreateEmpty_WithHeaders_IsEmpty_True()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "id", "name" });
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void CreateEmpty_WithHeaders_HasHeaders_True()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "col1", "col2" });
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void CreateEmpty_WithHeaders_Headers_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "x", "y", "z" });
        Assert.Contains("x", doc.Headers);
        Assert.Contains("y", doc.Headers);
        Assert.Contains("z", doc.Headers);
    }

    [Fact]
    public void CreateEmpty_WithHeaders_ColumnCount_Correct()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "a", "b", "c", "d" });
        Assert.Equal(4, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_False_AfterAddRow()
    {
        var doc = CsvDocument.CreateEmpty(new[] { "name", "dept" });
        doc.AddRow(new[] { "Alice", "Eng" });
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_False_AfterLoad()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng");
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_True_ZeroRowFilter()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng");
        var none = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.True(none.IsEmpty);
    }

    [Fact]
    public void IsEmpty_False_NonEmptyFilter()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng\nBob,Finance");
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.False(eng.IsEmpty);
    }

    [Fact]
    public void IsEmpty_True_AfterClear()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng\nBob,Finance");
        doc.Clear();
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_True_AfterRemovingAllRows()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng");
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmptyAddRowsIsEmptyFilterIsEmptyClearIsEmptyVerify_Pipeline()
    {
        // CreateEmpty with headers
        var doc = CsvDocument.CreateEmpty(new[] { "name", "dept", "score" });
        Assert.True(doc.IsEmpty);
        Assert.Equal(0, doc.RowCount);

        // AddRows
        doc.AddRow(new[] { "Alice", "Eng", "95" });
        Assert.False(doc.IsEmpty);
        Assert.Equal(1, doc.RowCount);

        doc.AddRow(new[] { "Bob", "Finance", "82" });
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        Assert.Equal(3, doc.RowCount);
        Assert.False(doc.IsEmpty);

        // Filter Eng — not empty
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.False(eng.IsEmpty);
        Assert.Equal(2, eng.RowCount);

        // Filter Marketing — empty
        var mkt = doc.Filter(r => r.GetValue("dept") == "Marketing");
        Assert.True(mkt.IsEmpty);
        Assert.Equal(0, mkt.RowCount);

        // Clear original
        doc.Clear();
        Assert.True(doc.IsEmpty);
        Assert.Equal(0, doc.RowCount);

        // HasHeaders preserved after clear
        Assert.True(doc.HasHeaders);
        Assert.Contains("name", doc.Headers);

        // Add again
        doc.AddRow(new[] { "Dave", "HR", "77" });
        Assert.False(doc.IsEmpty);
        Assert.Equal(1, doc.RowCount);
    }
}
