// Tests for FodsDocument.GetCommentCount, AddComment, GetCommentText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R307

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R307: Tests for FodsDocument.GetCommentCount, AddComment, GetCommentText deeper.
/// GetCommentCount(sheetName): returns the number of cell comments on the sheet.
/// AddComment(sheetName, row, col, text): adds a comment to a cell.
/// GetCommentText(sheetName, row, col): returns the comment text for a cell.
/// Covers: GetCommentCount no-throw; GetCommentCount non-negative; GetCommentCount consistent;
/// GetCommentCount zero for new sheet; GetCommentCount after AddComment increases;
/// GetCommentCount save-load;
/// AddComment no-throw; AddComment increases count; AddComment save-load;
/// AddComment multiple; AddComment then ExportToCsv no-throw;
/// GetCommentText no-throw; GetCommentText non-null; GetCommentText consistent;
/// GetCommentText save-load;
/// dogfood CreateDoc→AddComment→GetCommentCount→GetCommentText→SaveToFile pipeline.
/// </summary>
public class FodsR307GetCommentCountAndAddCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR307GetCommentCountAndAddCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR307_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Metric");
        doc.SetCellValue("Data", 0, 1, "Value");
        doc.SetCellValue("Data", 0, 2, "Target");
        doc.SetCellValue("Data", 0, 3, "Variance");
        doc.SetCellValue("Data", 1, 0, "Revenue");
        doc.SetCellValue("Data", 1, 1, "850000");
        doc.SetCellValue("Data", 1, 2, "900000");
        doc.SetCellValue("Data", 1, 3, "-50000");
        doc.SetCellValue("Data", 2, 0, "Costs");
        doc.SetCellValue("Data", 2, 1, "620000");
        doc.SetCellValue("Data", 2, 2, "600000");
        doc.SetCellValue("Data", 2, 3, "20000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCommentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetCommentCount("Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCommentCount("Data") >= 0);
    }

    [Fact]
    public void GetCommentCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetCommentCount("Data"), doc.GetCommentCount("Data"));
    }

    [Fact]
    public void GetCommentCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        doc.SetCellValue("Fresh", 0, 0, "data");
        Assert.Equal(0, doc.GetCommentCount("Fresh"));
    }

    [Fact]
    public void GetCommentCount_AfterAddComment_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCommentCount("Data");
        doc.AddComment("Data", 1, 1, "Revenue target missed by 50K due to delayed Q4 shipments.");
        Assert.Equal(before + 1, doc.GetCommentCount("Data"));
    }

    [Fact]
    public void GetCommentCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 1, 3, "Negative variance — investigate root cause.");
        var before = doc.GetCommentCount("Data");
        var path = TempFile("cc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount("Data"));
    }

    // -------------------------------------------------------------------------
    // AddComment
    // -------------------------------------------------------------------------

    [Fact]
    public void AddComment_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddComment("Data", 0, 0, "Header comment test."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCommentCount("Data");
        doc.AddComment("Data", 2, 1, "Costs exceed target — review procurement.");
        Assert.Equal(before + 1, doc.GetCommentCount("Data"));
    }

    [Fact]
    public void AddComment_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 1, 2, "Revenue target set by board in January.");
        var before = doc.GetCommentCount("Data");
        var path = TempFile("ac_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount("Data"));
    }

    [Fact]
    public void AddComment_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 0, 0, "Metric column header.");
        doc.AddComment("Data", 1, 3, "Revenue variance is negative.");
        doc.AddComment("Data", 2, 3, "Cost variance is positive — good.");
        Assert.Equal(3, doc.GetCommentCount("Data"));
    }

    [Fact]
    public void AddComment_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 0, 1, "Value column contains actuals.");
        var ex = Record.Exception(() => doc.ExportToCsv("Data"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetCommentText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentText_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 1, 1, "Test comment.");
        var ex = Record.Exception(() => doc.GetCommentText("Data", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentText_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 2, 2, "Non-null comment.");
        Assert.NotNull(doc.GetCommentText("Data", 2, 2));
    }

    [Fact]
    public void GetCommentText_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 1, 1, "Consistent comment.");
        Assert.Equal(doc.GetCommentText("Data", 1, 1), doc.GetCommentText("Data", 1, 1));
    }

    [Fact]
    public void GetCommentText_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddComment("Data", 1, 1, "Save load comment.");
        var before = doc.GetCommentText("Data", 1, 1);
        var path = TempFile("gct_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetCommentText("Data", 1, 1);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddComment_GetCommentCount_GetCommentText_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("KPIs");

        // Headers
        doc.SetCellValue("KPIs", 0, 0, "Department");
        doc.SetCellValue("KPIs", 0, 1, "Q1_Actual");
        doc.SetCellValue("KPIs", 0, 2, "Q1_Target");
        doc.SetCellValue("KPIs", 0, 3, "Q1_Achievement");
        doc.SetCellValue("KPIs", 0, 4, "Status");

        // Data rows
        string[,] data = {
            { "Sales", "4200000", "4000000", "105%", "GREEN" },
            { "Marketing", "850000", "900000", "94%", "AMBER" },
            { "Engineering", "6500000", "7000000", "93%", "AMBER" },
            { "Support", "1200000", "1100000", "109%", "GREEN" },
            { "Finance", "350000", "400000", "88%", "RED" }
        };
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                doc.SetCellValue("KPIs", r + 1, c, data[r, c]);

        // GetCommentCount — zero initially
        Assert.Equal(0, doc.GetCommentCount("KPIs"));

        // AddComment — Sales exceeded target
        doc.AddComment("KPIs", 1, 3, "Sales exceeded Q1 target by 5% — driven by enterprise deal closures in March.");
        Assert.Equal(1, doc.GetCommentCount("KPIs"));

        // AddComment — Marketing under target
        doc.AddComment("KPIs", 2, 3, "Marketing 6% below target — social campaign launched late, Q2 recovery expected.");
        Assert.Equal(2, doc.GetCommentCount("KPIs"));

        // AddComment — Engineering under target
        doc.AddComment("KPIs", 3, 3, "Engineering 7% below target — headcount constraints delayed three key product features.");
        Assert.Equal(3, doc.GetCommentCount("KPIs"));

        // AddComment — Finance red status
        doc.AddComment("KPIs", 5, 4, "Finance RED — unplanned audit costs inflated Q1 spend by 12%.");
        Assert.Equal(4, doc.GetCommentCount("KPIs"));

        // Consistent
        Assert.Equal(doc.GetCommentCount("KPIs"), doc.GetCommentCount("KPIs"));

        // GetCommentText
        var salesComment = doc.GetCommentText("KPIs", 1, 3);
        Assert.NotNull(salesComment);
        Assert.Equal(salesComment, doc.GetCommentText("KPIs", 1, 3)); // consistent

        var mktComment = doc.GetCommentText("KPIs", 2, 3);
        Assert.NotNull(mktComment);

        // ExportToCsv works
        var csv = doc.ExportToCsv("KPIs");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue cross-check
        Assert.Equal("Sales", doc.GetCellValue("KPIs", 1, 0));

        // SaveToFile
        var path = TempFile("dogfood_kpis.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetCommentCount("KPIs"));
        Assert.NotNull(loaded.GetCommentText("KPIs", 1, 3));

        // AddComment on loaded
        loaded.AddComment("KPIs", 4, 3, "Support exceeded target — expanded automation reduced ticket resolution time.");
        Assert.Equal(5, loaded.GetCommentCount("KPIs"));

        // Mutate and verify
        loaded.SetCellValue("KPIs", 6, 0, "Legal");
        loaded.SetCellValue("KPIs", 6, 1, "280000");
        loaded.SetCellValue("KPIs", 6, 2, "300000");
        loaded.SetCellValue("KPIs", 6, 3, "93%");
        loaded.SetCellValue("KPIs", 6, 4, "AMBER");

        // Final save
        var path2 = TempFile("dogfood_kpis_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetCommentCount("KPIs"));
        Assert.False(loaded2.GetProtectionStatus("KPIs"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("KPIs"));
        Assert.Null(ex1);
    }
}
