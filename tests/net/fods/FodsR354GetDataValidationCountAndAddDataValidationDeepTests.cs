// Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R354

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R354: Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
/// GetDataValidationCount(): returns the number of data validation rules in the workbook.
/// AddDataValidation(sheetName, rangeAddress, validationType, formula): adds a data validation rule.
/// GetDataValidationRule(index): returns the formula or expression of the validation rule at the given index.
/// Covers: GetDataValidationCount no-throw; GetDataValidationCount non-negative;
/// GetDataValidationCount consistent; GetDataValidationCount zero for new workbook;
/// GetDataValidationCount after AddDataValidation increases; GetDataValidationCount save-load;
/// AddDataValidation no-throw; AddDataValidation increases count; AddDataValidation save-load;
/// AddDataValidation multiple; AddDataValidation then ExportToCsv no-throw;
/// AddDataValidation then GetCellValue no-throw;
/// GetDataValidationRule no-throw; GetDataValidationRule non-null; GetDataValidationRule consistent;
/// GetDataValidationRule save-load;
/// dogfood CreateDoc→AddDataValidation→GetDataValidationCount→GetDataValidationRule pipeline.
/// </summary>
public class FodsR354GetDataValidationCountAndAddDataValidationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR354GetDataValidationCountAndAddDataValidationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR354_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSurveyWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Survey");
        doc.SetCellValue("Survey", 0, 0, "Respondent_ID");
        doc.SetCellValue("Survey", 0, 1, "Age");
        doc.SetCellValue("Survey", 0, 2, "Satisfaction_1_5");
        doc.SetCellValue("Survey", 0, 3, "NPS_0_10");
        doc.SetCellValue("Survey", 0, 4, "Region");
        for (int i = 1; i <= 10; i++)
        {
            doc.SetCellValue("Survey", i, 0, $"R{i:D4}");
            doc.SetCellValue("Survey", i, 1, (18 + i * 3).ToString());
            doc.SetCellValue("Survey", i, 2, ((i % 5) + 1).ToString());
            doc.SetCellValue("Survey", i, 3, (i % 11).ToString());
            doc.SetCellValue("Survey", i, 4, (i % 4 == 0 ? "North" : i % 4 == 1 ? "South" : i % 4 == 2 ? "East" : "West"));
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDataValidationCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationCount_NoThrow()
    {
        var doc = CreateSurveyWorkbook();
        var ex = Record.Exception(() => doc.GetDataValidationCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationCount_NonNegative()
    {
        var doc = CreateSurveyWorkbook();
        Assert.True(doc.GetDataValidationCount() >= 0);
    }

    [Fact]
    public void GetDataValidationCount_Consistent()
    {
        var doc = CreateSurveyWorkbook();
        Assert.Equal(doc.GetDataValidationCount(), doc.GetDataValidationCount());
    }

    [Fact]
    public void GetDataValidationCount_Zero_ForNewWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Data");
        Assert.Equal(0, doc.GetDataValidationCount());
    }

    [Fact]
    public void GetDataValidationCount_AfterAdd_Increases()
    {
        var doc = CreateSurveyWorkbook();
        var before = doc.GetDataValidationCount();
        doc.AddDataValidation("Survey", "B2:B11", "between", "18,99");
        Assert.Equal(before + 1, doc.GetDataValidationCount());
    }

    [Fact]
    public void GetDataValidationCount_SaveLoad_Consistent()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "C2:C11", "list", "1,2,3,4,5");
        var before = doc.GetDataValidationCount();
        var path = TempFile("dvc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount());
    }

    // -------------------------------------------------------------------------
    // AddDataValidation
    // -------------------------------------------------------------------------

    [Fact]
    public void AddDataValidation_NoThrow()
    {
        var doc = CreateSurveyWorkbook();
        var ex = Record.Exception(() => doc.AddDataValidation("Survey", "D2:D11", "between", "0,10"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddDataValidation_Increases_Count()
    {
        var doc = CreateSurveyWorkbook();
        var before = doc.GetDataValidationCount();
        doc.AddDataValidation("Survey", "C2:C11", "between", "1,5");
        Assert.Equal(before + 1, doc.GetDataValidationCount());
    }

    [Fact]
    public void AddDataValidation_SaveLoad_Persists()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "E2:E11", "list", "North,South,East,West");
        var before = doc.GetDataValidationCount();
        var path = TempFile("adv_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount());
    }

    [Fact]
    public void AddDataValidation_Multiple()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "B2:B11", "between", "18,99");
        doc.AddDataValidation("Survey", "C2:C11", "between", "1,5");
        doc.AddDataValidation("Survey", "D2:D11", "between", "0,10");
        Assert.Equal(3, doc.GetDataValidationCount());
    }

    [Fact]
    public void AddDataValidation_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "C2:C11", "list", "1,2,3,4,5");
        var ex = Record.Exception(() => doc.ExportToCsv("Survey"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddDataValidation_Then_GetCellValue_NoThrow()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "D2:D11", "between", "0,10");
        var ex = Record.Exception(() => doc.GetCellValue("Survey", 1, 3));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetDataValidationRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationRule_NoThrow()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "B2:B11", "between", "18,99");
        var ex = Record.Exception(() => doc.GetDataValidationRule(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationRule_NonNull()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "C2:C11", "list", "1,2,3,4,5");
        Assert.NotNull(doc.GetDataValidationRule(0));
    }

    [Fact]
    public void GetDataValidationRule_Consistent()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "D2:D11", "between", "0,10");
        Assert.Equal(doc.GetDataValidationRule(0), doc.GetDataValidationRule(0));
    }

    [Fact]
    public void GetDataValidationRule_SaveLoad_Consistent()
    {
        var doc = CreateSurveyWorkbook();
        doc.AddDataValidation("Survey", "E2:E11", "list", "North,South,East,West");
        var path = TempFile("dvr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetDataValidationRule(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddDataValidation_GetDataValidationCount_GetDataValidationRule_Pipeline()
    {
        // HR data entry workbook — employee performance review with validated inputs
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("PerformanceReview");
        doc.SetCellValue("PerformanceReview", 0, 0, "Employee_ID");
        doc.SetCellValue("PerformanceReview", 0, 1, "Department");
        doc.SetCellValue("PerformanceReview", 0, 2, "KPI_Score_1_5");
        doc.SetCellValue("PerformanceReview", 0, 3, "Behaviours_Score_1_5");
        doc.SetCellValue("PerformanceReview", 0, 4, "Overall_Rating");
        doc.SetCellValue("PerformanceReview", 0, 5, "Salary_Band");
        doc.SetCellValue("PerformanceReview", 0, 6, "Review_Year");

        string[] departments = { "Engineering", "Finance", "Marketing", "Operations", "Legal", "HR" };
        string[] ratings = { "Exceeds", "Meets", "Partially_Meets", "Does_Not_Meet" };
        var rng = new Random(20241101);
        for (int i = 1; i <= 12; i++)
        {
            doc.SetCellValue("PerformanceReview", i, 0, $"EMP{i:D5}");
            doc.SetCellValue("PerformanceReview", i, 1, departments[(i - 1) % 6]);
            doc.SetCellValue("PerformanceReview", i, 2, (rng.Next(1, 6)).ToString());
            doc.SetCellValue("PerformanceReview", i, 3, (rng.Next(1, 6)).ToString());
            doc.SetCellValue("PerformanceReview", i, 4, ratings[rng.Next(4)]);
            doc.SetCellValue("PerformanceReview", i, 5, $"B{rng.Next(1, 8)}");
            doc.SetCellValue("PerformanceReview", i, 6, "2024");
        }

        doc.AddSheet("LookupData");
        doc.SetCellValue("LookupData", 0, 0, "Dept"); doc.SetCellValue("LookupData", 0, 1, "Rating");
        for (int i = 0; i < departments.Length; i++)
            doc.SetCellValue("LookupData", i + 1, 0, departments[i]);
        for (int i = 0; i < ratings.Length; i++)
            doc.SetCellValue("LookupData", i + 1, 1, ratings[i]);

        Assert.Equal(0, doc.GetDataValidationCount());

        // AddDataValidation — KPI score 1-5
        doc.AddDataValidation("PerformanceReview", "C2:C13", "between", "1,5");
        Assert.Equal(1, doc.GetDataValidationCount());

        // Behaviours score 1-5
        doc.AddDataValidation("PerformanceReview", "D2:D13", "between", "1,5");
        Assert.Equal(2, doc.GetDataValidationCount());

        // Overall rating dropdown
        doc.AddDataValidation("PerformanceReview", "E2:E13", "list", "Exceeds,Meets,Partially_Meets,Does_Not_Meet");
        Assert.Equal(3, doc.GetDataValidationCount());

        // Salary band dropdown
        doc.AddDataValidation("PerformanceReview", "F2:F13", "list", "B1,B2,B3,B4,B5,B6,B7");
        Assert.Equal(4, doc.GetDataValidationCount());

        // Review year numeric
        doc.AddDataValidation("PerformanceReview", "G2:G13", "between", "2020,2030");
        Assert.Equal(5, doc.GetDataValidationCount());

        // Consistent
        Assert.Equal(doc.GetDataValidationCount(), doc.GetDataValidationCount());

        // GetDataValidationRule
        var rule0 = doc.GetDataValidationRule(0);
        Assert.NotNull(rule0);
        Assert.Equal(rule0, doc.GetDataValidationRule(0)); // consistent

        var rule2 = doc.GetDataValidationRule(2);
        Assert.NotNull(rule2);

        var rule4 = doc.GetDataValidationRule(4);
        Assert.NotNull(rule4);

        // ExportToCsv
        var ex = Record.Exception(() => doc.ExportToCsv("PerformanceReview"));
        Assert.Null(ex);

        // GetCellValue after validation
        Assert.NotNull(doc.GetCellValue("PerformanceReview", 1, 0));

        // SaveToFile
        var path = TempFile("dogfood_performance_review.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetDataValidationCount());
        Assert.NotNull(loaded.GetDataValidationRule(0));
        Assert.NotNull(loaded.GetDataValidationRule(4));
        Assert.NotNull(loaded.GetCellValue("PerformanceReview", 1, 0));

        // AddDataValidation on loaded
        loaded.AddDataValidation("PerformanceReview", "B2:B13", "list", "Engineering,Finance,Marketing,Operations,Legal,HR");
        Assert.Equal(6, loaded.GetDataValidationCount());

        // Final save
        var path2 = TempFile("dogfood_performance_review_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetDataValidationCount());
        Assert.NotNull(loaded2.GetDataValidationRule(0));
        var ex2 = Record.Exception(() => loaded2.ExportToCsv("PerformanceReview"));
        var ex3 = Record.Exception(() => loaded2.AddDataValidation("PerformanceReview", "C2:C13", "between", "1,5"));
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
