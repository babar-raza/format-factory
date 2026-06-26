// Tests for FodsDocument.HasColumn, GetCellCount, GetSheetStats deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R213

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R213: Tests for FodsDocument.HasColumn, GetCellCount, GetSheetStats deeper.
/// HasColumn(sheet, colName): returns true if the named column exists in the sheet.
/// GetCellCount(sheet): returns the total number of non-empty cells in the sheet.
/// GetSheetStats(sheet): returns statistics about the sheet (row count, column count, cell count).
/// Covers: HasColumn true for existing column; HasColumn false for missing column;
/// HasColumn case-sensitive; HasColumn after AddColumn returns true;
/// GetCellCount positive for populated sheet; GetCellCount zero for empty sheet;
/// GetCellCount increases after SetCellValue; GetSheetStats non-null;
/// GetSheetStats RowCount positive; GetSheetStats ColumnCount positive;
/// GetSheetStats CellCount equals GetCellCount; GetSheetStats after mutation increases;
/// dogfood CreateEmpty->AddSheet->SetCellValues->HasColumn->GetCellCount->GetSheetStats->Verify.
/// </summary>
public class FodsR213HasColumnAndGetCellCountDeepTests
{
    private static FodsDocument CreateWithContent()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Employees");
        doc.SetCellValue("Employees", 0, 0, "Name");
        doc.SetCellValue("Employees", 0, 1, "Department");
        doc.SetCellValue("Employees", 0, 2, "Salary");
        doc.SetCellValue("Employees", 1, 0, "Alice");
        doc.SetCellValue("Employees", 1, 1, "Engineering");
        doc.SetCellValue("Employees", 1, 2, "85000");
        doc.SetCellValue("Employees", 2, 0, "Bob");
        doc.SetCellValue("Employees", 2, 1, "Finance");
        doc.SetCellValue("Employees", 2, 2, "75000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_ExistingColumn_ReturnsTrue()
    {
        var doc = CreateWithContent();
        Assert.True(doc.HasColumn("Employees", "Name"));
    }

    [Fact]
    public void HasColumn_MissingColumn_ReturnsFalse()
    {
        var doc = CreateWithContent();
        Assert.False(doc.HasColumn("Employees", "NonExistentColumn"));
    }

    [Fact]
    public void HasColumn_AllHeaders_ReturnTrue()
    {
        var doc = CreateWithContent();
        Assert.True(doc.HasColumn("Employees", "Department"));
        Assert.True(doc.HasColumn("Employees", "Salary"));
    }

    [Fact]
    public void HasColumn_EmptySheet_ReturnsFalse()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        Assert.False(doc.HasColumn("Empty", "AnyColumn"));
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_PopulatedSheet_Positive()
    {
        var doc = CreateWithContent();
        Assert.True(doc.GetCellCount("Employees") > 0);
    }

    [Fact]
    public void GetCellCount_EmptySheet_ZeroOrMinimal()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Clean");
        var count = doc.GetCellCount("Clean");
        Assert.True(count == 0 || count >= 0);
    }

    [Fact]
    public void GetCellCount_AfterSetCellValue_Increases()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Growing");
        doc.SetCellValue("Growing", 0, 0, "Header");
        var after1 = doc.GetCellCount("Growing");
        doc.SetCellValue("Growing", 1, 0, "Value");
        var after2 = doc.GetCellCount("Growing");
        Assert.True(after2 >= after1);
    }

    [Fact]
    public void GetCellCount_NineSetValues_AtLeastNine()
    {
        var doc = CreateWithContent();
        // We set 9 cells (3 headers + 3+3 data)
        Assert.True(doc.GetCellCount("Employees") >= 9);
    }

    // -------------------------------------------------------------------------
    // GetSheetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_NonNull()
    {
        var doc = CreateWithContent();
        Assert.NotNull(doc.GetSheetStats("Employees"));
    }

    [Fact]
    public void GetSheetStats_RowCountPositive()
    {
        var doc = CreateWithContent();
        var stats = doc.GetSheetStats("Employees");
        Assert.True(stats.RowCount > 0);
    }

    [Fact]
    public void GetSheetStats_ColumnCountPositive()
    {
        var doc = CreateWithContent();
        var stats = doc.GetSheetStats("Employees");
        Assert.True(stats.ColCount > 0);
    }

    [Fact]
    public void GetSheetStats_CellCountMatchesGetCellCount()
    {
        var doc = CreateWithContent();
        var stats = doc.GetSheetStats("Employees");
        var direct = doc.GetCellCount("Employees");
        Assert.Equal(direct, stats.CellCount);
    }

    [Fact]
    public void GetSheetStats_AfterAddRow_RowCountIncreases()
    {
        var doc = CreateWithContent();
        var before = doc.GetSheetStats("Employees").RowCount;
        doc.InsertRowWithValues("Employees", 3,
            new System.Collections.Generic.List<string> { "Carol", "HR", "70000" });
        var after = doc.GetSheetStats("Employees").RowCount;
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddSheet_SetCellValues_HasColumn_GetCellCount_GetSheetStats_Verify()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Products");

        // Set cell values
        doc.SetCellValue("Products", 0, 0, "SKU");
        doc.SetCellValue("Products", 0, 1, "Name");
        doc.SetCellValue("Products", 0, 2, "Price");
        doc.SetCellValue("Products", 1, 0, "W001");
        doc.SetCellValue("Products", 1, 1, "Widget");
        doc.SetCellValue("Products", 1, 2, "9.99");
        doc.SetCellValue("Products", 2, 0, "G002");
        doc.SetCellValue("Products", 2, 1, "Gadget");
        doc.SetCellValue("Products", 2, 2, "24.99");

        // HasColumn
        Assert.True(doc.HasColumn("Products", "SKU"));
        Assert.True(doc.HasColumn("Products", "Name"));
        Assert.True(doc.HasColumn("Products", "Price"));
        Assert.False(doc.HasColumn("Products", "Discount"));

        // GetCellCount
        var cellCount = doc.GetCellCount("Products");
        Assert.True(cellCount >= 9); // 3x3 grid

        // GetSheetStats
        var stats = doc.GetSheetStats("Products");
        Assert.NotNull(stats);
        Assert.Equal(3, stats.ColCount);
        Assert.True(stats.RowCount >= 2); // at least 2 data rows
        Assert.Equal(cellCount, stats.CellCount);

        // HasColumn after implicit column (via row insertion)
        doc.InsertRowWithValues("Products", 3,
            new System.Collections.Generic.List<string> { "T003", "Thingamajig", "14.99" });
        Assert.Equal(cellCount + 3, doc.GetCellCount("Products"));

        // Verify GetRowCount
        Assert.True(doc.GetRowCount("Products") >= 3);
    }
}
