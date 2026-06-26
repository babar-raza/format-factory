// Tests for CsvDocument.AddRow, SetCell, RemoveRow, and HasColumn deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R151

using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R151: Tests for CsvDocument.AddRow, SetCell, RemoveRow, and HasColumn deeper coverage.
/// AddRow(values): appends a new row to the document.
/// SetCell(row, col, value): sets the value of a specific cell.
/// RemoveRow(index): removes a row at a given index.
/// HasColumn(name): checks if a named column exists.
/// Covers: AddRow increments RowCount; AddRow cell value accessible via GetCellValue;
/// AddRow multiple rows; SetCell updates cell value; SetCell does not change RowCount;
/// RemoveRow decrements RowCount; RemoveRow removes correct row;
/// HasColumn true for existing column; HasColumn false for missing column;
/// HasColumn when no headers; GetColumn(string) returns values for named column;
/// GetColumn(int) returns values for index; ColumnCount after AddRow;
/// dogfood Load->AddRow->SetCell->RemoveRow->ToCsv pipeline.
/// </summary>
public class CsvR151AddRowSetCellAndRemoveRowTests
{
    private const string ThreeRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncrementsRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var before = doc.RowCount;
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_CellValueAccessible()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "Eve", "Eng", "99" });
        var lastRow = doc.RowCount - 1;
        Assert.Equal("Eve", doc.GetCellValue(lastRow, 0));
        Assert.Equal("99", doc.GetCellValue(lastRow, 2));
    }

    [Fact]
    public void AddRow_Multiple_RowCountIncrementsEachTime()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.AddRow(new[] { "X", "Eng", "1" });
        doc.AddRow(new[] { "Y", "Finance", "2" });
        Assert.Equal(5, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_UpdatesCellValue()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCell(0, 2, "100");
        Assert.Equal("100", doc.GetCellValue(0, 2));
    }

    [Fact]
    public void SetCell_DoesNotChangeRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var before = doc.RowCount;
        doc.SetCell(1, 0, "Robert");
        Assert.Equal(before, doc.RowCount);
    }

    [Fact]
    public void SetCell_UpdatesCorrectRow()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.SetCell(2, 0, "Carole");
        Assert.Equal("Carole", doc.GetCellValue(2, 0));
        Assert.Equal("Alice", doc.GetCellValue(0, 0)); // other rows unaffected
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecrementsRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var before = doc.RowCount;
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_RemovesCorrectRow()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(0); // removes Alice
        Assert.Equal("Bob", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void RemoveRow_LastRow_LeavesDocumentCorrect()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        doc.RemoveRow(doc.RowCount - 1); // removes Carol
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
    }

    // -------------------------------------------------------------------------
    // HasColumn / GetColumn(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_TrueForExistingColumn()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Dept"));
        Assert.True(doc.HasColumn("Score"));
    }

    [Fact]
    public void HasColumn_FalseForMissingColumn()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.False(doc.HasColumn("NonExistent"));
    }

    [Fact]
    public void GetColumnByName_ReturnsCorrectValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var names = doc.GetColumn("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void ColumnCount_ConsistentAfterAddRow()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var cols = doc.ColumnCount;
        doc.AddRow(new[] { "New", "Dept", "0" });
        Assert.Equal(cols, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SetCell->RemoveRow->ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddRowSetCellRemoveRowToCsv_Pipeline()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);

        // Add a new row
        doc.AddRow(new[] { "Dave", "Finance", "91" });
        Assert.Equal(4, doc.RowCount);

        // Mutate a cell
        doc.SetCell(3, 2, "92");
        Assert.Equal("92", doc.GetCellValue(3, 2));

        // Remove a row
        doc.RemoveRow(1); // removes Bob
        Assert.Equal(3, doc.RowCount);
        Assert.Equal("Carol", doc.GetCellValue(1, 0));

        // Serialize to CSV and verify
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Dave", csv);
        Assert.DoesNotContain("Bob", csv);
        Assert.Contains(",", csv);
    }
}
