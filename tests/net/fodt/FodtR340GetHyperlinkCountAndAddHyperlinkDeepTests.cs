// Tests for FodtDocument.GetHyperlinkCount, AddHyperlink, GetHyperlinkUrl deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R340

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R340: Tests for FodtDocument.GetHyperlinkCount, AddHyperlink, GetHyperlinkUrl deeper.
/// GetHyperlinkCount(): returns the number of hyperlinks in the document.
/// AddHyperlink(paragraphIndex, displayText, url): inserts a hyperlink at the given paragraph.
/// GetHyperlinkUrl(index): returns the URL of the hyperlink at the given index.
/// Covers: GetHyperlinkCount no-throw; GetHyperlinkCount non-negative; GetHyperlinkCount consistent;
/// GetHyperlinkCount zero for new doc; GetHyperlinkCount after AddHyperlink increases;
/// GetHyperlinkCount save-load;
/// AddHyperlink no-throw; AddHyperlink increases count; AddHyperlink save-load;
/// AddHyperlink multiple; AddHyperlink then ExportToHtml no-throw;
/// AddHyperlink then ExportToMarkdown no-throw; AddHyperlink then GetWordCount positive;
/// GetHyperlinkUrl no-throw; GetHyperlinkUrl non-null; GetHyperlinkUrl consistent;
/// GetHyperlinkUrl save-load;
/// dogfood CreateDoc→AddHyperlink→GetHyperlinkCount→GetHyperlinkUrl→SaveToFile pipeline.
/// </summary>
public class FodtR340GetHyperlinkCountAndAddHyperlinkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR340GetHyperlinkCountAndAddHyperlinkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR340_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateResearchDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Open Data in Urban Transport Planning: Methodology and Data Sources for Multi-Modal Accessibility Analysis", 1);
        doc.AppendParagraph("Urban transport accessibility analysis requires integration of multiple open data sources including GTFS transit feeds, OpenStreetMap pedestrian network data, census origin-destination matrices, and land use datasets from local planning authorities.");
        doc.AppendParagraph("This paper presents a reproducible analytical framework using Python and R, with all code, data, and results published openly under CC-BY 4.0 licence to support replication and extension by other research groups.");
        doc.InsertHeading(3, "Data Sources and Availability", 2);
        doc.AppendParagraph("General Transit Feed Specification (GTFS) data for UK operators is available from the Department for Transport Bus Open Data Service and from Transport for London (TfL) Unified API.");
        doc.AppendParagraph("Ordnance Survey Open Roads dataset provides topologically corrected road network data at 1:1250 to 1:2500 scale, licensed under Open Government Licence v3.0 and updated quarterly.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHyperlinkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkCount_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.GetHyperlinkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkCount_NonNegative()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetHyperlinkCount() >= 0);
    }

    [Fact]
    public void GetHyperlinkCount_Consistent()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetHyperlinkCount(), doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no hyperlinks.");
        Assert.Equal(0, doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_AfterAddHyperlink_Increases()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetHyperlinkCount();
        doc.AddHyperlink(1, "DfT Bus Open Data", "https://www.bus-data.dft.gov.uk/");
        Assert.Equal(before + 1, doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(2, "TfL Unified API", "https://api.tfl.gov.uk/");
        var before = doc.GetHyperlinkCount();
        var path = TempFile("hlc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHyperlinkCount());
    }

    // -------------------------------------------------------------------------
    // AddHyperlink
    // -------------------------------------------------------------------------

    [Fact]
    public void AddHyperlink_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.AddHyperlink(0, "OpenStreetMap", "https://www.openstreetmap.org/"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Increases_Count()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetHyperlinkCount();
        doc.AddHyperlink(3, "OS Open Roads", "https://www.ordnancesurvey.co.uk/products/os-open-roads");
        Assert.Equal(before + 1, doc.GetHyperlinkCount());
    }

    [Fact]
    public void AddHyperlink_SaveLoad_Persists()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(4, "Office for National Statistics", "https://www.ons.gov.uk/");
        var before = doc.GetHyperlinkCount();
        var path = TempFile("ahl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHyperlinkCount());
    }

    [Fact]
    public void AddHyperlink_Multiple()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(0, "Link 1", "https://example.com/1");
        doc.AddHyperlink(1, "Link 2", "https://example.com/2");
        doc.AddHyperlink(3, "Link 3", "https://example.com/3");
        Assert.Equal(3, doc.GetHyperlinkCount());
    }

    [Fact]
    public void AddHyperlink_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(2, "GTFS Reference", "https://gtfs.org/");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(1, "Creative Commons", "https://creativecommons.org/licenses/by/4.0/");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Then_GetWordCount_Positive()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(0, "GitHub Repository", "https://github.com/example/repo");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetHyperlinkUrl
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkUrl_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(1, "Test Link", "https://www.example.com/");
        var ex = Record.Exception(() => doc.GetHyperlinkUrl(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkUrl_NonNull()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(2, "Non-null Link", "https://www.test.org/");
        Assert.NotNull(doc.GetHyperlinkUrl(0));
    }

    [Fact]
    public void GetHyperlinkUrl_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(0, "Consistent Link", "https://www.consistent.net/");
        Assert.Equal(doc.GetHyperlinkUrl(0), doc.GetHyperlinkUrl(0));
    }

    [Fact]
    public void GetHyperlinkUrl_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddHyperlink(3, "SaveLoad Link", "https://www.saveload.io/");
        var path = TempFile("hlu_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetHyperlinkUrl(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddHyperlink_GetHyperlinkCount_GetHyperlinkUrl_SaveToFile_Pipeline()
    {
        // Academic bibliography — systematic review of machine learning in healthcare diagnostics
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Systematic Review: Machine Learning Applications in Radiological Diagnostics — PRISMA 2020 Compliant Review of Deep Learning for Chest X-ray Interpretation", 1);
        doc.AppendParagraph("This systematic review follows PRISMA 2020 reporting guidelines and was registered prospectively on PROSPERO (registration CRD20240158). Electronic database searches were conducted in MEDLINE, Embase, Cochrane Library, and IEEE Xplore from January 2015 to December 2023.");
        doc.AppendParagraph("Search terms combined MeSH headings for diagnostic imaging, artificial intelligence, and chest radiography with free-text terms for convolutional neural networks, deep learning, and computer-aided detection systems.");

        doc.InsertHeading(3, "Included Studies", 2);
        doc.AppendParagraph("Following deduplication and two-stage screening, 47 studies met eligibility criteria, comprising 31 retrospective diagnostic accuracy studies and 16 prospective comparative studies against radiologist interpretation.");
        doc.AppendParagraph("Quality assessment using QUADAS-2 tool identified high risk of bias in patient selection domain for 18 studies (38%), primarily due to case-control designs with artificially enriched disease prevalence.");

        doc.InsertHeading(6, "Key Findings", 2);
        doc.AppendParagraph("Pooled AUC for pneumonia detection across 12 studies was 0.94 (95% CI 0.92-0.96), with significant heterogeneity (I² = 78%) attributable to variation in reference standard quality and patient population characteristics.");
        doc.AppendParagraph("Three studies achieving AUROC > 0.97 used CheXpert-trained models evaluated on external validation sets from geographically distinct populations, suggesting robust generalisation for pneumonia classification.");

        doc.InsertHeading(9, "Data and Code Availability", 1);
        doc.AppendParagraph("All screening decisions, data extraction forms, and statistical analysis code are deposited in the Open Science Framework repository with pre-registration of the analysis plan.");
        doc.AppendParagraph("Requests for individual patient data from included studies should be directed to the corresponding author of each included trial; meta-analysis code is available under MIT licence.");

        Assert.Equal(10, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetHyperlinkCount());

        // AddHyperlink — bibliography links
        doc.AddHyperlink(0, "PROSPERO CRD20240158", "https://www.crd.york.ac.uk/prospero/display_record.php?RecordID=20240158");
        Assert.Equal(1, doc.GetHyperlinkCount());

        doc.AddHyperlink(1, "PRISMA 2020 Checklist", "https://prisma-statement.org/prisma2020");
        Assert.Equal(2, doc.GetHyperlinkCount());

        doc.AddHyperlink(2, "Cochrane Database of Systematic Reviews", "https://www.cochranelibrary.com/");
        Assert.Equal(3, doc.GetHyperlinkCount());

        doc.AddHyperlink(4, "QUADAS-2 Tool Documentation", "https://www.bristol.ac.uk/population-health-sciences/projects/quadas/quadas-2/");
        Assert.Equal(4, doc.GetHyperlinkCount());

        doc.AddHyperlink(6, "CheXpert Dataset (Stanford ML Group)", "https://stanfordmlgroup.github.io/competitions/chexpert/");
        Assert.Equal(5, doc.GetHyperlinkCount());

        doc.AddHyperlink(8, "Open Science Framework Repository", "https://osf.io/");
        Assert.Equal(6, doc.GetHyperlinkCount());

        // Consistent
        Assert.Equal(doc.GetHyperlinkCount(), doc.GetHyperlinkCount());

        // GetHyperlinkUrl
        var url0 = doc.GetHyperlinkUrl(0);
        Assert.NotNull(url0);
        Assert.Equal(url0, doc.GetHyperlinkUrl(0)); // consistent

        var url3 = doc.GetHyperlinkUrl(3);
        Assert.NotNull(url3);

        var url5 = doc.GetHyperlinkUrl(5);
        Assert.NotNull(url5);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_systematic_review.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetHyperlinkCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetHyperlinkUrl(0));
        Assert.NotNull(loaded.GetHyperlinkUrl(5));

        // AddHyperlink on loaded
        loaded.AddHyperlink(9, "MIT Licence", "https://opensource.org/licenses/MIT");
        Assert.Equal(7, loaded.GetHyperlinkCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: deep learning models demonstrate high diagnostic accuracy for pneumonia detection on chest radiographs, with pooled AUC of 0.94, though significant heterogeneity and risk of bias require cautious interpretation before clinical deployment.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_systematic_review_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetHyperlinkCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetHyperlinkUrl(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddHyperlink(0, "Final Link", "https://www.example.com/"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
