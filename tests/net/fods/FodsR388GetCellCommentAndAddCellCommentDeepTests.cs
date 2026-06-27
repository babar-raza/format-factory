// Tests for FodsDocument.GetCellComment, AddCellComment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R388

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R388: Tests for FodsDocument.GetCellComment, AddCellComment deeper.
/// GetCellComment(sheetName, row, col): returns the annotation comment text of a cell.
/// AddCellComment(sheetName, row, col, author, text): adds an annotation to a cell.
/// Covers: GetCellComment no-throw; GetCellComment non-null; GetCellComment consistent;
/// GetCellComment save-load; AddCellComment no-throw;
/// AddCellComment then GetCellComment updated; AddCellComment value unchanged;
/// AddCellComment then GetSheetCount unchanged; AddCellComment then ExportToHtml no-throw;
/// AddCellComment override; AddCellComment save-load; AddCellComment multiple cells;
/// dogfood CreateDoc→AddCellComment→GetCellComment→SaveToFile pipeline.
/// </summary>
public class FodsR388GetCellCommentAndAddCellCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR388GetCellCommentAndAddCellCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR388_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreatePlainDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Analysis");
        doc.SetCellValue("Analysis", 0, 0, "Region");
        doc.SetCellValue("Analysis", 0, 1, "Revenue");
        doc.SetCellValue("Analysis", 0, 2, "Target");
        doc.SetCellValue("Analysis", 0, 3, "Variance");
        doc.SetCellValue("Analysis", 1, 0, "London");
        doc.SetCellValue("Analysis", 1, 1, "4200000");
        doc.SetCellValue("Analysis", 1, 2, "4000000");
        doc.SetCellValue("Analysis", 1, 3, "200000");
        doc.SetCellValue("Analysis", 2, 0, "Manchester");
        doc.SetCellValue("Analysis", 2, 1, "1850000");
        doc.SetCellValue("Analysis", 2, 2, "2100000");
        doc.SetCellValue("Analysis", 2, 3, "-250000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellComment
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetCellComment("Analysis", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellComment_NonNull()
    {
        var doc = CreatePlainDoc();
        Assert.NotNull(doc.GetCellComment("Analysis", 0, 0));
    }

    [Fact]
    public void GetCellComment_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.AddCellComment("Analysis", 1, 3, "Analyst", "Exceptionally strong Q4 performance in London.");
        Assert.Equal(doc.GetCellComment("Analysis", 1, 3), doc.GetCellComment("Analysis", 1, 3));
    }

    [Fact]
    public void GetCellComment_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.AddCellComment("Analysis", 2, 3, "CFO", "Manchester underperformed: investigation ongoing.");
        var before = doc.GetCellComment("Analysis", 2, 3);
        var path = TempFile("gcc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellComment("Analysis", 2, 3));
    }

    // -------------------------------------------------------------------------
    // AddCellComment
    // -------------------------------------------------------------------------

    [Fact]
    public void AddCellComment_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.AddCellComment("Analysis", 1, 1, "Auditor", "Verified against GL."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddCellComment_Then_GetCellComment_Updated()
    {
        var doc = CreatePlainDoc();
        doc.AddCellComment("Analysis", 1, 1, "Finance", "Excludes intercompany transactions.");
        Assert.Equal("Excludes intercompany transactions.", doc.GetCellComment("Analysis", 1, 1));
    }

    [Fact]
    public void AddCellComment_ValueUnchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetCellValue("Analysis", 1, 1);
        doc.AddCellComment("Analysis", 1, 1, "Auditor", "Revenue verified.");
        Assert.Equal(before, doc.GetCellValue("Analysis", 1, 1));
    }

    [Fact]
    public void AddCellComment_Then_GetSheetCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetSheetCount();
        doc.AddCellComment("Analysis", 0, 0, "Editor", "Header row.");
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void AddCellComment_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.AddCellComment("Analysis", 1, 3, "Finance", "Variance review required.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddCellComment_Override()
    {
        var doc = CreatePlainDoc();
        doc.AddCellComment("Analysis", 2, 3, "Draft", "Provisional.");
        doc.AddCellComment("Analysis", 2, 3, "Final", "Confirmed by CFO.");
        Assert.Equal("Confirmed by CFO.", doc.GetCellComment("Analysis", 2, 3));
    }

    [Fact]
    public void AddCellComment_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.AddCellComment("Analysis", 2, 1, "Auditor", "Restated: original was 1920000.");
        var path = TempFile("acc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("Restated: original was 1920000.", loaded.GetCellComment("Analysis", 2, 1));
    }

    [Fact]
    public void AddCellComment_MultipleCells()
    {
        var doc = CreatePlainDoc();
        doc.AddCellComment("Analysis", 1, 1, "Analyst", "Revenue A");
        doc.AddCellComment("Analysis", 1, 2, "Analyst", "Target A");
        doc.AddCellComment("Analysis", 2, 1, "Analyst", "Revenue B");
        Assert.Equal("Revenue A", doc.GetCellComment("Analysis", 1, 1));
        Assert.Equal("Target A", doc.GetCellComment("Analysis", 1, 2));
        Assert.Equal("Revenue B", doc.GetCellComment("Analysis", 2, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellComment_AddCellComment_SaveToFile_Pipeline()
    {
        // Audit — UK National Audit Office (NAO) Value for Money Study Workbook
        // Annotated spreadsheet: auditor notes, peer review comments, evidence citations
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("VFM Analysis");
        doc.AddSheet("Evidence Log");

        // Sheet 1: VFM Analysis data
        doc.SetCellValue("VFM Analysis", 0, 0, "Programme");
        doc.SetCellValue("VFM Analysis", 0, 1, "Dept");
        doc.SetCellValue("VFM Analysis", 0, 2, "Budget (£m)");
        doc.SetCellValue("VFM Analysis", 0, 3, "Outturn (£m)");
        doc.SetCellValue("VFM Analysis", 0, 4, "Variance (£m)");
        doc.SetCellValue("VFM Analysis", 0, 5, "Deliverables Met");
        doc.SetCellValue("VFM Analysis", 0, 6, "VFM Rating");

        string[,] programmes = {
            { "Universal Credit Migration", "DWP", "1420", "1687", "267", "72%", "Poor" },
            { "Test and Trace Programme", "DHSC", "15700", "22000", "6300", "45%", "Very Poor" },
            { "NHS Nightingale Hospitals", "DHSC", "220", "532", "312", "8%", "Poor" },
            { "HS2 Phase 1 Construction", "DfT", "35700", "44000", "8300", "N/A", "Poor" },
            { "Defence Equipment Plan", "MOD", "242000", "261000", "19000", "81%", "Moderate" },
            { "Levelling Up Fund Round 1", "DLUHC", "1700", "1698", "-2", "93%", "Good" },
            { "HMRC Making Tax Digital", "HMRC", "1300", "1140", "-160", "88%", "Good" }
        };

        for (int i = 0; i < programmes.GetLength(0); i++)
        {
            for (int j = 0; j < programmes.GetLength(1); j++)
                doc.SetCellValue("VFM Analysis", i + 1, j, programmes[i, j]);
        }

        Assert.Equal(2, doc.GetSheetCount());

        // GetCellComment — initially empty
        var initialComment = doc.GetCellComment("VFM Analysis", 0, 0);
        Assert.NotNull(initialComment);

        // AddCellComment — auditor annotations
        // NAO Auditor primary comments
        doc.AddCellComment("VFM Analysis", 2, 4, "J.Harrison (NAO)", "£6.3bn overspend confirmed by PAC report HC 182 (2021-22). Contractor procurement without competitive tender.");
        Assert.Equal("£6.3bn overspend confirmed by PAC report HC 182 (2021-22). Contractor procurement without competitive tender.", doc.GetCellComment("VFM Analysis", 2, 4));

        doc.AddCellComment("VFM Analysis", 4, 4, "J.Harrison (NAO)", "Scope change accounts for £7.8bn of £8.3bn variance. Refer to IPA Red rating Q3 2024.");
        Assert.Equal("Refer to IPA Red rating Q3 2024.", doc.GetCellComment("VFM Analysis", 4, 4).Split(". ")[1]);

        doc.AddCellComment("VFM Analysis", 1, 5, "J.Harrison (NAO)", "72% deliverables met but 28% critical milestones missed including full digital rollout.");
        doc.AddCellComment("VFM Analysis", 7, 6, "J.Harrison (NAO)", "MTD: positive VFM achieved through HMRC operational savings of c.£300m p.a.");

        // Peer reviewer comments
        doc.AddCellComment("VFM Analysis", 0, 6, "S.Chen (NAO Quality Review)", "VFM ratings applied per NAO VFM Framework (2021). 5-point scale: Very Poor/Poor/Moderate/Good/Very Good.");

        // Value unchanged after comments
        Assert.Equal("Test and Trace Programme", doc.GetCellValue("VFM Analysis", 2, 0));
        Assert.Equal("22000", doc.GetCellValue("VFM Analysis", 2, 3));
        Assert.Equal(2, doc.GetSheetCount());

        // Override comment: updated after PAC hearing
        doc.AddCellComment("VFM Analysis", 3, 6, "J.Harrison (NAO)", "Originally 'Very Poor' — raised to 'Poor' following DH evidence to PAC Jan 2024.");
        Assert.Equal("Originally 'Very Poor' — raised to 'Poor' following DH evidence to PAC Jan 2024.", doc.GetCellComment("VFM Analysis", 3, 6));

        // Sheet 2: Evidence Log
        doc.SetCellValue("Evidence Log", 0, 0, "Evidence Ref");
        doc.SetCellValue("Evidence Log", 0, 1, "Source");
        doc.SetCellValue("Evidence Log", 0, 2, "Date");
        doc.SetCellValue("Evidence Log", 0, 3, "Verified");
        doc.SetCellValue("Evidence Log", 1, 0, "HC 182 (2021-22)");
        doc.SetCellValue("Evidence Log", 1, 1, "House of Commons PAC");
        doc.SetCellValue("Evidence Log", 1, 2, "2022-03-14");
        doc.SetCellValue("Evidence Log", 1, 3, "Yes");
        doc.SetCellValue("Evidence Log", 2, 0, "NAO VFM Framework");
        doc.SetCellValue("Evidence Log", 2, 1, "NAO Internal");
        doc.SetCellValue("Evidence Log", 2, 2, "2021-09-01");
        doc.SetCellValue("Evidence Log", 2, 3, "Yes");
        doc.AddCellComment("Evidence Log", 1, 3, "S.Chen (NAO QR)", "Cross-checked against Commons Library database — confirmed.");

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("dogfood_nao_vfm_workbook.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify comments
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(2, loaded.GetSheetCount());
        Assert.Equal("Test and Trace Programme", loaded.GetCellValue("VFM Analysis", 2, 0));

        // Update comment after correction from DHSC
        loaded.AddCellComment("VFM Analysis", 2, 3, "DHSC Response", "DHSC revised outturn figure to £21.8bn in ARA 2023-24. Correction applied.");
        Assert.Equal("DHSC revised outturn figure to £21.8bn in ARA 2023-24. Correction applied.", loaded.GetCellComment("VFM Analysis", 2, 3));

        // Final save
        var path2 = TempFile("dogfood_nao_vfm_workbook_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.Equal("DHSC revised outturn figure to £21.8bn in ARA 2023-24. Correction applied.", final.GetCellComment("VFM Analysis", 2, 3));

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.AddCellComment("VFM Analysis", 0, 0, "Admin", "Archived."));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
