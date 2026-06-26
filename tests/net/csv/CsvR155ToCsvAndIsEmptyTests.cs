// Tests for CsvDocument.ToCsv, IsEmpty, and HasColumn edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R155

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R155: Tests for CsvDocument.ToCsv output, IsEmpty edge cases, and HasColumn.
/// ToCsv(): serializes back to CSV string with headers.
/// IsEmpty: true when RowCount==0.
/// HasColumn(name): true when header exists.
/// Covers: ToCsv non-null; ToCsv contains header names; ToCsv contains cell values;
/// ToCsv->Load round-trip row count; ToCsv->Load cell values match;
/// ToCsv after AddRow contains new values; IsEmpty after Load is false;
/// IsEmpty after Filter-none is true; IsEmpty single-row doc is false;
/// HasColumn true for existing header; HasColumn false for nonexistent;
/// HasColumn case-sensitive; ColumnCount after ToCsv->Load;
/// GetColumn after ToCsv->Load round-trip;
/// dogfood Load->AddRow->ToCsv->Load->Filter->ToCsv.
/// </summary>
public class CsvR155ToCsvAndIsEmptyTests
{
    private const string ThreeRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_IsNonNull()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.NotNull(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_ContainsHeaderNames()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Name", csv);
        Assert.Contains("Dept", csv);
        Assert.Contains("Score", csv);
    }

    [Fact]
    public void ToCsv_ContainsCellValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
    }

    [Fact]
    public void ToCsv_Load_RoundTrip_RowCountMatches()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void ToCsv_Load_RoundTrip_CellValuesMatch()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal("Alice", loaded.GetCellValue(0, 0));
        Assert.Equal("Carol", loaded.GetCellValue(2, 0));
    }

    [Fact]
    public void ToCsv_AfterAddRow_ContainsNewValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        var csv = doc.ToCsv();
        Assert.Contains("Dave", csv);
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_AfterLoad_IsFalse()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_AfterFilterNone_IsTrue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var none = doc.Filter(_ => false);
        Assert.True(none.IsEmpty);
    }

    [Fact]
    public void IsEmpty_SingleRowDoc_IsFalse()
    {
        var doc = CsvDocument.Load("A,B\n1,2");
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_ExistingHeader_ReturnsTrue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Dept"));
        Assert.True(doc.HasColumn("Score"));
    }

    [Fact]
    public void HasColumn_NonExistent_ReturnsFalse()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.HasColumn("Salary"));
    }

    [Fact]
    public void HasColumn_CaseSensitive_ReturnsFalse()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        // Default comparison is case-sensitive
        Assert.False(doc.HasColumn("name")); // "Name" exists, "name" does not
    }

    // -------------------------------------------------------------------------
    // ToCsv -> Load -> GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_AfterToCsvLoad_Unchanged()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(doc.ColumnCount, loaded.ColumnCount);
    }

    [Fact]
    public void GetColumn_AfterToCsvLoadRoundTrip_ContainsValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        var col = loaded.GetColumn("Name");
        Assert.Contains("Alice", col);
        Assert.Contains("Carol", col);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->ToCsv->Load->Filter->ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadAddRowToCsvLoadFilterToCsv_Pipeline()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);
        Assert.False(doc.IsEmpty);

        // AddRow
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        doc.AddRow(new[] { "Eve", "Eng", "79" });
        Assert.Equal(5, doc.RowCount);

        // ToCsv->Load
        var csv = doc.ToCsv();
        var loaded = CsvDocument.Load(csv);
        Assert.Equal(5, loaded.RowCount);
        Assert.True(loaded.HasHeaders);

        // Filter
        var eng = loaded.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(3, eng.RowCount); // Alice, Carol, Eve

        // ToCsv on filtered
        var filteredCsv = eng.ToCsv();
        Assert.Contains("Alice", filteredCsv);
        Assert.Contains("Carol", filteredCsv);
        Assert.Contains("Eve", filteredCsv);
        Assert.DoesNotContain("Bob", filteredCsv);
    }
}
