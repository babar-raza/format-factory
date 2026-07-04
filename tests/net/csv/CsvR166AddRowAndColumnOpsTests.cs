// Tests for CsvDocument.AddRow, SetCellValue mutation, ColumnCount, GetColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R166

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R166: Tests for CsvDocument.AddRow, SetCellValue mutation, ColumnCount, GetColumn.
/// AddRow(values): appends a new row.
/// SetCellValue(row, col, value): mutates a cell by index.
/// ColumnCount: number of columns in the document.
/// GetColumn(name): returns all values for a named column.
/// GetColumn(index): returns all values for a column by index.
/// Covers: AddRow increases RowCount; AddRow values accessible;
/// AddRow->ToCsv contains new row; AddRow->Filter includes new row;
/// SetCellValue reflects in GetCellValue; SetCellValue reflects in GetColumn;
/// ColumnCount equals header count; ColumnCount unchanged after AddRow;
/// GetColumn by name returns all values; GetColumn by index matches by name;
/// GetColumn after SetCellValue reflects mutation;
/// Multiple AddRow calls accumulate; SetCellValue->ToCsv->Load reflects;
/// dogfood Load->GetColumn->AddRow->SetCellValue->GetColumn->ToCsv->Load verify.
/// </summary>
public class CsvR166AddRowAndColumnOpsTests
{
    private const string ThreeRowCsv =
        "name,dept,salary\n" +
        "Alice,Eng,95000\n" +
        "Bob,Finance,82000\n" +
        "Carol,Eng,88000";

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Dave", "HR", "76000" });
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValuesAccessibleByGetCellValue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Eve", "Legal", "91000" });
        Assert.Equal("Eve", doc.GetCellValue(3, 0));
    }

    [Fact]
    public void AddRow_ToCsv_ContainsNewRow()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Frank", "Sales", "79000" });
        var csv = doc.ToCsv();
        Assert.Contains("Frank", csv);
    }

    [Fact]
    public void AddRow_Filter_IncludesNewRow()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Grace", "Eng", "93000" });
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);
    }

    [Fact]
    public void MultipleAddRows_Accumulate()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "H", "HR", "70000" });
        doc.AddRow(new[] { "I", "IT", "85000" });
        Assert.Equal(5, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ReflectsInGetCellValue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCellValue(0, 0, "Alicia");
        Assert.Equal("Alicia", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_ReflectsInGetColumn()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCellValue(1, 1, "Marketing");
        var depts = doc.GetColumn("dept");
        Assert.Contains("Marketing", depts);
    }

    [Fact]
    public void SetCellValue_ToCsv_Load_Reflects()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCellValue(0, 2, "99000");
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal("99000", reloaded.GetCellValue(0, 2));
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_EqualsHeaderCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(doc.Headers.Length, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_IsThreeForThreeColumns()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_UnchangedAfterAddRow()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var before = doc.ColumnCount;
        doc.AddRow(new[] { "X", "Y", "Z" });
        Assert.Equal(before, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_ByName_AllValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var names = doc.GetColumn("name");
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);
    }

    [Fact]
    public void GetColumn_ByIndex_MatchesByName()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var byName = doc.GetColumn("dept");
        var byIndex = doc.GetColumn(1);
        Assert.Equal(byName.Count, byIndex.Count);
        for (var i = 0; i < byName.Count; i++)
            Assert.Equal(byName[i], byIndex[i]);
    }

    [Fact]
    public void GetColumn_AfterSetCellValue_Reflects()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCellValue(0, 0, "Zara");
        var names = doc.GetColumn("name");
        Assert.Contains("Zara", names);
        Assert.DoesNotContain("Alice", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadGetColumnAddRowSetCellGetColumnToCsvLoadVerify_Pipeline()
    {
        // Load
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);

        // GetColumn
        var names = doc.GetColumn("name");
        Assert.Contains("Alice", names);

        // AddRow
        doc.AddRow(new[] { "Dave", "Eng", "90000" });
        Assert.Equal(4, doc.RowCount);

        // SetCellValue
        doc.SetCellValue(1, 0, "Bobby");

        // GetColumn after mutation
        var updatedNames = doc.GetColumn("name");
        Assert.Contains("Bobby", updatedNames);
        Assert.DoesNotContain("Bob", updatedNames);
        Assert.Contains("Dave", updatedNames);

        // ToCsv
        var csv = doc.ToCsv();
        Assert.Contains("Dave", csv);
        Assert.Contains("Bobby", csv);

        // Load round-trip
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal(4, reloaded.RowCount);
        var reloadedNames = reloaded.GetColumn("name");
        Assert.Contains("Dave", reloadedNames);
        Assert.Contains("Bobby", reloadedNames);
    }
}
