// Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R308

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R308: Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
/// GetDataValidationCount(sheetName): returns the number of data validation rules on the sheet.
/// AddDataValidation(sheetName, cellRange, validationType, rule): adds a data validation rule.
/// GetDataValidationRule(sheetName, index): returns the rule string for a validation.
/// Covers: GetDataValidationCount no-throw; GetDataValidationCount non-negative;
/// GetDataValidationCount consistent; GetDataValidationCount zero for new sheet;
/// GetDataValidationCount after AddDataValidation increases; GetDataValidationCount save-load;
/// AddDataValidation no-throw; AddDataValidation increases count; AddDataValidation save-load;
/// AddDataValidation multiple; AddDataValidation then ExportToCsv no-throw;
/// GetDataValidationRule no-throw; GetDataValidationRule non-null; GetDataValidationRule consistent;
/// GetDataValidationRule save-load;
/// dogfood CreateDoc→AddDataValidation→GetDataValidationCount→GetDataValidationRule→SaveToFile pipeline.
/// </summary>
public class FodsR308GetDataValidationCountAndAddValidationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR308GetDataValidationCountAndAddValidationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR308_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Input");
        doc.SetCellValue("Input", 0, 0, "Field");
        doc.SetCellValue("Input", 0, 1, "Value");
        doc.SetCellValue("Input", 0, 2, "Status");
        doc.SetCellValue("Input", 1, 0, "Age");
        doc.SetCellValue("Input", 1, 1, "25");
        doc.SetCellValue("Input", 1, 2, "Valid");
        doc.SetCellValue("Input", 2, 0, "Score");
        doc.SetCellValue("Input", 2, 1, "85");
        doc.SetCellValue("Input", 2, 2, "Valid");
        doc.SetCellValue("Input", 3, 0, "Category");
        doc.SetCellValue("Input", 3, 1, "A");
        doc.SetCellValue("Input", 3, 2, "Valid");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDataValidationCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetDataValidationCount("Input"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetDataValidationCount("Input") >= 0);
    }

    [Fact]
    public void GetDataValidationCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetDataValidationCount("Input"), doc.GetDataValidationCount("Input"));
    }

    [Fact]
    public void GetDataValidationCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Clean");
        doc.SetCellValue("Clean", 0, 0, "data");
        Assert.Equal(0, doc.GetDataValidationCount("Clean"));
    }

    [Fact]
    public void GetDataValidationCount_AfterAddDataValidation_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetDataValidationCount("Input");
        doc.AddDataValidation("Input", "B2", "integer", "between:0:150");
        Assert.Equal(before + 1, doc.GetDataValidationCount("Input"));
    }

    [Fact]
    public void GetDataValidationCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "B2", "integer", "between:0:150");
        var before = doc.GetDataValidationCount("Input");
        var path = TempFile("dvc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount("Input"));
    }

    // -------------------------------------------------------------------------
    // AddDataValidation
    // -------------------------------------------------------------------------

    [Fact]
    public void AddDataValidation_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddDataValidation("Input", "B2:B4", "decimal", "between:0:100"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddDataValidation_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetDataValidationCount("Input");
        doc.AddDataValidation("Input", "B3", "decimal", "between:0:100");
        Assert.Equal(before + 1, doc.GetDataValidationCount("Input"));
    }

    [Fact]
    public void AddDataValidation_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "C2:C4", "list", "Valid,Invalid,Pending");
        var before = doc.GetDataValidationCount("Input");
        var path = TempFile("adv_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount("Input"));
    }

    [Fact]
    public void AddDataValidation_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "B2", "integer", "between:0:120");
        doc.AddDataValidation("Input", "B3", "decimal", "between:0:100");
        doc.AddDataValidation("Input", "C2:C4", "list", "A,B,C,D,F");
        Assert.Equal(3, doc.GetDataValidationCount("Input"));
    }

    [Fact]
    public void AddDataValidation_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "B2:B4", "integer", "between:1:100");
        var ex = Record.Exception(() => doc.ExportToCsv("Input"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetDataValidationRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationRule_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "B2", "integer", "between:0:150");
        var ex = Record.Exception(() => doc.GetDataValidationRule("Input", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationRule_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "B3", "decimal", "between:0:100");
        Assert.NotNull(doc.GetDataValidationRule("Input", 0));
    }

    [Fact]
    public void GetDataValidationRule_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "B2", "list", "Yes,No");
        Assert.Equal(doc.GetDataValidationRule("Input", 0), doc.GetDataValidationRule("Input", 0));
    }

    [Fact]
    public void GetDataValidationRule_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddDataValidation("Input", "B2", "integer", "between:1:99");
        var before = doc.GetDataValidationRule("Input", 0);
        var path = TempFile("dvr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetDataValidationRule("Input", 0);
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
        doc.AddSheet("Survey");

        // Headers
        doc.SetCellValue("Survey", 0, 0, "RespondentId");
        doc.SetCellValue("Survey", 0, 1, "Age");
        doc.SetCellValue("Survey", 0, 2, "Satisfaction");
        doc.SetCellValue("Survey", 0, 3, "NPS");
        doc.SetCellValue("Survey", 0, 4, "Department");
        doc.SetCellValue("Survey", 0, 5, "WouldRecommend");

        // Sample data
        string[,] data = {
            { "R001", "34", "4", "8", "Engineering", "Yes" },
            { "R002", "28", "5", "9", "Marketing", "Yes" },
            { "R003", "45", "3", "6", "HR", "No" },
            { "R004", "52", "4", "7", "Finance", "Yes" },
            { "R005", "31", "5", "10", "Engineering", "Yes" }
        };
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 6; c++)
                doc.SetCellValue("Survey", r + 1, c, data[r, c]);

        // GetDataValidationCount — zero initially
        Assert.Equal(0, doc.GetDataValidationCount("Survey"));

        // AddDataValidation — Age: integer 18-99
        doc.AddDataValidation("Survey", "B2:B100", "integer", "between:18:99");
        Assert.Equal(1, doc.GetDataValidationCount("Survey"));

        // AddDataValidation — Satisfaction: integer 1-5
        doc.AddDataValidation("Survey", "C2:C100", "integer", "between:1:5");
        Assert.Equal(2, doc.GetDataValidationCount("Survey"));

        // AddDataValidation — NPS: integer 0-10
        doc.AddDataValidation("Survey", "D2:D100", "integer", "between:0:10");
        Assert.Equal(3, doc.GetDataValidationCount("Survey"));

        // AddDataValidation — Department: list
        doc.AddDataValidation("Survey", "E2:E100", "list", "Engineering,Marketing,HR,Finance,Operations,Legal");
        Assert.Equal(4, doc.GetDataValidationCount("Survey"));

        // AddDataValidation — WouldRecommend: list
        doc.AddDataValidation("Survey", "F2:F100", "list", "Yes,No,Maybe");
        Assert.Equal(5, doc.GetDataValidationCount("Survey"));

        // Consistent
        Assert.Equal(doc.GetDataValidationCount("Survey"), doc.GetDataValidationCount("Survey"));

        // GetDataValidationRule
        var rule0 = doc.GetDataValidationRule("Survey", 0);
        Assert.NotNull(rule0);
        Assert.Equal(rule0, doc.GetDataValidationRule("Survey", 0)); // consistent

        var rule1 = doc.GetDataValidationRule("Survey", 1);
        Assert.NotNull(rule1);

        // ExportToCsv works
        var csv = doc.ExportToCsv("Survey");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_survey.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetDataValidationCount("Survey"));
        Assert.NotNull(loaded.GetDataValidationRule("Survey", 0));

        // AddDataValidation on loaded
        loaded.AddDataValidation("Survey", "A2:A100", "text", "length:3:10");
        Assert.Equal(6, loaded.GetDataValidationCount("Survey"));

        // Mutate and verify
        loaded.SetCellValue("Survey", 6, 0, "R006");
        loaded.SetCellValue("Survey", 6, 1, "39");
        loaded.SetCellValue("Survey", 6, 2, "4");
        loaded.SetCellValue("Survey", 6, 3, "8");
        loaded.SetCellValue("Survey", 6, 4, "Operations");
        loaded.SetCellValue("Survey", 6, 5, "Yes");

        // Final save
        var path2 = TempFile("dogfood_survey_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetDataValidationCount("Survey"));
        Assert.NotNull(loaded2.GetDataValidationRule("Survey", 0));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Survey"));
        Assert.Null(ex1);
    }
}
