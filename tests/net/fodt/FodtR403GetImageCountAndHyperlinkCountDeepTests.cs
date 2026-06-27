// Tests for FodtDocument.GetImageCount, GetHyperlinkCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R403

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R403: Tests for FodtDocument.GetImageCount, GetHyperlinkCount deeper.
/// GetImageCount(): returns the number of embedded images in the document.
/// GetHyperlinkCount(): returns the number of hyperlinks/external references in the document.
/// Covers: GetImageCount no-throw; GetImageCount non-negative; GetImageCount zero for plain doc;
/// GetImageCount consistent; GetImageCount increases after InsertImage;
/// GetImageCount save-load;
/// GetHyperlinkCount no-throw; GetHyperlinkCount non-negative;
/// GetHyperlinkCount consistent; GetHyperlinkCount increases after InsertHyperlink;
/// GetHyperlinkCount save-load; dogfood pipeline.
/// </summary>
public class FodtR403GetImageCountAndHyperlinkCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR403GetImageCountAndHyperlinkCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR403_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreatePlainDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Plain Document", 1);
        doc.AppendParagraph("This document contains only text — no images and no hyperlinks.");
        doc.AppendParagraph("A second paragraph provides additional prose content.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetImageCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetImageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageCount_NonNegative()
    {
        var doc = CreatePlainDoc();
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void GetImageCount_Zero_ForPlainDoc()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(0, doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetImageCount(), doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_Increases_After_InsertImage()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetImageCount();
        doc.InsertImage(0, TempFile("placeholder.png"), "Figure 1: Diagram");
        Assert.True(doc.GetImageCount() > before);
    }

    [Fact]
    public void GetImageCount_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.InsertImage(0, TempFile("placeholder2.png"), "Figure 2");
        var before = doc.GetImageCount();
        var path = TempFile("img_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetImageCount());
    }

    // -------------------------------------------------------------------------
    // GetHyperlinkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkCount_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetHyperlinkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkCount_NonNegative()
    {
        var doc = CreatePlainDoc();
        Assert.True(doc.GetHyperlinkCount() >= 0);
    }

    [Fact]
    public void GetHyperlinkCount_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetHyperlinkCount(), doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_Increases_After_InsertHyperlink()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetHyperlinkCount();
        doc.InsertHyperlink(0, "https://www.gov.uk/", "GOV.UK");
        Assert.True(doc.GetHyperlinkCount() > before);
    }

    [Fact]
    public void GetHyperlinkCount_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.InsertHyperlink(0, "https://www.legislation.gov.uk/", "Legislation.gov.uk");
        var before = doc.GetHyperlinkCount();
        var path = TempFile("hl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHyperlinkCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetImageCount_GetHyperlinkCount_Pipeline()
    {
        // Government — Cabinet Office / GDS: UK Digital Strategy 2024 Progress Report
        // Policy document with embedded diagrams (governance charts, roadmaps) and legislative hyperlinks
        // Image and hyperlink counts verify accessibility compliance under WCAG 2.1 and PDF/UA

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "UK Digital Strategy 2024 — Annual Progress Report", 1);
        doc.AppendParagraph("Published by the Cabinet Office / Government Digital Service | Reference: CO/GDS/2024/PROG/001 | October 2024");

        var img0 = doc.GetImageCount();
        var hl0 = doc.GetHyperlinkCount();
        Assert.Equal(0, img0);
        Assert.True(hl0 >= 0);

        // Section 1: Introduction with hyperlinks to strategy documents
        doc.InsertSection("1. Introduction and Strategic Context");
        doc.InsertHeading(1, "1.1 Policy Framework", 2);
        doc.AppendParagraph("The UK Digital Strategy sets out the government's vision for a globally competitive digital economy, grounded in safe and secure digital infrastructure. This progress report covers implementation of commitments across seven strategic pillars for the period January–September 2024.");
        doc.InsertHyperlink(1, "https://www.gov.uk/government/publications/uk-digital-strategy", "UK Digital Strategy (2022)");
        doc.InsertHyperlink(1, "https://www.gov.uk/government/publications/national-cyber-strategy-2022", "National Cyber Strategy 2022");

        var img1 = doc.GetImageCount();
        var hl1 = doc.GetHyperlinkCount();
        Assert.Equal(0, img1); // no images yet
        Assert.True(hl1 > hl0); // two hyperlinks added

        // Section 2: Infrastructure pillar with diagram
        doc.InsertSection("2. Digital Infrastructure");
        doc.InsertHeading(2, "2.1 Gigabit Broadband Coverage", 2);
        doc.AppendParagraph("Project Gigabit has achieved 87.3% gigabit-capable coverage as of September 2024, up from 73.8% in September 2023. The £5bn public investment programme targets 99% coverage by December 2025 with BDUK-funded contracts in 47 procurement areas.");
        doc.InsertImage(2, TempFile("gigabit_coverage_map_q3_2024.png"), "Figure 1: Gigabit broadband coverage map by local authority (Q3 2024). Source: BDUK/Ofcom Connected Nations.");
        doc.InsertHyperlink(2, "https://www.gov.uk/guidance/project-gigabit-uk-programme", "Project Gigabit Programme");
        doc.InsertHyperlink(2, "https://www.ofcom.org.uk/research-and-data/telecoms-research/connected-nations", "Ofcom Connected Nations Report");

        var img2 = doc.GetImageCount();
        var hl2 = doc.GetHyperlinkCount();
        Assert.True(img2 > img1); // one image added
        Assert.True(hl2 > hl1); // two more hyperlinks

        // Section 3: AI pillar with governance diagram and multiple links
        doc.InsertSection("3. Artificial Intelligence");
        doc.InsertHeading(3, "3.1 AI Regulation Framework", 2);
        doc.AppendParagraph("The AI Safety Institute (AISI), established under DSIT in November 2023, has conducted evaluations of five frontier AI systems under the voluntary safety framework agreed at the Bletchley Park AI Safety Summit. The DSIT AI Opportunities Action Plan commits £240m to AI Research Resource infrastructure.");
        doc.InsertImage(3, TempFile("ai_governance_framework_diagram.png"), "Figure 2: UK AI governance ecosystem — regulatory bodies, oversight mechanisms, and international coordination.");
        doc.InsertImage(3, TempFile("aisi_evaluation_timeline.png"), "Figure 3: AISI frontier model evaluation timeline 2024.");
        doc.InsertHyperlink(3, "https://www.gov.uk/government/organisations/ai-safety-institute", "AI Safety Institute");
        doc.InsertHyperlink(3, "https://www.gov.uk/government/publications/ai-safety-summit-2023-the-bletchley-declaration", "Bletchley Declaration");
        doc.InsertHyperlink(3, "https://www.gov.uk/government/publications/ai-opportunities-action-plan", "AI Opportunities Action Plan");

        var img3 = doc.GetImageCount();
        var hl3 = doc.GetHyperlinkCount();
        Assert.True(img3 > img2); // two more images
        Assert.True(hl3 > hl2); // three more hyperlinks
        Assert.True(doc.GetImageCount() == img3); // consistent
        Assert.True(doc.GetHyperlinkCount() == hl3); // consistent

        // Section 4: Cyber with third diagram
        doc.InsertSection("4. Cyber Security");
        doc.InsertHeading(4, "4.1 NCSC Incident Response", 2);
        doc.AppendParagraph("The National Cyber Security Centre managed 2,124 incidents in 2023/24, including 371 incidents of national significance — a 47% increase on the prior year. The Cyber Resilience Strategy milestones for Q3 2024 show 68% of critical national infrastructure sectors meeting the Target Profile.");
        doc.InsertImage(4, TempFile("ncsc_incident_trends_2024.png"), "Figure 4: NCSC incident category and severity trends 2021–2024.");
        doc.InsertHyperlink(4, "https://www.ncsc.gov.uk/collection/annual-review-2024", "NCSC Annual Review 2024");
        doc.InsertHyperlink(4, "https://www.gov.uk/government/publications/cyber-resilience-strategy", "Cyber Resilience Strategy");
        doc.InsertHyperlink(4, "https://www.gov.uk/government/collections/national-cyber-security-programme", "National Cyber Security Programme");

        var img4 = doc.GetImageCount();
        var hl4 = doc.GetHyperlinkCount();
        Assert.True(img4 > img3);
        Assert.True(hl4 > hl3);

        // Document integrity
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("uk_digital_strategy_2024_progress.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(img4, loaded.GetImageCount());
        Assert.Equal(hl4, loaded.GetHyperlinkCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Add appendix with more links
        loaded.InsertSection("Appendix: Key Reference Links");
        loaded.InsertHyperlink(5, "https://www.gov.uk/government/organisations/department-for-science-innovation-and-technology", "DSIT");
        loaded.InsertHyperlink(5, "https://www.gov.uk/government/organisations/government-digital-service", "GDS");
        loaded.InsertHyperlink(5, "https://ico.org.uk/", "Information Commissioner's Office");

        var hlFinal = loaded.GetHyperlinkCount();
        Assert.True(hlFinal > hl4);

        var path2 = TempFile("uk_digital_strategy_2024_with_appendix.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(img4, final.GetImageCount());
        Assert.Equal(hlFinal, final.GetHyperlinkCount());

        var ex1 = Record.Exception(() => final.GetImageCount());
        var ex2 = Record.Exception(() => final.GetHyperlinkCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
