// Tests for FodtDocument.GetHyperlinkCount, AddHyperlink, GetHyperlinkUrl deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R326

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R326: Tests for FodtDocument.GetHyperlinkCount, AddHyperlink, GetHyperlinkUrl deeper.
/// GetHyperlinkCount(): returns the number of hyperlinks in the document.
/// AddHyperlink(paragraphIndex, url, displayText): adds a hyperlink to the specified paragraph.
/// GetHyperlinkUrl(index): returns the URL of the hyperlink at the given index.
/// Covers: GetHyperlinkCount no-throw; GetHyperlinkCount non-negative; GetHyperlinkCount consistent;
/// GetHyperlinkCount zero for new doc; GetHyperlinkCount after AddHyperlink increases;
/// GetHyperlinkCount save-load;
/// AddHyperlink no-throw; AddHyperlink increases count; AddHyperlink save-load;
/// AddHyperlink multiple; AddHyperlink then ExportToHtml no-throw;
/// AddHyperlink then ExportToMarkdown no-throw; AddHyperlink then GetCharCount positive;
/// GetHyperlinkUrl no-throw; GetHyperlinkUrl non-null; GetHyperlinkUrl consistent;
/// GetHyperlinkUrl save-load;
/// dogfood CreateDoc→AddHyperlink→GetHyperlinkCount→GetHyperlinkUrl→SaveToFile pipeline.
/// </summary>
public class FodtR326GetHyperlinkCountAndAddHyperlinkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR326GetHyperlinkCountAndAddHyperlinkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR326_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateTechPolicyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Open Source Compliance Framework for Enterprise Software Procurement", 1);
        doc.AppendParagraph("Software composition analysis tools identify open source components and map declared licences against enterprise-approved licence categories.");
        doc.AppendParagraph("SPDX licence expressions provide a standardised machine-readable format for communicating complex licence obligations across supply chain boundaries.");
        doc.InsertHeading(3, "Licence Compatibility Matrix", 2);
        doc.AppendParagraph("Copyleft licences including GPL-2.0 and AGPL-3.0 impose reciprocal disclosure obligations that restrict incorporation into proprietary commercial products.");
        doc.AppendParagraph("Permissive licences including MIT, Apache-2.0, and BSD-3-Clause impose attribution requirements only, without distribution or disclosure obligations.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHyperlinkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkCount_NoThrow()
    {
        var doc = CreateTechPolicyDoc();
        var ex = Record.Exception(() => doc.GetHyperlinkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkCount_NonNegative()
    {
        var doc = CreateTechPolicyDoc();
        Assert.True(doc.GetHyperlinkCount() >= 0);
    }

    [Fact]
    public void GetHyperlinkCount_Consistent()
    {
        var doc = CreateTechPolicyDoc();
        Assert.Equal(doc.GetHyperlinkCount(), doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document containing no hyperlinks.");
        Assert.Equal(0, doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_AfterAddHyperlink_Increases()
    {
        var doc = CreateTechPolicyDoc();
        var before = doc.GetHyperlinkCount();
        doc.AddHyperlink(1, "https://spdx.org/licenses/", "SPDX Licence List");
        Assert.Equal(before + 1, doc.GetHyperlinkCount());
    }

    [Fact]
    public void GetHyperlinkCount_SaveLoad_Consistent()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(2, "https://www.gnu.org/licenses/gpl-3.0.html", "GNU GPL v3");
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
        var doc = CreateTechPolicyDoc();
        var ex = Record.Exception(() => doc.AddHyperlink(0, "https://opensource.org/licenses/MIT", "MIT Licence"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Increases_Count()
    {
        var doc = CreateTechPolicyDoc();
        var before = doc.GetHyperlinkCount();
        doc.AddHyperlink(3, "https://www.apache.org/licenses/LICENSE-2.0", "Apache 2.0");
        Assert.Equal(before + 1, doc.GetHyperlinkCount());
    }

    [Fact]
    public void AddHyperlink_SaveLoad_Persists()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(4, "https://opensource.org/licenses/BSD-3-Clause", "BSD 3-Clause");
        var before = doc.GetHyperlinkCount();
        var path = TempFile("ahl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHyperlinkCount());
    }

    [Fact]
    public void AddHyperlink_Multiple()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(0, "https://spdx.org/", "SPDX Home");
        doc.AddHyperlink(1, "https://opensource.org/", "OSI Home");
        doc.AddHyperlink(3, "https://www.gnu.org/", "GNU Project");
        Assert.Equal(3, doc.GetHyperlinkCount());
    }

    [Fact]
    public void AddHyperlink_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(2, "https://example.com/html-test", "HTML test link");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(1, "https://example.com/md-test", "Markdown test link");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddHyperlink_Then_GetCharCount_Positive()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(0, "https://example.com/char-test", "Char count link");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetHyperlinkUrl
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkUrl_NoThrow()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(1, "https://spdx.org/licenses/MIT.html", "MIT at SPDX");
        var ex = Record.Exception(() => doc.GetHyperlinkUrl(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkUrl_NonNull()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(2, "https://choosealicense.com/", "Choose a Licence");
        Assert.NotNull(doc.GetHyperlinkUrl(0));
    }

    [Fact]
    public void GetHyperlinkUrl_Consistent()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(0, "https://tldrlegal.com/", "TL;DR Legal");
        Assert.Equal(doc.GetHyperlinkUrl(0), doc.GetHyperlinkUrl(0));
    }

    [Fact]
    public void GetHyperlinkUrl_SaveLoad_Consistent()
    {
        var doc = CreateTechPolicyDoc();
        doc.AddHyperlink(3, "https://fossa.com/blog/open-source-software-licenses-101/", "FOSSA Licence Guide");
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
        // Policy brief — EU AI Act compliance guidance for enterprise AI deployment
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "EU AI Act Compliance Framework: Risk Classification and Conformity Assessment for Enterprise AI Systems", 1);
        doc.AppendParagraph("The EU AI Act establishes a risk-based regulatory framework categorising AI systems into unacceptable risk, high risk, limited risk, and minimal risk tiers.");
        doc.AppendParagraph("High-risk AI systems deployed in employment, education, law enforcement, and critical infrastructure require mandatory conformity assessment and CE marking before market placement.");

        doc.InsertHeading(3, "Prohibited AI Practices", 2);
        doc.AppendParagraph("Social scoring systems operated by public authorities and AI systems exploiting psychological vulnerabilities are categorically prohibited under Article 5 of the AI Act.");
        doc.AppendParagraph("Real-time remote biometric identification in publicly accessible spaces is prohibited except for specified law enforcement purposes subject to judicial authorisation.");

        doc.InsertHeading(6, "High-Risk System Requirements", 2);
        doc.AppendParagraph("High-risk AI systems must implement risk management systems, data governance frameworks, technical documentation, logging capabilities, and human oversight mechanisms.");
        doc.AppendParagraph("Conformity assessment procedures vary: Annex VI (internal control) applies to most high-risk systems; Annex VII (third-party assessment) applies to biometric and critical infrastructure AI.");

        doc.InsertHeading(9, "Implementation Timeline", 1);
        doc.AppendParagraph("Prohibited practices provisions entered force six months after publication; GPAI model obligations apply twelve months post-publication; full high-risk system obligations apply 36 months post-publication.");
        doc.AppendParagraph("Notified body accreditation, standardisation mandate execution (CEN/CENELEC), and national authority designation constitute the critical path for market readiness.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetHyperlinkCount — zero initially
        Assert.Equal(0, doc.GetHyperlinkCount());

        // AddHyperlink — regulatory source references
        doc.AddHyperlink(1, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689", "EU AI Act Official Text (OJ L 2024/1689)");
        Assert.Equal(1, doc.GetHyperlinkCount());

        doc.AddHyperlink(2, "https://artificialintelligenceact.eu/the-act/", "EU AI Act Interactive Guide");
        Assert.Equal(2, doc.GetHyperlinkCount());

        doc.AddHyperlink(3, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689#d1e2466-1-1", "Article 5 — Prohibited AI Practices");
        Assert.Equal(3, doc.GetHyperlinkCount());

        doc.AddHyperlink(5, "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689#d1e3012-1-1", "Article 9 — Risk Management System");
        Assert.Equal(4, doc.GetHyperlinkCount());

        doc.AddHyperlink(6, "https://www.cencenelec.eu/areas-of-work/cenelec-topics/artificial-intelligence/", "CEN/CENELEC AI Standardisation");
        Assert.Equal(5, doc.GetHyperlinkCount());

        doc.AddHyperlink(8, "https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence", "EC AI Policy Portal");
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

        // ExportToPlainText
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_eu_ai_act.fodt");
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
        loaded.AddHyperlink(9, "https://www.enisa.europa.eu/topics/artificial-intelligence", "ENISA AI Cybersecurity");
        Assert.Equal(7, loaded.GetHyperlinkCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: enterprises deploying high-risk AI must integrate conformity assessment into the product development lifecycle, not as a post-deployment audit exercise.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_eu_ai_act_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetHyperlinkCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetHyperlinkUrl(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddHyperlink(0, "https://example.com/final", "Final link"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
