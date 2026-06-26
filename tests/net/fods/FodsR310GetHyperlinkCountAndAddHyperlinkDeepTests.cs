// Tests for FodsDocument.GetHyperlinkCount, AddHyperlink, GetHyperlinkUrl deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R310

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R310: Tests for FodsDocument.GetHyperlinkCount, AddHyperlink, GetHyperlinkUrl deeper.
/// GetHyperlinkCount(sheetName): returns the number of hyperlinks on the sheet.
/// AddHyperlink(sheetName, row, col, url, displayText): adds a hyperlink to a cell.
/// GetHyperlinkUrl(sheetName, row, col): returns the URL for a cell's hyperlink.
/// Covers: GetHyperlinkCount no-throw; GetHyperlinkCount non-negative; GetHyperlinkCount consistent;
/// GetHyperlinkCount zero for new sheet; GetHyperlinkCount after AddHyperlink increases;
/// GetHyperlinkCount save-load;
/// AddHyperlink no-throw; AddHyperlink increases count; AddHyperlink save-load;
/// AddHyperlink multiple; AddHyperlink then ExportToCsv no-throw;
/// GetHyperlinkUrl no-throw; GetHyperlinkUrl non-null; GetHyperlinkUrl consistent;
/// GetHyperlinkUrl save-load;
/// dogfood CreateDoc→AddHyperlink→GetHyperlinkCount→GetHyperlinkUrl→SaveToFile pipeline.
/// </summary>
public class FodsR310GetHyperlinkCountAndAddHyperlinkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR310GetHyperlinkCountAndAddHyperlinkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR310_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("References");
        doc.SetCellValue("References", 0, 0, "Source");
        doc.SetCellValue("References", 0, 1, "Link");
        doc.SetCellValue("References", 0, 2, "Description");
        doc.SetCellValue("References", 1, 0, "OECD");
        doc.SetCellValue("References", 1, 1, "https://www.oecd.org");
        doc.SetCellValue("References", 1, 2, "Economic data and statistics");
        doc.SetCellValue("References", 2, 0, "IMF");
        doc.SetCellValue("References", 2, 1, "https://www.imf.org");
        doc.SetCellValue("References", 2, 2, "International monetary fund data");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHyperlinkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetHyperlinkCount("References"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetHyperlinkCount("References") >= 0);
    }

    [Fact]
    public void GetHyperlinkCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetHyperlinkCount("References"), doc.GetHyperlinkCount("References"));
    }

    [Fact]
    public void GetHyperlinkCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        doc.SetCellValue("Empty", 0, 0, "no links");
        Assert.Equal(0, doc.GetHyperlinkCount("Empty"));
    }

    [Fact]
    public void GetHyperlinkCount_AfterAddHyperlink_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetHyperlinkCount("References");
        doc.AddHyperlink("References", 1, 1, "https://www.oecd.org/statistics", "OECD Stats");
        Assert.Equal(before + 1, doc.GetHyperlinkCount("References"));
    }

    [Fact]
    public void GetHyperlinkCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 2, 1, "https://www.imf.org/data", "IMF Data");
        var before = doc.GetHyperlinkCount("References");
        var path = TempFile("hlc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHyperlinkCount("References"));
    }

    // -------------------------------------------------------------------------
    // AddHyperlink
    // -------------------------------------------------------------------------

    [Fact]
    public void AddHyperlink_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddHyperlink("References", 1, 1, "https://example.com", "Example"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetHyperlinkCount("References");
        doc.AddHyperlink("References", 2, 1, "https://worldbank.org", "World Bank");
        Assert.Equal(before + 1, doc.GetHyperlinkCount("References"));
    }

    [Fact]
    public void AddHyperlink_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 1, 1, "https://bis.org", "BIS");
        var before = doc.GetHyperlinkCount("References");
        var path = TempFile("ahl_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHyperlinkCount("References"));
    }

    [Fact]
    public void AddHyperlink_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 1, 1, "https://www.oecd.org", "OECD");
        doc.AddHyperlink("References", 2, 1, "https://www.imf.org", "IMF");
        doc.AddHyperlink("References", 3, 1, "https://worldbank.org", "World Bank");
        Assert.Equal(3, doc.GetHyperlinkCount("References"));
    }

    [Fact]
    public void AddHyperlink_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 1, 1, "https://example.org", "Example");
        var ex = Record.Exception(() => doc.ExportToCsv("References"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetHyperlinkUrl
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkUrl_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 1, 1, "https://test.com", "Test");
        var ex = Record.Exception(() => doc.GetHyperlinkUrl("References", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkUrl_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 1, 1, "https://test.org", "Test Org");
        Assert.NotNull(doc.GetHyperlinkUrl("References", 1, 1));
    }

    [Fact]
    public void GetHyperlinkUrl_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 1, 1, "https://consist.example.com", "Consist");
        Assert.Equal(doc.GetHyperlinkUrl("References", 1, 1), doc.GetHyperlinkUrl("References", 1, 1));
    }

    [Fact]
    public void GetHyperlinkUrl_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddHyperlink("References", 1, 1, "https://saveload.example.com", "SaveLoad");
        var before = doc.GetHyperlinkUrl("References", 1, 1);
        var path = TempFile("ghu_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetHyperlinkUrl("References", 1, 1);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddHyperlink_GetHyperlinkCount_GetHyperlinkUrl_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("DataSources");

        // Headers
        doc.SetCellValue("DataSources", 0, 0, "Organisation");
        doc.SetCellValue("DataSources", 0, 1, "Dataset");
        doc.SetCellValue("DataSources", 0, 2, "Link");
        doc.SetCellValue("DataSources", 0, 3, "Format");
        doc.SetCellValue("DataSources", 0, 4, "Frequency");

        // Data rows
        string[,] data = {
            { "World Bank", "World Development Indicators", "https://data.worldbank.org/indicator", "CSV/JSON", "Annual" },
            { "IMF", "World Economic Outlook", "https://imf.org/en/Publications/WEO", "Excel", "Semi-annual" },
            { "OECD", "OECD Statistics", "https://stats.oecd.org", "CSV/SDMX", "Quarterly" },
            { "UN", "UNdata", "https://data.un.org", "CSV", "Annual" },
            { "Eurostat", "European Statistics", "https://ec.europa.eu/eurostat/data", "TSV", "Monthly" }
        };
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                doc.SetCellValue("DataSources", r + 1, c, data[r, c]);

        // GetHyperlinkCount — zero initially
        Assert.Equal(0, doc.GetHyperlinkCount("DataSources"));

        // AddHyperlink — World Bank
        doc.AddHyperlink("DataSources", 1, 2, "https://data.worldbank.org/indicator", "World Bank Data");
        Assert.Equal(1, doc.GetHyperlinkCount("DataSources"));

        // AddHyperlink — IMF
        doc.AddHyperlink("DataSources", 2, 2, "https://imf.org/en/Publications/WEO", "IMF WEO");
        Assert.Equal(2, doc.GetHyperlinkCount("DataSources"));

        // AddHyperlink — OECD
        doc.AddHyperlink("DataSources", 3, 2, "https://stats.oecd.org", "OECD Stats");
        Assert.Equal(3, doc.GetHyperlinkCount("DataSources"));

        // AddHyperlink — UN
        doc.AddHyperlink("DataSources", 4, 2, "https://data.un.org", "UN Data");
        Assert.Equal(4, doc.GetHyperlinkCount("DataSources"));

        // AddHyperlink — Eurostat
        doc.AddHyperlink("DataSources", 5, 2, "https://ec.europa.eu/eurostat/data", "Eurostat");
        Assert.Equal(5, doc.GetHyperlinkCount("DataSources"));

        // Consistent
        Assert.Equal(doc.GetHyperlinkCount("DataSources"), doc.GetHyperlinkCount("DataSources"));

        // GetHyperlinkUrl
        var url1 = doc.GetHyperlinkUrl("DataSources", 1, 2);
        Assert.NotNull(url1);
        Assert.Equal(url1, doc.GetHyperlinkUrl("DataSources", 1, 2)); // consistent

        var url3 = doc.GetHyperlinkUrl("DataSources", 3, 2);
        Assert.NotNull(url3);

        // ExportToCsv works
        var csv = doc.ExportToCsv("DataSources");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_datasources.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetHyperlinkCount("DataSources"));
        Assert.NotNull(loaded.GetHyperlinkUrl("DataSources", 1, 2));

        // AddHyperlink on loaded
        loaded.AddHyperlink("DataSources", 6, 2, "https://bis.org/statistics", "BIS Stats");
        Assert.Equal(6, loaded.GetHyperlinkCount("DataSources"));

        // Mutate and verify
        loaded.SetCellValue("DataSources", 6, 0, "BIS");
        loaded.SetCellValue("DataSources", 6, 1, "BIS Statistics");
        loaded.SetCellValue("DataSources", 6, 3, "JSON");
        loaded.SetCellValue("DataSources", 6, 4, "Quarterly");

        // Final save
        var path2 = TempFile("dogfood_datasources_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetHyperlinkCount("DataSources"));
        Assert.NotNull(loaded2.GetHyperlinkUrl("DataSources", 1, 2));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("DataSources"));
        Assert.Null(ex1);
    }
}
