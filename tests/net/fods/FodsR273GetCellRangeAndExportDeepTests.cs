// Tests for FodsDocument.GetCellRange, SetCellRange, ExportSheetToJson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R273

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R273: Tests for FodsDocument.GetCellRange, SetCellRange, ExportSheetToJson deeper.
/// GetCellRange(sheetName, startRow, startCol, endRow, endCol): returns 2D array of cell values.
/// SetCellRange(sheetName, startRow, startCol, values[][]): bulk-sets cells.
/// ExportSheetToJson(sheetName): exports the sheet as a JSON string.
/// Covers: GetCellRange non-null; GetCellRange no-throw; GetCellRange row count correct;
/// GetCellRange col count correct; GetCellRange values match; GetCellRange consistent;
/// GetCellRange single cell; GetCellRange save-load;
/// SetCellRange no-throw; SetCellRange values readable; SetCellRange updates GetCellValue;
/// SetCellRange then save-load; SetCellRange larger than existing;
/// ExportSheetToJson non-null; ExportSheetToJson non-empty; ExportSheetToJson has braces;
/// ExportSheetToJson has content; ExportSheetToJson consistent; ExportSheetToJson no-throw;
/// ExportSheetToJson after SetCellValue changes; ExportSheetToJson save-load;
/// dogfood CreateDoc→SetCellRange→GetCellRange→ExportSheetToJson→SaveToFile pipeline.
/// </summary>
public class FodsR273GetCellRangeAndExportDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR273GetCellRangeAndExportDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR273_" + Guid.NewGuid().ToString("N"));
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
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        // 3x4 grid (rows 0-2, cols 0-3)
        doc.SetCellValue("Data", 0, 0, "Alpha"); doc.SetCellValue("Data", 0, 1, "Beta"); doc.SetCellValue("Data", 0, 2, "Gamma"); doc.SetCellValue("Data", 0, 3, "Delta");
        doc.SetCellValue("Data", 1, 0, "10");    doc.SetCellValue("Data", 1, 1, "20");   doc.SetCellValue("Data", 1, 2, "30");    doc.SetCellValue("Data", 1, 3, "40");
        doc.SetCellValue("Data", 2, 0, "100");   doc.SetCellValue("Data", 2, 1, "200");  doc.SetCellValue("Data", 2, 2, "300");   doc.SetCellValue("Data", 2, 3, "400");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellRange_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetCellRange("Data", 0, 0, 2, 3));
    }

    [Fact]
    public void GetCellRange_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.GetCellRange("Data", 0, 0, 2, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellRange_RowCount_Correct()
    {
        var doc = CreateDataDoc();
        var range = doc.GetCellRange("Data", 0, 0, 2, 3);
        Assert.Equal(3, range.Length);
    }

    [Fact]
    public void GetCellRange_ColCount_Correct()
    {
        var doc = CreateDataDoc();
        var range = doc.GetCellRange("Data", 0, 0, 2, 3);
        Assert.Equal(4, range[0].Length);
    }

    [Fact]
    public void GetCellRange_Values_Match()
    {
        var doc = CreateDataDoc();
        var range = doc.GetCellRange("Data", 0, 0, 2, 3);
        Assert.Equal("Alpha", range[0][0]);
        Assert.Equal("20", range[1][1]);
        Assert.Equal("400", range[2][3]);
    }

    [Fact]
    public void GetCellRange_Consistent()
    {
        var doc = CreateDataDoc();
        var r1 = doc.GetCellRange("Data", 0, 0, 2, 3);
        var r2 = doc.GetCellRange("Data", 0, 0, 2, 3);
        Assert.Equal(r1[0][0], r2[0][0]);
        Assert.Equal(r1.Length, r2.Length);
    }

    [Fact]
    public void GetCellRange_SingleCell()
    {
        var doc = CreateDataDoc();
        var range = doc.GetCellRange("Data", 1, 2, 1, 2);
        Assert.Equal(1, range.Length);
        Assert.Equal(1, range[0].Length);
        Assert.Equal("30", range[0][0]);
    }

    [Fact]
    public void GetCellRange_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        var before = doc.GetCellRange("Data", 0, 0, 2, 3)[1][1];
        var path = TempFile("range_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetCellRange("Data", 0, 0, 2, 3)[1][1];
        Assert.Equal(before, after);
    }

    // -------------------------------------------------------------------------
    // SetCellRange
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellRange_NoThrow()
    {
        var doc = CreateDataDoc();
        var values = new[] { new[] { "X1", "X2" }, new[] { "Y1", "Y2" } };
        var ex = Record.Exception(() => doc.SetCellRange("Data", 0, 0, values));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellRange_ValuesReadable()
    {
        var doc = CreateDataDoc();
        var values = new[] { new[] { "NewA", "NewB" }, new[] { "NewC", "NewD" } };
        doc.SetCellRange("Data", 0, 0, values);
        Assert.Equal("NewA", doc.GetCellValue("Data", 0, 0));
        Assert.Equal("NewD", doc.GetCellValue("Data", 1, 1));
    }

    [Fact]
    public void SetCellRange_Updates_GetCellValue()
    {
        var doc = CreateDataDoc();
        var values = new[] { new[] { "Updated" } };
        doc.SetCellRange("Data", 2, 2, values);
        Assert.Equal("Updated", doc.GetCellValue("Data", 2, 2));
    }

    [Fact]
    public void SetCellRange_Then_SaveLoad()
    {
        var doc = CreateDataDoc();
        var values = new[] { new[] { "SL_A", "SL_B" }, new[] { "SL_C", "SL_D" } };
        doc.SetCellRange("Data", 0, 0, values);
        var path = TempFile("setrange_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("SL_A", loaded.GetCellValue("Data", 0, 0));
        Assert.Equal("SL_D", loaded.GetCellValue("Data", 1, 1));
    }

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.ExportSheetToJson("Data"));
    }

    [Fact]
    public void ExportSheetToJson_NonEmpty()
    {
        var doc = CreateDataDoc();
        Assert.NotEmpty(doc.ExportSheetToJson("Data"));
    }

    [Fact]
    public void ExportSheetToJson_HasBraces()
    {
        var doc = CreateDataDoc();
        var json = doc.ExportSheetToJson("Data");
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportSheetToJson_HasContent()
    {
        var doc = CreateDataDoc();
        var json = doc.ExportSheetToJson("Data");
        Assert.True(json.Contains("Alpha") || json.Contains("10") || json.Contains("Data"));
    }

    [Fact]
    public void ExportSheetToJson_Consistent()
    {
        var doc = CreateDataDoc();
        var j1 = doc.ExportSheetToJson("Data");
        var j2 = doc.ExportSheetToJson("Data");
        Assert.Equal(j1.Length, j2.Length);
    }

    [Fact]
    public void ExportSheetToJson_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.ExportSheetToJson("Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportSheetToJson_AfterSetCellValue_Changes()
    {
        var doc = CreateDataDoc();
        var before = doc.ExportSheetToJson("Data");
        doc.SetCellValue("Data", 0, 0, "UniqueXYZ999");
        var after = doc.ExportSheetToJson("Data");
        Assert.NotEqual(before, after);
    }

    [Fact]
    public void ExportSheetToJson_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        var before = doc.ExportSheetToJson("Data").Length;
        var path = TempFile("json_export_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportSheetToJson("Data").Length - before) <= 20);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetCellRange_GetCellRange_ExportSheetToJson_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Report");

        // Set headers individually
        doc.SetCellValue("Report", 0, 0, "Department");
        doc.SetCellValue("Report", 0, 1, "Q1");
        doc.SetCellValue("Report", 0, 2, "Q2");
        doc.SetCellValue("Report", 0, 3, "Q3");
        doc.SetCellValue("Report", 0, 4, "Q4");

        // SetCellRange for data rows
        var dataBlock = new[]
        {
            new[] { "Engineering", "150000", "162000", "175000", "188000" },
            new[] { "Marketing",   "85000",  "92000",  "98000",  "105000" },
            new[] { "Finance",     "72000",  "76000",  "80000",  "84000" },
            new[] { "Operations",  "95000",  "99000",  "103000", "108000" },
        };
        doc.SetCellRange("Report", 1, 0, dataBlock);

        // Verify via GetCellValue
        Assert.Equal("Engineering", doc.GetCellValue("Report", 1, 0));
        Assert.Equal("162000", doc.GetCellValue("Report", 1, 2));
        Assert.Equal("Operations", doc.GetCellValue("Report", 4, 0));
        Assert.Equal("108000", doc.GetCellValue("Report", 4, 4));

        // GetCellRange — full data block
        var range = doc.GetCellRange("Report", 1, 0, 4, 4);
        Assert.NotNull(range);
        Assert.Equal(4, range.Length);
        Assert.Equal(5, range[0].Length);
        Assert.Equal("Engineering", range[0][0]);
        Assert.Equal("188000", range[0][4]);
        Assert.Equal("Finance", range[2][0]);

        // GetCellRange — single row
        var row2 = doc.GetCellRange("Report", 2, 0, 2, 4);
        Assert.Equal(1, row2.Length);
        Assert.Equal("Marketing", row2[0][0]);

        // GetCellRange — single column
        var col0 = doc.GetCellRange("Report", 1, 0, 4, 0);
        Assert.Equal(4, col0.Length);
        Assert.Equal(1, col0[0].Length);

        // Consistent
        var r1 = doc.GetCellRange("Report", 1, 0, 4, 4);
        var r2 = doc.GetCellRange("Report", 1, 0, 4, 4);
        Assert.Equal(r1[0][0], r2[0][0]);

        // ExportSheetToJson
        var json = doc.ExportSheetToJson("Report");
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.True(json.Contains("Engineering") || json.Contains("Report") || json.Contains("150000"));

        // Consistent
        Assert.Equal(json.Length, doc.ExportSheetToJson("Report").Length);

        // SetCellRange update
        var updateBlock = new[] { new[] { "EngineeringDept", "155000", "167000", "180000", "195000" } };
        doc.SetCellRange("Report", 1, 0, updateBlock);
        var updatedJson = doc.ExportSheetToJson("Report");
        Assert.NotEqual(json, updatedJson);

        // SaveToFile
        var path = TempFile("dogfood_report.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("EngineeringDept", loaded.GetCellValue("Report", 1, 0));
        Assert.Equal("Operations", loaded.GetCellValue("Report", 4, 0));

        // GetCellRange on loaded
        var loadedRange = loaded.GetCellRange("Report", 1, 0, 4, 4);
        Assert.Equal(4, loadedRange.Length);
        Assert.Equal("EngineeringDept", loadedRange[0][0]);

        // ExportSheetToJson on loaded
        var loadedJson = loaded.ExportSheetToJson("Report");
        Assert.NotNull(loadedJson);
        Assert.NotEmpty(loadedJson);

        // SetCellRange on loaded — add summary row
        var summaryBlock = new[] { new[] { "TOTAL", "507000", "534000", "561000", "587000" } };
        loaded.SetCellRange("Report", 5, 0, summaryBlock);
        Assert.Equal("TOTAL", loaded.GetCellValue("Report", 5, 0));

        // Final save
        var path2 = TempFile("dogfood_report_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal("TOTAL", loaded2.GetCellValue("Report", 5, 0));
        var finalRange = loaded2.GetCellRange("Report", 1, 0, 5, 4);
        Assert.Equal(5, finalRange.Length);
        Assert.NotNull(loaded2.ExportSheetToJson("Report"));
    }
}
