// Tests for FodsDocument.GetCellHyperlink, SetCellHyperlink deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R382

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R382: Tests for FodsDocument.GetCellHyperlink, SetCellHyperlink deeper.
/// GetCellHyperlink(sheetName, row, col): returns the hyperlink URL for a cell, or empty/null.
/// SetCellHyperlink(sheetName, row, col, url): sets a hyperlink on a cell.
/// Covers: GetCellHyperlink no-throw; GetCellHyperlink non-null;
/// GetCellHyperlink consistent; GetCellHyperlink save-load;
/// SetCellHyperlink no-throw; SetCellHyperlink then GetCellHyperlink updated;
/// SetCellHyperlink then GetRowCount unchanged; SetCellHyperlink then GetCellValue unchanged;
/// SetCellHyperlink save-load; SetCellHyperlink multiple cells;
/// SetCellHyperlink then ExportSheetToCsv no-throw;
/// dogfood CreateDoc→SetCellHyperlink→GetCellHyperlink→SaveToFile pipeline.
/// </summary>
public class FodsR382GetCellHyperlinkAndSetCellHyperlinkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR382GetCellHyperlinkAndSetCellHyperlinkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR382_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSampleDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("References");
        doc.SetCellValue("References", 0, 0, "Source");
        doc.SetCellValue("References", 0, 1, "URL");
        doc.SetCellValue("References", 1, 0, "ONS");
        doc.SetCellValue("References", 1, 1, "https://www.ons.gov.uk");
        doc.SetCellValue("References", 2, 0, "GOV.UK");
        doc.SetCellValue("References", 2, 1, "https://www.gov.uk");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellHyperlink
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHyperlink_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetCellHyperlink("References", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellHyperlink_NonNull()
    {
        var doc = CreateSampleDoc();
        Assert.NotNull(doc.GetCellHyperlink("References", 0, 0));
    }

    [Fact]
    public void GetCellHyperlink_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("References", 1, 0, "https://www.ons.gov.uk");
        Assert.Equal(doc.GetCellHyperlink("References", 1, 0),
                     doc.GetCellHyperlink("References", 1, 0));
    }

    [Fact]
    public void GetCellHyperlink_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("References", 1, 0, "https://www.ons.gov.uk/economy");
        var before = doc.GetCellHyperlink("References", 1, 0);
        var path = TempFile("hl_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellHyperlink("References", 1, 0));
    }

    // -------------------------------------------------------------------------
    // SetCellHyperlink
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellHyperlink_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetCellHyperlink("References", 1, 0, "https://www.gov.uk"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellHyperlink_Then_GetCellHyperlink_Updated()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("References", 1, 0, "https://www.ons.gov.uk/statistics");
        Assert.Equal("https://www.ons.gov.uk/statistics", doc.GetCellHyperlink("References", 1, 0));
    }

    [Fact]
    public void SetCellHyperlink_Then_GetRowCount_Unchanged()
    {
        var doc = CreateSampleDoc();
        var before = doc.GetRowCount("References");
        doc.SetCellHyperlink("References", 1, 0, "https://www.gov.uk");
        Assert.Equal(before, doc.GetRowCount("References"));
    }

    [Fact]
    public void SetCellHyperlink_Then_GetCellValue_Unchanged()
    {
        var doc = CreateSampleDoc();
        var valueBefore = doc.GetCellValue("References", 1, 0);
        doc.SetCellHyperlink("References", 1, 0, "https://www.ons.gov.uk");
        Assert.Equal(valueBefore, doc.GetCellValue("References", 1, 0));
    }

    [Fact]
    public void SetCellHyperlink_SaveLoad_Persists()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("References", 2, 0, "https://www.gov.uk/browse");
        var path = TempFile("schl_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("https://www.gov.uk/browse", loaded.GetCellHyperlink("References", 2, 0));
    }

    [Fact]
    public void SetCellHyperlink_MultipleCells()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("References", 1, 0, "https://www.ons.gov.uk");
        doc.SetCellHyperlink("References", 2, 0, "https://www.gov.uk");
        Assert.Equal("https://www.ons.gov.uk", doc.GetCellHyperlink("References", 1, 0));
        Assert.Equal("https://www.gov.uk", doc.GetCellHyperlink("References", 2, 0));
    }

    [Fact]
    public void SetCellHyperlink_Then_ExportSheetToCsv_NoThrow()
    {
        var doc = CreateSampleDoc();
        doc.SetCellHyperlink("References", 1, 1, "https://www.ons.gov.uk");
        var path = TempFile("export.csv");
        var ex = Record.Exception(() => doc.ExportSheetToCsvFile("References", path));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellHyperlink_SetCellHyperlink_SaveToFile_Pipeline()
    {
        // Government — UK Parliament: Committee Report Citation Index
        // Cross-referencing tool linking committee evidence to Hansard records and legislation
        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: Committee Evidence Index
        doc.AddSheet("Evidence_Index");
        string[] evidenceHeaders = { "Ref", "Witness", "Organisation", "Date", "Subject", "Hansard_Link" };
        for (int c = 0; c < evidenceHeaders.Length; c++)
            doc.SetCellValue("Evidence_Index", 0, c, evidenceHeaders[c]);

        string[][] evidenceData = {
            new[] { "EV001", "Dame Sarah Munby", "DSIT Permanent Secretary", "2024-01-16", "Digital Markets Bill progress", "https://hansard.parliament.uk/commons/2024-01-16/debates/2401161000001" },
            new[] { "EV002", "Kirsty Cooper", "Ofcom CEO", "2024-01-23", "Online Safety Act implementation", "https://hansard.parliament.uk/commons/2024-01-23/debates/2401230000002" },
            new[] { "EV003", "Sarah Cardell", "CMA CEO", "2024-02-06", "Competition enforcement AI markets", "https://hansard.parliament.uk/commons/2024-02-06/debates/2402060000003" },
            new[] { "EV004", "John Edwards", "ICO Commissioner", "2024-02-20", "Data protection reform progress", "https://hansard.parliament.uk/commons/2024-02-20/debates/2402200000004" },
            new[] { "EV005", "Edwina Dunn OBE", "Safe Data Trust chair", "2024-03-05", "AI Safety Institute framework", "https://hansard.parliament.uk/commons/2024-03-05/debates/2403050000005" },
            new[] { "EV006", "Nigel Adams MP", "DSIT Minister", "2024-03-19", "AI governance white paper update", "https://hansard.parliament.uk/commons/2024-03-19/debates/2403190000006" },
        };
        for (int r = 0; r < evidenceData.Length; r++)
            for (int c = 0; c < evidenceData[r].Length; c++)
                doc.SetCellValue("Evidence_Index", r + 1, c, evidenceData[r][c]);

        // Sheet 2: Legislation Cross-Reference
        doc.AddSheet("Legislation_Refs");
        string[] legHeaders = { "Act", "Section", "Subject", "Legislation_gov_uk" };
        for (int c = 0; c < legHeaders.Length; c++)
            doc.SetCellValue("Legislation_Refs", 0, c, legHeaders[c]);

        string[][] legData = {
            new[] { "Digital Markets Competition and Consumers Act 2024", "Part 1", "Strategic Market Status", "https://www.legislation.gov.uk/ukpga/2024/13/part/1" },
            new[] { "Online Safety Act 2023", "Part 2", "User-to-user services", "https://www.legislation.gov.uk/ukpga/2023/50/part/2" },
            new[] { "Data Protection Act 2018", "Part 2", "GDPR supplements", "https://www.legislation.gov.uk/ukpga/2018/12/part/2" },
            new[] { "Communications Act 2003", "Part 2", "Ofcom functions", "https://www.legislation.gov.uk/ukpga/2003/21/part/2" },
        };
        for (int r = 0; r < legData.Length; r++)
            for (int c = 0; c < legData[r].Length; c++)
                doc.SetCellValue("Legislation_Refs", r + 1, c, legData[r][c]);

        Assert.Equal(2, doc.GetSheetCount());

        // SetCellHyperlink — evidence Hansard links
        for (int r = 1; r <= evidenceData.Length; r++)
            doc.SetCellHyperlink("Evidence_Index", r, 5, evidenceData[r - 1][5]);

        // Verify hyperlinks set
        for (int r = 1; r <= evidenceData.Length; r++)
            Assert.Equal(evidenceData[r - 1][5], doc.GetCellHyperlink("Evidence_Index", r, 5));

        // Consistent
        Assert.Equal(doc.GetCellHyperlink("Evidence_Index", 1, 5),
                     doc.GetCellHyperlink("Evidence_Index", 1, 5));

        // SetCellHyperlink — legislation links
        for (int r = 1; r <= legData.Length; r++)
            doc.SetCellHyperlink("Legislation_Refs", r, 3, legData[r - 1][3]);

        Assert.Equal("https://www.legislation.gov.uk/ukpga/2024/13/part/1",
                     doc.GetCellHyperlink("Legislation_Refs", 1, 3));

        // Row counts unchanged
        Assert.Equal(7, doc.GetRowCount("Evidence_Index"));
        Assert.Equal(5, doc.GetRowCount("Legislation_Refs"));

        // Cell values preserved
        Assert.Equal("EV001", doc.GetCellValue("Evidence_Index", 1, 0));
        Assert.Equal("Dame Sarah Munby", doc.GetCellValue("Evidence_Index", 1, 1));

        // ExportSheetToCsvFile
        var csvPath = TempFile("evidence_index.csv");
        var exCsv = Record.Exception(() => doc.ExportSheetToCsvFile("Evidence_Index", csvPath));
        Assert.Null(exCsv);

        // SaveToFile
        var path = TempFile("dogfood_parliament_index.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetSheetCount());
        for (int r = 1; r <= evidenceData.Length; r++)
            Assert.Equal(evidenceData[r - 1][5], loaded.GetCellHyperlink("Evidence_Index", r, 5));
        Assert.Equal("https://www.legislation.gov.uk/ukpga/2024/13/part/1",
                     loaded.GetCellHyperlink("Legislation_Refs", 1, 3));
        Assert.Equal("EV001", loaded.GetCellValue("Evidence_Index", 1, 0));

        // Update hyperlink on loaded
        loaded.SetCellHyperlink("Evidence_Index", 1, 5, "https://hansard.parliament.uk/commons/2024-01-16/updated");
        Assert.Equal("https://hansard.parliament.uk/commons/2024-01-16/updated",
                     loaded.GetCellHyperlink("Evidence_Index", 1, 5));

        // Final save
        var path2 = TempFile("dogfood_parliament_index_v2.fods");
        loaded.SaveToFile(path2);
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal("https://hansard.parliament.uk/commons/2024-01-16/updated",
                     loaded2.GetCellHyperlink("Evidence_Index", 1, 5));
        var ex1 = Record.Exception(() => loaded2.GetCellHyperlink("Evidence_Index", 2, 5));
        var ex2 = Record.Exception(() => loaded2.SetCellHyperlink("Legislation_Refs", 1, 3, "https://www.legislation.gov.uk"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
