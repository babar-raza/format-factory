// Tests for FodtDocument.GetCommentCount, AddComment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R358

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R358: Tests for FodtDocument.GetCommentCount, AddComment deeper.
/// GetCommentCount(): returns the number of annotation comments in the document.
/// AddComment(author, text, paragraphIndex): adds an annotation comment to the document.
/// Covers: GetCommentCount no-throw; GetCommentCount non-negative; GetCommentCount consistent;
/// GetCommentCount zero for plain doc; GetCommentCount save-load;
/// AddComment no-throw; AddComment then GetCommentCount increases;
/// AddComment then GetParagraphCount unchanged; AddComment then ExportToHtml no-throw;
/// AddComment then ExportToMarkdown no-throw; AddComment save-load;
/// AddComment multiple authors; AddComment then GetWordCount positive;
/// dogfood CreateDoc→AddComment→GetCommentCount→SaveToFile pipeline.
/// </summary>
public class FodtR358GetCommentCountAndAddCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR358GetCommentCountAndAddCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR358_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Draft Policy: UK Procurement Reform and Social Value Framework", 1);
        doc.AppendParagraph("This policy paper sets out the Government's approach to embedding social value in public procurement decisions, implementing the Social Value Act 2012 in the context of the Procurement Act 2023.");
        doc.AppendParagraph("The framework requires contracting authorities to consider how proposed procurement can improve economic, social, and environmental wellbeing in the relevant area.");
        doc.AppendParagraph("Weighting of social value considerations must be proportionate to the contract subject matter and should not distort competition or conflict with best value duty.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCommentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetCommentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentCount_NonNegative()
    {
        var doc = CreatePlainDoc();
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void GetCommentCount_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetCommentCount(), doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_Zero_ForPlainDoc()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(0, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.AddComment("Reviewer", "Needs clearer definition", 1);
        var before = doc.GetCommentCount();
        var path = TempFile("cc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount());
    }

    // -------------------------------------------------------------------------
    // AddComment
    // -------------------------------------------------------------------------

    [Fact]
    public void AddComment_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.AddComment("Alice", "Check citation", 1));
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Then_GetCommentCount_Increases()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetCommentCount();
        doc.AddComment("Bob", "Needs legal review", 1);
        Assert.True(doc.GetCommentCount() > before);
    }

    [Fact]
    public void AddComment_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetParagraphCount();
        doc.AddComment("Alice", "Check this paragraph", 1);
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void AddComment_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.AddComment("Reviewer", "Clarify scope", 1);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.AddComment("Editor", "Rephrase for clarity", 2);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.AddComment("Legal", "Statutory reference needed", 1);
        var count = doc.GetCommentCount();
        var path = TempFile("ac_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(count, loaded.GetCommentCount());
    }

    [Fact]
    public void AddComment_MultipleAuthors()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetCommentCount();
        doc.AddComment("Alice", "Needs expansion", 1);
        doc.AddComment("Bob", "Agreed — see CCS guidance", 1);
        doc.AddComment("Carol", "Check Procurement Act s.12", 2);
        Assert.True(doc.GetCommentCount() >= before + 3);
    }

    [Fact]
    public void AddComment_Then_GetWordCount_Positive()
    {
        var doc = CreatePlainDoc();
        doc.AddComment("Reviewer", "Word count check", 1);
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddComment_GetCommentCount_SaveToFile_Pipeline()
    {
        // Legal — UK Law Commission Consultation Paper: Digital Assets
        // Multi-reviewer annotation workflow for statutory consultation response
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Digital Assets: Law Commission Consultation Paper No. 256 — Draft Response", 1);
        doc.AppendParagraph("This response is submitted by the Technology Law Group in respect of the Law Commission's Consultation Paper on Digital Assets (CP 256). The Group comprises practitioners specialising in financial technology, digital assets, and distributed ledger technology regulation.");

        doc.InsertHeading(3, "Question 1: Legal Status of Crypto-Tokens as Personal Property", 2);
        doc.AppendParagraph("We agree with the Law Commission's provisional conclusion that crypto-tokens are capable of being objects of personal property rights. The proposed 'third category' of personal property — distinct from choses in possession and choses in action — appropriately captures the unique characteristics of crypto-tokens.");
        doc.AppendParagraph("However, we note that the criterion of 'rivalrousness' requires further elaboration. The Law Commission's formulation at paragraph 4.60 — that the thing can only be used by one person at a time — may be difficult to apply to tokens that are technically divisible or to situations involving wrapping and bridging protocols.");

        doc.InsertHeading(3, "Question 3: Control-based Indicia of Title", 2);
        doc.AppendParagraph("We support a control-based approach to determining title to crypto-tokens, consistent with the approach adopted in other jurisdictions (Singapore, Singapore High Court, CLM v CLN [2022] SGHC 46; Australia, AA v BB [2022] FCA 1033). The concept of 'factual control' as proposed provides a workable standard for English courts.");
        doc.AppendParagraph("We caution, however, that the definition of 'control' should explicitly address multi-signature arrangements, custodian relationships, and the use of hardware security modules, where effective control may be split between multiple parties.");

        doc.InsertHeading(3, "Question 7: Netting Arrangements and Digital Asset Collateral", 2);
        doc.AppendParagraph("The Law Commission's provisional view that existing netting legislation does not adequately address digital asset collateral is supported by our members' experience. We endorse the recommendation for reform of the Financial Collateral Arrangements (No. 2) Regulations 2003 to extend their scope to digital asset collateral.");
        doc.AppendParagraph("We recommend that any reform expressly address the characterisation of on-chain settlement finality for the purposes of netting close-out, and the treatment of smart contract-embedded collateral arrangements under the proposed framework.");

        Assert.Equal(6, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetCommentCount());

        // AddComment — first reviewer (partner)
        doc.AddComment("J.Thornton", "Strong opening — note CP 256 published March 2023 for citation accuracy", 0);
        Assert.Equal(1, doc.GetCommentCount());

        doc.AddComment("J.Thornton", "Rivalrousness criterion: cite Jones v Skinner (1835) for historical context of choses in action", 2);
        Assert.Equal(2, doc.GetCommentCount());

        // Second reviewer (associate)
        doc.AddComment("S.Mehta", "CLM v CLN citation confirmed — check neutral citation [2022] SGHCR 4 vs SGHC 46", 4);
        Assert.Equal(3, doc.GetCommentCount());

        doc.AddComment("S.Mehta", "Multi-sig arrangements: add reference to ISDA's Digital Asset Derivatives paper (2023)", 4);
        Assert.Equal(4, doc.GetCommentCount());

        // Third reviewer (compliance)
        doc.AddComment("R.Clarke", "FCA guidance on Digital Securities Sandbox (DSS) relevant to Q7 — add citation", 6);
        Assert.Equal(5, doc.GetCommentCount());

        doc.AddComment("R.Clarke", "HMRC's position on netting for CGT purposes should be flagged as open issue", 6);
        Assert.Equal(6, doc.GetCommentCount());

        // Consistent
        Assert.Equal(6, doc.GetCommentCount());
        Assert.Equal(6, doc.GetParagraphCount()); // paragraph count unchanged

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount and GetCharCount
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_law_commission_response.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetCommentCount());
        Assert.Equal(6, loaded.GetParagraphCount());

        // Add resolution comment on loaded
        loaded.AddComment("J.Thornton", "RESOLVED: citation verified — both SGHCR 4 and SGHC 46 are correct (different proceedings)", 4);
        Assert.Equal(7, loaded.GetCommentCount());

        // AppendParagraph and comment on new content
        loaded.AppendParagraph("We would welcome the opportunity to engage further with the Law Commission during the consultation period and are available to participate in roundtable discussions.");
        loaded.AddComment("S.Mehta", "Standard closing paragraph — approved for submission", 7);
        Assert.Equal(8, loaded.GetCommentCount());
        Assert.Equal(7, loaded.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_law_commission_response_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(8, loaded2.GetCommentCount());
        Assert.Equal(7, loaded2.GetParagraphCount());
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddComment("Admin", "Submitted", 0));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
