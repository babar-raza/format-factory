// Tests for TsvDocument row mutation, AddRow, RowCount edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R162

using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R162: Tests for TsvDocument row mutation, AddRow, RowCount edge cases.
/// AddRow(values): appends a new row.
/// SetCellValue(row, col, value): mutates a cell.
/// RowCount: total row count.
/// GetColumnValues(header): returns all values in a named column.
/// Covers: AddRow increases RowCount; AddRow values accessible;
/// AddRow preserves existing rows; AddRow multiple times;
/// SetCellValue updates existing cell; SetCellValue->GetColumnValues;
/// RowCount zero for empty; RowCount after AddRow; RowCount after multiple adds;
/// GetColumnValues count matches RowCount; AddRow->ToTsv->Load round-trip;
/// SetCellValue->ToTsv->Load reflects change; AddRow then Filter;
/// RowCount after Filter; GetColumnValues after mutation;
/// dogfood Load->AddRow->SetCell->GetColVals->Filter->ToTsv->Load verify.
/// </summary>
public class TsvR162RowMutationAndAddRowTests
{
    private const string TwoRowTsv =
        "name\tdept\tscore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82";

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        var before = doc.RowCount;
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValuesAccessibleViaGetColumnValues()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        var names = doc.GetColumnValues("name");
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void AddRow_PreservesExistingRows()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.AddRow(new[] { "Dave", "HR", "77" });
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void AddRow_MultipleTimes_CountGrowsCorrectly()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        doc.AddRow(new[] { "Dave", "HR", "77" });
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void AddRow_ToTsv_Load_RoundTrip()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        var tsv = doc.ToTsv();
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(3, loaded.RowCount);
        Assert.Contains("Carol", loaded.GetColumnValues("name"));
    }

    [Fact]
    public void AddRow_ThenFilter_Works()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_UpdatesExistingCell()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_GetColumnValues_ContainsNewValue()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alicia", names);
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void SetCellValue_ToTsv_Load_ReflectsChange()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.SetCellValue(1, 2, "99");
        var tsv = doc.ToTsv();
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal("99", loaded.GetCellValue(1, "score"));
    }

    // -------------------------------------------------------------------------
    // RowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void RowCount_ZeroForEmptyDoc()
    {
        var doc = TsvDocument.Load(string.Empty);
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void RowCount_TwoForTwoRows()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void GetColumnValues_CountMatchesRowCount()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        var names = doc.GetColumnValues("name");
        Assert.Equal(doc.RowCount, names.Count);
    }

    [Fact]
    public void GetColumnValues_AfterMutation_ContainsCorrectValues()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        doc.SetCellValue(0, 1, "Finance");
        var depts = doc.GetColumnValues("dept");
        Assert.Equal(2, depts.Count(d => d == "Finance"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SetCell->GetColVals->Filter->ToTsv->Load verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadAddRowSetCellGetColValsFilterToTsvLoad_Verify()
    {
        var doc = TsvDocument.Load(TwoRowTsv);
        Assert.Equal(2, doc.RowCount);

        // AddRow
        doc.AddRow(new[] { "Carol", "Eng", "88" });
        Assert.Equal(3, doc.RowCount);

        // SetCell
        doc.SetCellValue(2, 2, "90"); // Carol's score
        Assert.Equal("90", doc.GetCellValue(2, "score"));

        // GetColumnValues
        var names = doc.GetColumnValues("name");
        Assert.Equal(3, names.Count);
        Assert.Contains("Carol", names);

        // Filter
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // ToTsv -> Load
        var tsv = eng.ToTsv();
        var loaded = TsvDocument.Load(tsv);
        Assert.Equal(2, loaded.RowCount);
        var loadedNames = loaded.GetColumnValues("name");
        Assert.Contains("Alice", loadedNames);
        Assert.Contains("Carol", loadedNames);
        Assert.DoesNotContain("Bob", loadedNames);
    }
}
