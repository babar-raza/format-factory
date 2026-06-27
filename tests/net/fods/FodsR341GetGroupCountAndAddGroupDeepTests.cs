// Tests for FodsDocument.GetGroupCount, AddGroup, GetGroupRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R341

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R341: Tests for FodsDocument.GetGroupCount, AddGroup, GetGroupRange deeper.
/// GetGroupCount(sheet): returns the number of row or column groups on the specified sheet.
/// AddGroup(sheet, startRow, endRow, groupType): adds a row group spanning the specified rows.
/// GetGroupRange(sheet, groupIndex): returns the start and end indices of the group.
/// Covers: GetGroupCount no-throw; GetGroupCount non-negative; GetGroupCount consistent;
/// GetGroupCount zero for unmodified sheet; GetGroupCount after AddGroup increases;
/// GetGroupCount save-load;
/// AddGroup no-throw; AddGroup increases count; AddGroup save-load;
/// AddGroup multiple; AddGroup then ExportToHtml no-throw; AddGroup then GetCellValue no-throw;
/// GetGroupRange no-throw; GetGroupRange non-null; GetGroupRange consistent;
/// GetGroupRange save-load;
/// dogfood CreateDoc→AddGroup→GetGroupCount→GetGroupRange→SaveToFile pipeline.
/// </summary>
public class FodsR341GetGroupCountAndAddGroupDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR341GetGroupCountAndAddGroupDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR341_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateFinancialOutlineDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("IncomeStatement");
        doc.SetCellValue("IncomeStatement", 0, 0, "Line Item");
        doc.SetCellValue("IncomeStatement", 0, 1, "Q1");
        doc.SetCellValue("IncomeStatement", 0, 2, "Q2");
        doc.SetCellValue("IncomeStatement", 0, 3, "Q3");
        doc.SetCellValue("IncomeStatement", 0, 4, "Q4");
        string[] items = {
            "Revenue", "Product Sales", "Service Revenue", "Other Revenue",
            "Cost of Goods Sold", "COGS-Product", "COGS-Service",
            "Gross Profit",
            "Operating Expenses", "Salaries", "Marketing", "R&D", "Admin",
            "EBITDA", "Depreciation", "EBIT", "Interest", "PBT", "Tax", "Net Profit"
        };
        var rng = new Random(44001);
        for (int i = 0; i < items.Length; i++)
        {
            doc.SetCellValue("IncomeStatement", i + 1, 0, items[i]);
            for (int q = 1; q <= 4; q++)
                doc.SetCellValue("IncomeStatement", i + 1, q, (rng.Next(10000, 500000)).ToString());
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetGroupCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGroupCount_NoThrow()
    {
        var doc = CreateFinancialOutlineDoc();
        var ex = Record.Exception(() => doc.GetGroupCount("IncomeStatement"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetGroupCount_NonNegative()
    {
        var doc = CreateFinancialOutlineDoc();
        Assert.True(doc.GetGroupCount("IncomeStatement") >= 0);
    }

    [Fact]
    public void GetGroupCount_Consistent()
    {
        var doc = CreateFinancialOutlineDoc();
        Assert.Equal(doc.GetGroupCount("IncomeStatement"), doc.GetGroupCount("IncomeStatement"));
    }

    [Fact]
    public void GetGroupCount_Zero_ForUnmodifiedSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Plain");
        doc.SetCellValue("Plain", 0, 0, "No groups here");
        Assert.Equal(0, doc.GetGroupCount("Plain"));
    }

    [Fact]
    public void GetGroupCount_AfterAddGroup_Increases()
    {
        var doc = CreateFinancialOutlineDoc();
        var before = doc.GetGroupCount("IncomeStatement");
        doc.AddGroup("IncomeStatement", 2, 4, "row"); // Revenue detail rows
        Assert.Equal(before + 1, doc.GetGroupCount("IncomeStatement"));
    }

    [Fact]
    public void GetGroupCount_SaveLoad_Consistent()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 5, 7, "row"); // COGS detail
        var before = doc.GetGroupCount("IncomeStatement");
        var path = TempFile("gc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetGroupCount("IncomeStatement"));
    }

    // -------------------------------------------------------------------------
    // AddGroup
    // -------------------------------------------------------------------------

    [Fact]
    public void AddGroup_NoThrow()
    {
        var doc = CreateFinancialOutlineDoc();
        var ex = Record.Exception(() => doc.AddGroup("IncomeStatement", 9, 13, "row"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddGroup_Increases_Count()
    {
        var doc = CreateFinancialOutlineDoc();
        var before = doc.GetGroupCount("IncomeStatement");
        doc.AddGroup("IncomeStatement", 2, 4, "row");
        Assert.Equal(before + 1, doc.GetGroupCount("IncomeStatement"));
    }

    [Fact]
    public void AddGroup_SaveLoad_Persists()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 9, 13, "row");
        var before = doc.GetGroupCount("IncomeStatement");
        var path = TempFile("ag_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetGroupCount("IncomeStatement"));
    }

    [Fact]
    public void AddGroup_Multiple()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 2, 4, "row");   // Revenue detail
        doc.AddGroup("IncomeStatement", 5, 7, "row");   // COGS detail
        doc.AddGroup("IncomeStatement", 9, 13, "row");  // OpEx detail
        Assert.Equal(3, doc.GetGroupCount("IncomeStatement"));
    }

    [Fact]
    public void AddGroup_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 2, 4, "row");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddGroup_Then_GetCellValue_NoThrow()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 5, 7, "row");
        var ex = Record.Exception(() => doc.GetCellValue("IncomeStatement", 1, 0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetGroupRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGroupRange_NoThrow()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 2, 4, "row");
        var ex = Record.Exception(() => doc.GetGroupRange("IncomeStatement", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetGroupRange_NonNull()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 9, 13, "row");
        Assert.NotNull(doc.GetGroupRange("IncomeStatement", 0));
    }

    [Fact]
    public void GetGroupRange_Consistent()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 5, 7, "row");
        Assert.Equal(doc.GetGroupRange("IncomeStatement", 0), doc.GetGroupRange("IncomeStatement", 0));
    }

    [Fact]
    public void GetGroupRange_SaveLoad_Consistent()
    {
        var doc = CreateFinancialOutlineDoc();
        doc.AddGroup("IncomeStatement", 2, 4, "row");
        var path = TempFile("gr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetGroupRange("IncomeStatement", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddGroup_GetGroupCount_GetGroupRange_SaveToFile_Pipeline()
    {
        // Management accounting — quarterly budget vs actual variance analysis with drill-down groups
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("BudgetVsActual");
        string[] headers = { "Cost Centre", "Budget Q1", "Actual Q1", "Var Q1", "Budget Q2", "Actual Q2", "Var Q2", "Full Year Budget", "Full Year Actual", "FY Var" };
        for (int c = 0; c < headers.Length; c++)
            doc.SetCellValue("BudgetVsActual", 0, c, headers[c]);

        // Cost centre hierarchy
        string[][] rows = {
            new[] { "1000 Sales", "500000", "523000", "23000", "510000", "498000", "-12000", "2040000", "2021000", "-19000" },
            new[] { "1001 Field Sales", "300000", "315000", "15000", "306000", "299000", "-7000", "1224000", "1214000", "-10000" },
            new[] { "1002 Inside Sales", "120000", "128000", "8000", "122000", "119000", "-3000", "488000", "492000", "4000" },
            new[] { "1003 Channel Sales", "80000", "80000", "0", "82000", "80000", "-2000", "328000", "315000", "-13000" },
            new[] { "2000 Marketing", "200000", "215000", "15000", "205000", "198000", "-7000", "820000", "826000", "6000" },
            new[] { "2001 Digital Mktg", "80000", "92000", "12000", "82000", "78000", "-4000", "328000", "340000", "12000" },
            new[] { "2002 Events", "60000", "65000", "5000", "61000", "60000", "-1000", "244000", "250000", "6000" },
            new[] { "2003 Content", "60000", "58000", "-2000", "62000", "60000", "-2000", "248000", "236000", "-12000" },
            new[] { "3000 R&D", "400000", "388000", "-12000", "410000", "420000", "10000", "1640000", "1608000", "-32000" },
            new[] { "3001 Product Dev", "250000", "242000", "-8000", "256000", "262000", "6000", "1024000", "1004000", "-20000" },
            new[] { "3002 QA", "100000", "96000", "-4000", "102000", "106000", "4000", "408000", "404000", "-4000" },
            new[] { "3003 DevOps", "50000", "50000", "0", "52000", "52000", "0", "208000", "200000", "-8000" },
        };
        for (int i = 0; i < rows.Length; i++)
            for (int c = 0; c < rows[i].Length; c++)
                doc.SetCellValue("BudgetVsActual", i + 1, c, rows[i][c]);

        Assert.Equal(0, doc.GetGroupCount("BudgetVsActual"));

        // AddGroup — Sales sub-centres (rows 2-4 = indices 1-3 as detail under row 0)
        doc.AddGroup("BudgetVsActual", 2, 4, "row");
        Assert.Equal(1, doc.GetGroupCount("BudgetVsActual"));

        // AddGroup — Marketing sub-centres (rows 6-8)
        doc.AddGroup("BudgetVsActual", 6, 8, "row");
        Assert.Equal(2, doc.GetGroupCount("BudgetVsActual"));

        // AddGroup — R&D sub-centres (rows 10-12)
        doc.AddGroup("BudgetVsActual", 10, 12, "row");
        Assert.Equal(3, doc.GetGroupCount("BudgetVsActual"));

        // Consistent
        Assert.Equal(doc.GetGroupCount("BudgetVsActual"), doc.GetGroupCount("BudgetVsActual"));

        // GetGroupRange
        var range0 = doc.GetGroupRange("BudgetVsActual", 0);
        Assert.NotNull(range0);
        Assert.Equal(range0, doc.GetGroupRange("BudgetVsActual", 0)); // consistent

        var range1 = doc.GetGroupRange("BudgetVsActual", 1);
        Assert.NotNull(range1);

        var range2 = doc.GetGroupRange("BudgetVsActual", 2);
        Assert.NotNull(range2);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCellValue preserved
        Assert.Equal("1000 Sales", doc.GetCellValue("BudgetVsActual", 1, 0));

        // SaveToFile
        var path = TempFile("dogfood_budget_variance.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetGroupCount("BudgetVsActual"));
        Assert.NotNull(loaded.GetGroupRange("BudgetVsActual", 0));
        Assert.NotNull(loaded.GetGroupRange("BudgetVsActual", 2));
        Assert.Equal("1000 Sales", loaded.GetCellValue("BudgetVsActual", 1, 0));

        // AddGroup on loaded — second sheet
        loaded.AddSheet("Headcount");
        loaded.SetCellValue("Headcount", 0, 0, "Department");
        loaded.SetCellValue("Headcount", 0, 1, "HC Budget");
        loaded.SetCellValue("Headcount", 0, 2, "HC Actual");
        for (int i = 1; i <= 6; i++)
        {
            loaded.SetCellValue("Headcount", i, 0, $"Dept{i}");
            loaded.SetCellValue("Headcount", i, 1, (10 * i).ToString());
            loaded.SetCellValue("Headcount", i, 2, (10 * i + 1).ToString());
        }
        loaded.AddGroup("Headcount", 2, 3, "row");
        Assert.Equal(0 + 1, loaded.GetGroupCount("Headcount")); // new sheet starts at 0

        // Final save
        var path2 = TempFile("dogfood_budget_variance_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(3, loaded2.GetGroupCount("BudgetVsActual"));
        Assert.NotNull(loaded2.GetGroupRange("BudgetVsActual", 0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.AddGroup("BudgetVsActual", 5, 7, "row"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
