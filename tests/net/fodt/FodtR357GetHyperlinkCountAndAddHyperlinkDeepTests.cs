// Tests for FodtDocument.GetHyperlinkCount, AddHyperlink deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R357

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R357: Tests for FodtDocument.GetHyperlinkCount, AddHyperlink deeper.
/// GetHyperlinkCount(): returns the number of hyperlinks in the document.
/// AddHyperlink(url, displayText, paragraphIndex): inserts a hyperlink into the document.
/// Covers: GetHyperlinkCount no-throw; GetHyperlinkCount non-negative; GetHyperlinkCount consistent;
/// GetHyperlinkCount zero for plain doc; GetHyperlinkCount save-load;
/// AddHyperlink no-throw; AddHyperlink then GetHyperlinkCount increases;
/// AddHyperlink then GetParagraphCount unchanged; AddHyperlink then ExportToHtml no-throw;
/// AddHyperlink then ExportToMarkdown no-throw; AddHyperlink save-load;
/// AddHyperlink multiple; AddHyperlink then GetWordCount positive;
/// dogfood CreateDoc→AddHyperlink→GetHyperlinkCount→SaveToFile pipeline.
/// </summary>
public class FodtR357GetHyperlinkCountAndAddHyperlinkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR357GetHyperlinkCountAndAddHyperlinkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR357_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "UK Parliamentary Committee Reports: Digital Markets and Competition", 1);
        doc.AppendParagraph("This report examines the Digital Markets, Competition and Consumers Act 2024 and its implications for platform operators designated with Strategic Market Status.");
        doc.AppendParagraph("The Competition and Markets Authority (CMA) has been granted enhanced powers to impose pro-competitive interventions on SMS-designated firms, including mandatory interoperability requirements and data access obligations.");
        return doc;
    }

    private static FodtDocument CreateDocWithHyperlinks()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Digital Regulation Resource Hub", 1);
        doc.AppendParagraph("Key legislative resources for digital markets practitioners.");
        doc.AddHyperlink("https://www.legislation.gov.uk/ukpga/2024/13/contents", "Digital Markets, Competition and Consumers Act 2024", 1);
        doc.AppendParagraph("Regulatory guidance and enforcement decisions.");
        doc.AddHyperlink("https://www.gov.uk/cma-cases", "CMA Cases Register", 2);
        return doc;
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
    public void GetHyperlinkCount_Zero_ForPlainDoc()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(0, doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_SaveLoad_Consistent()
    {
        var doc = CreateDocWithHyperlinks();
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
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.AddHyperlink("https://www.gov.uk", "GOV.UK", 1));
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Then_GetHyperlinkCount_Increases()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetHyperlinkCount();
        doc.AddHyperlink("https://www.legislation.gov.uk", "legislation.gov.uk", 1);
        Assert.True(doc.GetHyperlinkCount() > before);
    }

    [Fact]
    public void AddHyperlink_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetParagraphCount();
        doc.AddHyperlink("https://www.gov.uk/cma", "CMA", 1);
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void AddHyperlink_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.AddHyperlink("https://www.gov.uk", "GOV.UK", 1);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.AddHyperlink("https://www.gov.uk", "GOV.UK", 1);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.AddHyperlink("https://www.gov.uk/cma", "CMA", 1);
        var count = doc.GetHyperlinkCount();
        var path = TempFile("hl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(count, loaded.GetHyperlinkCount());
    }

    [Fact]
    public void AddHyperlink_Multiple()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetHyperlinkCount();
        doc.AddHyperlink("https://www.gov.uk/cma", "CMA", 1);
        doc.AddHyperlink("https://www.legislation.gov.uk", "Legislation", 1);
        doc.AddHyperlink("https://www.ico.org.uk", "ICO", 1);
        Assert.True(doc.GetHyperlinkCount() >= before + 3);
    }

    [Fact]
    public void AddHyperlink_Then_GetWordCount_Positive()
    {
        var doc = CreatePlainDoc();
        doc.AddHyperlink("https://www.gov.uk", "GOV.UK Home", 1);
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddHyperlink_GetHyperlinkCount_SaveToFile_Pipeline()
    {
        // Legal — UK Supreme Court judgments and legislative citation handbook
        // Structured legal document with cross-references to primary and secondary sources
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Citation and Reference Handbook: UK Digital Regulation 2024", 1);
        doc.AppendParagraph("This handbook provides practitioners with authoritative citations and cross-references for the evolving UK digital regulation landscape, including competition law, data protection, online safety, and AI governance frameworks.");

        doc.InsertHeading(3, "Primary Legislation", 2);
        doc.AppendParagraph("The Digital Markets, Competition and Consumers Act 2024 (DMCC Act) received Royal Assent on 24 May 2024. It creates the Strategic Market Status (SMS) designation for firms with substantial and entrenched market power in at least one digital activity.");
        doc.AppendParagraph("The Online Safety Act 2023 established the regulatory framework for user-to-user services and search services, with Ofcom as the designated regulator. Category 1 and 2A/2B service providers face graduated duties.");
        doc.AppendParagraph("The Data Protection and Digital Information Act 2024 modernises the UK GDPR framework post-Brexit, introducing the concept of Recognised Legitimate Interests and simplifying certain compliance obligations for UK-based controllers.");
        doc.AppendParagraph("The Investigatory Powers (Amendment) Act 2024 extends the bulk personal dataset retention powers and introduces the Automated Processing Regime for bulk data analysis by intelligence services.");

        doc.InsertHeading(3, "Regulatory Guidance", 2);
        doc.AppendParagraph("The Competition and Markets Authority has published guidance on its approach to SMS investigations under the DMCC Act, including indicative timelines (9 months for designation decisions), evidentiary standards, and the treatment of countervailing efficiencies.");
        doc.AppendParagraph("The Information Commissioner's Office has issued updated guidance on legitimate interests balancing tests, AI and data protection, and biometric data processing following the UK AI Safety Institute's framework publication.");
        doc.AppendParagraph("Ofcom published its Phase 1 implementation roadmap in January 2024, covering risk assessments, safety codes of practice, and enforcement procedures for Online Safety Act compliance.");

        Assert.Equal(11, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetHyperlinkCount()); // no hyperlinks yet

        // AddHyperlink — primary legislation sources
        doc.AddHyperlink("https://www.legislation.gov.uk/ukpga/2024/13/contents", "DMCC Act 2024 — Full Text", 3);
        Assert.Equal(1, doc.GetHyperlinkCount());

        doc.AddHyperlink("https://www.legislation.gov.uk/ukpga/2023/50/contents", "Online Safety Act 2023 — Full Text", 4);
        Assert.Equal(2, doc.GetHyperlinkCount());

        doc.AddHyperlink("https://www.legislation.gov.uk/ukpga/2024/35/contents", "DPDI Act 2024 — Full Text", 5);
        Assert.Equal(3, doc.GetHyperlinkCount());

        doc.AddHyperlink("https://www.legislation.gov.uk/ukpga/2024/21/contents", "Investigatory Powers (Amendment) Act 2024", 6);
        Assert.Equal(4, doc.GetHyperlinkCount());

        // AddHyperlink — regulatory guidance sources
        doc.AddHyperlink("https://www.gov.uk/cma-cases/digital-markets-investigations", "CMA SMS Investigation Guidance", 7);
        Assert.Equal(5, doc.GetHyperlinkCount());

        doc.AddHyperlink("https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/", "ICO UK GDPR Guidance Hub", 8);
        Assert.Equal(6, doc.GetHyperlinkCount());

        doc.AddHyperlink("https://www.ofcom.org.uk/research-and-data/telecoms-research/online-safety", "Ofcom Online Safety Implementation Roadmap", 9);
        Assert.Equal(7, doc.GetHyperlinkCount());

        // Consistent
        Assert.Equal(7, doc.GetHyperlinkCount());
        Assert.Equal(11, doc.GetParagraphCount()); // paragraph count unchanged

        // ExportToHtml — hyperlinks should be rendered
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown — hyperlinks should be rendered in Markdown format
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_citation_handbook.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(7, loaded.GetHyperlinkCount());
        Assert.Equal(11, loaded.GetParagraphCount());

        // AddHyperlink on loaded — UK Supreme Court cases
        loaded.AddHyperlink("https://www.supremecourt.uk/cases/", "UK Supreme Court Cases", 1);
        Assert.Equal(8, loaded.GetHyperlinkCount());

        loaded.AddHyperlink("https://www.bailii.org/uk/cases/UKSC/", "BAILII — UKSC Judgments", 1);
        Assert.Equal(9, loaded.GetHyperlinkCount());

        // AppendParagraph and another hyperlink
        loaded.AppendParagraph("International frameworks: the OECD AI Principles, EU AI Act (Regulation 2024/1689), and UK-EU Data Bridge adequacy decision are key cross-border reference points for multinational practitioners.");
        loaded.AddHyperlink("https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0449", "OECD AI Principles — Legal Instrument", 9);
        Assert.Equal(10, loaded.GetHyperlinkCount());
        Assert.Equal(12, loaded.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_citation_handbook_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(10, loaded2.GetHyperlinkCount());
        Assert.Equal(12, loaded2.GetParagraphCount());
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.GetWordCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
