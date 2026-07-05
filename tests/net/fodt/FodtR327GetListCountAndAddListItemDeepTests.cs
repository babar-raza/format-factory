// Tests for FodtDocument.GetListCount, AddListItem, GetListItemText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R327

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R327: Tests for FodtDocument.GetListCount, AddListItem, GetListItemText deeper.
/// GetListCount(): returns the number of list items in the document.
/// AddListItem(text, level, listStyle): adds a list item with the given text and nesting level.
/// GetListItemText(index): returns the text content of the list item at the given index.
/// Covers: GetListCount no-throw; GetListCount non-negative; GetListCount consistent;
/// GetListCount zero for new doc; GetListCount after AddListItem increases; GetListCount save-load;
/// AddListItem no-throw; AddListItem increases count; AddListItem save-load;
/// AddListItem multiple; AddListItem then ExportToHtml no-throw;
/// AddListItem then ExportToMarkdown no-throw; AddListItem then GetWordCount positive;
/// GetListItemText no-throw; GetListItemText non-null; GetListItemText consistent;
/// GetListItemText save-load;
/// dogfood CreateDoc→AddListItem→GetListCount→GetListItemText→SaveToFile pipeline.
/// </summary>
public class FodtR327GetListCountAndAddListItemDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR327GetListCountAndAddListItemDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR327_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreatePolicyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "UK Financial Services Regulatory Compliance Framework: Post-Brexit Implementation Guide", 1);
        doc.AppendParagraph("The Financial Conduct Authority and Prudential Regulation Authority jointly supervise UK financial services firms under the Financial Services and Markets Act 2000.");
        doc.AppendParagraph("Post-Brexit regulatory divergence has created distinct UK prudential standards including UK CRR2, UK EMIR, and UK MiFID2 replacing their EU counterparts.");
        doc.InsertHeading(3, "Regulatory Obligations", 2);
        doc.AppendParagraph("Capital requirements under UK CRR2 mandate minimum Common Equity Tier 1 ratios of 4.5% plus firm-specific capital buffer requirements.");
        doc.AppendParagraph("Operational resilience obligations require boards to set impact tolerances for important business services within defined self-assessment timelines.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = CreatePolicyDoc();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_NonNegative()
    {
        var doc = CreatePolicyDoc();
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = CreatePolicyDoc();
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no list items.");
        Assert.Equal(0, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_AfterAddListItem_Increases()
    {
        var doc = CreatePolicyDoc();
        var before = doc.GetListCount();
        doc.AddListItem("FCA authorisation under FSMA 2000 Part 4A", 1, "bullet");
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_SaveLoad_Consistent()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("Annual regulatory reporting obligations", 1, "bullet");
        var before = doc.GetListCount();
        var path = TempFile("lc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    // -------------------------------------------------------------------------
    // AddListItem
    // -------------------------------------------------------------------------

    [Fact]
    public void AddListItem_NoThrow()
    {
        var doc = CreatePolicyDoc();
        var ex = Record.Exception(() => doc.AddListItem("SMCR Senior Manager certification requirement", 1, "numbered"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddListItem_Increases_Count()
    {
        var doc = CreatePolicyDoc();
        var before = doc.GetListCount();
        doc.AddListItem("Conduct Rules training obligation under SM&CR", 1, "bullet");
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void AddListItem_SaveLoad_Persists()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("MiFID2 transaction reporting to FCA", 1, "numbered");
        var before = doc.GetListCount();
        var path = TempFile("ali_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    [Fact]
    public void AddListItem_Multiple()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("Capital adequacy: minimum CET1 4.5%", 1, "numbered");
        doc.AddListItem("Leverage ratio: minimum 3.25% for G-SIIs", 1, "numbered");
        doc.AddListItem("Liquidity coverage ratio: minimum 100%", 1, "numbered");
        Assert.Equal(3, doc.GetListCount());
    }

    [Fact]
    public void AddListItem_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("HTML export list item test", 1, "bullet");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddListItem_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("Markdown export list item test", 1, "bullet");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddListItem_Then_GetWordCount_Positive()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("Word count list item test", 1, "bullet");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetListItemText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItemText_NoThrow()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("List item text retrieval test", 1, "bullet");
        var ex = Record.Exception(() => doc.GetListItemText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetListItemText_NonNull()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("Non-null list item text", 1, "numbered");
        Assert.NotNull(doc.GetListItemText(0));
    }

    [Fact]
    public void GetListItemText_Consistent()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("Consistency test list item", 1, "bullet");
        Assert.Equal(doc.GetListItemText(0), doc.GetListItemText(0));
    }

    [Fact]
    public void GetListItemText_SaveLoad_Consistent()
    {
        var doc = CreatePolicyDoc();
        doc.AddListItem("Save-load list item text persistence", 1, "numbered");
        var path = TempFile("lit_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetListItemText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddListItem_GetListCount_GetListItemText_SaveToFile_Pipeline()
    {
        // Compliance procedures manual — AML/CFT programme requirements for UK authorised firms
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Anti-Money Laundering and Counter-Terrorist Financing Programme: Authorised Firm Requirements", 1);
        doc.AppendParagraph("The Proceeds of Crime Act 2002 and Terrorism Act 2000 impose criminal liability on individuals and firms facilitating money laundering and terrorist financing.");
        doc.AppendParagraph("The Money Laundering, Terrorist Financing and Transfer of Funds Regulations 2017 (MLRs) implement the Fourth and Fifth EU Money Laundering Directives into UK law.");

        doc.InsertHeading(3, "Customer Due Diligence", 2);
        doc.AppendParagraph("Standard CDD must be applied to all new customers and existing customers presenting updated risk indicators or triggering periodic review thresholds.");
        doc.AppendParagraph("Enhanced due diligence is mandatory for politically exposed persons, high-risk third countries, and complex ownership structures with potential concealment risk.");

        doc.InsertHeading(6, "Suspicious Activity Reports", 2);
        doc.AppendParagraph("SARs must be submitted to the National Crime Agency via the SAR Online system within the tipping-off restriction window before any transaction proceeds.");
        doc.AppendParagraph("Defence against money laundering requires NCA consent or expiry of the 7-day moratorium period before completing a transaction subject to a submitted SAR.");

        doc.InsertHeading(9, "Governance Requirements", 1);
        doc.AppendParagraph("A nominated officer (Money Laundering Reporting Officer) must be appointed at board level with direct reporting line and authority to file SARs independently.");
        doc.AppendParagraph("Annual MLRO report to the board must cover SAR statistics, training completion rates, control effectiveness assessments, and emerging typologies.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetListCount());

        // AddListItem — CDD programme elements
        doc.AddListItem("Collect and verify customer identity documents to requisite standard", 1, "numbered");
        Assert.Equal(1, doc.GetListCount());

        doc.AddListItem("Identify and verify beneficial owners above 25% threshold", 1, "numbered");
        Assert.Equal(2, doc.GetListCount());

        doc.AddListItem("Assess purpose and intended nature of business relationship", 1, "numbered");
        Assert.Equal(3, doc.GetListCount());

        doc.AddListItem("Screen customer names against sanctions lists and PEP databases", 1, "numbered");
        Assert.Equal(4, doc.GetListCount());

        doc.AddListItem("Apply ongoing monitoring proportionate to risk classification", 1, "numbered");
        Assert.Equal(5, doc.GetListCount());

        // Nested list items — EDD triggers
        doc.AddListItem("Correspondent banking relationships in non-EEA jurisdictions", 2, "bullet");
        Assert.Equal(6, doc.GetListCount());

        doc.AddListItem("Non-face-to-face account opening above threshold", 2, "bullet");
        Assert.Equal(7, doc.GetListCount());

        doc.AddListItem("Transactions involving high-risk third countries per FATF list", 2, "bullet");
        Assert.Equal(8, doc.GetListCount());

        // Consistent
        Assert.Equal(doc.GetListCount(), doc.GetListCount());

        // GetListItemText
        var text0 = doc.GetListItemText(0);
        Assert.NotNull(text0);
        Assert.Equal(text0, doc.GetListItemText(0)); // consistent

        var text4 = doc.GetListItemText(4);
        Assert.NotNull(text4);

        var text7 = doc.GetListItemText(7);
        Assert.NotNull(text7);

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

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_aml_cft.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(8, loaded.GetListCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetListItemText(0));
        Assert.NotNull(loaded.GetListItemText(7));

        // AddListItem on loaded
        loaded.AddListItem("Maintain records for minimum 5 years post-relationship termination", 1, "bullet");
        Assert.Equal(9, loaded.GetListCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: an effective AML/CFT programme requires board-level ownership, risk-based customer segmentation, and continuous monitoring with documented rationale.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_aml_cft_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(9, loaded2.GetListCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetListItemText(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddListItem("Final list item.", 1, "bullet"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
