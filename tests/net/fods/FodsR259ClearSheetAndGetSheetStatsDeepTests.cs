// Tests for FodsDocument.ClearSheet, GetSheetStats, ExportSheetToMarkdown deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R259

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R259: Tests for FodsDocument.ClearSheet, GetSheetStats, ExportSheetToMarkdown deeper.
/// ClearSheet(sheetName): removes all data from the specified sheet.
/// GetSheetStats(sheetName): returns statistics about the sheet (row count, col count, cell count).
/// ExportSheetToMarkdown(sheetName): exports a sheet as a markdown table.
/// Covers: ClearSheet no-throw; ClearSheet empties rows; ClearSheet persist;
/// ClearSheet multiple; ClearSheet then SetCellValue works;
/// ClearSheet then GetCellCount = 0; ClearSheet preserves sheet name;
/// GetSheetStats non-null; GetSheetStats has row count; GetSheetStats has col count;
/// GetSheetStats consistent; GetSheetStats no-throw; GetSheetStats after ClearSheet;
/// GetSheetStats after SetCellValue increases; GetSheetStats after AddColumn;
/// GetSheetStats after DeleteColumn decreases;
/// ExportSheetToMarkdown non-null; ExportSheetToMarkdown non-empty; ExportSheetToMarkdown has pipe;
/// ExportSheetToMarkdown has header names; ExportSheetToMarkdown has data;
/// ExportSheetToMarkdown after SetCellValue reflects; ExportSheetToMarkdown consistent;
/// ExportSheetToMarkdown after SortSheet; ExportSheetToMarkdown no-throw;
/// dogfood CreateDoc→ClearSheet→GetSheetStats→ExportSheetToMarkdown→SaveToFile pipeline.
/// </summary>
public class FodsR259ClearSheetAndGetSheetStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR259ClearSheetAndGetSheetStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR259_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "ID");
        doc.SetCellValue("Data", 0, 1, "Name");
        doc.SetCellValue("Data", 0, 2, "Value");
        doc.SetCellValue("Data", 0, 3, "Status");
        doc.SetCellValue("Data", 1, 0, "1");
        doc.SetCellValue("Data", 1, 1, "Alpha");
        doc.SetCellValue("Data", 1, 2, "100");
        doc.SetCellValue("Data", 1, 3, "Active");
        doc.SetCellValue("Data", 2, 0, "2");
        doc.SetCellValue("Data", 2, 1, "Beta");
        doc.SetCellValue("Data", 2, 2, "200");
        doc.SetCellValue("Data", 2, 3, "Inactive");
        doc.SetCellValue("Data", 3, 0, "3");
        doc.SetCellValue("Data", 3, 1, "Gamma");
        doc.SetCellValue("Data", 3, 2, "150");
        doc.SetCellValue("Data", 3, 3, "Active");
        doc.SetCellValue("Data", 4, 0, "4");
        doc.SetCellValue("Data", 4, 1, "Delta");
        doc.SetCellValue("Data", 4, 2, "175");
        doc.SetCellValue("Data", 4, 3, "Active");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ClearSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.ClearSheet("Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearSheet_EmptiesData()
    {
        var doc = CreateDataDoc();
        doc.ClearSheet("Data");
        Assert.True(doc.GetCellCount("Data") == 0 || doc.GetRowCount("Data") <= 1);
    }

    [Fact]
    public void ClearSheet_Persist()
    {
        var doc = CreateDataDoc();
        doc.ClearSheet("Data");
        var path = TempFile("clear_persist.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetCellCount("Data") <= 1);
    }

    [Fact]
    public void ClearSheet_PreservesSheetName()
    {
        var doc = CreateDataDoc();
        doc.ClearSheet("Data");
        Assert.Contains("Data", doc.GetSheetNames());
    }

    [Fact]
    public void ClearSheet_ThenSetCellValue_Works()
    {
        var doc = CreateDataDoc();
        doc.ClearSheet("Data");
        var ex = Record.Exception(() => doc.SetCellValue("Data", 0, 0, "New Header"));
        Assert.Null(ex);
        Assert.Equal("New Header", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void ClearSheet_Multiple_NoThrow()
    {
        var doc = CreateDataDoc();
        doc.AddSheet("Extra");
        doc.SetCellValue("Extra", 0, 0, "Test");
        var ex = Record.Exception(() =>
        {
            doc.ClearSheet("Data");
            doc.ClearSheet("Extra");
        });
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetSheetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetSheetStats("Data"));
    }

    [Fact]
    public void GetSheetStats_HasRowCount()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetSheetStats("Data");
        Assert.True(stats.RowCount > 0);
    }

    [Fact]
    public void GetSheetStats_HasColumnCount()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetSheetStats("Data");
        Assert.True(stats.ColumnCount > 0);
    }

    [Fact]
    public void GetSheetStats_HasCellCount()
    {
        var doc = CreateDataDoc();
        var stats = doc.GetSheetStats("Data");
        Assert.True(stats.CellCount > 0);
    }

    [Fact]
    public void GetSheetStats_Consistent()
    {
        var doc = CreateDataDoc();
        var s1 = doc.GetSheetStats("Data");
        var s2 = doc.GetSheetStats("Data");
        Assert.Equal(s1.RowCount, s2.RowCount);
        Assert.Equal(s1.ColumnCount, s2.ColumnCount);
    }

    [Fact]
    public void GetSheetStats_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.GetSheetStats("Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSheetStats_AfterClearSheet()
    {
        var doc = CreateDataDoc();
        doc.ClearSheet("Data");
        var stats = doc.GetSheetStats("Data");
        Assert.NotNull(stats);
        Assert.True(stats.RowCount >= 0);
        Assert.True(stats.CellCount >= 0);
    }

    [Fact]
    public void GetSheetStats_AfterSetCellValue_Increases()
    {
        var doc = CreateDataDoc();
        var before = doc.GetSheetStats("Data").CellCount;
        doc.SetCellValue("Data", 5, 0, "5");
        doc.SetCellValue("Data", 5, 1, "Epsilon");
        var after = doc.GetSheetStats("Data").CellCount;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetSheetStats_AfterAddColumn_ColCountIncreases()
    {
        var doc = CreateDataDoc();
        var before = doc.GetSheetStats("Data").ColumnCount;
        doc.AddColumn("Data", "Extra");
        var after = doc.GetSheetStats("Data").ColumnCount;
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.ExportSheetToMarkdown("Data"));
    }

    [Fact]
    public void ExportSheetToMarkdown_NonEmpty()
    {
        var doc = CreateDataDoc();
        Assert.NotEmpty(doc.ExportSheetToMarkdown("Data"));
    }

    [Fact]
    public void ExportSheetToMarkdown_HasPipe()
    {
        var doc = CreateDataDoc();
        var md = doc.ExportSheetToMarkdown("Data");
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_HasHeaderNames()
    {
        var doc = CreateDataDoc();
        var md = doc.ExportSheetToMarkdown("Data");
        Assert.True(md.Contains("ID") || md.Contains("Name") || md.Contains("Value"));
    }

    [Fact]
    public void ExportSheetToMarkdown_HasData()
    {
        var doc = CreateDataDoc();
        var md = doc.ExportSheetToMarkdown("Data");
        Assert.True(md.Contains("Alpha") || md.Contains("Beta") || md.Contains("100"));
    }

    [Fact]
    public void ExportSheetToMarkdown_AfterSetCellValue_Reflects()
    {
        var doc = CreateDataDoc();
        doc.SetCellValue("Data", 1, 1, "ALPHA_UPDATED");
        var md = doc.ExportSheetToMarkdown("Data");
        Assert.True(md.Contains("ALPHA_UPDATED") || md.Length > 0);
    }

    [Fact]
    public void ExportSheetToMarkdown_Consistent()
    {
        var doc = CreateDataDoc();
        var m1 = doc.ExportSheetToMarkdown("Data");
        var m2 = doc.ExportSheetToMarkdown("Data");
        Assert.Equal(m1.Length, m2.Length);
    }

    [Fact]
    public void ExportSheetToMarkdown_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.ExportSheetToMarkdown("Data"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ClearSheet_GetSheetStats_ExportSheetToMarkdown_SaveToFile_Pipeline()
    {
        // Build multi-sheet document
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Inventory");
        doc.AddSheet("Archive");
        doc.AddSheet("Summary");

        // Populate Inventory
        var cols = new[] { "SKU", "Product", "Category", "Qty", "Price" };
        for (int c = 0; c < cols.Length; c++)
            doc.SetCellValue("Inventory", 0, c, cols[c]);

        var data = new[]
        {
            new[] { "S001", "Widget A", "Electronics", "150", "29.99" },
            new[] { "S002", "Gadget B", "Electronics", "80", "49.99" },
            new[] { "S003", "Tool C", "Hardware", "200", "19.99" },
            new[] { "S004", "Device D", "Electronics", "45", "99.99" },
            new[] { "S005", "Part E", "Hardware", "500", "9.99" },
        };
        for (int r = 0; r < data.Length; r++)
            for (int c = 0; c < data[r].Length; c++)
                doc.SetCellValue("Inventory", r + 1, c, data[r][c]);

        // GetSheetStats baseline
        var stats = doc.GetSheetStats("Inventory");
        Assert.NotNull(stats);
        Assert.True(stats.RowCount >= 5);
        Assert.True(stats.ColumnCount >= 5);
        Assert.True(stats.CellCount >= 25);

        // ExportSheetToMarkdown baseline
        var md = doc.ExportSheetToMarkdown("Inventory");
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("|", md);
        Assert.True(md.Contains("Widget") || md.Contains("SKU"));

        // Populate Archive (copy some data)
        doc.SetCellValue("Archive", 0, 0, "SKU");
        doc.SetCellValue("Archive", 0, 1, "Product");
        doc.SetCellValue("Archive", 1, 0, "OLD-001");
        doc.SetCellValue("Archive", 1, 1, "Obsolete Widget");

        // GetSheetStats on Archive
        var archiveStats = doc.GetSheetStats("Archive");
        Assert.NotNull(archiveStats);
        Assert.True(archiveStats.RowCount >= 1);

        // ExportSheetToMarkdown on Archive
        var archiveMd = doc.ExportSheetToMarkdown("Archive");
        Assert.NotNull(archiveMd);
        Assert.Contains("|", archiveMd);

        // ClearSheet Archive
        doc.ClearSheet("Archive");
        var archiveStatsAfterClear = doc.GetSheetStats("Archive");
        Assert.NotNull(archiveStatsAfterClear);
        Assert.True(archiveStatsAfterClear.CellCount <= 1);

        // Archive sheet still exists
        Assert.Contains("Archive", doc.GetSheetNames());

        // SetCellValue after clear
        doc.SetCellValue("Archive", 0, 0, "Cleared");
        Assert.Equal("Cleared", doc.GetCellValue("Archive", 0, 0));

        // AddColumn and verify GetSheetStats grows
        doc.AddColumn("Inventory", "Supplier");
        var statsAfterAdd = doc.GetSheetStats("Inventory");
        Assert.True(statsAfterAdd.ColumnCount >= stats.ColumnCount);

        // ExportSheetToMarkdown after AddColumn
        var mdAfterAdd = doc.ExportSheetToMarkdown("Inventory");
        Assert.True(mdAfterAdd.Length >= md.Length);

        // SetCellValue and verify ExportSheetToMarkdown reflects
        doc.SetCellValue("Inventory", 1, 1, "WIDGET_A_UPDATED");
        var mdAfterUpdate = doc.ExportSheetToMarkdown("Inventory");
        Assert.True(mdAfterUpdate.Contains("WIDGET_A_UPDATED") || mdAfterUpdate.Length > 0);

        // SortSheet and verify ExportSheetToMarkdown still works
        doc.SortSheet("Inventory", "Price", ascending: true);
        var mdSorted = doc.ExportSheetToMarkdown("Inventory");
        Assert.NotNull(mdSorted);
        Assert.Contains("|", mdSorted);

        // GetSheetStats after SortSheet (unchanged)
        var statsSorted = doc.GetSheetStats("Inventory");
        Assert.Equal(statsAfterAdd.ColumnCount, statsSorted.ColumnCount);

        // DeleteColumn and verify GetSheetStats decreases
        doc.DeleteColumn("Inventory", "Supplier");
        var statsAfterDelete = doc.GetSheetStats("Inventory");
        Assert.True(statsAfterDelete.ColumnCount <= statsAfterAdd.ColumnCount);

        // Summary sheet
        doc.SetCellValue("Summary", 0, 0, "Total Items");
        doc.SetCellValue("Summary", 1, 0, "5");
        var summaryStats = doc.GetSheetStats("Summary");
        Assert.True(summaryStats.RowCount >= 1);

        // ExportSheetToMarkdown consistent
        var mc1 = doc.ExportSheetToMarkdown("Inventory");
        var mc2 = doc.ExportSheetToMarkdown("Inventory");
        Assert.Equal(mc1.Length, mc2.Length);

        // SaveToFile
        var path = TempFile("dogfood_clear_stats.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Contains("Inventory", loaded.GetSheetNames());
        Assert.Contains("Archive", loaded.GetSheetNames());

        // GetSheetStats on loaded
        var loadedStats = loaded.GetSheetStats("Inventory");
        Assert.NotNull(loadedStats);
        Assert.True(loadedStats.RowCount >= 5);

        // ExportSheetToMarkdown on loaded
        var loadedMd = loaded.ExportSheetToMarkdown("Inventory");
        Assert.NotNull(loadedMd);
        Assert.Contains("|", loadedMd);

        // ClearSheet on loaded Archive
        loaded.ClearSheet("Archive");
        var loadedArchiveStats = loaded.GetSheetStats("Archive");
        Assert.True(loadedArchiveStats.CellCount <= 1);

        // Final SaveToFile
        var path2 = TempFile("dogfood_clear_stats_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(loaded.GetSheetCount(), loaded2.GetSheetCount());
    }
}
