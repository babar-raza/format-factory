// Tests for CsvDocument.RenameColumn, HasColumn, GetColumnIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R217

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R217: Tests for CsvDocument.RenameColumn, HasColumn, GetColumnIndex deeper.
/// RenameColumn(oldName, newName): renames a column header.
/// HasColumn(colName): returns true if the column exists.
/// GetColumnIndex(colName): returns the zero-based index of a column by name.
/// Covers: RenameColumn no-throw; RenameColumn reflected in HasColumn; RenameColumn old name gone;
/// RenameColumn save-load; RenameColumn then GetColumnValues; RenameColumn multiple;
/// HasColumn no-throw; HasColumn true for existing; HasColumn false for missing;
/// HasColumn consistent; HasColumn save-load; HasColumn after RenameColumn;
/// GetColumnIndex no-throw; GetColumnIndex correct index; GetColumnIndex consistent;
/// GetColumnIndex save-load; GetColumnIndex after RenameColumn;
/// dogfood LoadFile→HasColumn→GetColumnIndex→RenameColumn→SaveToFile pipeline.
/// </summary>
public class CsvR217RenameColumnAndHasColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR217RenameColumnAndHasColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR217_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProductCsv()
    {
        var path = TempFile("products.csv");
        var content =
            "ProductId,ProductName,Category,Price,Stock\n" +
            "P001,Laptop,Electronics,1299.99,42\n" +
            "P002,Desk Chair,Furniture,349.50,18\n" +
            "P003,Notebook,Stationery,4.99,500\n" +
            "P004,Monitor,Electronics,549.00,27\n" +
            "P005,Keyboard,Electronics,89.00,63\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var ex = Record.Exception(() => doc.HasColumn("ProductName"));
        Assert.Null(ex);
    }

    [Fact]
    public void HasColumn_True_ForExisting()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.True(doc.HasColumn("Category"));
    }

    [Fact]
    public void HasColumn_False_ForMissing()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.False(doc.HasColumn("NonExistentColumn"));
    }

    [Fact]
    public void HasColumn_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.Equal(doc.HasColumn("Price"), doc.HasColumn("Price"));
    }

    [Fact]
    public void HasColumn_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var before = doc.HasColumn("Stock");
        var path = TempFile("hc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.HasColumn("Stock"));
    }

    [Fact]
    public void HasColumn_AllOriginalColumns_True()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.True(doc.HasColumn("ProductId"));
        Assert.True(doc.HasColumn("ProductName"));
        Assert.True(doc.HasColumn("Category"));
        Assert.True(doc.HasColumn("Price"));
        Assert.True(doc.HasColumn("Stock"));
    }

    // -------------------------------------------------------------------------
    // GetColumnIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIndex_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var ex = Record.Exception(() => doc.GetColumnIndex("ProductId"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIndex_CorrectIndex()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.Equal(0, doc.GetColumnIndex("ProductId"));
        Assert.Equal(1, doc.GetColumnIndex("ProductName"));
        Assert.Equal(2, doc.GetColumnIndex("Category"));
        Assert.Equal(3, doc.GetColumnIndex("Price"));
        Assert.Equal(4, doc.GetColumnIndex("Stock"));
    }

    [Fact]
    public void GetColumnIndex_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.Equal(doc.GetColumnIndex("Category"), doc.GetColumnIndex("Category"));
    }

    [Fact]
    public void GetColumnIndex_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var before = doc.GetColumnIndex("Price");
        var path = TempFile("gci_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnIndex("Price"));
    }

    // -------------------------------------------------------------------------
    // RenameColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var ex = Record.Exception(() => doc.RenameColumn("Stock", "InventoryCount"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameColumn_NewName_Exists_In_HasColumn()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        doc.RenameColumn("ProductName", "ItemName");
        Assert.True(doc.HasColumn("ItemName"));
    }

    [Fact]
    public void RenameColumn_OldName_Gone_From_HasColumn()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        doc.RenameColumn("Category", "ItemCategory");
        Assert.False(doc.HasColumn("Category"));
    }

    [Fact]
    public void RenameColumn_SaveLoad_Persists()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        doc.RenameColumn("Price", "UnitPrice");
        var path = TempFile("rc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(loaded.HasColumn("UnitPrice"));
    }

    [Fact]
    public void RenameColumn_Then_GetColumnValues_Works()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        doc.RenameColumn("Stock", "Inventory");
        var values = doc.GetColumnValues("Inventory");
        Assert.NotNull(values);
        Assert.Equal(doc.GetRowCount(), values.Count);
    }

    [Fact]
    public void RenameColumn_Multiple_Columns()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        doc.RenameColumn("ProductId", "Id");
        doc.RenameColumn("ProductName", "Name");
        doc.RenameColumn("Category", "Type");
        Assert.True(doc.HasColumn("Id"));
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Type"));
        Assert.False(doc.HasColumn("ProductId"));
        Assert.False(doc.HasColumn("ProductName"));
        Assert.False(doc.HasColumn("Category"));
    }

    [Fact]
    public void GetColumnIndex_After_RenameColumn()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var originalIndex = doc.GetColumnIndex("Price");
        doc.RenameColumn("Price", "Cost");
        Assert.Equal(originalIndex, doc.GetColumnIndex("Cost"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_HasColumn_GetColumnIndex_RenameColumn_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_inventory.csv");
        var content =
            "SKU,Description,Warehouse,Quantity,CostPerUnit,SellingPrice\n" +
            "SKU001,Industrial Pump,W-North,25,450.00,699.00\n" +
            "SKU002,Pressure Gauge,W-South,142,28.50,44.99\n" +
            "SKU003,Valve Assembly,W-North,67,175.00,249.00\n" +
            "SKU004,Control Unit,W-East,12,1200.00,1849.00\n" +
            "SKU005,Sensor Module,W-South,89,320.00,499.00\n" +
            "SKU006,Pipe Fitting,W-North,340,12.50,19.99\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // HasColumn — all original columns
        Assert.True(doc.HasColumn("SKU"));
        Assert.True(doc.HasColumn("Description"));
        Assert.True(doc.HasColumn("Warehouse"));
        Assert.True(doc.HasColumn("Quantity"));
        Assert.True(doc.HasColumn("CostPerUnit"));
        Assert.True(doc.HasColumn("SellingPrice"));
        Assert.False(doc.HasColumn("NonExistent"));

        // Consistent
        Assert.Equal(doc.HasColumn("SKU"), doc.HasColumn("SKU"));

        // GetColumnIndex — verify all positions
        Assert.Equal(0, doc.GetColumnIndex("SKU"));
        Assert.Equal(1, doc.GetColumnIndex("Description"));
        Assert.Equal(2, doc.GetColumnIndex("Warehouse"));
        Assert.Equal(3, doc.GetColumnIndex("Quantity"));
        Assert.Equal(4, doc.GetColumnIndex("CostPerUnit"));
        Assert.Equal(5, doc.GetColumnIndex("SellingPrice"));

        // Consistent
        Assert.Equal(doc.GetColumnIndex("Quantity"), doc.GetColumnIndex("Quantity"));

        // RenameColumn — normalize column names
        doc.RenameColumn("SKU", "ItemCode");
        doc.RenameColumn("CostPerUnit", "BuyPrice");
        doc.RenameColumn("SellingPrice", "SellPrice");

        Assert.True(doc.HasColumn("ItemCode"));
        Assert.True(doc.HasColumn("BuyPrice"));
        Assert.True(doc.HasColumn("SellPrice"));
        Assert.False(doc.HasColumn("SKU"));
        Assert.False(doc.HasColumn("CostPerUnit"));
        Assert.False(doc.HasColumn("SellingPrice"));

        // Unchanged columns still exist
        Assert.True(doc.HasColumn("Description"));
        Assert.True(doc.HasColumn("Warehouse"));
        Assert.True(doc.HasColumn("Quantity"));

        // Index unchanged after rename
        Assert.Equal(0, doc.GetColumnIndex("ItemCode"));
        Assert.Equal(4, doc.GetColumnIndex("BuyPrice"));
        Assert.Equal(5, doc.GetColumnIndex("SellPrice"));

        // GetColumnValues on renamed column
        var codes = doc.GetColumnValues("ItemCode");
        Assert.NotNull(codes);
        Assert.Equal(6, codes.Count);

        // ExportToHtml works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var savePath = TempFile("dogfood_inventory_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(6, loaded.GetRowCount());
        Assert.True(loaded.HasColumn("ItemCode"));
        Assert.True(loaded.HasColumn("BuyPrice"));
        Assert.True(loaded.HasColumn("SellPrice"));
        Assert.Equal(0, loaded.GetColumnIndex("ItemCode"));

        // RenameColumn on loaded
        loaded.RenameColumn("Warehouse", "Location");
        Assert.True(loaded.HasColumn("Location"));
        Assert.False(loaded.HasColumn("Warehouse"));

        // Final save
        var path2 = TempFile("dogfood_inventory_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.True(loaded2.HasColumn("Location"));
        Assert.True(loaded2.HasColumn("ItemCode"));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        Assert.Null(ex1);
    }
}
