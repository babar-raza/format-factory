// Tests for FodsDocument.MergeSheets, GetCellCount, ExportSheetToCsv deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R270

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R270: Tests for FodsDocument.MergeSheets, GetCellCount, ExportSheetToCsv deeper.
/// MergeSheets(sourceSheet, targetSheet): merges content from source into target sheet.
/// GetCellCount(sheetName): returns the number of non-empty cells in the sheet.
/// ExportSheetToCsv(sheetName): exports a single sheet as a CSV string.
/// Covers: MergeSheets no-throw; MergeSheets target has more cells after;
/// MergeSheets source data appears in target; MergeSheets consistent;
/// MergeSheets save-load; MergeSheets multiple;
/// GetCellCount non-negative; GetCellCount>0 for non-empty sheet;
/// GetCellCount=0 for empty sheet; GetCellCount consistent; GetCellCount no-throw;
/// GetCellCount after SetCellValue increases; GetCellCount save-load;
/// GetCellCount different sheets differ; GetCellCount after MergeSheets updates;
/// ExportSheetToCsv non-null; ExportSheetToCsv non-empty; ExportSheetToCsv no-throw;
/// ExportSheetToCsv has commas; ExportSheetToCsv has header content;
/// ExportSheetToCsv consistent; ExportSheetToCsv after SetCellValue updates;
/// ExportSheetToCsv save-load consistent; ExportSheetToCsv different sheets differ;
/// dogfood CreateDoc→MergeSheets→GetCellCount→ExportSheetToCsv→SaveToFile pipeline.
/// </summary>
public class FodsR270MergeSheetsAndGetCellCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR270MergeSheetsAndGetCellCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR270_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        // Sales sheet
        doc.SetCellValue("Sales", 0, 0, "Region");
        doc.SetCellValue("Sales", 0, 1, "Product");
        doc.SetCellValue("Sales", 0, 2, "Revenue");
        doc.SetCellValue("Sales", 1, 0, "North");
        doc.SetCellValue("Sales", 1, 1, "Alpha");
        doc.SetCellValue("Sales", 1, 2, "85000");
        doc.SetCellValue("Sales", 2, 0, "South");
        doc.SetCellValue("Sales", 2, 1, "Beta");
        doc.SetCellValue("Sales", 2, 2, "72000");
        doc.SetCellValue("Sales", 3, 0, "East");
        doc.SetCellValue("Sales", 3, 1, "Alpha");
        doc.SetCellValue("Sales", 3, 2, "91000");

        // HR sheet
        doc.AddSheet("HR");
        doc.SetCellValue("HR", 0, 0, "Name");
        doc.SetCellValue("HR", 0, 1, "Dept");
        doc.SetCellValue("HR", 1, 0, "Alice");
        doc.SetCellValue("HR", 1, 1, "Eng");
        doc.SetCellValue("HR", 2, 0, "Bob");
        doc.SetCellValue("HR", 2, 1, "Marketing");

        // Summary sheet (empty initially)
        doc.AddSheet("Summary");

        return doc;
    }

    // -------------------------------------------------------------------------
    // MergeSheets
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeSheets_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.MergeSheets("Sales", "Summary"));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeSheets_TargetHasMoreCells()
    {
        var doc = CreateWorkbook();
        var before = doc.GetCellCount("Summary");
        doc.MergeSheets("Sales", "Summary");
        Assert.True(doc.GetCellCount("Summary") > before);
    }

    [Fact]
    public void MergeSheets_SourceDataInTarget()
    {
        var doc = CreateWorkbook();
        doc.MergeSheets("Sales", "Summary");
        var csv = doc.ExportSheetToCsv("Summary");
        Assert.True(csv.Contains("Region") || csv.Contains("North") || csv.Contains("85000"));
    }

    [Fact]
    public void MergeSheets_Consistent()
    {
        var doc = CreateWorkbook();
        doc.MergeSheets("Sales", "Summary");
        var count1 = doc.GetCellCount("Summary");
        doc.MergeSheets("HR", "Summary");
        var count2 = doc.GetCellCount("Summary");
        Assert.True(count2 >= count1);
    }

    [Fact]
    public void MergeSheets_SaveLoad()
    {
        var doc = CreateWorkbook();
        doc.MergeSheets("Sales", "Summary");
        var beforeCount = doc.GetCellCount("Summary");
        var path = TempFile("merge_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetCellCount("Summary") >= beforeCount);
    }

    // -------------------------------------------------------------------------
    // GetCellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_NonNegative()
    {
        var doc = CreateWorkbook();
        Assert.True(doc.GetCellCount("Sales") >= 0);
    }

    [Fact]
    public void GetCellCount_PositiveForNonEmptySheet()
    {
        var doc = CreateWorkbook();
        Assert.True(doc.GetCellCount("Sales") > 0);
    }

    [Fact]
    public void GetCellCount_Zero_EmptySheet()
    {
        var doc = CreateWorkbook();
        // Summary sheet is empty
        Assert.Equal(0, doc.GetCellCount("Summary"));
    }

    [Fact]
    public void GetCellCount_Consistent()
    {
        var doc = CreateWorkbook();
        Assert.Equal(doc.GetCellCount("Sales"), doc.GetCellCount("Sales"));
    }

    [Fact]
    public void GetCellCount_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.GetCellCount("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellCount_AfterSetCellValue_Increases()
    {
        var doc = CreateWorkbook();
        var before = doc.GetCellCount("Summary");
        doc.SetCellValue("Summary", 0, 0, "New Value");
        Assert.True(doc.GetCellCount("Summary") > before);
    }

    [Fact]
    public void GetCellCount_SaveLoad_Consistent()
    {
        var doc = CreateWorkbook();
        var before = doc.GetCellCount("Sales");
        var path = TempFile("cellcount_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellCount("Sales"));
    }

    [Fact]
    public void GetCellCount_DifferentSheets_Differ()
    {
        var doc = CreateWorkbook();
        // Sales has 12 cells, HR has 6, Summary has 0
        Assert.NotEqual(doc.GetCellCount("Sales"), doc.GetCellCount("Summary"));
    }

    [Fact]
    public void GetCellCount_Sales_TwelveValues()
    {
        var doc = CreateWorkbook();
        // 4 rows × 3 cols = 12 cells
        Assert.Equal(12, doc.GetCellCount("Sales"));
    }

    // -------------------------------------------------------------------------
    // ExportSheetToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsv_NonNull()
    {
        var doc = CreateWorkbook();
        Assert.NotNull(doc.ExportSheetToCsv("Sales"));
    }

    [Fact]
    public void ExportSheetToCsv_NonEmpty()
    {
        var doc = CreateWorkbook();
        Assert.NotEmpty(doc.ExportSheetToCsv("Sales"));
    }

    [Fact]
    public void ExportSheetToCsv_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.ExportSheetToCsv("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportSheetToCsv_HasCommas()
    {
        var doc = CreateWorkbook();
        var csv = doc.ExportSheetToCsv("Sales");
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ExportSheetToCsv_HasHeaderContent()
    {
        var doc = CreateWorkbook();
        var csv = doc.ExportSheetToCsv("Sales");
        Assert.True(csv.Contains("Region") || csv.Contains("Product") || csv.Contains("Revenue"));
    }

    [Fact]
    public void ExportSheetToCsv_Consistent()
    {
        var doc = CreateWorkbook();
        var csv1 = doc.ExportSheetToCsv("Sales");
        var csv2 = doc.ExportSheetToCsv("Sales");
        Assert.Equal(csv1.Length, csv2.Length);
    }

    [Fact]
    public void ExportSheetToCsv_AfterSetCellValue_Updates()
    {
        var doc = CreateWorkbook();
        var before = doc.ExportSheetToCsv("Sales").Length;
        doc.SetCellValue("Sales", 4, 0, "West");
        doc.SetCellValue("Sales", 4, 1, "Gamma");
        doc.SetCellValue("Sales", 4, 2, "68000");
        Assert.True(doc.ExportSheetToCsv("Sales").Length > before);
    }

    [Fact]
    public void ExportSheetToCsv_DifferentSheets_Differ()
    {
        var doc = CreateWorkbook();
        var salesCsv = doc.ExportSheetToCsv("Sales");
        var hrCsv = doc.ExportSheetToCsv("HR");
        Assert.NotEqual(salesCsv, hrCsv);
    }

    [Fact]
    public void ExportSheetToCsv_SaveLoad_Consistent()
    {
        var doc = CreateWorkbook();
        var before = doc.ExportSheetToCsv("Sales").Length;
        var path = TempFile("export_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.ExportSheetToCsv("Sales").Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_MergeSheets_GetCellCount_ExportSheetToCsv_SaveToFile_Pipeline()
    {
        // Build 4-sheet workbook
        var doc = FodsDocument.CreateEmpty();

        // Q1 sheet — 4 rows × 4 cols = 16 cells
        doc.SetCellValue("Q1", 0, 0, "Product"); doc.SetCellValue("Q1", 0, 1, "Region"); doc.SetCellValue("Q1", 0, 2, "Units"); doc.SetCellValue("Q1", 0, 3, "Revenue");
        doc.SetCellValue("Q1", 1, 0, "Alpha"); doc.SetCellValue("Q1", 1, 1, "North"); doc.SetCellValue("Q1", 1, 2, "120"); doc.SetCellValue("Q1", 1, 3, "84000");
        doc.SetCellValue("Q1", 2, 0, "Beta"); doc.SetCellValue("Q1", 2, 1, "South"); doc.SetCellValue("Q1", 2, 2, "95"); doc.SetCellValue("Q1", 2, 3, "66500");
        doc.SetCellValue("Q1", 3, 0, "Gamma"); doc.SetCellValue("Q1", 3, 1, "East"); doc.SetCellValue("Q1", 3, 2, "80"); doc.SetCellValue("Q1", 3, 3, "56000");

        // Q2 sheet — 4 rows × 4 cols = 16 cells
        doc.AddSheet("Q2");
        doc.SetCellValue("Q2", 0, 0, "Product"); doc.SetCellValue("Q2", 0, 1, "Region"); doc.SetCellValue("Q2", 0, 2, "Units"); doc.SetCellValue("Q2", 0, 3, "Revenue");
        doc.SetCellValue("Q2", 1, 0, "Alpha"); doc.SetCellValue("Q2", 1, 1, "North"); doc.SetCellValue("Q2", 1, 2, "140"); doc.SetCellValue("Q2", 1, 3, "98000");
        doc.SetCellValue("Q2", 2, 0, "Beta"); doc.SetCellValue("Q2", 2, 1, "South"); doc.SetCellValue("Q2", 2, 2, "110"); doc.SetCellValue("Q2", 2, 3, "77000");
        doc.SetCellValue("Q2", 3, 0, "Gamma"); doc.SetCellValue("Q2", 3, 1, "East"); doc.SetCellValue("Q2", 3, 2, "92"); doc.SetCellValue("Q2", 3, 3, "64400");

        // H1Summary — empty for merge target
        doc.AddSheet("H1Summary");

        // GetCellCount per sheet
        Assert.Equal(16, doc.GetCellCount("Q1"));
        Assert.Equal(16, doc.GetCellCount("Q2"));
        Assert.Equal(0, doc.GetCellCount("H1Summary"));

        // ExportSheetToCsv for Q1
        var q1Csv = doc.ExportSheetToCsv("Q1");
        Assert.NotNull(q1Csv);
        Assert.NotEmpty(q1Csv);
        Assert.Contains(",", q1Csv);
        Assert.True(q1Csv.Contains("Product") || q1Csv.Contains("Alpha"));

        // ExportSheetToCsv for Q2
        var q2Csv = doc.ExportSheetToCsv("Q2");
        Assert.NotNull(q2Csv);
        Assert.NotEmpty(q2Csv);
        Assert.NotEqual(q1Csv, q2Csv); // different data

        // Consistent
        Assert.Equal(q1Csv.Length, doc.ExportSheetToCsv("Q1").Length);

        // MergeSheets Q1 into H1Summary
        doc.MergeSheets("Q1", "H1Summary");
        Assert.True(doc.GetCellCount("H1Summary") > 0);

        // MergeSheets Q2 into H1Summary
        doc.MergeSheets("Q2", "H1Summary");
        Assert.True(doc.GetCellCount("H1Summary") >= 16); // at least the Q1 data

        // H1Summary CSV contains merged data
        var h1Csv = doc.ExportSheetToCsv("H1Summary");
        Assert.NotNull(h1Csv);
        Assert.NotEmpty(h1Csv);

        // GetCellCount after SetCellValue
        var countBefore = doc.GetCellCount("Q1");
        doc.SetCellValue("Q1", 4, 0, "Delta");
        doc.SetCellValue("Q1", 4, 1, "West");
        doc.SetCellValue("Q1", 4, 2, "75");
        doc.SetCellValue("Q1", 4, 3, "52500");
        Assert.Equal(countBefore + 4, doc.GetCellCount("Q1"));

        // ExportSheetToCsv after SetCellValue grows
        var q1CsvAfter = doc.ExportSheetToCsv("Q1");
        Assert.True(q1CsvAfter.Length > q1Csv.Length);

        // GetCellCount consistent
        Assert.Equal(doc.GetCellCount("Q1"), doc.GetCellCount("Q1"));

        // SaveToFile
        var path = TempFile("dogfood_workbook.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(doc.GetCellCount("Q1"), loaded.GetCellCount("Q1"));
        Assert.Equal(doc.GetCellCount("Q2"), loaded.GetCellCount("Q2"));

        // ExportSheetToCsv on loaded
        var loadedQ1Csv = loaded.ExportSheetToCsv("Q1");
        Assert.Equal(q1CsvAfter.Length, loadedQ1Csv.Length);

        // MergeSheets on loaded
        loaded.MergeSheets("Q1", "Q2");
        Assert.True(loaded.GetCellCount("Q2") >= 16);

        // Final save
        var path2 = TempFile("dogfood_workbook_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(loaded.GetCellCount("Q1"), loaded2.GetCellCount("Q1"));
    }
}
