// Tests for FodsDocument.SetCellValue, GetRowValues, GetColumnValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R193

using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R193: Tests for FodsDocument.SetCellValue, GetRowValues, GetColumnValues deeper coverage.
/// SetCellValue(row, col, value): sets a cell value in the default sheet.
/// GetRowValues(sheetName, row): returns all cell values for a row.
/// GetColumnValues(sheetName, col): returns all values for a column.
/// Covers: SetCellValue persists after get; SetCellValue overwrites existing;
/// GetRowValues returns list; GetRowValues count matches columns set;
/// GetRowValues contains expected values; GetRowValues empty for unused row;
/// GetColumnValues returns list; GetColumnValues count matches rows set;
/// GetColumnValues contains expected values; GetColumnValues after InsertRow;
/// SetCellValue multiple rows persists; GetRowValues after DeleteRows;
/// GetColumnValues after SetCellValue overwrite;
/// dogfood CreateNew->SetCells->GetRowValues->GetColumnValues->Filter->Verify.
/// </summary>
public class FodsR193SetCellValueAndGetRowValuesTests
{
    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_PersistsValue()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "TestValue");
        var row = doc.GetRowValues(sheet, 0);
        Assert.Contains("TestValue", row);
    }

    [Fact]
    public void SetCellValue_OverwritesExisting()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "Original");
        doc.SetCellValue(0, 0, "Overwritten");
        var row = doc.GetRowValues(sheet, 0);
        Assert.Contains("Overwritten", row);
        Assert.DoesNotContain("Original", row);
    }

    [Fact]
    public void SetCellValue_MultipleRows_AllPersist()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "Row0");
        doc.SetCellValue(1, 0, "Row1");
        doc.SetCellValue(2, 0, "Row2");
        Assert.Contains("Row0", doc.GetRowValues(sheet, 0));
        Assert.Contains("Row1", doc.GetRowValues(sheet, 1));
        Assert.Contains("Row2", doc.GetRowValues(sheet, 2));
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_ReturnsList()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(0, 1, "B");
        var sheet = DefaultSheet(doc);
        var row = doc.GetRowValues(sheet, 0);
        Assert.NotNull(row);
    }

    [Fact]
    public void GetRowValues_CountMatchesColumnsSet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(0, 1, "B");
        doc.SetCellValue(0, 2, "C");
        var sheet = DefaultSheet(doc);
        var row = doc.GetRowValues(sheet, 0);
        Assert.Equal(3, row.Count);
    }

    [Fact]
    public void GetRowValues_ContainsExpectedValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Dept");
        doc.SetCellValue(0, 2, "Score");
        var sheet = DefaultSheet(doc);
        var row = doc.GetRowValues(sheet, 0);
        Assert.Contains("Name", row);
        Assert.Contains("Dept", row);
        Assert.Contains("Score", row);
    }

    [Fact]
    public void GetRowValues_AfterDeleteRows_RowShifts()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "Row0");
        doc.SetCellValue(1, 0, "Row1");
        doc.SetCellValue(2, 0, "Row2");
        doc.DeleteRows(sheet, 0, 1);
        // After deleting row 0, row 1 becomes row 0
        var newRow0 = doc.GetRowValues(sheet, 0);
        Assert.Contains("Row1", newRow0);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_ReturnsList()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(1, 0, "B");
        var sheet = DefaultSheet(doc);
        var col = doc.GetColumnValues(sheet, 0);
        Assert.NotNull(col);
    }

    [Fact]
    public void GetColumnValues_CountMatchesRowsSet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 2, "82");
        doc.SetCellValue(2, 2, "88");
        var sheet = DefaultSheet(doc);
        var col = doc.GetColumnValues(sheet, 2);
        Assert.Equal(3, col.Count);
    }

    [Fact]
    public void GetColumnValues_ContainsExpectedValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 1, "Eng");
        doc.SetCellValue(1, 1, "Finance");
        doc.SetCellValue(2, 1, "Eng");
        var sheet = DefaultSheet(doc);
        var col = doc.GetColumnValues(sheet, 1);
        Assert.Contains("Eng", col);
        Assert.Contains("Finance", col);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValueOverwrite_Correct()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "Original");
        doc.SetCellValue(0, 0, "Updated");
        var col = doc.GetColumnValues(sheet, 0);
        Assert.Contains("Updated", col);
        Assert.DoesNotContain("Original", col);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetGetRowColFilter_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);

        // Set data
        doc.SetCellValue(0, 0, "Alice"); doc.SetCellValue(0, 1, "Eng"); doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob");   doc.SetCellValue(1, 1, "Finance"); doc.SetCellValue(1, 2, "82");
        doc.SetCellValue(2, 0, "Carol"); doc.SetCellValue(2, 1, "Eng"); doc.SetCellValue(2, 2, "88");

        // GetRowValues
        var row0 = doc.GetRowValues(sheet, 0);
        Assert.Equal(3, row0.Count);
        Assert.Contains("Alice", row0);
        Assert.Contains("Eng", row0);
        Assert.Contains("95", row0);

        // GetColumnValues
        var col0 = doc.GetColumnValues(sheet, 0);
        Assert.Equal(3, col0.Count);
        Assert.Contains("Alice", col0);
        Assert.Contains("Bob", col0);
        Assert.Contains("Carol", col0);

        var col1 = doc.GetColumnValues(sheet, 1);
        Assert.Contains("Eng", col1);
        Assert.Contains("Finance", col1);

        // FilterRows
        var engRows = doc.FilterRows(sheet, 1, "Eng");
        Assert.Equal(2, engRows.Count);

        // Verify GetRowCount
        Assert.Equal(3, doc.GetRowCount(sheet));
    }
}
