// Tests for FodsDocument.SortSheet, GetCellCount, CreateNew deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R255

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R255: Tests for FodsDocument.SortSheet, GetCellCount, CreateNew deeper.
/// SortSheet(sheetName, colName, ascending): sorts all data rows in a sheet by column.
/// GetCellCount(sheetName): returns total number of non-empty cells in the sheet.
/// CreateNew(): creates a new empty FodsDocument with no sheets.
/// Covers: SortSheet no-throw; SortSheet ascending first row correct;
/// SortSheet descending first row correct; SortSheet preserves row count;
/// SortSheet preserves column structure; SortSheet consistent; SortSheet then FilterRows;
/// SortSheet then ExportSheetToCsv;
/// GetCellCount positive; GetCellCount after SetCellValue increases;
/// GetCellCount after AddColumn increases; GetCellCount consistent;
/// GetCellCount across sheets; GetCellCount then SortSheet unchanged;
/// GetCellCount after DeleteColumn decreases;
/// CreateNew non-null; CreateNew no sheets; CreateNew then AddSheet;
/// CreateNew then AddSheet then SetCellValue; CreateNew multiple instances independent;
/// CreateNew then SaveToFile; CreateNew then LoadFile round-trip;
/// dogfood CreateNew→AddSheet→SortSheet→GetCellCount→SaveToFile pipeline.
/// </summary>
public class FodsR255SortSheetAndGetCellCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR255SortSheetAndGetCellCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR255_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateScoreDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Scores");
        doc.SetCellValue("Scores", 0, 0, "Name");
        doc.SetCellValue("Scores", 0, 1, "Score");
        doc.SetCellValue("Scores", 0, 2, "Grade");
        doc.SetCellValue("Scores", 1, 0, "Charlie");
        doc.SetCellValue("Scores", 1, 1, "78");
        doc.SetCellValue("Scores", 1, 2, "C");
        doc.SetCellValue("Scores", 2, 0, "Alice");
        doc.SetCellValue("Scores", 2, 1, "92");
        doc.SetCellValue("Scores", 2, 2, "A");
        doc.SetCellValue("Scores", 3, 0, "Eve");
        doc.SetCellValue("Scores", 3, 1, "85");
        doc.SetCellValue("Scores", 3, 2, "B");
        doc.SetCellValue("Scores", 4, 0, "Bob");
        doc.SetCellValue("Scores", 4, 1, "88");
        doc.SetCellValue("Scores", 4, 2, "B+");
        doc.SetCellValue("Scores", 5, 0, "Diana");
        doc.SetCellValue("Scores", 5, 1, "91");
        doc.SetCellValue("Scores", 5, 2, "A-");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SortSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void SortSheet_NoThrow()
    {
        var doc = CreateScoreDoc();
        var ex = Record.Exception(() => doc.SortSheet("Scores", "Name", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortSheet_Ascending_FirstRowCorrect()
    {
        var doc = CreateScoreDoc();
        doc.SortSheet("Scores", "Name", ascending: true);
        // Alice should be first data row
        Assert.Equal("Alice", doc.GetCellValue("Scores", 1, 0));
    }

    [Fact]
    public void SortSheet_Descending_FirstRowCorrect()
    {
        var doc = CreateScoreDoc();
        doc.SortSheet("Scores", "Name", ascending: false);
        // Eve should be first data row
        Assert.Equal("Eve", doc.GetCellValue("Scores", 1, 0));
    }

    [Fact]
    public void SortSheet_PreservesRowCount()
    {
        var doc = CreateScoreDoc();
        var range = doc.GetUsedRange("Scores");
        doc.SortSheet("Scores", "Name", ascending: true);
        var rangeAfter = doc.GetUsedRange("Scores");
        Assert.Equal(range.Item1, rangeAfter.Item1);
    }

    [Fact]
    public void SortSheet_PreservesColumnStructure()
    {
        var doc = CreateScoreDoc();
        doc.SortSheet("Scores", "Score", ascending: true);
        var cols = doc.GetColumnNames("Scores");
        Assert.Contains("Name", cols);
        Assert.Contains("Score", cols);
        Assert.Contains("Grade", cols);
    }

    [Fact]
    public void SortSheet_ByScore_Ascending_FirstIsLowest()
    {
        var doc = CreateScoreDoc();
        doc.SortSheet("Scores", "Score", ascending: true);
        // Charlie=78 is lowest
        Assert.Equal("Charlie", doc.GetCellValue("Scores", 1, 0));
    }

    [Fact]
    public void SortSheet_ByScore_Descending_FirstIsHighest()
    {
        var doc = CreateScoreDoc();
        doc.SortSheet("Scores", "Score", ascending: false);
        // Alice=92 is highest
        Assert.Equal("Alice", doc.GetCellValue("Scores", 1, 0));
    }

    [Fact]
    public void SortSheet_Consistent()
    {
        var doc = CreateScoreDoc();
        doc.SortSheet("Scores", "Name", ascending: true);
        var first1 = doc.GetCellValue("Scores", 1, 0);
        doc.SortSheet("Scores", "Name", ascending: true);
        var first2 = doc.GetCellValue("Scores", 1, 0);
        Assert.Equal(first1, first2);
    }

    [Fact]
    public void SortSheet_ThenExportSheetToCsv_Works()
    {
        var doc = CreateScoreDoc();
        doc.SortSheet("Scores", "Name", ascending: true);
        var csv = doc.ExportSheetToCsv("Scores");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);
        Assert.Contains("Alice", csv);
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_Positive()
    {
        var doc = CreateScoreDoc();
        Assert.True(doc.GetCellCount("Scores") > 0);
    }

    [Fact]
    public void GetCellCount_AfterSetCellValue_Increases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Test");
        doc.SetCellValue("Test", 0, 0, "Value1");
        var before = doc.GetCellCount("Test");
        doc.SetCellValue("Test", 1, 0, "Value2");
        var after = doc.GetCellCount("Test");
        Assert.True(after > before);
    }

    [Fact]
    public void GetCellCount_Consistent()
    {
        var doc = CreateScoreDoc();
        var c1 = doc.GetCellCount("Scores");
        var c2 = doc.GetCellCount("Scores");
        Assert.Equal(c1, c2);
    }

    [Fact]
    public void GetCellCount_AfterAddColumn_Increases()
    {
        var doc = CreateScoreDoc();
        var before = doc.GetCellCount("Scores");
        doc.AddColumn("Scores", "Rank", new[] { "1", "2", "3", "4", "5" });
        var after = doc.GetCellCount("Scores");
        Assert.True(after > before);
    }

    [Fact]
    public void GetCellCount_AfterSortSheet_Unchanged()
    {
        var doc = CreateScoreDoc();
        var before = doc.GetCellCount("Scores");
        doc.SortSheet("Scores", "Name", ascending: true);
        var after = doc.GetCellCount("Scores");
        Assert.Equal(before, after);
    }

    [Fact]
    public void GetCellCount_AfterDeleteColumn_Decreases()
    {
        var doc = CreateScoreDoc();
        var before = doc.GetCellCount("Scores");
        doc.DeleteColumn("Scores", "Grade");
        var after = doc.GetCellCount("Scores");
        Assert.True(after < before);
    }

    [Fact]
    public void GetCellCount_EmptySheet_Zero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        Assert.Equal(0, doc.GetCellCount("Empty"));
    }

    // -------------------------------------------------------------------------
    // CreateNew
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateNew_NonNull()
    {
        Assert.NotNull(FodsDocument.CreateNew());
    }

    [Fact]
    public void CreateNew_ThenAddSheet_Works()
    {
        var doc = FodsDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddSheet("NewSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void CreateNew_ThenAddSheet_SheetAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("MySheet");
        var sheets = doc.GetSheetNames();
        Assert.Contains("MySheet", sheets);
    }

    [Fact]
    public void CreateNew_ThenSetCellValue_Works()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex = Record.Exception(() => doc.SetCellValue("Data", 0, 0, "Hello"));
        Assert.Null(ex);
        Assert.Equal("Hello", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void CreateNew_MultipleInstances_Independent()
    {
        var doc1 = FodsDocument.CreateNew();
        var doc2 = FodsDocument.CreateNew();
        doc1.AddSheet("Sheet1");
        var doc1Sheets = doc1.GetSheetNames();
        var doc2Sheets = doc2.GetSheetNames();
        Assert.True(doc1Sheets.Count > doc2Sheets.Count);
    }

    [Fact]
    public void CreateNew_ThenSaveToFile_Works()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Test");
        var path = TempFile("create_new.fods");
        var ex = Record.Exception(() => doc.SaveToFile(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CreateNew_ThenLoadFile_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("RoundTrip");
        doc.SetCellValue("RoundTrip", 0, 0, "Name");
        doc.SetCellValue("RoundTrip", 1, 0, "Alice");
        var path = TempFile("create_new_rt.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Contains("RoundTrip", loaded.GetSheetNames());
        Assert.Equal("Alice", loaded.GetCellValue("RoundTrip", 1, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateNew_AddSheet_SortSheet_GetCellCount_SaveToFile_Pipeline()
    {
        // CreateNew
        var doc = FodsDocument.CreateNew();
        Assert.NotNull(doc);

        // AddSheet — Inventory
        doc.AddSheet("Inventory");
        var invCols = new[] { "Product", "Category", "Price", "Stock" };
        for (int c = 0; c < invCols.Length; c++)
            doc.SetCellValue("Inventory", 0, c, invCols[c]);

        var invData = new[]
        {
            new[] { "Widget A", "Electronics", "29.99", "150" },
            new[] { "Gadget B", "Tools", "49.99", "80" },
            new[] { "Part C", "Hardware", "9.99", "500" },
            new[] { "Device D", "Electronics", "99.99", "45" },
            new[] { "Kit E", "Tools", "19.99", "200" },
            new[] { "Component F", "Hardware", "4.99", "1000" },
        };
        for (int r = 0; r < invData.Length; r++)
            for (int c = 0; c < invData[r].Length; c++)
                doc.SetCellValue("Inventory", r + 1, c, invData[r][c]);

        // AddSheet — Summary
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Metric");
        doc.SetCellValue("Summary", 0, 1, "Value");
        doc.SetCellValue("Summary", 1, 0, "TotalProducts");
        doc.SetCellValue("Summary", 1, 1, "6");

        // GetSheetNames
        var sheets = doc.GetSheetNames();
        Assert.Equal(2, sheets.Count);
        Assert.Contains("Inventory", sheets);
        Assert.Contains("Summary", sheets);

        // GetCellCount
        var invCellCount = doc.GetCellCount("Inventory");
        Assert.True(invCellCount > 0);
        // 7 rows × 4 cols = 28 cells
        Assert.Equal(28, invCellCount);

        var sumCellCount = doc.GetCellCount("Summary");
        Assert.Equal(4, sumCellCount); // 2 rows × 2 cols

        // SortSheet by Product ascending
        doc.SortSheet("Inventory", "Product", ascending: true);
        Assert.Equal("Component F", doc.GetCellValue("Inventory", 1, 0));
        Assert.Equal(28, doc.GetCellCount("Inventory")); // unchanged

        // SortSheet by Price descending
        doc.SortSheet("Inventory", "Price", ascending: false);
        Assert.Equal("Device D", doc.GetCellValue("Inventory", 1, 0)); // 99.99 highest
        Assert.Equal(28, doc.GetCellCount("Inventory")); // unchanged

        // ExportSheetToCsv after sort
        var csv = doc.ExportSheetToCsv("Inventory");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);
        Assert.Contains("Device D", csv);
        Assert.Contains("Product", csv);

        // AddColumn to Inventory
        doc.AddColumn("Inventory", "OnSale",
            new[] { "No", "Yes", "No", "Yes", "No", "Yes" });
        var invCellCountAfterCol = doc.GetCellCount("Inventory");
        Assert.True(invCellCountAfterCol > invCellCount);

        // GetColumnNames
        var cols = doc.GetColumnNames("Inventory");
        Assert.Equal(5, cols.Count);
        Assert.Contains("OnSale", cols);

        // FilterRows
        var electronics = doc.FilterRows("Inventory", "Category", "Electronics");
        Assert.NotNull(electronics);
        var elecRange = electronics.GetUsedRange("Inventory");
        Assert.Equal(3, elecRange.Item1); // 2 electronics + 1 header

        // DeleteColumn on inventory
        doc.DeleteColumn("Inventory", "OnSale");
        var invCellCountAfterDel = doc.GetCellCount("Inventory");
        Assert.Equal(invCellCount, invCellCountAfterDel);

        // SortSheet by Stock descending
        doc.SortSheet("Inventory", "Stock", ascending: false);
        Assert.Equal("Component F", doc.GetCellValue("Inventory", 1, 0)); // stock=1000

        // Second CreateNew — independent
        var doc2 = FodsDocument.CreateNew();
        doc2.AddSheet("Other");
        Assert.NotNull(doc2);
        var doc2Sheets = doc2.GetSheetNames();
        Assert.Equal(1, doc2Sheets.Count);
        // doc still has 2 sheets
        Assert.Equal(2, doc.GetSheetNames().Count);

        // SaveToFile
        var path = TempFile("dogfood_sort_count.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
        var loadedSheets = loaded.GetSheetNames();
        Assert.Contains("Inventory", loadedSheets);
        Assert.Contains("Summary", loadedSheets);

        var loadedCellCount = loaded.GetCellCount("Inventory");
        Assert.Equal(invCellCount, loadedCellCount);

        // SortSheet on loaded
        loaded.SortSheet("Inventory", "Product", ascending: true);
        var loadedFirst = loaded.GetCellValue("Inventory", 1, 0);
        Assert.Equal("Component F", loadedFirst);

        // GetCellCount on loaded Summary
        var loadedSumCount = loaded.GetCellCount("Summary");
        Assert.Equal(4, loadedSumCount);
    }
}
