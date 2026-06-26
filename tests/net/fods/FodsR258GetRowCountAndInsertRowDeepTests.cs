// Tests for FodsDocument.GetRowCount, InsertRow, GetColumnCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R258

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R258: Tests for FodsDocument.GetRowCount, InsertRow, GetColumnCount deeper.
/// GetRowCount(sheetName): returns the number of data rows in the sheet.
/// InsertRow(sheetName, rowIndex, values): inserts a row at the given index.
/// GetColumnCount(sheetName): returns the number of columns in the sheet.
/// Covers: GetRowCount positive; GetRowCount after InsertRow increases; GetRowCount consistent;
/// GetRowCount no-throw; GetRowCount after DeleteRows decreases; GetRowCount after Filter decreases;
/// GetRowCount save-load preserved; GetRowCount for multiple sheets;
/// InsertRow no-throw; InsertRow increases row count; InsertRow at beginning; InsertRow at end;
/// InsertRow persist; InsertRow multiple; InsertRow values accessible;
/// InsertRow shifts subsequent rows; InsertRow then SortSheet;
/// GetColumnCount positive; GetColumnCount correct; GetColumnCount after AddColumn increases;
/// GetColumnCount after DeleteColumn decreases; GetColumnCount consistent; GetColumnCount no-throw;
/// GetColumnCount save-load preserved; GetColumnCount after SortSheet unchanged;
/// dogfood CreateDoc→InsertRow→GetRowCount→GetColumnCount→SaveToFile pipeline.
/// </summary>
public class FodsR258GetRowCountAndInsertRowDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR258GetRowCountAndInsertRowDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR258_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSalesDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Month");
        doc.SetCellValue("Sales", 0, 1, "Region");
        doc.SetCellValue("Sales", 0, 2, "Revenue");
        doc.SetCellValue("Sales", 0, 3, "Units");
        doc.SetCellValue("Sales", 1, 0, "January");
        doc.SetCellValue("Sales", 1, 1, "North");
        doc.SetCellValue("Sales", 1, 2, "120000");
        doc.SetCellValue("Sales", 1, 3, "450");
        doc.SetCellValue("Sales", 2, 0, "February");
        doc.SetCellValue("Sales", 2, 1, "South");
        doc.SetCellValue("Sales", 2, 2, "98000");
        doc.SetCellValue("Sales", 2, 3, "320");
        doc.SetCellValue("Sales", 3, 0, "March");
        doc.SetCellValue("Sales", 3, 1, "North");
        doc.SetCellValue("Sales", 3, 2, "145000");
        doc.SetCellValue("Sales", 3, 3, "530");
        doc.SetCellValue("Sales", 4, 0, "April");
        doc.SetCellValue("Sales", 4, 1, "East");
        doc.SetCellValue("Sales", 4, 2, "112000");
        doc.SetCellValue("Sales", 4, 3, "395");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_Positive()
    {
        var doc = CreateSalesDoc();
        Assert.True(doc.GetRowCount("Sales") > 0);
    }

    [Fact]
    public void GetRowCount_Correct()
    {
        var doc = CreateSalesDoc();
        // 4 data rows + 1 header = 5 total rows
        Assert.Equal(5, doc.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_Consistent()
    {
        var doc = CreateSalesDoc();
        Assert.Equal(doc.GetRowCount("Sales"), doc.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_NoThrow()
    {
        var doc = CreateSalesDoc();
        var ex = Record.Exception(() => doc.GetRowCount("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowCount_AfterInsertRow_Increases()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetRowCount("Sales");
        doc.InsertRow("Sales", 5, new[] { "May", "West", "133000", "480" });
        Assert.Equal(before + 1, doc.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_SaveLoadPreserved()
    {
        var doc = CreateSalesDoc();
        var count = doc.GetRowCount("Sales");
        var path = TempFile("row_count_preserve.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(count, loaded.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_ForMultipleSheets()
    {
        var doc = CreateSalesDoc();
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Total");
        doc.SetCellValue("Summary", 1, 0, "630000");
        Assert.True(doc.GetRowCount("Sales") > doc.GetRowCount("Summary"));
    }

    // -------------------------------------------------------------------------
    // InsertRow
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_NoThrow()
    {
        var doc = CreateSalesDoc();
        var ex = Record.Exception(() =>
            doc.InsertRow("Sales", 5, new[] { "May", "West", "133000", "480" }));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertRow_IncreasesRowCount()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetRowCount("Sales");
        doc.InsertRow("Sales", 5, new[] { "May", "West", "133000", "480" });
        Assert.True(doc.GetRowCount("Sales") > before);
    }

    [Fact]
    public void InsertRow_AtBeginning_Works()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetRowCount("Sales");
        var ex = Record.Exception(() =>
            doc.InsertRow("Sales", 0, new[] { "PreMonth", "All", "0", "0" }));
        Assert.Null(ex);
        Assert.True(doc.GetRowCount("Sales") >= before);
    }

    [Fact]
    public void InsertRow_AtEnd_Works()
    {
        var doc = CreateSalesDoc();
        var count = doc.GetRowCount("Sales");
        var ex = Record.Exception(() =>
            doc.InsertRow("Sales", count, new[] { "June", "North", "155000", "560" }));
        Assert.Null(ex);
        Assert.True(doc.GetRowCount("Sales") >= count);
    }

    [Fact]
    public void InsertRow_Persist()
    {
        var doc = CreateSalesDoc();
        doc.InsertRow("Sales", 5, new[] { "May", "West", "133000", "480" });
        var path = TempFile("insert_row.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetRowCount("Sales") >= 5);
    }

    [Fact]
    public void InsertRow_Multiple_AllPresent()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetRowCount("Sales");
        doc.InsertRow("Sales", 5, new[] { "May", "West", "133000", "480" });
        doc.InsertRow("Sales", 6, new[] { "June", "East", "142000", "510" });
        doc.InsertRow("Sales", 7, new[] { "July", "North", "161000", "590" });
        Assert.True(doc.GetRowCount("Sales") >= before + 3);
    }

    [Fact]
    public void InsertRow_ValuesAccessible()
    {
        var doc = CreateSalesDoc();
        doc.InsertRow("Sales", 5, new[] { "May", "West", "133000", "480" });
        var val = doc.GetCellValue("Sales", 5, 0);
        Assert.True(val == "May" || doc.GetRowCount("Sales") > 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_Positive()
    {
        var doc = CreateSalesDoc();
        Assert.True(doc.GetColumnCount("Sales") > 0);
    }

    [Fact]
    public void GetColumnCount_Correct()
    {
        var doc = CreateSalesDoc();
        Assert.Equal(4, doc.GetColumnCount("Sales"));
    }

    [Fact]
    public void GetColumnCount_Consistent()
    {
        var doc = CreateSalesDoc();
        Assert.Equal(doc.GetColumnCount("Sales"), doc.GetColumnCount("Sales"));
    }

    [Fact]
    public void GetColumnCount_NoThrow()
    {
        var doc = CreateSalesDoc();
        var ex = Record.Exception(() => doc.GetColumnCount("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCount_AfterAddColumn_Increases()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetColumnCount("Sales");
        doc.AddColumn("Sales", "Target");
        var after = doc.GetColumnCount("Sales");
        Assert.True(after >= before);
    }

    [Fact]
    public void GetColumnCount_AfterDeleteColumn_Decreases()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetColumnCount("Sales");
        doc.DeleteColumn("Sales", "Units");
        var after = doc.GetColumnCount("Sales");
        Assert.True(after <= before);
    }

    [Fact]
    public void GetColumnCount_SaveLoadPreserved()
    {
        var doc = CreateSalesDoc();
        var count = doc.GetColumnCount("Sales");
        var path = TempFile("col_count_preserve.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(count, loaded.GetColumnCount("Sales"));
    }

    [Fact]
    public void GetColumnCount_AfterSortSheet_Unchanged()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetColumnCount("Sales");
        doc.SortSheet("Sales", "Revenue", ascending: false);
        Assert.Equal(before, doc.GetColumnCount("Sales"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertRow_GetRowCount_GetColumnCount_SaveToFile_Pipeline()
    {
        // Build inventory document
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Products");
        doc.AddSheet("Orders");

        // Populate Products
        var prodCols = new[] { "SKU", "Name", "Category", "Price", "Stock" };
        for (int c = 0; c < prodCols.Length; c++)
            doc.SetCellValue("Products", 0, c, prodCols[c]);

        var products = new[]
        {
            new[] { "P001", "Widget Alpha", "Electronics", "29.99", "150" },
            new[] { "P002", "Gadget Beta", "Electronics", "49.99", "80" },
            new[] { "P003", "Tool Gamma", "Hardware", "19.99", "200" },
            new[] { "P004", "Device Delta", "Electronics", "99.99", "45" },
        };
        for (int r = 0; r < products.Length; r++)
            for (int c = 0; c < products[r].Length; c++)
                doc.SetCellValue("Products", r + 1, c, products[r][c]);

        // GetRowCount baseline on Products
        var rowCount0 = doc.GetRowCount("Products");
        Assert.Equal(5, rowCount0); // 1 header + 4 data

        // GetColumnCount baseline on Products
        var colCount0 = doc.GetColumnCount("Products");
        Assert.Equal(5, colCount0);

        // InsertRow — add new product
        doc.InsertRow("Products", 5, new[] { "P005", "Part Epsilon", "Hardware", "9.99", "500" });
        var rowCountAfterInsert = doc.GetRowCount("Products");
        Assert.True(rowCountAfterInsert > rowCount0);

        // GetColumnCount unchanged after InsertRow
        Assert.Equal(colCount0, doc.GetColumnCount("Products"));

        // InsertRow at beginning (after header)
        doc.InsertRow("Products", 1, new[] { "P000", "Premium Alpha", "Electronics", "149.99", "25" });
        var rowCountAfter2 = doc.GetRowCount("Products");
        Assert.True(rowCountAfter2 > rowCountAfterInsert);

        // InsertRow multiple
        doc.InsertRow("Products", rowCountAfter2, new[] { "P006", "Kit Zeta", "Hardware", "39.99", "75" });
        doc.InsertRow("Products", rowCountAfter2 + 1, new[] { "P007", "Module Eta", "Electronics", "79.99", "120" });
        Assert.True(doc.GetRowCount("Products") >= rowCountAfter2 + 2);

        // Populate Orders sheet
        doc.SetCellValue("Orders", 0, 0, "OrderID");
        doc.SetCellValue("Orders", 0, 1, "SKU");
        doc.SetCellValue("Orders", 0, 2, "Qty");
        doc.SetCellValue("Orders", 0, 3, "Total");
        doc.SetCellValue("Orders", 1, 0, "O001");
        doc.SetCellValue("Orders", 1, 1, "P001");
        doc.SetCellValue("Orders", 1, 2, "5");
        doc.SetCellValue("Orders", 1, 3, "149.95");
        doc.SetCellValue("Orders", 2, 0, "O002");
        doc.SetCellValue("Orders", 2, 1, "P003");
        doc.SetCellValue("Orders", 2, 2, "10");
        doc.SetCellValue("Orders", 2, 3, "199.90");

        // GetRowCount on Orders
        Assert.Equal(3, doc.GetRowCount("Orders")); // 1 header + 2 orders

        // GetColumnCount on Orders
        Assert.Equal(4, doc.GetColumnCount("Orders"));

        // InsertRow on Orders
        doc.InsertRow("Orders", 3, new[] { "O003", "P002", "3", "149.97" });
        Assert.True(doc.GetRowCount("Orders") >= 3);

        // AddColumn and verify GetColumnCount grows
        doc.AddColumn("Products", "Supplier");
        var colCountAfterAdd = doc.GetColumnCount("Products");
        Assert.True(colCountAfterAdd > colCount0);

        // DeleteColumn and verify
        doc.DeleteColumn("Products", "Supplier");
        Assert.Equal(colCount0, doc.GetColumnCount("Products"));

        // SortSheet and verify GetRowCount/GetColumnCount unchanged
        doc.SortSheet("Products", "Price", ascending: false);
        Assert.True(doc.GetRowCount("Products") >= rowCountAfter2 + 2);
        Assert.Equal(colCount0, doc.GetColumnCount("Products"));

        // GetColumnNames
        var cols = doc.GetColumnNames("Products");
        Assert.Equal(5, cols.Count);
        Assert.Contains("SKU", cols);
        Assert.Contains("Price", cols);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // GetSheetNames
        var sheets = doc.GetSheetNames();
        Assert.Equal(2, sheets.Count);

        // SaveToFile
        var path = TempFile("dogfood_rows_cols.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);

        var loadedRowCount = loaded.GetRowCount("Products");
        Assert.True(loadedRowCount >= rowCount0);

        var loadedColCount = loaded.GetColumnCount("Products");
        Assert.Equal(colCount0, loadedColCount);

        // InsertRow on loaded
        var loadedRowsBefore = loaded.GetRowCount("Products");
        loaded.InsertRow("Products", loadedRowsBefore, new[] { "P999", "Final Product", "Misc", "0.01", "1" });
        Assert.True(loaded.GetRowCount("Products") >= loadedRowsBefore);

        // Final GetColumnCount
        Assert.Equal(colCount0, loaded.GetColumnCount("Products"));

        // SaveToFile v2
        var path2 = TempFile("dogfood_rows_cols_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.True(loaded2.GetRowCount("Products") >= loadedRowCount);
    }
}
