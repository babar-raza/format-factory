// Tests for FodsDocument.GetPrintAreaCount, SetPrintArea, GetPrintArea deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R359

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R359: Tests for FodsDocument.GetPrintAreaCount, SetPrintArea, GetPrintArea deeper.
/// GetPrintAreaCount(): returns the number of sheets that have a print area defined.
/// SetPrintArea(sheetName, range): defines the print area for the named sheet.
/// GetPrintArea(sheetName): returns the print area range string for the named sheet.
/// Covers: GetPrintAreaCount no-throw; GetPrintAreaCount non-negative; GetPrintAreaCount consistent;
/// GetPrintAreaCount zero for new doc; GetPrintAreaCount after SetPrintArea increases;
/// GetPrintAreaCount save-load;
/// SetPrintArea no-throw; SetPrintArea increases count; SetPrintArea save-load;
/// SetPrintArea multiple; SetPrintArea then ExportToCsv no-throw;
/// SetPrintArea then GetCellValue non-null; SetPrintArea then GetSheetCount unchanged;
/// GetPrintArea no-throw; GetPrintArea non-null; GetPrintArea consistent;
/// GetPrintArea save-load;
/// dogfood CreateDoc→SetPrintArea→GetPrintAreaCount→GetPrintArea→SaveToFile pipeline.
/// </summary>
public class FodsR359GetPrintAreaCountAndSetPrintAreaDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR359GetPrintAreaCountAndSetPrintAreaDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR359_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateBudgetDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Q1_Budget");
        doc.SetCellValue("Q1_Budget", 0, 0, "Category");
        doc.SetCellValue("Q1_Budget", 0, 1, "Jan");
        doc.SetCellValue("Q1_Budget", 0, 2, "Feb");
        doc.SetCellValue("Q1_Budget", 0, 3, "Mar");
        doc.SetCellValue("Q1_Budget", 1, 0, "Revenue");
        doc.SetCellValue("Q1_Budget", 1, 1, "145000");
        doc.SetCellValue("Q1_Budget", 1, 2, "152000");
        doc.SetCellValue("Q1_Budget", 1, 3, "163000");
        doc.SetCellValue("Q1_Budget", 2, 0, "COGS");
        doc.SetCellValue("Q1_Budget", 2, 1, "58000");
        doc.SetCellValue("Q1_Budget", 2, 2, "61000");
        doc.SetCellValue("Q1_Budget", 2, 3, "65200");
        doc.AddSheet("Q2_Budget");
        doc.SetCellValue("Q2_Budget", 0, 0, "Category");
        doc.SetCellValue("Q2_Budget", 0, 1, "Apr");
        doc.SetCellValue("Q2_Budget", 0, 2, "May");
        doc.SetCellValue("Q2_Budget", 0, 3, "Jun");
        doc.SetCellValue("Q2_Budget", 1, 0, "Revenue");
        doc.SetCellValue("Q2_Budget", 1, 1, "171000");
        doc.SetCellValue("Q2_Budget", 1, 2, "178000");
        doc.SetCellValue("Q2_Budget", 1, 3, "185000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPrintAreaCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPrintAreaCount_NoThrow()
    {
        var doc = CreateBudgetDoc();
        var ex = Record.Exception(() => doc.GetPrintAreaCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPrintAreaCount_NonNegative()
    {
        var doc = CreateBudgetDoc();
        Assert.True(doc.GetPrintAreaCount() >= 0);
    }

    [Fact]
    public void GetPrintAreaCount_Consistent()
    {
        var doc = CreateBudgetDoc();
        Assert.Equal(doc.GetPrintAreaCount(), doc.GetPrintAreaCount());
    }

    [Fact]
    public void GetPrintAreaCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Data");
        Assert.Equal(0, doc.GetPrintAreaCount());
    }

    [Fact]
    public void GetPrintAreaCount_AfterSetPrintArea_Increases()
    {
        var doc = CreateBudgetDoc();
        var before = doc.GetPrintAreaCount();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        Assert.Equal(before + 1, doc.GetPrintAreaCount());
    }

    [Fact]
    public void GetPrintAreaCount_SaveLoad_Consistent()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        var before = doc.GetPrintAreaCount();
        var path = TempFile("pac_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPrintAreaCount());
    }

    // -------------------------------------------------------------------------
    // SetPrintArea
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPrintArea_NoThrow()
    {
        var doc = CreateBudgetDoc();
        var ex = Record.Exception(() => doc.SetPrintArea("Q1_Budget", "A1:D3"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetPrintArea_Increases_Count()
    {
        var doc = CreateBudgetDoc();
        var before = doc.GetPrintAreaCount();
        doc.SetPrintArea("Q2_Budget", "A1:D3");
        Assert.Equal(before + 1, doc.GetPrintAreaCount());
    }

    [Fact]
    public void SetPrintArea_SaveLoad_Persists()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "B1:D3");
        var before = doc.GetPrintAreaCount();
        var path = TempFile("spa_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPrintAreaCount());
    }

    [Fact]
    public void SetPrintArea_Multiple()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        doc.SetPrintArea("Q2_Budget", "A1:D3");
        Assert.Equal(2, doc.GetPrintAreaCount());
    }

    [Fact]
    public void SetPrintArea_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        var ex = Record.Exception(() => doc.ExportToCsv("Q1_Budget"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetPrintArea_Then_GetCellValue_NonNull()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        Assert.NotNull(doc.GetCellValue("Q1_Budget", 0, 0));
    }

    [Fact]
    public void SetPrintArea_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateBudgetDoc();
        var before = doc.GetSheetCount();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        Assert.Equal(before, doc.GetSheetCount());
    }

    // -------------------------------------------------------------------------
    // GetPrintArea
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPrintArea_NoThrow()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        var ex = Record.Exception(() => doc.GetPrintArea("Q1_Budget"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPrintArea_NonNull()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        Assert.NotNull(doc.GetPrintArea("Q1_Budget"));
    }

    [Fact]
    public void GetPrintArea_Consistent()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q1_Budget", "A1:D3");
        Assert.Equal(doc.GetPrintArea("Q1_Budget"), doc.GetPrintArea("Q1_Budget"));
    }

    [Fact]
    public void GetPrintArea_SaveLoad_Consistent()
    {
        var doc = CreateBudgetDoc();
        doc.SetPrintArea("Q2_Budget", "A1:D3");
        var path = TempFile("gpa_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetPrintArea("Q2_Budget"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetPrintArea_GetPrintAreaCount_GetPrintArea_SaveToFile_Pipeline()
    {
        // Annual budget model — UK local authority CIPFA-aligned budget workbook
        var doc = FodsDocument.CreateEmpty();

        doc.AddSheet("Revenue_Outturn");
        doc.SetCellValue("Revenue_Outturn", 0, 0, "Service_Area");
        doc.SetCellValue("Revenue_Outturn", 0, 1, "Budget_GBP");
        doc.SetCellValue("Revenue_Outturn", 0, 2, "Outturn_GBP");
        doc.SetCellValue("Revenue_Outturn", 0, 3, "Variance_GBP");
        doc.SetCellValue("Revenue_Outturn", 0, 4, "Variance_Pct");
        string[] services = { "Adults_Social_Care", "Childrens_Social_Care", "Highways_Transport", "Housing_Benefits", "Planning_Economic_Dev", "Environmental_Services" };
        int[] budgets = { 42800000, 31500000, 18200000, 67400000, 8900000, 12300000 };
        int[] outturn = { 44100000, 30800000, 17900000, 67100000, 9200000, 12800000 };
        for (int i = 0; i < services.Length; i++)
        {
            int v = outturn[i] - budgets[i];
            double vp = (double)v / budgets[i] * 100.0;
            doc.SetCellValue("Revenue_Outturn", i + 1, 0, services[i]);
            doc.SetCellValue("Revenue_Outturn", i + 1, 1, budgets[i].ToString());
            doc.SetCellValue("Revenue_Outturn", i + 1, 2, outturn[i].ToString());
            doc.SetCellValue("Revenue_Outturn", i + 1, 3, v.ToString());
            doc.SetCellValue("Revenue_Outturn", i + 1, 4, $"{vp:F2}");
        }

        doc.AddSheet("Capital_Programme");
        doc.SetCellValue("Capital_Programme", 0, 0, "Scheme_Ref");
        doc.SetCellValue("Capital_Programme", 0, 1, "Scheme_Name");
        doc.SetCellValue("Capital_Programme", 0, 2, "Approved_Budget");
        doc.SetCellValue("Capital_Programme", 0, 3, "Expenditure_YTD");
        doc.SetCellValue("Capital_Programme", 0, 4, "Forecast_Outturn");
        string[] schemes = { "CAP-001", "CAP-002", "CAP-003", "CAP-004", "CAP-005" };
        for (int i = 0; i < schemes.Length; i++)
        {
            doc.SetCellValue("Capital_Programme", i + 1, 0, schemes[i]);
            doc.SetCellValue("Capital_Programme", i + 1, 1, $"Capital_Scheme_{i + 1}");
            doc.SetCellValue("Capital_Programme", i + 1, 2, ((i + 1) * 850000).ToString());
            doc.SetCellValue("Capital_Programme", i + 1, 3, ((i + 1) * 620000).ToString());
            doc.SetCellValue("Capital_Programme", i + 1, 4, ((i + 1) * 830000).ToString());
        }

        doc.AddSheet("Reserves_Summary");
        doc.SetCellValue("Reserves_Summary", 0, 0, "Reserve_Name");
        doc.SetCellValue("Reserves_Summary", 0, 1, "Opening_Balance");
        doc.SetCellValue("Reserves_Summary", 0, 2, "Contributions");
        doc.SetCellValue("Reserves_Summary", 0, 3, "Drawdowns");
        doc.SetCellValue("Reserves_Summary", 0, 4, "Closing_Balance");
        doc.SetCellValue("Reserves_Summary", 1, 0, "General_Fund");
        doc.SetCellValue("Reserves_Summary", 1, 1, "8500000");
        doc.SetCellValue("Reserves_Summary", 1, 2, "1200000");
        doc.SetCellValue("Reserves_Summary", 1, 3, "950000");
        doc.SetCellValue("Reserves_Summary", 1, 4, "8750000");

        Assert.Equal(3, doc.GetSheetCount());
        Assert.Equal(0, doc.GetPrintAreaCount());

        // SetPrintArea
        doc.SetPrintArea("Revenue_Outturn", "A1:E7");
        Assert.Equal(1, doc.GetPrintAreaCount());

        doc.SetPrintArea("Capital_Programme", "A1:E6");
        Assert.Equal(2, doc.GetPrintAreaCount());

        doc.SetPrintArea("Reserves_Summary", "A1:E2");
        Assert.Equal(3, doc.GetPrintAreaCount());

        // Consistent
        Assert.Equal(doc.GetPrintAreaCount(), doc.GetPrintAreaCount());

        // GetPrintArea
        var area1 = doc.GetPrintArea("Revenue_Outturn");
        Assert.NotNull(area1);
        Assert.Equal(area1, doc.GetPrintArea("Revenue_Outturn")); // consistent

        var area2 = doc.GetPrintArea("Capital_Programme");
        Assert.NotNull(area2);

        var area3 = doc.GetPrintArea("Reserves_Summary");
        Assert.NotNull(area3);

        // ExportToCsv
        var csv = doc.ExportToCsv("Revenue_Outturn");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue
        Assert.Equal("Adults_Social_Care", doc.GetCellValue("Revenue_Outturn", 1, 0));

        // GetRowCount / GetColumnCount
        Assert.True(doc.GetRowCount("Revenue_Outturn") > 0);
        Assert.True(doc.GetColumnCount("Revenue_Outturn") > 0);

        // SaveToFile
        var path = TempFile("dogfood_cipfa_budget.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetPrintAreaCount());
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.NotNull(loaded.GetPrintArea("Revenue_Outturn"));
        Assert.NotNull(loaded.GetPrintArea("Capital_Programme"));

        // SetPrintArea on loaded (override)
        loaded.SetPrintArea("Revenue_Outturn", "A1:E7");
        Assert.Equal(3, loaded.GetPrintAreaCount());

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("Capital_Programme");
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);

        // AddSheet on loaded
        loaded.AddSheet("Treasury_Management");
        loaded.SetCellValue("Treasury_Management", 0, 0, "Counterparty");
        loaded.SetCellValue("Treasury_Management", 0, 1, "Principal");
        loaded.SetCellValue("Treasury_Management", 0, 2, "Rate_Pct");
        loaded.SetCellValue("Treasury_Management", 0, 3, "Maturity_Date");
        loaded.SetPrintArea("Treasury_Management", "A1:D2");
        Assert.Equal(4, loaded.GetPrintAreaCount());
        Assert.Equal(4, loaded.GetSheetCount());

        // Final save
        var path2 = TempFile("dogfood_cipfa_budget_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetPrintAreaCount());
        Assert.Equal(4, loaded2.GetSheetCount());
        Assert.NotNull(loaded2.GetPrintArea("Revenue_Outturn"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Capital_Programme"));
        var ex2 = Record.Exception(() => loaded2.SetPrintArea("Reserves_Summary", "A1:E2"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
