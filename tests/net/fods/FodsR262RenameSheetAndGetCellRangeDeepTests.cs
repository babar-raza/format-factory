// Tests for FodsDocument.RenameSheet, GetCellRange, SetColumnWidth deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R262

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R262: Tests for FodsDocument.RenameSheet, GetCellRange, SetColumnWidth deeper.
/// RenameSheet(oldName, newName): renames a sheet in the document.
/// GetCellRange(sheetName, startRow, startCol, endRow, endCol): returns cell values in range.
/// SetColumnWidth(sheetName, colIndex, width): sets the column width.
/// Covers: RenameSheet no-throw; RenameSheet sheet exists after; RenameSheet old gone;
/// RenameSheet updates GetSheetNames; RenameSheet persist; RenameSheet then SetCellValue;
/// RenameSheet multiple; RenameSheet preserves cell values; RenameSheet then ExportToJson;
/// GetCellRange non-null; GetCellRange non-empty; GetCellRange count correct;
/// GetCellRange contains known; GetCellRange consistent; GetCellRange no-throw;
/// GetCellRange single cell; GetCellRange full sheet; GetCellRange after SetCellValue reflects;
/// GetCellRange after RenameSheet accessible; GetCellRange row count correct;
/// SetColumnWidth no-throw; SetColumnWidth multiple; SetColumnWidth persist;
/// SetColumnWidth does not change cell values; SetColumnWidth then ExportToJson;
/// SetColumnWidth then SaveToFile;
/// dogfood CreateDoc→RenameSheet→GetCellRange→SetColumnWidth→SaveToFile pipeline.
/// </summary>
public class FodsR262RenameSheetAndGetCellRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR262RenameSheetAndGetCellRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR262_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSheetDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("DataSheet");
        doc.SetCellValue("DataSheet", 0, 0, "ID");
        doc.SetCellValue("DataSheet", 0, 1, "Name");
        doc.SetCellValue("DataSheet", 0, 2, "Value");
        doc.SetCellValue("DataSheet", 1, 0, "1");
        doc.SetCellValue("DataSheet", 1, 1, "Alice");
        doc.SetCellValue("DataSheet", 1, 2, "100");
        doc.SetCellValue("DataSheet", 2, 0, "2");
        doc.SetCellValue("DataSheet", 2, 1, "Bob");
        doc.SetCellValue("DataSheet", 2, 2, "200");
        doc.SetCellValue("DataSheet", 3, 0, "3");
        doc.SetCellValue("DataSheet", 3, 1, "Carol");
        doc.SetCellValue("DataSheet", 3, 2, "300");
        doc.SetCellValue("DataSheet", 4, 0, "4");
        doc.SetCellValue("DataSheet", 4, 1, "Dave");
        doc.SetCellValue("DataSheet", 4, 2, "400");
        return doc;
    }

    // -------------------------------------------------------------------------
    // RenameSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_NoThrow()
    {
        var doc = CreateSheetDoc();
        var ex = Record.Exception(() => doc.RenameSheet("DataSheet", "RenamedSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameSheet_NewNameExists()
    {
        var doc = CreateSheetDoc();
        doc.RenameSheet("DataSheet", "RenamedSheet");
        var names = doc.GetSheetNames();
        Assert.Contains("RenamedSheet", names);
    }

    [Fact]
    public void RenameSheet_OldNameGone()
    {
        var doc = CreateSheetDoc();
        doc.RenameSheet("DataSheet", "RenamedSheet");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("DataSheet", names);
    }

    [Fact]
    public void RenameSheet_UpdatesGetSheetNames()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.RenameSheet("Sheet1", "Renamed1");
        var names = doc.GetSheetNames();
        Assert.Contains("Renamed1", names);
        Assert.Contains("Sheet2", names);
    }

    [Fact]
    public void RenameSheet_Persist()
    {
        var doc = CreateSheetDoc();
        doc.RenameSheet("DataSheet", "PersistSheet");
        var path = TempFile("rename_persist.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.Contains("PersistSheet", loaded.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_PreservesCellValues()
    {
        var doc = CreateSheetDoc();
        doc.RenameSheet("DataSheet", "PreservedSheet");
        Assert.Equal("Alice", doc.GetCellValue("PreservedSheet", 1, 1));
        Assert.Equal("300", doc.GetCellValue("PreservedSheet", 3, 2));
    }

    [Fact]
    public void RenameSheet_ThenSetCellValue()
    {
        var doc = CreateSheetDoc();
        doc.RenameSheet("DataSheet", "UpdatedSheet");
        doc.SetCellValue("UpdatedSheet", 1, 1, "RENAMED_ALICE");
        Assert.Equal("RENAMED_ALICE", doc.GetCellValue("UpdatedSheet", 1, 1));
    }

    [Fact]
    public void RenameSheet_Multiple()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("A");
        doc.AddSheet("B");
        doc.AddSheet("C");
        doc.RenameSheet("A", "Alpha");
        doc.RenameSheet("B", "Beta");
        doc.RenameSheet("C", "Gamma");
        var names = doc.GetSheetNames();
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
        Assert.Contains("Gamma", names);
    }

    [Fact]
    public void RenameSheet_ThenExportToJson_NonNull()
    {
        var doc = CreateSheetDoc();
        doc.RenameSheet("DataSheet", "JsonSheet");
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    // -------------------------------------------------------------------------
    // GetCellRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellRange_NonNull()
    {
        var doc = CreateSheetDoc();
        Assert.NotNull(doc.GetCellRange("DataSheet", 0, 0, 2, 2));
    }

    [Fact]
    public void GetCellRange_NonEmpty()
    {
        var doc = CreateSheetDoc();
        var range = doc.GetCellRange("DataSheet", 0, 0, 2, 2);
        Assert.True(range.Count > 0);
    }

    [Fact]
    public void GetCellRange_CountCorrect()
    {
        var doc = CreateSheetDoc();
        // rows 0-2 (3 rows), cols 0-2 (3 cols) = 9 cells
        var range = doc.GetCellRange("DataSheet", 0, 0, 2, 2);
        Assert.Equal(9, range.Count);
    }

    [Fact]
    public void GetCellRange_ContainsKnown()
    {
        var doc = CreateSheetDoc();
        var range = doc.GetCellRange("DataSheet", 0, 0, 4, 2);
        Assert.Contains("Alice", range);
        Assert.Contains("Bob", range);
        Assert.Contains("Carol", range);
    }

    [Fact]
    public void GetCellRange_Consistent()
    {
        var doc = CreateSheetDoc();
        var r1 = doc.GetCellRange("DataSheet", 0, 0, 2, 2);
        var r2 = doc.GetCellRange("DataSheet", 0, 0, 2, 2);
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetCellRange_NoThrow()
    {
        var doc = CreateSheetDoc();
        var ex = Record.Exception(() => doc.GetCellRange("DataSheet", 0, 0, 2, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellRange_SingleCell()
    {
        var doc = CreateSheetDoc();
        var range = doc.GetCellRange("DataSheet", 1, 1, 1, 1);
        Assert.Equal(1, range.Count);
        Assert.Contains("Alice", range);
    }

    [Fact]
    public void GetCellRange_AfterSetCellValue_Reflects()
    {
        var doc = CreateSheetDoc();
        doc.SetCellValue("DataSheet", 1, 1, "ALICE_UPDATED");
        var range = doc.GetCellRange("DataSheet", 1, 1, 1, 1);
        Assert.Contains("ALICE_UPDATED", range);
    }

    [Fact]
    public void GetCellRange_AfterRenameSheet_AccessibleByNewName()
    {
        var doc = CreateSheetDoc();
        doc.RenameSheet("DataSheet", "AccessibleSheet");
        var range = doc.GetCellRange("AccessibleSheet", 0, 0, 1, 1);
        Assert.NotNull(range);
        Assert.True(range.Count > 0);
    }

    [Fact]
    public void GetCellRange_RowCountCorrect()
    {
        var doc = CreateSheetDoc();
        // rows 1-3 (3 rows), col 1 (1 col) = 3 cells
        var range = doc.GetCellRange("DataSheet", 1, 1, 3, 1);
        Assert.Equal(3, range.Count);
    }

    // -------------------------------------------------------------------------
    // SetColumnWidth
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NoThrow()
    {
        var doc = CreateSheetDoc();
        var ex = Record.Exception(() => doc.SetColumnWidth("DataSheet", 0, 120));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_Multiple_NoThrow()
    {
        var doc = CreateSheetDoc();
        var ex = Record.Exception(() =>
        {
            doc.SetColumnWidth("DataSheet", 0, 100);
            doc.SetColumnWidth("DataSheet", 1, 150);
            doc.SetColumnWidth("DataSheet", 2, 80);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_Persist()
    {
        var doc = CreateSheetDoc();
        doc.SetColumnWidth("DataSheet", 1, 200);
        var path = TempFile("col_width_persist.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void SetColumnWidth_DoesNotChangeCellValues()
    {
        var doc = CreateSheetDoc();
        var before = doc.GetCellValue("DataSheet", 1, 1);
        doc.SetColumnWidth("DataSheet", 1, 180);
        Assert.Equal(before, doc.GetCellValue("DataSheet", 1, 1));
    }

    [Fact]
    public void SetColumnWidth_ThenExportToJson_NonNull()
    {
        var doc = CreateSheetDoc();
        doc.SetColumnWidth("DataSheet", 0, 120);
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    [Fact]
    public void SetColumnWidth_ThenSaveToFile()
    {
        var doc = CreateSheetDoc();
        doc.SetColumnWidth("DataSheet", 2, 95);
        var path = TempFile("col_width_save.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_RenameSheet_GetCellRange_SetColumnWidth_SaveToFile_Pipeline()
    {
        // Build multi-sheet workbook
        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: Sales Data
        doc.AddSheet("RawSales");
        doc.SetCellValue("RawSales", 0, 0, "Product");
        doc.SetCellValue("RawSales", 0, 1, "Region");
        doc.SetCellValue("RawSales", 0, 2, "Q1");
        doc.SetCellValue("RawSales", 0, 3, "Q2");
        doc.SetCellValue("RawSales", 1, 0, "Widget");
        doc.SetCellValue("RawSales", 1, 1, "Europe");
        doc.SetCellValue("RawSales", 1, 2, "45000");
        doc.SetCellValue("RawSales", 1, 3, "52000");
        doc.SetCellValue("RawSales", 2, 0, "Gadget");
        doc.SetCellValue("RawSales", 2, 1, "Americas");
        doc.SetCellValue("RawSales", 2, 2, "78000");
        doc.SetCellValue("RawSales", 2, 3, "85000");
        doc.SetCellValue("RawSales", 3, 0, "Doohickey");
        doc.SetCellValue("RawSales", 3, 1, "APAC");
        doc.SetCellValue("RawSales", 3, 2, "32000");
        doc.SetCellValue("RawSales", 3, 3, "38000");
        doc.SetCellValue("RawSales", 4, 0, "Thingamajig");
        doc.SetCellValue("RawSales", 4, 1, "Europe");
        doc.SetCellValue("RawSales", 4, 2, "61000");
        doc.SetCellValue("RawSales", 4, 3, "71000");

        // Sheet 2: Summary
        doc.AddSheet("RawSummary");
        doc.SetCellValue("RawSummary", 0, 0, "Metric");
        doc.SetCellValue("RawSummary", 0, 1, "Value");
        doc.SetCellValue("RawSummary", 1, 0, "Total Products");
        doc.SetCellValue("RawSummary", 1, 1, "4");
        doc.SetCellValue("RawSummary", 2, 0, "Top Region");
        doc.SetCellValue("RawSummary", 2, 1, "Americas");

        // GetCellRange on RawSales before rename
        var headerRange = doc.GetCellRange("RawSales", 0, 0, 0, 3);
        Assert.Equal(4, headerRange.Count);
        Assert.Contains("Product", headerRange);
        Assert.Contains("Region", headerRange);

        var dataRange = doc.GetCellRange("RawSales", 1, 0, 4, 3);
        Assert.Equal(16, dataRange.Count);
        Assert.Contains("Widget", dataRange);
        Assert.Contains("Thingamajig", dataRange);

        // RenameSheet
        doc.RenameSheet("RawSales", "Q3SalesData");
        doc.RenameSheet("RawSummary", "Q3Summary");

        var names = doc.GetSheetNames();
        Assert.Contains("Q3SalesData", names);
        Assert.Contains("Q3Summary", names);
        Assert.DoesNotContain("RawSales", names);
        Assert.DoesNotContain("RawSummary", names);

        // GetCellRange after rename — accessible by new name
        var renamedRange = doc.GetCellRange("Q3SalesData", 0, 0, 0, 3);
        Assert.Equal(4, renamedRange.Count);
        Assert.Contains("Product", renamedRange);

        // Cell values preserved after rename
        Assert.Equal("Widget", doc.GetCellValue("Q3SalesData", 1, 0));
        Assert.Equal("Americas", doc.GetCellValue("Q3SalesData", 2, 1));

        // SetColumnWidth on renamed sheet
        doc.SetColumnWidth("Q3SalesData", 0, 120); // Product column
        doc.SetColumnWidth("Q3SalesData", 1, 100); // Region column
        doc.SetColumnWidth("Q3SalesData", 2, 80);  // Q1 column
        doc.SetColumnWidth("Q3SalesData", 3, 80);  // Q2 column

        // Cell values unchanged after SetColumnWidth
        Assert.Equal("Widget", doc.GetCellValue("Q3SalesData", 1, 0));
        Assert.Equal("45000", doc.GetCellValue("Q3SalesData", 1, 2));

        // SetColumnWidth on summary sheet
        doc.SetColumnWidth("Q3Summary", 0, 150);
        doc.SetColumnWidth("Q3Summary", 1, 100);

        // Add new sheet with data
        doc.AddSheet("Q4Forecast");
        doc.SetCellValue("Q4Forecast", 0, 0, "Product");
        doc.SetCellValue("Q4Forecast", 0, 1, "Q3 Actual");
        doc.SetCellValue("Q4Forecast", 0, 2, "Q4 Forecast");
        doc.SetCellValue("Q4Forecast", 1, 0, "Widget");
        doc.SetCellValue("Q4Forecast", 1, 1, "52000");
        doc.SetCellValue("Q4Forecast", 1, 2, "58000");
        doc.SetCellValue("Q4Forecast", 2, 0, "Gadget");
        doc.SetCellValue("Q4Forecast", 2, 1, "85000");
        doc.SetCellValue("Q4Forecast", 2, 2, "92000");

        // GetCellRange on new sheet
        var forecastRange = doc.GetCellRange("Q4Forecast", 1, 0, 2, 2);
        Assert.Equal(6, forecastRange.Count);
        Assert.Contains("Widget", forecastRange);
        Assert.Contains("92000", forecastRange);

        // RenameSheet the new sheet
        doc.RenameSheet("Q4Forecast", "ForecastFinal");
        Assert.Contains("ForecastFinal", doc.GetSheetNames());

        // GetCellRange single cell
        var singleCell = doc.GetCellRange("ForecastFinal", 1, 2, 1, 2);
        Assert.Equal(1, singleCell.Count);
        Assert.Contains("58000", singleCell);

        // SetCellValue after rename and verify via GetCellRange
        doc.SetCellValue("Q3SalesData", 1, 2, "47000"); // Update Q1 Widget
        var updatedRange = doc.GetCellRange("Q3SalesData", 1, 2, 1, 2);
        Assert.Contains("47000", updatedRange);

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // GetCellRange consistent
        var cr1 = doc.GetCellRange("Q3SalesData", 0, 0, 2, 2);
        var cr2 = doc.GetCellRange("Q3SalesData", 0, 0, 2, 2);
        Assert.Equal(cr1.Count, cr2.Count);

        // SaveToFile
        var path = TempFile("dogfood_workbook.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetSheetCount());
        var loadedNames = loaded.GetSheetNames();
        Assert.Contains("Q3SalesData", loadedNames);
        Assert.Contains("Q3Summary", loadedNames);
        Assert.Contains("ForecastFinal", loadedNames);

        // GetCellRange on loaded
        var loadedRange = loaded.GetCellRange("Q3SalesData", 0, 0, 0, 3);
        Assert.Equal(4, loadedRange.Count);

        // RenameSheet on loaded
        loaded.RenameSheet("Q3Summary", "FinalSummary");
        Assert.Contains("FinalSummary", loaded.GetSheetNames());

        // SetColumnWidth on loaded
        var colWidthEx = Record.Exception(() => loaded.SetColumnWidth("Q3SalesData", 0, 130));
        Assert.Null(colWidthEx);

        // Final SaveToFile
        var path2 = TempFile("dogfood_workbook_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(3, loaded2.GetSheetCount());
    }
}
