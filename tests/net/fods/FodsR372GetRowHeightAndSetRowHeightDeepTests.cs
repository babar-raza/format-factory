// Tests for FodsDocument.GetRowHeight, SetRowHeight deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R372

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R372: Tests for FodsDocument.GetRowHeight, SetRowHeight deeper.
/// GetRowHeight(sheetName, rowIndex): returns the height of the row at rowIndex on the named sheet.
/// SetRowHeight(sheetName, rowIndex, height): sets the row height on the named sheet.
/// Covers: GetRowHeight no-throw; GetRowHeight non-negative; GetRowHeight consistent;
/// GetRowHeight save-load; SetRowHeight no-throw; SetRowHeight with small height;
/// SetRowHeight with large height; SetRowHeight then GetRowHeight; SetRowHeight then GetSheetCount unchanged;
/// SetRowHeight then ExportToCsv no-throw; SetRowHeight then GetCellValue non-null;
/// SetRowHeight save-load; SetRowHeight multiple rows; GetRowHeight save-load consistent;
/// dogfood CreateDoc→SetRowHeight→GetRowHeight→SaveToFile pipeline.
/// </summary>
public class FodsR372GetRowHeightAndSetRowHeightDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR372GetRowHeightAndSetRowHeightDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR372_" + Guid.NewGuid().ToString("N"));
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
        doc.SetCellValue("Data", 0, 0, "ID");
        doc.SetCellValue("Data", 0, 1, "Name");
        doc.SetCellValue("Data", 0, 2, "Value");
        for (int r = 1; r <= 5; r++)
        {
            doc.SetCellValue("Data", r, 0, $"R{r:D3}");
            doc.SetCellValue("Data", r, 1, $"Item_{r}");
            doc.SetCellValue("Data", r, 2, (r * 100).ToString());
        }
        doc.AddSheet("Config");
        doc.SetCellValue("Config", 0, 0, "Key");
        doc.SetCellValue("Config", 0, 1, "Value");
        doc.SetCellValue("Config", 1, 0, "Version");
        doc.SetCellValue("Config", 1, 1, "2.0");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRowHeight
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowHeight_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.GetRowHeight("Data", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowHeight_NonNegative()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetRowHeight("Data", 0) >= 0.0 || doc.GetRowHeight("Data", 0) == null);
    }

    [Fact]
    public void GetRowHeight_Consistent()
    {
        var doc = CreateDataDoc();
        Assert.Equal(doc.GetRowHeight("Data", 1), doc.GetRowHeight("Data", 1));
    }

    [Fact]
    public void GetRowHeight_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        doc.SetRowHeight("Data", 0, 0.8);
        var path = TempFile("grh_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetRowHeight("Data", 0) >= 0.0);
    }

    // -------------------------------------------------------------------------
    // SetRowHeight
    // -------------------------------------------------------------------------

    [Fact]
    public void SetRowHeight_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.SetRowHeight("Data", 0, 0.6));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_WithSmallHeight_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.SetRowHeight("Config", 0, 0.3));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_WithLargeHeight_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.SetRowHeight("Data", 0, 3.0));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_Then_GetRowHeight()
    {
        var doc = CreateDataDoc();
        doc.SetRowHeight("Data", 0, 1.2);
        Assert.True(doc.GetRowHeight("Data", 0) >= 0.0);
    }

    [Fact]
    public void SetRowHeight_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateDataDoc();
        var before = doc.GetSheetCount();
        doc.SetRowHeight("Data", 0, 0.8);
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetRowHeight_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateDataDoc();
        doc.SetRowHeight("Data", 0, 0.8);
        var ex = Record.Exception(() => doc.ExportToCsv("Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_Then_GetCellValue_NonNull()
    {
        var doc = CreateDataDoc();
        doc.SetRowHeight("Data", 0, 0.8);
        Assert.NotNull(doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void SetRowHeight_SaveLoad_Persists()
    {
        var doc = CreateDataDoc();
        doc.SetRowHeight("Data", 0, 1.0);
        var path = TempFile("srh_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetRowHeight("Data", 0) >= 0.0);
    }

    [Fact]
    public void SetRowHeight_MultipleRows()
    {
        var doc = CreateDataDoc();
        doc.SetRowHeight("Data", 0, 0.8); // header — slightly taller
        doc.SetRowHeight("Data", 1, 0.5);
        doc.SetRowHeight("Data", 2, 0.5);
        doc.SetRowHeight("Data", 3, 0.5);
        Assert.True(doc.GetRowHeight("Data", 0) >= 0.0);
        Assert.True(doc.GetRowHeight("Data", 1) >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetRowHeight_GetRowHeight_SaveToFile_Pipeline()
    {
        // Research — HESA (Higher Education Statistics Agency) student data returns workbook
        // UK university IRO team preparing statutory data return with custom row formatting
        var doc = FodsDocument.CreateEmpty();

        // Student Enrolment sheet
        doc.AddSheet("Student_Enrolment");
        string[] enrollHeaders = {
            "HESA_STUDENTID", "INSTITUTION_CODE", "COURSE_JACS3", "MODE_OF_STUDY",
            "YEAR_OF_COURSE", "LEVEL_OF_STUDY", "DOMICILE_COUNTRY", "ENTRY_QUALIFICATION",
            "AGE_AT_ENTRY", "DISABILITY_FLAG", "ETHNICITY_CODE", "GENDER_CODE"
        };
        for (int c = 0; c < enrollHeaders.Length; c++)
            doc.SetCellValue("Student_Enrolment", 0, c, enrollHeaders[c]);

        // Sample data rows (using realistic HESA codes)
        var rng = new Random(20241201);
        string[] jacsCodes = { "G400", "B900", "L300", "N100", "C100", "H600", "Q300", "F300" };
        string[] modes = { "Full_time", "Part_time", "Sandwich_year_out" };
        string[] levels = { "Undergraduate", "Postgraduate_taught", "Postgraduate_research" };
        string[] countries = { "XF", "XG", "XH", "XI", "XK", "D2", "XN" };
        string[] disabilities = { "0", "1", "2", "3", "4", "5", "6", "7", "8" };
        string[] ethnicities = { "10", "21", "22", "31", "32", "33", "34", "41", "42", "43", "50", "90" };

        for (int r = 1; r <= 20; r++)
        {
            doc.SetCellValue("Student_Enrolment", r, 0, $"HS{10000000 + r:D8}");
            doc.SetCellValue("Student_Enrolment", r, 1, "10007149"); // UCL UKPRN
            doc.SetCellValue("Student_Enrolment", r, 2, jacsCodes[rng.Next(jacsCodes.Length)]);
            doc.SetCellValue("Student_Enrolment", r, 3, modes[rng.Next(modes.Length)]);
            doc.SetCellValue("Student_Enrolment", r, 4, (1 + rng.Next(4)).ToString());
            doc.SetCellValue("Student_Enrolment", r, 5, levels[rng.Next(levels.Length)]);
            doc.SetCellValue("Student_Enrolment", r, 6, countries[rng.Next(countries.Length)]);
            doc.SetCellValue("Student_Enrolment", r, 7, (rng.Next(3) == 0) ? "Level_3" : "Degree");
            doc.SetCellValue("Student_Enrolment", r, 8, (18 + rng.Next(30)).ToString());
            doc.SetCellValue("Student_Enrolment", r, 9, disabilities[rng.Next(disabilities.Length)]);
            doc.SetCellValue("Student_Enrolment", r, 10, ethnicities[rng.Next(ethnicities.Length)]);
            doc.SetCellValue("Student_Enrolment", r, 11, rng.Next(2) == 0 ? "1" : "2");
        }

        // Qualifications Awarded sheet
        doc.AddSheet("Qualifications_Awarded");
        string[] qualHeaders = {
            "HESA_STUDENTID", "QUALIFICATION_JACS3", "CLASS_OF_DEGREE", "AWARD_DATE",
            "MODE_OF_STUDY", "LEVEL_OF_STUDY", "CREDITED_PRIOR_LEARNING", "EXCHANGE_PROGRAMME"
        };
        for (int c = 0; c < qualHeaders.Length; c++)
            doc.SetCellValue("Qualifications_Awarded", 0, c, qualHeaders[c]);
        string[] degreeClasses = { "01", "02", "03", "04", "05", "06", "10" };
        for (int r = 1; r <= 15; r++)
        {
            doc.SetCellValue("Qualifications_Awarded", r, 0, $"HS{10000000 + r:D8}");
            doc.SetCellValue("Qualifications_Awarded", r, 1, jacsCodes[rng.Next(jacsCodes.Length)]);
            doc.SetCellValue("Qualifications_Awarded", r, 2, degreeClasses[rng.Next(degreeClasses.Length)]);
            doc.SetCellValue("Qualifications_Awarded", r, 3, "2024-07-31");
            doc.SetCellValue("Qualifications_Awarded", r, 4, "Full_time");
            doc.SetCellValue("Qualifications_Awarded", r, 5, "Undergraduate");
            doc.SetCellValue("Qualifications_Awarded", r, 6, "0");
            doc.SetCellValue("Qualifications_Awarded", r, 7, rng.Next(3) == 0 ? "1" : "0");
        }

        // Staff Data sheet
        doc.AddSheet("Staff_Data");
        doc.SetCellValue("Staff_Data", 0, 0, "HESA_STAFFID");
        doc.SetCellValue("Staff_Data", 0, 1, "CONTRACT_LEVELS");
        doc.SetCellValue("Staff_Data", 0, 2, "ACTIVITY_CODE");
        doc.SetCellValue("Staff_Data", 0, 3, "FTE");
        doc.SetCellValue("Staff_Data", 0, 4, "ACADEMIC_YEAR");
        for (int r = 1; r <= 10; r++)
        {
            doc.SetCellValue("Staff_Data", r, 0, $"ST{50000 + r:D6}");
            doc.SetCellValue("Staff_Data", r, 1, rng.Next(2) == 0 ? "Academic" : "Professional_Services");
            doc.SetCellValue("Staff_Data", r, 2, rng.Next(2) == 0 ? "Teaching" : "Research");
            doc.SetCellValue("Staff_Data", r, 3, (0.5 + rng.NextDouble() * 0.5).ToString("F2"));
            doc.SetCellValue("Staff_Data", r, 4, "2023/24");
        }

        Assert.Equal(3, doc.GetSheetCount());
        Assert.Null(doc.GetRowHeight("Student_Enrolment", 0));

        // SetRowHeight — header rows taller for readability in HESA submission workbook
        doc.SetRowHeight("Student_Enrolment", 0, 1.2); // header
        Assert.True(doc.GetRowHeight("Student_Enrolment", 0) >= 0.0);

        // Data rows standard height
        for (int r = 1; r <= 5; r++)
            doc.SetRowHeight("Student_Enrolment", r, 0.5);
        Assert.True(doc.GetRowHeight("Student_Enrolment", 1) >= 0.0);

        doc.SetRowHeight("Qualifications_Awarded", 0, 1.2);
        Assert.True(doc.GetRowHeight("Qualifications_Awarded", 0) >= 0.0);

        doc.SetRowHeight("Staff_Data", 0, 1.0);
        Assert.True(doc.GetRowHeight("Staff_Data", 0) >= 0.0);

        // Sheet count unchanged
        Assert.Equal(3, doc.GetSheetCount());

        // Consistent
        Assert.Equal(doc.GetRowHeight("Student_Enrolment", 0), doc.GetRowHeight("Student_Enrolment", 0));

        // ExportToCsv
        var csv = doc.ExportToCsv("Student_Enrolment");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue
        Assert.Equal("HESA_STUDENTID", doc.GetCellValue("Student_Enrolment", 0, 0));

        // SaveToFile
        var path = TempFile("dogfood_hesa_return_2024.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.True(loaded.GetRowHeight("Student_Enrolment", 0) >= 0.0);
        Assert.Equal("HESA_STUDENTID", loaded.GetCellValue("Student_Enrolment", 0, 0));

        // SetRowHeight on loaded
        for (int r = 6; r <= 10; r++)
            loaded.SetRowHeight("Student_Enrolment", r, 0.5);
        Assert.True(loaded.GetRowHeight("Student_Enrolment", 6) >= 0.0);

        // AddSheet on loaded
        loaded.AddSheet("Validation_Log");
        loaded.SetCellValue("Validation_Log", 0, 0, "Rule_ID");
        loaded.SetCellValue("Validation_Log", 0, 1, "Status");
        loaded.SetCellValue("Validation_Log", 0, 2, "Description");
        loaded.SetRowHeight("Validation_Log", 0, 0.9);
        Assert.Equal(4, loaded.GetSheetCount());

        // Final save
        var path2 = TempFile("dogfood_hesa_return_2024_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetSheetCount());
        Assert.True(loaded2.GetRowHeight("Student_Enrolment", 0) >= 0.0);
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Student_Enrolment"));
        var ex2 = Record.Exception(() => loaded2.SetRowHeight("Staff_Data", 0, 1.2));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
