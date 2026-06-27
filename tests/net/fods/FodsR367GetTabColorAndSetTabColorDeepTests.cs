// Tests for FodsDocument.GetTabColor, SetTabColor deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R367

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R367: Tests for FodsDocument.GetTabColor, SetTabColor deeper.
/// GetTabColor(sheetName): returns the tab colour for the named sheet, or null if unset.
/// SetTabColor(sheetName, color): sets the tab colour for the named sheet (hex or named colour string).
/// Covers: GetTabColor no-throw; GetTabColor consistent; GetTabColor null for uncolored sheet;
/// SetTabColor no-throw; SetTabColor with hex color; SetTabColor with named color;
/// SetTabColor then GetTabColor non-null; SetTabColor save-load;
/// SetTabColor multiple sheets; SetTabColor then ExportToCsv no-throw;
/// SetTabColor then GetCellValue non-null; SetTabColor then GetSheetCount unchanged;
/// GetTabColor save-load consistent;
/// dogfood CreateDoc→SetTabColor→GetTabColor→SaveToFile pipeline.
/// </summary>
public class FodsR367GetTabColorAndSetTabColorDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR367GetTabColorAndSetTabColorDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR367_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateProjectDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Project");
        doc.SetCellValue("Summary", 0, 1, "Status");
        doc.SetCellValue("Summary", 0, 2, "Owner");
        doc.SetCellValue("Summary", 1, 0, "Alpha");
        doc.SetCellValue("Summary", 1, 1, "On_Track");
        doc.SetCellValue("Summary", 1, 2, "Alice");
        doc.AddSheet("Risks");
        doc.SetCellValue("Risks", 0, 0, "Risk_ID");
        doc.SetCellValue("Risks", 0, 1, "Description");
        doc.SetCellValue("Risks", 0, 2, "Severity");
        doc.SetCellValue("Risks", 1, 0, "R001");
        doc.SetCellValue("Risks", 1, 1, "Dependency_delay");
        doc.SetCellValue("Risks", 1, 2, "High");
        doc.AddSheet("Actions");
        doc.SetCellValue("Actions", 0, 0, "Action_ID");
        doc.SetCellValue("Actions", 0, 1, "Description");
        doc.SetCellValue("Actions", 0, 2, "Due_Date");
        doc.SetCellValue("Actions", 1, 0, "A001");
        doc.SetCellValue("Actions", 1, 1, "Review_timeline");
        doc.SetCellValue("Actions", 1, 2, "2024-06-30");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTabColor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTabColor_NoThrow()
    {
        var doc = CreateProjectDoc();
        var ex = Record.Exception(() => doc.GetTabColor("Summary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTabColor_Consistent()
    {
        var doc = CreateProjectDoc();
        Assert.Equal(doc.GetTabColor("Summary"), doc.GetTabColor("Summary"));
    }

    [Fact]
    public void GetTabColor_Null_ForUncoloredSheet()
    {
        var doc = CreateProjectDoc();
        // New sheets have no tab colour
        Assert.Null(doc.GetTabColor("Summary"));
    }

    // -------------------------------------------------------------------------
    // SetTabColor
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTabColor_NoThrow()
    {
        var doc = CreateProjectDoc();
        var ex = Record.Exception(() => doc.SetTabColor("Summary", "#4CAF50"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTabColor_WithHexColor_NoThrow()
    {
        var doc = CreateProjectDoc();
        var ex = Record.Exception(() => doc.SetTabColor("Risks", "#F44336"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTabColor_WithNamedColor_NoThrow()
    {
        var doc = CreateProjectDoc();
        var ex = Record.Exception(() => doc.SetTabColor("Actions", "blue"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTabColor_Then_GetTabColor_NonNull()
    {
        var doc = CreateProjectDoc();
        doc.SetTabColor("Summary", "#4CAF50");
        Assert.NotNull(doc.GetTabColor("Summary"));
    }

    [Fact]
    public void SetTabColor_SaveLoad_Persists()
    {
        var doc = CreateProjectDoc();
        doc.SetTabColor("Summary", "#4CAF50");
        var path = TempFile("stc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetTabColor("Summary"));
    }

    [Fact]
    public void SetTabColor_MultipleSheets()
    {
        var doc = CreateProjectDoc();
        doc.SetTabColor("Summary", "#4CAF50");
        doc.SetTabColor("Risks", "#F44336");
        doc.SetTabColor("Actions", "#2196F3");
        Assert.NotNull(doc.GetTabColor("Summary"));
        Assert.NotNull(doc.GetTabColor("Risks"));
        Assert.NotNull(doc.GetTabColor("Actions"));
    }

    [Fact]
    public void SetTabColor_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateProjectDoc();
        doc.SetTabColor("Summary", "#4CAF50");
        var ex = Record.Exception(() => doc.ExportToCsv("Summary"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTabColor_Then_GetCellValue_NonNull()
    {
        var doc = CreateProjectDoc();
        doc.SetTabColor("Summary", "#4CAF50");
        Assert.NotNull(doc.GetCellValue("Summary", 0, 0));
    }

    [Fact]
    public void SetTabColor_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateProjectDoc();
        var before = doc.GetSheetCount();
        doc.SetTabColor("Summary", "#4CAF50");
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void GetTabColor_SaveLoad_Consistent()
    {
        var doc = CreateProjectDoc();
        doc.SetTabColor("Risks", "#FF9800");
        var path = TempFile("gtc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetTabColor("Risks"));
        Assert.Equal(doc.GetTabColor("Risks"), loaded.GetTabColor("Risks"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetTabColor_GetTabColor_SaveToFile_Pipeline()
    {
        // Programme management — NHS digital transformation programme master workbook
        var doc = FodsDocument.CreateEmpty();

        doc.AddSheet("Programme_Overview");
        doc.SetCellValue("Programme_Overview", 0, 0, "Initiative_ID");
        doc.SetCellValue("Programme_Overview", 0, 1, "Initiative_Name");
        doc.SetCellValue("Programme_Overview", 0, 2, "Status");
        doc.SetCellValue("Programme_Overview", 0, 3, "Owner");
        doc.SetCellValue("Programme_Overview", 0, 4, "Budget_GBP");
        string[] initiatives = {
            "EHR_Rollout", "Patient_Portal", "Clinical_Analytics_Platform",
            "Workforce_Management", "Radiology_AI_Deployment"
        };
        string[] statuses = { "Green", "Amber", "Green", "Red", "Green" };
        int[] budgets = { 4200000, 850000, 1750000, 620000, 2100000 };
        for (int i = 0; i < initiatives.Length; i++)
        {
            doc.SetCellValue("Programme_Overview", i + 1, 0, $"NHS-DT-{i + 1:D3}");
            doc.SetCellValue("Programme_Overview", i + 1, 1, initiatives[i]);
            doc.SetCellValue("Programme_Overview", i + 1, 2, statuses[i]);
            doc.SetCellValue("Programme_Overview", i + 1, 3, $"SRO_{i + 1}");
            doc.SetCellValue("Programme_Overview", i + 1, 4, budgets[i].ToString());
        }

        doc.AddSheet("Risk_Register");
        doc.SetCellValue("Risk_Register", 0, 0, "Risk_ID");
        doc.SetCellValue("Risk_Register", 0, 1, "Description");
        doc.SetCellValue("Risk_Register", 0, 2, "Likelihood");
        doc.SetCellValue("Risk_Register", 0, 3, "Impact");
        doc.SetCellValue("Risk_Register", 0, 4, "RAG_Score");
        doc.SetCellValue("Risk_Register", 1, 0, "R001");
        doc.SetCellValue("Risk_Register", 1, 1, "Interoperability_with_legacy_PAS");
        doc.SetCellValue("Risk_Register", 1, 2, "High");
        doc.SetCellValue("Risk_Register", 1, 3, "High");
        doc.SetCellValue("Risk_Register", 1, 4, "Red");

        doc.AddSheet("Benefits_Realisation");
        doc.SetCellValue("Benefits_Realisation", 0, 0, "Benefit_ID");
        doc.SetCellValue("Benefits_Realisation", 0, 1, "Description");
        doc.SetCellValue("Benefits_Realisation", 0, 2, "Target_Date");
        doc.SetCellValue("Benefits_Realisation", 0, 3, "Baseline_Value");
        doc.SetCellValue("Benefits_Realisation", 0, 4, "Current_Value");
        doc.SetCellValue("Benefits_Realisation", 1, 0, "B001");
        doc.SetCellValue("Benefits_Realisation", 1, 1, "Reduced_duplicate_test_ordering");
        doc.SetCellValue("Benefits_Realisation", 1, 2, "2025-03-31");
        doc.SetCellValue("Benefits_Realisation", 1, 3, "12.4");
        doc.SetCellValue("Benefits_Realisation", 1, 4, "8.7");

        doc.AddSheet("Milestones");
        doc.SetCellValue("Milestones", 0, 0, "Milestone_ID");
        doc.SetCellValue("Milestones", 0, 1, "Description");
        doc.SetCellValue("Milestones", 0, 2, "Due_Date");
        doc.SetCellValue("Milestones", 0, 3, "Status");

        doc.AddSheet("Financials");
        doc.SetCellValue("Financials", 0, 0, "Cost_Category");
        doc.SetCellValue("Financials", 0, 1, "Approved_Budget_GBP");
        doc.SetCellValue("Financials", 0, 2, "Spend_YTD_GBP");
        doc.SetCellValue("Financials", 0, 3, "Forecast_Outturn_GBP");

        Assert.Equal(5, doc.GetSheetCount());
        Assert.Null(doc.GetTabColor("Programme_Overview"));
        Assert.Null(doc.GetTabColor("Risk_Register"));

        // SetTabColor — RAG status colour-coding for NHS programme management
        doc.SetTabColor("Programme_Overview", "#4CAF50"); // green — executive summary
        Assert.NotNull(doc.GetTabColor("Programme_Overview"));

        doc.SetTabColor("Risk_Register", "#F44336"); // red — risk register always highlighted
        Assert.NotNull(doc.GetTabColor("Risk_Register"));

        doc.SetTabColor("Benefits_Realisation", "#2196F3"); // blue — benefits
        Assert.NotNull(doc.GetTabColor("Benefits_Realisation"));

        doc.SetTabColor("Milestones", "#FF9800"); // amber — milestones at risk
        Assert.NotNull(doc.GetTabColor("Milestones"));

        doc.SetTabColor("Financials", "#9C27B0"); // purple — financial data
        Assert.NotNull(doc.GetTabColor("Financials"));

        // Consistent
        Assert.Equal(doc.GetTabColor("Programme_Overview"), doc.GetTabColor("Programme_Overview"));
        Assert.Equal(doc.GetTabColor("Risk_Register"), doc.GetTabColor("Risk_Register"));

        // Sheet count unchanged
        Assert.Equal(5, doc.GetSheetCount());

        // ExportToCsv
        var csv = doc.ExportToCsv("Programme_Overview");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue
        Assert.Equal("NHS-DT-001", doc.GetCellValue("Programme_Overview", 1, 0));

        // GetRowCount
        Assert.True(doc.GetRowCount("Programme_Overview") > 0);

        // SaveToFile
        var path = TempFile("dogfood_nhs_dt_programme.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetSheetCount());
        Assert.NotNull(loaded.GetTabColor("Programme_Overview"));
        Assert.NotNull(loaded.GetTabColor("Risk_Register"));
        Assert.NotNull(loaded.GetTabColor("Benefits_Realisation"));
        Assert.NotNull(loaded.GetTabColor("Milestones"));
        Assert.NotNull(loaded.GetTabColor("Financials"));
        Assert.Equal(doc.GetTabColor("Risk_Register"), loaded.GetTabColor("Risk_Register"));

        // Modify tab colour on loaded
        loaded.SetTabColor("Milestones", "#4CAF50"); // now green — milestone achieved
        Assert.NotNull(loaded.GetTabColor("Milestones"));

        // AddSheet with colour on loaded
        loaded.AddSheet("Lessons_Learned");
        loaded.SetCellValue("Lessons_Learned", 0, 0, "Lesson_ID");
        loaded.SetTabColor("Lessons_Learned", "#607D8B"); // grey — reference
        Assert.NotNull(loaded.GetTabColor("Lessons_Learned"));
        Assert.Equal(6, loaded.GetSheetCount());

        // Final save
        var path2 = TempFile("dogfood_nhs_dt_programme_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetSheetCount());
        Assert.NotNull(loaded2.GetTabColor("Programme_Overview"));
        Assert.NotNull(loaded2.GetTabColor("Lessons_Learned"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Programme_Overview"));
        var ex2 = Record.Exception(() => loaded2.SetTabColor("Financials", "#E91E63"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
