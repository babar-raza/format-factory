// Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetProtectionStatus deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R295

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R295: Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetProtectionStatus deeper.
/// GetConditionalFormatCount(sheetName): returns the number of conditional format rules on the sheet.
/// AddConditionalFormat(sheetName, cellRange, condition, formatStyle): adds a conditional format rule.
/// GetProtectionStatus(sheetName): returns whether the sheet is protected.
/// Covers: GetConditionalFormatCount no-throw; GetConditionalFormatCount non-negative; GetConditionalFormatCount consistent;
/// GetConditionalFormatCount zero for new sheet; GetConditionalFormatCount after AddConditionalFormat increases;
/// GetConditionalFormatCount save-load;
/// AddConditionalFormat no-throw; AddConditionalFormat increases count; AddConditionalFormat save-load;
/// AddConditionalFormat multiple; AddConditionalFormat then ExportToCsv no-throw;
/// GetProtectionStatus no-throw; GetProtectionStatus bool; GetProtectionStatus consistent;
/// GetProtectionStatus save-load;
/// dogfood CreateDoc→AddConditionalFormat→GetConditionalFormatCount→GetProtectionStatus→SaveToFile pipeline.
/// </summary>
public class FodsR295GetConditionalFormatsAndProtectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR295GetConditionalFormatsAndProtectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR295_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateRichDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Region");
        doc.SetCellValue("Sales", 0, 1, "Q1");
        doc.SetCellValue("Sales", 0, 2, "Q2");
        doc.SetCellValue("Sales", 0, 3, "Q3");
        doc.SetCellValue("Sales", 1, 0, "North");
        doc.SetCellValue("Sales", 1, 1, "125000");
        doc.SetCellValue("Sales", 1, 2, "148000");
        doc.SetCellValue("Sales", 1, 3, "162000");
        doc.SetCellValue("Sales", 2, 0, "South");
        doc.SetCellValue("Sales", 2, 1, "98000");
        doc.SetCellValue("Sales", 2, 2, "115000");
        doc.SetCellValue("Sales", 2, 3, "131000");
        doc.SetCellValue("Sales", 3, 0, "East");
        doc.SetCellValue("Sales", 3, 1, "87000");
        doc.SetCellValue("Sales", 3, 2, "94000");
        doc.SetCellValue("Sales", 3, 3, "108000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetConditionalFormatCount("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetConditionalFormatCount("Sales") >= 0);
    }

    [Fact]
    public void GetConditionalFormatCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetConditionalFormatCount("Sales"), doc.GetConditionalFormatCount("Sales"));
    }

    [Fact]
    public void GetConditionalFormatCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        doc.SetCellValue("Fresh", 0, 0, "NoRules");
        Assert.Equal(0, doc.GetConditionalFormatCount("Fresh"));
    }

    [Fact]
    public void GetConditionalFormatCount_AfterAddConditionalFormat_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetConditionalFormatCount("Sales");
        doc.AddConditionalFormat("Sales", "B2:D4", "cell-value > 100000", "bold");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount("Sales"));
    }

    [Fact]
    public void GetConditionalFormatCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("Sales", "B2:B4", "cell-value < 100000", "red");
        var before = doc.GetConditionalFormatCount("Sales");
        var path = TempFile("cfc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount("Sales"));
    }

    // -------------------------------------------------------------------------
    // AddConditionalFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void AddConditionalFormat_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddConditionalFormat("Sales", "B2:D4", "cell-value > 120000", "green"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetConditionalFormatCount("Sales");
        doc.AddConditionalFormat("Sales", "C2:C4", "cell-value >= 115000", "highlight");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount("Sales"));
    }

    [Fact]
    public void AddConditionalFormat_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("Sales", "D2:D4", "cell-value > 130000", "bold-green");
        var before = doc.GetConditionalFormatCount("Sales");
        var path = TempFile("acf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount("Sales"));
    }

    [Fact]
    public void AddConditionalFormat_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("Sales", "B2:B4", "cell-value > 100000", "green");
        doc.AddConditionalFormat("Sales", "C2:C4", "cell-value > 110000", "blue");
        doc.AddConditionalFormat("Sales", "D2:D4", "cell-value > 120000", "bold");
        Assert.Equal(3, doc.GetConditionalFormatCount("Sales"));
    }

    [Fact]
    public void AddConditionalFormat_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("Sales", "B2:D4", "cell-value != 0", "normal");
        var ex = Record.Exception(() => doc.ExportToCsv("Sales"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetProtectionStatus
    // -------------------------------------------------------------------------

    [Fact]
    public void GetProtectionStatus_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetProtectionStatus("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetProtectionStatus_ReturnsBool()
    {
        var doc = CreateRichDoc();
        var result = doc.GetProtectionStatus("Sales");
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void GetProtectionStatus_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetProtectionStatus("Sales"), doc.GetProtectionStatus("Sales"));
    }

    [Fact]
    public void GetProtectionStatus_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetProtectionStatus("Sales");
        var path = TempFile("gps_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetProtectionStatus("Sales"));
    }

    [Fact]
    public void GetProtectionStatus_False_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Unprotected");
        doc.SetCellValue("Unprotected", 0, 0, "data");
        // A newly created sheet should not be protected by default
        Assert.False(doc.GetProtectionStatus("Unprotected"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddConditionalFormat_GetConditionalFormatCount_GetProtectionStatus_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Budget");

        // Headers
        doc.SetCellValue("Budget", 0, 0, "Department");
        doc.SetCellValue("Budget", 0, 1, "Allocated");
        doc.SetCellValue("Budget", 0, 2, "Spent");
        doc.SetCellValue("Budget", 0, 3, "Remaining");
        doc.SetCellValue("Budget", 0, 4, "Variance");

        // Data rows
        string[,] data = {
            { "Engineering", "500000", "423000", "77000", "77000" },
            { "Marketing", "200000", "218000", "-18000", "-18000" },
            { "Operations", "300000", "287000", "13000", "13000" },
            { "Research", "400000", "391000", "9000", "9000" },
            { "HR", "150000", "142000", "8000", "8000" }
        };
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                doc.SetCellValue("Budget", r + 1, c, data[r, c]);

        // GetConditionalFormatCount — zero initially
        Assert.Equal(0, doc.GetConditionalFormatCount("Budget"));

        // AddConditionalFormat — highlight over-budget
        doc.AddConditionalFormat("Budget", "D2:D6", "cell-value < 0", "red-background");
        Assert.Equal(1, doc.GetConditionalFormatCount("Budget"));

        // AddConditionalFormat — highlight under-spend
        doc.AddConditionalFormat("Budget", "C2:C6", "cell-value < B2", "green-background");
        Assert.Equal(2, doc.GetConditionalFormatCount("Budget"));

        // AddConditionalFormat — highlight allocated
        doc.AddConditionalFormat("Budget", "B2:B6", "cell-value > 350000", "bold");
        Assert.Equal(3, doc.GetConditionalFormatCount("Budget"));

        // AddConditionalFormat — variance alert
        doc.AddConditionalFormat("Budget", "E2:E6", "cell-value < -10000", "red-bold");
        Assert.Equal(4, doc.GetConditionalFormatCount("Budget"));

        // Consistent
        Assert.Equal(doc.GetConditionalFormatCount("Budget"), doc.GetConditionalFormatCount("Budget"));

        // GetProtectionStatus
        var isProtected = doc.GetProtectionStatus("Budget");
        Assert.Equal(isProtected, doc.GetProtectionStatus("Budget")); // consistent
        Assert.False(isProtected); // new sheet is unprotected

        // ExportToCsv works
        var csv = doc.ExportToCsv("Budget");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue cross-check
        Assert.Equal("Engineering", doc.GetCellValue("Budget", 1, 0));
        Assert.Equal("500000", doc.GetCellValue("Budget", 1, 1));

        // SaveToFile
        var path = TempFile("dogfood_budget.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetConditionalFormatCount("Budget"));
        Assert.Equal(isProtected, loaded.GetProtectionStatus("Budget"));

        // AddConditionalFormat on loaded
        loaded.AddConditionalFormat("Budget", "A2:A6", "cell-value = \"HR\"", "italic");
        Assert.Equal(5, loaded.GetConditionalFormatCount("Budget"));

        // Mutate and verify
        loaded.SetCellValue("Budget", 6, 0, "Legal");
        loaded.SetCellValue("Budget", 6, 1, "100000");
        loaded.SetCellValue("Budget", 6, 2, "95000");
        loaded.SetCellValue("Budget", 6, 3, "5000");
        loaded.SetCellValue("Budget", 6, 4, "5000");

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("Budget");
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);

        // Final save
        var path2 = TempFile("dogfood_budget_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetConditionalFormatCount("Budget"));
        Assert.False(loaded2.GetProtectionStatus("Budget"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Budget"));
        Assert.Null(ex1);
    }
}
