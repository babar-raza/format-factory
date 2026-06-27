// Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R337

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R337: Tests for FodsDocument.GetDataValidationCount, AddDataValidation, GetDataValidationRule deeper.
/// GetDataValidationCount(sheet): returns the number of data validation rules in the given sheet.
/// AddDataValidation(sheet, range, type, rule, errorMsg): adds a data validation rule.
/// GetDataValidationRule(sheet, index): returns the validation rule at the given index.
/// Covers: GetDataValidationCount no-throw; GetDataValidationCount non-negative; GetDataValidationCount consistent;
/// GetDataValidationCount zero for new sheet; GetDataValidationCount after AddDataValidation increases;
/// GetDataValidationCount save-load;
/// AddDataValidation no-throw; AddDataValidation increases count; AddDataValidation save-load;
/// AddDataValidation multiple; AddDataValidation then ExportToHtml no-throw;
/// AddDataValidation then ExportToCsv no-throw; AddDataValidation then GetCharCount positive;
/// GetDataValidationRule no-throw; GetDataValidationRule non-null; GetDataValidationRule consistent;
/// GetDataValidationRule save-load;
/// dogfood CreateDoc→AddDataValidation→GetDataValidationCount→GetDataValidationRule→SaveToFile pipeline.
/// </summary>
public class FodsR337GetDataValidationCountAndAddDataValidationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR337GetDataValidationCountAndAddDataValidationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR337_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateFormSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("DataEntry");
        doc.SetCellValue("DataEntry", 0, 0, "Field");
        doc.SetCellValue("DataEntry", 0, 1, "Value");
        doc.SetCellValue("DataEntry", 0, 2, "Status");
        string[] fields = { "Age", "Score", "Category", "Date", "Amount", "Priority", "Rating", "Status", "Quantity", "Percentage", "Code", "Level" };
        for (int r = 0; r < fields.Length; r++)
        {
            doc.SetCellValue("DataEntry", r + 1, 0, fields[r]);
            doc.SetCellValue("DataEntry", r + 1, 2, "Pending");
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDataValidationCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationCount_NoThrow()
    {
        var doc = CreateFormSheet();
        var ex = Record.Exception(() => doc.GetDataValidationCount("DataEntry"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationCount_NonNegative()
    {
        var doc = CreateFormSheet();
        Assert.True(doc.GetDataValidationCount("DataEntry") >= 0);
    }

    [Fact]
    public void GetDataValidationCount_Consistent()
    {
        var doc = CreateFormSheet();
        Assert.Equal(doc.GetDataValidationCount("DataEntry"), doc.GetDataValidationCount("DataEntry"));
    }

    [Fact]
    public void GetDataValidationCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        Assert.Equal(0, doc.GetDataValidationCount("Fresh"));
    }

    [Fact]
    public void GetDataValidationCount_AfterAddDataValidation_Increases()
    {
        var doc = CreateFormSheet();
        var before = doc.GetDataValidationCount("DataEntry");
        doc.AddDataValidation("DataEntry", "B2", "integer", "between 0 and 120", "Age must be 0-120");
        Assert.Equal(before + 1, doc.GetDataValidationCount("DataEntry"));
    }

    [Fact]
    public void GetDataValidationCount_SaveLoad_Consistent()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B3", "decimal", "between 0 and 100", "Score must be 0-100");
        var before = doc.GetDataValidationCount("DataEntry");
        var path = TempFile("dvc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount("DataEntry"));
    }

    // -------------------------------------------------------------------------
    // AddDataValidation
    // -------------------------------------------------------------------------

    [Fact]
    public void AddDataValidation_NoThrow()
    {
        var doc = CreateFormSheet();
        var ex = Record.Exception(() => doc.AddDataValidation("DataEntry", "B4", "list", "Low,Medium,High", "Choose priority"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddDataValidation_Increases_Count()
    {
        var doc = CreateFormSheet();
        var before = doc.GetDataValidationCount("DataEntry");
        doc.AddDataValidation("DataEntry", "B5", "date", "after 2020-01-01", "Date must be after 2020");
        Assert.Equal(before + 1, doc.GetDataValidationCount("DataEntry"));
    }

    [Fact]
    public void AddDataValidation_SaveLoad_Persists()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B6", "decimal", "greaterThan 0", "Amount must be positive");
        var before = doc.GetDataValidationCount("DataEntry");
        var path = TempFile("adv_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDataValidationCount("DataEntry"));
    }

    [Fact]
    public void AddDataValidation_Multiple()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B2", "integer", "between 1 and 5", "Rating 1-5");
        doc.AddDataValidation("DataEntry", "B3", "decimal", "between 0 and 100", "Percentage 0-100");
        doc.AddDataValidation("DataEntry", "B4", "list", "A,B,C,D", "Grade category");
        Assert.Equal(3, doc.GetDataValidationCount("DataEntry"));
    }

    [Fact]
    public void AddDataValidation_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B2", "integer", "between 0 and 10", "Rating 0-10");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddDataValidation_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B3", "list", "Pass,Fail", "Pass or Fail");
        var path = TempFile("dv_csv.csv");
        var ex = Record.Exception(() => doc.ExportToCsv("DataEntry", path));
        Assert.Null(ex);
    }

    [Fact]
    public void AddDataValidation_Then_GetCharCount_Positive()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B2", "integer", "greaterThan 0", "Positive integer");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetDataValidationRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataValidationRule_NoThrow()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B2", "integer", "between 1 and 100", "Enter 1-100");
        var ex = Record.Exception(() => doc.GetDataValidationRule("DataEntry", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDataValidationRule_NonNull()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B3", "list", "Yes,No", "Yes or No");
        Assert.NotNull(doc.GetDataValidationRule("DataEntry", 0));
    }

    [Fact]
    public void GetDataValidationRule_Consistent()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B4", "decimal", "between 0 and 1", "Probability 0-1");
        Assert.Equal(doc.GetDataValidationRule("DataEntry", 0), doc.GetDataValidationRule("DataEntry", 0));
    }

    [Fact]
    public void GetDataValidationRule_SaveLoad_Consistent()
    {
        var doc = CreateFormSheet();
        doc.AddDataValidation("DataEntry", "B2", "integer", "between 1 and 10", "Score 1-10");
        var path = TempFile("dvr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetDataValidationRule("DataEntry", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddDataValidation_GetDataValidationCount_GetDataValidationRule_SaveToFile_Pipeline()
    {
        // Clinical trial data management — patient intake form validation template
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("PatientIntake");

        // Headers
        string[] headers = { "Patient_ID", "Age", "Weight_kg", "Height_cm", "BMI", "Systolic_BP", "Diastolic_BP", "Heart_Rate", "Blood_Glucose", "HbA1c", "Stage", "Protocol" };
        for (int c = 0; c < headers.Length; c++)
            doc.SetCellValue("PatientIntake", 0, c, headers[c]);

        // 12 patient rows (placeholder)
        for (int r = 1; r <= 12; r++)
        {
            doc.SetCellValue("PatientIntake", r, 0, $"PAT-{r:D4}");
            doc.SetCellValue("PatientIntake", r, 10, "Screening");
            doc.SetCellValue("PatientIntake", r, 11, "Protocol-A");
        }

        // Initial validation count — zero
        Assert.Equal(0, doc.GetDataValidationCount("PatientIntake"));

        // AddDataValidation — age (18-85)
        doc.AddDataValidation("PatientIntake", "B2:B13", "integer", "between 18 and 85", "Age must be 18-85 years");
        Assert.Equal(1, doc.GetDataValidationCount("PatientIntake"));
        Assert.NotNull(doc.GetDataValidationRule("PatientIntake", 0));

        // AddDataValidation — weight (30-200 kg)
        doc.AddDataValidation("PatientIntake", "C2:C13", "decimal", "between 30 and 200", "Weight must be 30-200 kg");
        Assert.Equal(2, doc.GetDataValidationCount("PatientIntake"));

        // AddDataValidation — systolic BP (80-200 mmHg)
        doc.AddDataValidation("PatientIntake", "F2:F13", "integer", "between 80 and 200", "Systolic BP 80-200 mmHg");
        Assert.Equal(3, doc.GetDataValidationCount("PatientIntake"));

        // AddDataValidation — HbA1c (4.0-15.0%)
        doc.AddDataValidation("PatientIntake", "J2:J13", "decimal", "between 4 and 15", "HbA1c 4.0-15.0%");
        Assert.Equal(4, doc.GetDataValidationCount("PatientIntake"));

        // AddDataValidation — Stage (dropdown list)
        doc.AddDataValidation("PatientIntake", "K2:K13", "list", "Screening,Baseline,Week4,Week12,Week24,Completion,Dropout", "Select visit stage");
        Assert.Equal(5, doc.GetDataValidationCount("PatientIntake"));

        // AddDataValidation — Protocol (dropdown list)
        doc.AddDataValidation("PatientIntake", "L2:L13", "list", "Protocol-A,Protocol-B,Protocol-C", "Select treatment protocol");
        Assert.Equal(6, doc.GetDataValidationCount("PatientIntake"));

        // Consistent
        Assert.Equal(doc.GetDataValidationCount("PatientIntake"), doc.GetDataValidationCount("PatientIntake"));
        Assert.Equal(doc.GetDataValidationRule("PatientIntake", 0), doc.GetDataValidationRule("PatientIntake", 0));

        // Check rules non-null
        Assert.NotNull(doc.GetDataValidationRule("PatientIntake", 4)); // Stage dropdown
        Assert.NotNull(doc.GetDataValidationRule("PatientIntake", 5)); // Protocol dropdown

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCharCount positive
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_clinical_form.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetDataValidationCount("PatientIntake"));
        Assert.NotNull(loaded.GetDataValidationRule("PatientIntake", 0));
        Assert.NotNull(loaded.GetDataValidationRule("PatientIntake", 4));

        // AddDataValidation on loaded
        loaded.AddDataValidation("PatientIntake", "D2:D13", "integer", "between 100 and 220", "Height 100-220 cm");
        Assert.Equal(7, loaded.GetDataValidationCount("PatientIntake"));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // SetCellValue on loaded — add patient data
        loaded.SetCellValue("PatientIntake", 1, 1, "42");
        loaded.SetCellValue("PatientIntake", 1, 2, "78.5");

        // Final save
        var path2 = TempFile("dogfood_clinical_form_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetDataValidationCount("PatientIntake"));
        Assert.NotNull(loaded2.GetDataValidationRule("PatientIntake", 0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetDataValidationCount("PatientIntake"));
        var ex3 = Record.Exception(() => loaded2.AddDataValidation("PatientIntake", "E2:E13", "decimal", "between 15 and 50", "BMI 15-50"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
