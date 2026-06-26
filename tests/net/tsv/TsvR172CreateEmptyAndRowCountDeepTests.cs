// Tests for TsvDocument.CreateEmpty, RowCount, IsEmpty deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R172

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R172: Tests for TsvDocument.CreateEmpty, RowCount, IsEmpty deeper coverage.
/// CreateEmpty(): creates empty TsvDocument with no headers.
/// CreateEmpty(headers[]): creates TsvDocument with headers and zero data rows.
/// RowCount: number of data rows (excludes headers).
/// IsEmpty: true when RowCount is zero.
/// Covers: CreateEmpty() IsEmpty true; CreateEmpty() RowCount zero; CreateEmpty() HasHeaders false;
/// CreateEmpty(headers) IsEmpty true; CreateEmpty(headers) RowCount zero;
/// CreateEmpty(headers) HasHeaders true; CreateEmpty(headers) headers accessible;
/// IsEmpty false after AddRow; RowCount increments per AddRow;
/// RowCount decrements after RemoveRow; IsEmpty true after clear;
/// RowCount preserved after SetCellValue; RowCount after Load;
/// dogfood CreateEmpty->AddRows->RowCount->RemoveRow->RowCount->Clear->RowCount verify.
/// </summary>
public class TsvR172CreateEmptyAndRowCountDeepTests
{
    // -------------------------------------------------------------------------
    // CreateEmpty()
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateEmpty_IsEmpty_True()
    {
        var doc = TsvDocument.CreateEmpty();
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void CreateEmpty_RowCount_IsZero()
    {
        var doc = TsvDocument.CreateEmpty();
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void CreateEmpty_HasHeaders_False()
    {
        var doc = TsvDocument.CreateEmpty();
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // CreateEmpty(headers)
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateEmpty_WithHeaders_IsEmpty_True()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept" });
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void CreateEmpty_WithHeaders_RowCount_IsZero()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept" });
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void CreateEmpty_WithHeaders_HasHeaders_True()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "a", "b", "c" });
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void CreateEmpty_WithHeaders_HeadersAccessible()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "x", "y" });
        Assert.Contains("x", doc.Headers);
        Assert.Contains("y", doc.Headers);
    }

    [Fact]
    public void CreateEmpty_WithFiveHeaders_ColumnCountFive()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "a", "b", "c", "d", "e" });
        Assert.Equal(5, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // RowCount and IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_False_AfterAddRow()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept" });
        doc.AddRow(new[] { "Alice", "Eng" });
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void RowCount_Increments_PerAddRow()
    {
        var doc = TsvDocument.CreateEmpty(new[] { "name" });
        Assert.Equal(0, doc.RowCount);
        doc.AddRow(new[] { "A" });
        Assert.Equal(1, doc.RowCount);
        doc.AddRow(new[] { "B" });
        Assert.Equal(2, doc.RowCount);
        doc.AddRow(new[] { "C" });
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void RowCount_DecrementsAfterRemoveRow()
    {
        var doc = TsvDocument.Load("name\tdept\nAlice\tEng\nBob\tFinance");
        doc.RemoveRow(0);
        Assert.Equal(1, doc.RowCount);
    }

    [Fact]
    public void IsEmpty_True_AfterRemovingAllRows()
    {
        var doc = TsvDocument.Load("name\tdept\nAlice\tEng");
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void RowCount_PreservedAfterSetCellValue()
    {
        var doc = TsvDocument.Load("name\tdept\nAlice\tEng\nBob\tFinance");
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void RowCount_AfterLoad_Correct()
    {
        var doc = TsvDocument.Load("id\tname\n1\tAlice\n2\tBob\n3\tCarol");
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void RowCount_AfterFilter_Reduced()
    {
        var doc = TsvDocument.Load("name\tdept\nAlice\tEng\nBob\tFinance\nCarol\tEng");
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmptyAddRowsRowCountRemoveRowRowCountClearRowCountVerify_Pipeline()
    {
        // CreateEmpty with headers
        var doc = TsvDocument.CreateEmpty(new[] { "name", "dept", "score" });
        Assert.True(doc.IsEmpty);
        Assert.Equal(0, doc.RowCount);
        Assert.True(doc.HasHeaders);

        // AddRows
        doc.AddRow(new[] { "Alice", "Eng", "95" });
        Assert.Equal(1, doc.RowCount);
        Assert.False(doc.IsEmpty);

        doc.AddRow(new[] { "Bob", "Finance", "82" });
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        doc.AddRow(new[] { "Dave", "HR", "76" });
        Assert.Equal(4, doc.RowCount);

        // SetCellValue — RowCount unchanged
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal(4, doc.RowCount);

        // RemoveRow — first row
        doc.RemoveRow(0);
        Assert.Equal(3, doc.RowCount);

        // Check names shifted
        var names = doc.GetColumnValues("name");
        Assert.Contains("Bob", names);
        Assert.DoesNotContain("Alicia", names);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(1, eng.RowCount); // Only Carol remains in Eng

        // Clear
        doc.Clear();
        Assert.True(doc.IsEmpty);
        Assert.Equal(0, doc.RowCount);

        // HasHeaders preserved after clear
        Assert.True(doc.HasHeaders);
        Assert.Equal(3, doc.ColumnCount);
    }
}
