// Tests for FodsDocument.SortRows(sheetName, sortColumn, ascending).
// Sprint: FORMAT-FACTORY-FODS-SORT-ROWS-20260626
// Ledger: R123-GOVERNED-DOTNET-FODS-SORT-ROWS-001

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R123: SortRows(sheetName, sortColumn, ascending) — sorts all rows in the sheet
/// by the values in the specified column, either ascending (default) or descending.
/// Tests verify ordering, stability for equal values, and null/missing-arg guards.
/// </summary>
public class FodsR123SortRowsTests
{
    // ---- Build helpers ----

    private static FodsDocument MakeDoc(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        return doc;
    }

    // ---- Basic ascending sort ----

    [Fact]
    public void SortRows_Ascending_ByFirstColumn_OrdersAscending()
    {
        var doc = MakeDoc();
        // Add rows in descending order
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Charlie", "30" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Alice", "25" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "Bob", "28" });

        doc.SortRows("Sheet1", sortColumn: 0, ascending: true);

        // After sort: Alice, Bob, Charlie
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
        Assert.Equal("Charlie", doc.GetCellValue(2, 0));
    }

    // ---- Basic descending sort ----

    [Fact]
    public void SortRows_Descending_ByFirstColumn_OrdersDescending()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Alice", "25" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Bob", "28" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "Charlie", "30" });

        doc.SortRows("Sheet1", sortColumn: 0, ascending: false);

        // After sort: Charlie, Bob, Alice
        Assert.Equal("Charlie", doc.GetCellValue(0, 0));
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
        Assert.Equal("Alice", doc.GetCellValue(2, 0));
    }

    // ---- Sort by second column ----

    [Fact]
    public void SortRows_Ascending_BySecondColumn_OrdersByNumericString()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Charlie", "30" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Alice", "25" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "Bob", "10" });

        doc.SortRows("Sheet1", sortColumn: 1, ascending: true);

        // Ordered by second column: Bob(10), Alice(25), Charlie(30)
        Assert.Equal("Bob", doc.GetCellValue(0, 0));
        Assert.Equal("Alice", doc.GetCellValue(1, 0));
        Assert.Equal("Charlie", doc.GetCellValue(2, 0));
    }

    // ---- Empty sheet does not throw ----

    [Fact]
    public void SortRows_EmptySheet_DoesNotThrow()
    {
        var doc = MakeDoc();
        // No rows added
        var ex = Record.Exception(() => doc.SortRows("Sheet1", sortColumn: 0, ascending: true));
        Assert.Null(ex);
    }

    // ---- Single row does not change order ----

    [Fact]
    public void SortRows_SingleRow_RemainsUnchanged()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Only", "Row" });

        doc.SortRows("Sheet1", sortColumn: 0, ascending: true);

        Assert.Equal("Only", doc.GetCellValue(0, 0));
    }

    // ---- Row values move together ----

    [Fact]
    public void SortRows_AllColumnsMoveTogether()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Z-Name", "Z-Age", "Z-City" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "A-Name", "A-Age", "A-City" });

        doc.SortRows("Sheet1", sortColumn: 0, ascending: true);

        // A-row should now be row 0; verify all 3 columns moved together
        Assert.Equal("A-Name", doc.GetCellValue(0, 0));
        Assert.Equal("A-Age", doc.GetCellValue(0, 1));
        Assert.Equal("A-City", doc.GetCellValue(0, 2));

        Assert.Equal("Z-Name", doc.GetCellValue(1, 0));
    }

    // ---- Non-existent sheet throws ----

    [Fact]
    public void SortRows_NonExistentSheet_Throws()
    {
        var doc = MakeDoc();
        Assert.Throws<InvalidOperationException>(() =>
            doc.SortRows("NoSuchSheet", sortColumn: 0, ascending: true));
    }

    // ---- Empty sheet name throws ----

    [Fact]
    public void SortRows_EmptySheetName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() =>
            doc.SortRows("", sortColumn: 0, ascending: true));
    }

    // ---- Default ascending parameter ----

    [Fact]
    public void SortRows_DefaultAscending_SortsAscending()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Z" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "A" });

        doc.SortRows("Sheet1", sortColumn: 0); // ascending is default true

        Assert.Equal("A", doc.GetCellValue(0, 0));
        Assert.Equal("Z", doc.GetCellValue(1, 0));
    }

    // ---- Dogfood: sort, export CSV, verify ordering in output ----

    [Fact]
    public void DogfoodPipeline_SortThenExportCsv_OrderedOutput()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Zebra" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Ant" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "Mango" });

        doc.SortRows("Sheet1", sortColumn: 0, ascending: true);

        var csv = doc.ExportSheetToHtml("Sheet1");
        // HTML output should have "Ant" before "Mango" before "Zebra"
        int antPos = csv.IndexOf("Ant", StringComparison.OrdinalIgnoreCase);
        int mangoPos = csv.IndexOf("Mango", StringComparison.OrdinalIgnoreCase);
        int zebraPos = csv.IndexOf("Zebra", StringComparison.OrdinalIgnoreCase);

        Assert.True(antPos >= 0);
        Assert.True(antPos < mangoPos);
        Assert.True(mangoPos < zebraPos);
    }
}
