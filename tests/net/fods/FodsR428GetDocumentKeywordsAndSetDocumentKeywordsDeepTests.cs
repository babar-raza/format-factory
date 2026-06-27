// Tests for FodsDocument.GetDocumentKeywords, SetDocumentKeywords deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R428

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R428: Tests for FodsDocument.GetDocumentKeywords, SetDocumentKeywords deeper.
/// GetDocumentKeywords(): returns the document keyword/tag string from metadata.
/// SetDocumentKeywords(keywords): sets the keyword metadata string on the document.
/// Covers: GetDocumentKeywords no-throw; GetDocumentKeywords non-null;
/// SetDocumentKeywords no-throw; SetDocumentKeywords updates value;
/// SetDocumentKeywords overwritable; SetDocumentKeywords save-load consistent;
/// GetDocumentKeywords consistent; dogfood pipeline.
/// </summary>
public class FodsR428GetDocumentKeywordsAndSetDocumentKeywordsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR428GetDocumentKeywordsAndSetDocumentKeywordsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR428_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetDocumentKeywords
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentKeywords_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetDocumentKeywords());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentKeywords_NonNull()
    {
        var doc = FodsDocument.CreateEmpty();
        Assert.NotNull(doc.GetDocumentKeywords());
    }

    [Fact]
    public void GetDocumentKeywords_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentKeywords("finance; budget; 2024");
        Assert.Equal(doc.GetDocumentKeywords(), doc.GetDocumentKeywords());
    }

    // -------------------------------------------------------------------------
    // SetDocumentKeywords
    // -------------------------------------------------------------------------

    [Fact]
    public void SetDocumentKeywords_NoThrow()
    {
        var doc = FodsDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.SetDocumentKeywords("test; keywords; spreadsheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetDocumentKeywords_UpdatesValue()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentKeywords("climate; data; analysis");
        Assert.Equal("climate; data; analysis", doc.GetDocumentKeywords());
    }

    [Fact]
    public void SetDocumentKeywords_Overwritable()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentKeywords("initial; keywords");
        doc.SetDocumentKeywords("updated; revised; keywords; 2024");
        Assert.Equal("updated; revised; keywords; 2024", doc.GetDocumentKeywords());
    }

    [Fact]
    public void SetDocumentKeywords_SaveLoad_Consistent()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentKeywords("macroeconomics; fiscal; OBR; HMT");
        var path = TempFile("kw_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("macroeconomics; fiscal; OBR; HMT", loaded.GetDocumentKeywords());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDocumentKeywords_SetDocumentKeywords_Pipeline()
    {
        // Statistics — ONS / DCMS: UK Creative Industries Economic Estimates 2024
        // Annual statistical release covering GVA, employment, and trade in creative sectors
        // Document keywords support discoverability in ONS metadata catalogue

        var doc = FodsDocument.CreateEmpty();
        doc.SetDocumentTitle("UK Creative Industries Economic Estimates 2024");
        doc.SetDocumentAuthor("ONS / DCMS Economic Statistics Group");
        doc.SetDocumentSubject("Creative Industries GVA, Employment and Trade Statistics");
        doc.SetDocumentKeywords("creative industries; GVA; employment; digital; film; music; publishing; design; architecture; ONS; DCMS; 2024");

        var kw0 = doc.GetDocumentKeywords();
        Assert.NotNull(kw0);
        Assert.NotEmpty(kw0);
        Assert.Equal(kw0, doc.GetDocumentKeywords()); // consistent

        // Sheet 1: Creative sector GVA estimates
        doc.AddSheet("GVA_Estimates");
        doc.SetCellValue("GVA_Estimates", 0, 0, "Sector");
        doc.SetCellValue("GVA_Estimates", 0, 1, "GVA_2022_GBPbn");
        doc.SetCellValue("GVA_Estimates", 0, 2, "GVA_2023_GBPbn");
        doc.SetCellValue("GVA_Estimates", 0, 3, "YoY_Change_Pct");
        doc.SetCellValue("GVA_Estimates", 0, 4, "Share_UK_GVA_Pct");

        string[] sectors = {
            "Advertising", "Architecture", "Crafts", "Design", "Fashion",
            "Film_TV_Video", "IT_Software", "Publishing", "Music_Performing_Arts",
            "Video_Games", "Radio_Photography", "Museums_Galleries"
        };
        double[] gva2022 = { 17.8, 6.3, 0.5, 4.2, 4.7, 11.6, 98.3, 10.9, 7.4, 5.2, 3.8, 2.1 };
        double[] gva2023 = { 18.9, 6.7, 0.5, 4.5, 5.1, 12.4, 104.6, 11.2, 7.9, 6.1, 4.0, 2.2 };

        for (int i = 0; i < sectors.Length; i++)
        {
            double yoy = (gva2023[i] - gva2022[i]) / gva2022[i] * 100;
            double share = gva2023[i] / 650.0 * 100; // approx UK GVA
            doc.SetCellValue("GVA_Estimates", i + 1, 0, sectors[i]);
            doc.SetCellValue("GVA_Estimates", i + 1, 1, gva2022[i].ToString("F1"));
            doc.SetCellValue("GVA_Estimates", i + 1, 2, gva2023[i].ToString("F1"));
            doc.SetCellValue("GVA_Estimates", i + 1, 3, yoy.ToString("F1"));
            doc.SetCellValue("GVA_Estimates", i + 1, 4, share.ToString("F2"));
        }

        // Sheet 2: Employment estimates
        doc.AddSheet("Employment");
        doc.SetCellValue("Employment", 0, 0, "Sector");
        doc.SetCellValue("Employment", 0, 1, "Employment_2023_000s");
        doc.SetCellValue("Employment", 0, 2, "Self_Employed_Pct");
        doc.SetCellValue("Employment", 0, 3, "Female_Share_Pct");
        doc.SetCellValue("Employment", 0, 4, "Regional_Concentration");

        double[] emp = { 245, 103, 22, 72, 88, 197, 1842, 186, 143, 92, 68, 41 };
        double[] selfEmp = { 28.4, 41.2, 55.7, 38.9, 34.6, 22.8, 12.4, 31.7, 47.2, 19.3, 39.8, 26.5 };
        double[] femShare = { 52.3, 41.8, 64.2, 55.7, 68.4, 31.6, 24.9, 49.2, 48.7, 22.1, 39.8, 57.4 };
        string[] regConc = { "London", "London", "Distributed", "London", "London",
                              "London/SE", "Distributed", "London/SE", "London", "Distributed", "Distributed", "London" };

        for (int i = 0; i < sectors.Length; i++)
        {
            doc.SetCellValue("Employment", i + 1, 0, sectors[i]);
            doc.SetCellValue("Employment", i + 1, 1, emp[i].ToString("F0"));
            doc.SetCellValue("Employment", i + 1, 2, selfEmp[i].ToString("F1"));
            doc.SetCellValue("Employment", i + 1, 3, femShare[i].ToString("F1"));
            doc.SetCellValue("Employment", i + 1, 4, regConc[i]);
        }

        // Update keywords to reflect full content
        doc.SetDocumentKeywords("creative industries; GVA; employment; gender; self-employment; regional; digital; ONS; DCMS; 2024; statistical release; economic estimates");
        var kw1 = doc.GetDocumentKeywords();
        Assert.NotNull(kw1);
        Assert.NotEqual(kw0, kw1); // updated
        Assert.Equal(kw1, doc.GetDocumentKeywords()); // consistent after update

        // Sheet count
        Assert.True(doc.GetSheetCount() >= 2);

        // SaveToFile
        var path1 = TempFile("ons_creative_industries_2024.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(kw1, loaded.GetDocumentKeywords());
        Assert.Equal(doc.GetDocumentTitle(), loaded.GetDocumentTitle());
        Assert.Equal(doc.GetDocumentAuthor(), loaded.GetDocumentAuthor());
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());

        // Further update keywords after load
        loaded.SetDocumentKeywords("creative industries; GVA; employment; trade; exports; 2024; FINAL");
        var kw2 = loaded.GetDocumentKeywords();
        Assert.Equal("creative industries; GVA; employment; trade; exports; 2024; FINAL", kw2);

        var path2 = TempFile("ons_creative_industries_2024_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.Equal(kw2, final.GetDocumentKeywords());

        var ex1 = Record.Exception(() => final.GetDocumentKeywords());
        var ex2 = Record.Exception(() => final.SetDocumentKeywords("any; value"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
