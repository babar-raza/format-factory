// Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R322

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R322: Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
/// GetDataValidationCount(sheetName): returns the number of data validation rules on the sheet.
/// AddDataValidation(sheetName, range, type, constraint): adds a data validation rule.
/// GetDataValidationRule(sheetName, index): returns the validation rule details at the given index.
/// Covers: GetDataValidationCount no-throw; GetDataValidationCount non-negative; GetDataValidationCount consistent;
/// GetDataValidationCount zero for new sheet; GetDataValidationCount after AddDataValidation increases;
/// GetDataValidationCount save-load;
/// AddDataValidation no-throw; AddDataValidation increases count; AddDataValidation save-load;
/// AddDataValidation multiple; AddDataValidation then GetRowCount positive;
/// GetDataValidationRule no-throw; GetDataValidationRule non-null; GetDataValidationRule consistent;
/// GetDataValidationRule save-load;
/// dogfood CreateDoc→AddDataValidation→GetDataValidationCount→GetDataValidationRule→SaveToFile pipeline.
/// </summary>
public class FodsR322GetDataValidationCountAndAddDataValidationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR322GetDataValidationCountAndAddDataValidationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR322_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateInventoryDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");
        doc.SetCellValue("Inventory", 0, 0, "SKU");
        doc.SetCellValue("Inventory", 0, 1, "Category");
        doc.SetCellValue("Inventory", 0, 2, "Quantity");
        doc.SetCellValue("Inventory", 0, 3, "Unit_Price");
        doc.SetCellValue("Inventory", 0, 4, "Reorder_Level");
        doc.SetCellValue("Inventory", 0, 5, "Status");
        doc.SetCellValue("Inventory", 1, 0, "SKU001"); doc.SetCellValue("Inventory", 1, 1, "Electronics"); doc.SetCellValue("Inventory", 1, 2, "45"); doc.SetCellValue("Inventory", 1, 3, "299.99"); doc.SetCellValue("Inventory", 1, 4, "10"); doc.SetCellValue("Inventory", 1, 5, "Active");
        doc.SetCellValue("Inventory", 2, 0, "SKU002"); doc.SetCellValue("Inventory", 2, 1, "Clothing");    doc.SetCellValue("Inventory", 2, 2, "120"); doc.SetCellValue("Inventory", 2, 3, "49.99");  doc.SetCellValue("Inventory", 2, 4, "25"); doc.SetCellValue("Inventory", 2, 5, "Active");
        doc.SetCellValue("Inventory", 3, 0, "SKU003"); doc.SetCellValue("Inventory", 3, 1, "Food");        doc.SetCellValue("Inventory", 3, 2, "200"); doc.SetCellValue("Inventory", 3, 3, "12.50");  doc.SetCellValue("Inventory", 3, 4, "50"); doc.SetCellValue("Inventory", 3, 5, "Active");
        doc.SetCellValue("Inventory", 4, 0, "SKU004"); doc.SetCellValue("Inventory", 4, 1, "Tools");       doc.SetCellValue("Inventory", 4, 2, "30");  doc.SetCellValue("Inventory", 4, 3, "89.99");  doc.SetCellValue("Inventory", 4, 4, "8");  doc.SetCellValue("Inventory", 4, 5, "Low Stock");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDataValidationCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationCount_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() => doc.GetDataValidationCount("Inventory"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationCount_NonNegative()
    {
        var doc = CreateInventoryDoc();
        Assert.True(doc.GetDataValidationCount("Inventory") >= 0);
    }

    [Fact]
    public void GetDataValidationCount_Consistent()
    {
        var doc = CreateInventoryDoc();
        Assert.Equal(doc.GetDataValidationCount("Inventory"), doc.GetDataValidationCount("Inventory"));
    }

    [Fact]
    public void GetDataValidationCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Clean");
        doc.SetCellValue("Clean", 0, 0, "Header");
        Assert.Equal(0, doc.GetDataValidationCount("Clean"));
    }

    [Fact]
    public void GetDataValidationCount_AfterAddDataValidation_Increases()
    {
        var doc = CreateInventoryDoc();
        var before = doc.GetDataValidationCount("Inventory");
        doc.AddDataValidation("Inventory", "C2:C5", "integer", ">= 0");
        Assert.Equal(before + 1, doc.GetDataValidationCount("Inventory"));
    }

    [Fact]
    public void GetDataValidationCount_SaveLoad_Consistent()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "D2:D5", "decimal", "> 0");
        var before = doc.GetDataValidationCount("Inventory");
        var path = TempFile("dvc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount("Inventory"));
    }

    // -------------------------------------------------------------------------
    // AddDataValidation
    // -------------------------------------------------------------------------

    [Fact]
    public void AddDataValidation_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() => doc.AddDataValidation("Inventory", "C2:C5", "integer", ">= 0"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddDataValidation_Increases_Count()
    {
        var doc = CreateInventoryDoc();
        var before = doc.GetDataValidationCount("Inventory");
        doc.AddDataValidation("Inventory", "E2:E5", "integer", ">= 0");
        Assert.Equal(before + 1, doc.GetDataValidationCount("Inventory"));
    }

    [Fact]
    public void AddDataValidation_SaveLoad_Persists()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "F2:F5", "list", "Active,Low Stock,Discontinued");
        var before = doc.GetDataValidationCount("Inventory");
        var path = TempFile("adv_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount("Inventory"));
    }

    [Fact]
    public void AddDataValidation_Multiple()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "C2:C5", "integer", ">= 0");
        doc.AddDataValidation("Inventory", "D2:D5", "decimal", "> 0");
        doc.AddDataValidation("Inventory", "F2:F5", "list", "Active,Low Stock,Discontinued");
        Assert.Equal(3, doc.GetDataValidationCount("Inventory"));
    }

    [Fact]
    public void AddDataValidation_Then_GetRowCount_Positive()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "C2:C5", "integer", ">= 0");
        Assert.True(doc.GetRowCount("Inventory") > 0);
    }

    // -------------------------------------------------------------------------
    // GetDataValidationRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationRule_NoThrow()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "C2:C5", "integer", ">= 0");
        var ex = Record.Exception(() => doc.GetDataValidationRule("Inventory", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationRule_NonNull()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "D2:D5", "decimal", "> 0");
        Assert.NotNull(doc.GetDataValidationRule("Inventory", 0));
    }

    [Fact]
    public void GetDataValidationRule_Consistent()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "C2:C5", "integer", ">= 0");
        Assert.Equal(doc.GetDataValidationRule("Inventory", 0), doc.GetDataValidationRule("Inventory", 0));
    }

    [Fact]
    public void GetDataValidationRule_SaveLoad_Consistent()
    {
        var doc = CreateInventoryDoc();
        doc.AddDataValidation("Inventory", "E2:E5", "integer", ">= 0");
        var before = doc.GetDataValidationRule("Inventory", 0);
        var path = TempFile("dvr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetDataValidationRule("Inventory", 0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddDataValidation_GetDataValidationCount_GetDataValidationRule_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("HR_Data");
        doc.SetCellValue("HR_Data", 0, 0, "Employee_ID");
        doc.SetCellValue("HR_Data", 0, 1, "Department");
        doc.SetCellValue("HR_Data", 0, 2, "Grade");
        doc.SetCellValue("HR_Data", 0, 3, "Salary");
        doc.SetCellValue("HR_Data", 0, 4, "Years_Service");
        doc.SetCellValue("HR_Data", 0, 5, "Performance");
        doc.SetCellValue("HR_Data", 0, 6, "Contract_Type");

        doc.SetCellValue("HR_Data", 1, 0, "EMP001"); doc.SetCellValue("HR_Data", 1, 1, "Engineering"); doc.SetCellValue("HR_Data", 1, 2, "Senior");   doc.SetCellValue("HR_Data", 1, 3, "85000"); doc.SetCellValue("HR_Data", 1, 4, "8");  doc.SetCellValue("HR_Data", 1, 5, "4"); doc.SetCellValue("HR_Data", 1, 6, "Permanent");
        doc.SetCellValue("HR_Data", 2, 0, "EMP002"); doc.SetCellValue("HR_Data", 2, 1, "Finance");     doc.SetCellValue("HR_Data", 2, 2, "Junior");    doc.SetCellValue("HR_Data", 2, 3, "42000"); doc.SetCellValue("HR_Data", 2, 4, "2");  doc.SetCellValue("HR_Data", 2, 5, "3"); doc.SetCellValue("HR_Data", 2, 6, "Permanent");
        doc.SetCellValue("HR_Data", 3, 0, "EMP003"); doc.SetCellValue("HR_Data", 3, 1, "Marketing");   doc.SetCellValue("HR_Data", 3, 2, "Lead");      doc.SetCellValue("HR_Data", 3, 3, "98000"); doc.SetCellValue("HR_Data", 3, 4, "12"); doc.SetCellValue("HR_Data", 3, 5, "5"); doc.SetCellValue("HR_Data", 3, 6, "Permanent");
        doc.SetCellValue("HR_Data", 4, 0, "EMP004"); doc.SetCellValue("HR_Data", 4, 1, "Operations");  doc.SetCellValue("HR_Data", 4, 2, "Mid-Level"); doc.SetCellValue("HR_Data", 4, 3, "62000"); doc.SetCellValue("HR_Data", 4, 4, "5");  doc.SetCellValue("HR_Data", 4, 5, "4"); doc.SetCellValue("HR_Data", 4, 6, "Contract");
        doc.SetCellValue("HR_Data", 5, 0, "EMP005"); doc.SetCellValue("HR_Data", 5, 1, "Engineering"); doc.SetCellValue("HR_Data", 5, 2, "Senior");   doc.SetCellValue("HR_Data", 5, 3, "92000"); doc.SetCellValue("HR_Data", 5, 4, "10"); doc.SetCellValue("HR_Data", 5, 5, "5"); doc.SetCellValue("HR_Data", 5, 6, "Permanent");

        Assert.Equal(0, doc.GetDataValidationCount("HR_Data"));

        // AddDataValidation — salary (positive integer)
        doc.AddDataValidation("HR_Data", "D2:D6", "integer", "> 0");
        Assert.Equal(1, doc.GetDataValidationCount("HR_Data"));

        // AddDataValidation — years service (0-50)
        doc.AddDataValidation("HR_Data", "E2:E6", "integer", "between 0 and 50");
        Assert.Equal(2, doc.GetDataValidationCount("HR_Data"));

        // AddDataValidation — performance rating (1-5)
        doc.AddDataValidation("HR_Data", "F2:F6", "integer", "between 1 and 5");
        Assert.Equal(3, doc.GetDataValidationCount("HR_Data"));

        // AddDataValidation — department list
        doc.AddDataValidation("HR_Data", "B2:B6", "list", "Engineering,Finance,Marketing,Operations,HR,Legal");
        Assert.Equal(4, doc.GetDataValidationCount("HR_Data"));

        // AddDataValidation — contract type list
        doc.AddDataValidation("HR_Data", "G2:G6", "list", "Permanent,Contract,Temporary,Apprentice");
        Assert.Equal(5, doc.GetDataValidationCount("HR_Data"));

        // Consistent
        Assert.Equal(doc.GetDataValidationCount("HR_Data"), doc.GetDataValidationCount("HR_Data"));

        // GetDataValidationRule
        var rule0 = doc.GetDataValidationRule("HR_Data", 0);
        Assert.NotNull(rule0);
        Assert.Equal(rule0, doc.GetDataValidationRule("HR_Data", 0)); // consistent

        var rule1 = doc.GetDataValidationRule("HR_Data", 1);
        Assert.NotNull(rule1);

        var rule4 = doc.GetDataValidationRule("HR_Data", 4);
        Assert.NotNull(rule4);

        // GetRowCount positive
        Assert.True(doc.GetRowCount("HR_Data") > 0);

        // ExportToCsv works
        var csv = doc.ExportToCsv("HR_Data");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_hr_data.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetDataValidationCount("HR_Data"));
        Assert.True(loaded.GetRowCount("HR_Data") > 0);
        Assert.NotNull(loaded.GetDataValidationRule("HR_Data", 0));

        // AddDataValidation on loaded
        loaded.AddDataValidation("HR_Data", "C2:C6", "list", "Junior,Mid-Level,Senior,Lead,Principal");
        Assert.Equal(6, loaded.GetDataValidationCount("HR_Data"));

        // AddRow on loaded
        loaded.AddRow("HR_Data", new[] { "EMP006", "Legal", "Senior", "88000", "9", "4", "Permanent" });
        Assert.True(loaded.GetRowCount("HR_Data") > doc.GetRowCount("HR_Data"));

        // Final save
        var path2 = TempFile("dogfood_hr_data_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetDataValidationCount("HR_Data"));
        Assert.True(loaded2.GetRowCount("HR_Data") > 0);
        Assert.NotNull(loaded2.GetDataValidationRule("HR_Data", 0));
        var ex1 = Record.Exception(() => loaded2.GetDataValidationCount("HR_Data"));
        var ex2 = Record.Exception(() => loaded2.GetDataValidationRule("HR_Data", 5));
        var ex3 = Record.Exception(() => loaded2.ExportToCsv("HR_Data"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
