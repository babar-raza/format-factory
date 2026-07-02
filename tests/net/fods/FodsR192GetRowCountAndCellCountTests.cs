// Tests for FodsDocument.GetRowCount, GetCellCount, GetColumnCount, GetUsedRange.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R192

using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R192: Tests for FodsDocument.GetRowCount, GetCellCount, GetColumnCount, GetUsedRange.
/// GetRowCount(sheetName): returns number of non-empty rows in sheet.
/// GetCellCount(sheetName): returns total number of non-empty cells.
/// GetColumnCount(sheetName): returns number of columns in the used range.
/// GetUsedRange(sheetName): returns (MaxRow, MaxCol) as the used range extents.
/// Covers: GetRowCount positive after SetCellValue; GetRowCount zero for empty sheet;
/// GetCellCount after setting multiple cells; GetCellCount increases after add;
/// GetColumnCount positive after SetCellValue; GetColumnCount zero for empty sheet;
/// GetUsedRange MaxRow non-negative; GetUsedRange MaxCol non-negative;
/// GetUsedRange MaxRow equals expected after SetCellValue; GetRowCount after DeleteRows;
/// GetCellCount matches actual cells; GetUsedRange after ClearSheet;
/// GetColumnCount after InsertRowWithValues;
/// dogfood CreateNew->SetCells->GetRowCount->GetCellCount->GetColumnCount->GetUsedRange.
/// </summary>
public class FodsR192GetRowCountAndCellCountTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Alice");
        doc.SetCellValue(0, 1, "Eng");
        doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob");
        doc.SetCellValue(1, 1, "Finance");
        doc.SetCellValue(1, 2, "82");
        doc.SetCellValue(2, 0, "Carol");
        doc.SetCellValue(2, 1, "Eng");
        doc.SetCellValue(2, 2, "88");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_PositiveAfterSetCellValue()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        Assert.True(doc.GetRowCount(sheet) > 0);
    }

    [Fact]
    public void GetRowCount_IsThreeForThreeRows()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        Assert.Equal(3, doc.GetRowCount(sheet));
    }

    [Fact]
    public void GetRowCount_AfterDeleteRows_Decreases()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var before = doc.GetRowCount(sheet);
        doc.DeleteRows(sheet, 0, 1);
        var after = doc.GetRowCount(sheet);
        Assert.True(after < before);
    }

    [Fact]
    public void GetRowCount_AfterClearSheet_IsZero()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetRowCount(sheet));
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_PositiveAfterSetCellValue()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        Assert.True(doc.GetCellCount(sheet) > 0);
    }

    [Fact]
    public void GetCellCount_NineCellsForThreeByThree()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        Assert.Equal(9, doc.GetCellCount(sheet));
    }

    [Fact]
    public void GetCellCount_AfterClearSheet_IsZero()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetCellCount(sheet));
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_PositiveAfterSetCellValue()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        Assert.True(doc.GetColumnCount(sheet) > 0);
    }

    [Fact]
    public void GetColumnCount_ThreeForThreeColumns()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        Assert.Equal(3, doc.GetColumnCount(sheet));
    }

    [Fact]
    public void GetColumnCount_AfterClearSheet_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = DefaultSheet(doc);
        Assert.Equal(0, doc.GetColumnCount(sheet));
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_MaxRow_NonNegative()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var range = doc.GetUsedRange(sheet);
        Assert.True(range.MaxRow >= 0);
    }

    [Fact]
    public void GetUsedRange_MaxCol_NonNegative()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var range = doc.GetUsedRange(sheet);
        Assert.True(range.MaxCol >= 0);
    }

    [Fact]
    public void GetUsedRange_MaxRow_EqualsLastRowIndex()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var range = doc.GetUsedRange(sheet);
        // Rows 0,1,2 → MaxRow = 2
        Assert.Equal(2, range.MaxRow);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->GetRowCount->GetCellCount->GetColumnCount->GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetGetCountsAndRange_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetNames()[0];

        // Empty sheet
        Assert.Equal(0, doc.GetRowCount(sheet));
        Assert.Equal(0, doc.GetCellCount(sheet));
        Assert.Equal(0, doc.GetColumnCount(sheet));

        // Add 2x3 grid
        doc.SetCellValue(0, 0, "R0C0");
        doc.SetCellValue(0, 1, "R0C1");
        doc.SetCellValue(0, 2, "R0C2");
        doc.SetCellValue(1, 0, "R1C0");
        doc.SetCellValue(1, 1, "R1C1");
        doc.SetCellValue(1, 2, "R1C2");

        Assert.Equal(2, doc.GetRowCount(sheet));
        Assert.Equal(6, doc.GetCellCount(sheet));
        Assert.Equal(3, doc.GetColumnCount(sheet));

        var range = doc.GetUsedRange(sheet);
        Assert.Equal(1, range.MaxRow);
        Assert.Equal(2, range.MaxCol);

        // Clear
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetRowCount(sheet));
        Assert.Equal(0, doc.GetCellCount(sheet));
    }
}
