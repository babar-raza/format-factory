// Tests for FodsDocument.GetPivotTableCount, AddPivotTable, GetPivotTableName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R345

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R345: Tests for FodsDocument.GetPivotTableCount, AddPivotTable, GetPivotTableName deeper.
/// GetPivotTableCount(): returns the number of pivot tables defined in the document.
/// AddPivotTable(sourceSheetName, targetSheetName, name): adds a pivot table summary.
/// GetPivotTableName(index): returns the name of the pivot table at the given index.
/// Covers: GetPivotTableCount no-throw; GetPivotTableCount non-negative; GetPivotTableCount consistent;
/// GetPivotTableCount zero for new doc; GetPivotTableCount after AddPivotTable increases;
/// GetPivotTableCount save-load;
/// AddPivotTable no-throw; AddPivotTable increases count; AddPivotTable save-load;
/// AddPivotTable multiple; AddPivotTable then ExportToHtml no-throw;
/// AddPivotTable then GetSheetCount positive;
/// GetPivotTableName no-throw; GetPivotTableName non-null; GetPivotTableName consistent;
/// GetPivotTableName save-load;
/// dogfood CreateDoc→AddPivotTable→GetPivotTableCount→GetPivotTableName→SaveToFile pipeline.
/// </summary>
public class FodsR345GetPivotTableCountAndAddPivotTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR345GetPivotTableCountAndAddPivotTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR345_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateHrDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("HeadcountData");
        doc.SetCellValue("HeadcountData", 0, 0, "EmployeeID");
        doc.SetCellValue("HeadcountData", 0, 1, "Department");
        doc.SetCellValue("HeadcountData", 0, 2, "Grade");
        doc.SetCellValue("HeadcountData", 0, 3, "Salary");
        doc.SetCellValue("HeadcountData", 0, 4, "Region");
        string[] depts = { "Finance", "Technology", "Operations", "HR", "Marketing" };
        string[] grades = { "G1", "G2", "G3", "G4", "G5" };
        string[] regions = { "London", "Manchester", "Edinburgh", "Bristol" };
        for (int r = 1; r <= 15; r++)
        {
            doc.SetCellValue("HeadcountData", r, 0, $"EMP{r:D4}");
            doc.SetCellValue("HeadcountData", r, 1, depts[r % 5]);
            doc.SetCellValue("HeadcountData", r, 2, grades[r % 5]);
            doc.SetCellValue("HeadcountData", r, 3, (30000 + r * 3000).ToString());
            doc.SetCellValue("HeadcountData", r, 4, regions[r % 4]);
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPivotTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPivotTableCount_NoThrow()
    {
        var doc = CreateHrDataDoc();
        var ex = Record.Exception(() => doc.GetPivotTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPivotTableCount_NonNegative()
    {
        var doc = CreateHrDataDoc();
        Assert.True(doc.GetPivotTableCount() >= 0);
    }

    [Fact]
    public void GetPivotTableCount_Consistent()
    {
        var doc = CreateHrDataDoc();
        Assert.Equal(doc.GetPivotTableCount(), doc.GetPivotTableCount());
    }

    [Fact]
    public void GetPivotTableCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        Assert.Equal(0, doc.GetPivotTableCount());
    }

    [Fact]
    public void GetPivotTableCount_AfterAddPivotTable_Increases()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_Dept");
        var before = doc.GetPivotTableCount();
        doc.AddPivotTable("HeadcountData", "Pivot_Dept", "DeptSummary");
        Assert.Equal(before + 1, doc.GetPivotTableCount());
    }

    [Fact]
    public void GetPivotTableCount_SaveLoad_Consistent()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_Region");
        doc.AddPivotTable("HeadcountData", "Pivot_Region", "RegionSummary");
        var before = doc.GetPivotTableCount();
        var path = TempFile("ptc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPivotTableCount());
    }

    // -------------------------------------------------------------------------
    // AddPivotTable
    // -------------------------------------------------------------------------

    [Fact]
    public void AddPivotTable_NoThrow()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_Test");
        var ex = Record.Exception(() => doc.AddPivotTable("HeadcountData", "Pivot_Test", "TestPivot"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddPivotTable_Increases_Count()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_Grade");
        var before = doc.GetPivotTableCount();
        doc.AddPivotTable("HeadcountData", "Pivot_Grade", "GradeSummary");
        Assert.Equal(before + 1, doc.GetPivotTableCount());
    }

    [Fact]
    public void AddPivotTable_SaveLoad_Persists()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_Save");
        doc.AddPivotTable("HeadcountData", "Pivot_Save", "SavePivot");
        var before = doc.GetPivotTableCount();
        var path = TempFile("pt_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPivotTableCount());
    }

    [Fact]
    public void AddPivotTable_Multiple()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("P1");
        doc.AddSheet("P2");
        doc.AddPivotTable("HeadcountData", "P1", "Pivot1");
        doc.AddPivotTable("HeadcountData", "P2", "Pivot2");
        Assert.Equal(2, doc.GetPivotTableCount());
    }

    [Fact]
    public void AddPivotTable_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_Html");
        doc.AddPivotTable("HeadcountData", "Pivot_Html", "HtmlPivot");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddPivotTable_Then_GetSheetCount_Positive()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_SC");
        doc.AddPivotTable("HeadcountData", "Pivot_SC", "SCPivot");
        Assert.True(doc.GetSheetCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetPivotTableName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPivotTableName_NoThrow()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_N");
        doc.AddPivotTable("HeadcountData", "Pivot_N", "NamePivot");
        var ex = Record.Exception(() => doc.GetPivotTableName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPivotTableName_NonNull()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_NN");
        doc.AddPivotTable("HeadcountData", "Pivot_NN", "NullCheckPivot");
        Assert.NotNull(doc.GetPivotTableName(0));
    }

    [Fact]
    public void GetPivotTableName_Consistent()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_C");
        doc.AddPivotTable("HeadcountData", "Pivot_C", "ConsistentPivot");
        Assert.Equal(doc.GetPivotTableName(0), doc.GetPivotTableName(0));
    }

    [Fact]
    public void GetPivotTableName_SaveLoad_Consistent()
    {
        var doc = CreateHrDataDoc();
        doc.AddSheet("Pivot_SL");
        doc.AddPivotTable("HeadcountData", "Pivot_SL", "SaveLoadPivot");
        var path = TempFile("ptn_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetPivotTableName(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddPivotTable_GetPivotTableCount_GetPivotTableName_SaveToFile_Pipeline()
    {
        // Financial management — cost centre reporting workbook with pivot summaries
        var doc = FodsDocument.CreateEmpty();

        // ---- Source data sheet ----
        doc.AddSheet("CostData");
        doc.SetCellValue("CostData", 0, 0, "CostCentre");
        doc.SetCellValue("CostData", 0, 1, "Division");
        doc.SetCellValue("CostData", 0, 2, "Category");
        doc.SetCellValue("CostData", 0, 3, "Month");
        doc.SetCellValue("CostData", 0, 4, "BudgetGBP");
        doc.SetCellValue("CostData", 0, 5, "ActualGBP");
        doc.SetCellValue("CostData", 0, 6, "VariancePct");
        string[] centres = { "CC-TECH-001", "CC-FIN-002", "CC-OPS-003", "CC-HR-004", "CC-MKT-005" };
        string[] divisions = { "Technology", "Finance", "Operations", "HR", "Marketing" };
        string[] categories = { "Headcount", "IT_Infrastructure", "Travel", "Training", "Facilities" };
        for (int r = 1; r <= 24; r++)
        {
            int cc = (r - 1) % 5;
            double budget = 50000 + cc * 10000 + (r % 3) * 5000;
            double actual = budget * (0.85 + (r % 7) * 0.04);
            double variance = (actual - budget) / budget * 100;
            doc.SetCellValue("CostData", r, 0, centres[cc]);
            doc.SetCellValue("CostData", r, 1, divisions[cc]);
            doc.SetCellValue("CostData", r, 2, categories[r % 5]);
            doc.SetCellValue("CostData", r, 3, $"2024-{(r % 12 + 1):D2}");
            doc.SetCellValue("CostData", r, 4, budget.ToString("F0"));
            doc.SetCellValue("CostData", r, 5, actual.ToString("F0"));
            doc.SetCellValue("CostData", r, 6, variance.ToString("F1"));
        }

        Assert.Equal(0, doc.GetPivotTableCount());

        // ---- Pivot sheets ----
        doc.AddSheet("Pivot_ByDivision");
        doc.AddSheet("Pivot_ByCategory");
        doc.AddSheet("Pivot_ByMonth");

        // AddPivotTable
        doc.AddPivotTable("CostData", "Pivot_ByDivision", "DivisionSummary");
        Assert.Equal(1, doc.GetPivotTableCount());

        doc.AddPivotTable("CostData", "Pivot_ByCategory", "CategorySummary");
        Assert.Equal(2, doc.GetPivotTableCount());

        doc.AddPivotTable("CostData", "Pivot_ByMonth", "MonthlyVariance");
        Assert.Equal(3, doc.GetPivotTableCount());

        // Consistent
        Assert.Equal(doc.GetPivotTableCount(), doc.GetPivotTableCount());

        // GetPivotTableName
        var name0 = doc.GetPivotTableName(0);
        Assert.NotNull(name0);
        Assert.Equal(name0, doc.GetPivotTableName(0)); // consistent

        var name1 = doc.GetPivotTableName(1);
        Assert.NotNull(name1);

        var name2 = doc.GetPivotTableName(2);
        Assert.NotNull(name2);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetSheetCount
        Assert.True(doc.GetSheetCount() >= 4);

        // GetCellValue
        var cellVal = doc.GetCellValue("CostData", 1, 0);
        Assert.NotNull(cellVal);

        // SaveToFile
        var path = TempFile("dogfood_cost_pivot.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetPivotTableCount());
        Assert.NotNull(loaded.GetPivotTableName(0));
        Assert.NotNull(loaded.GetPivotTableName(2));

        // AddPivotTable on loaded
        loaded.AddSheet("Pivot_Variance");
        loaded.AddPivotTable("CostData", "Pivot_Variance", "VarianceHeatmap");
        Assert.Equal(4, loaded.GetPivotTableCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final save
        var path2 = TempFile("dogfood_cost_pivot_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetPivotTableCount());
        Assert.NotNull(loaded2.GetPivotTableName(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetPivotTableName(3));
        var ex3 = Record.Exception(() => loaded2.AddPivotTable("CostData", "Pivot_Variance", "FinalPivot"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
