// Tests for FodtDocument.GetCommentCount, AddComment, GetComments deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R270

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R270: Tests for FodtDocument.GetCommentCount, AddComment, GetComments deeper.
/// GetCommentCount(): returns the number of comments in the document.
/// AddComment(paragraphIndex, text): adds a comment to a paragraph.
/// GetComments(): returns a list of all comment texts.
/// Covers: GetCommentCount non-negative; GetCommentCount no-throw;
/// GetCommentCount consistent; GetCommentCount zero for new doc;
/// GetCommentCount after AddComment increases; GetCommentCount save-load;
/// AddComment no-throw; AddComment increases count; AddComment then GetComments has entry;
/// AddComment multiple paragraphs; AddComment save-load; AddComment then ExportToHtml no-throw;
/// AddComment then ExportToMarkdown no-throw; AddComment consistent;
/// GetComments non-null; GetComments no-throw; GetComments count equals GetCommentCount;
/// GetComments consistent; GetComments has correct text; GetComments save-load;
/// GetComments after multiple AddComment; GetComments all non-null-items;
/// dogfood CreateDoc→AddComment→GetCommentCount→GetComments→SaveToFile pipeline.
/// </summary>
public class FodtR270GetCommentCountAndAddCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR270GetCommentCountAndAddCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR270_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Quarterly Performance Report", 1);
        doc.AppendParagraph("Revenue growth for Q3 exceeded projections by twelve percent.");
        doc.AppendParagraph("Operating costs were maintained within the approved budget parameters.");
        doc.InsertHeading(3, "Regional Analysis", 2);
        doc.AppendParagraph("North region achieved highest growth at twenty-two percent year over year.");
        doc.AppendParagraph("South region met targets but faces increased competitive pressure.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCommentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void GetCommentCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetCommentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetCommentCount(), doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fresh document with no comments yet.");
        Assert.Equal(0, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_AfterAddComment_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCommentCount();
        doc.AddComment(1, "Revenue figure needs verification against finance report.");
        Assert.Equal(before + 1, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Review this paragraph for accuracy.");
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
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddComment(1, "First comment text here."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCommentCount();
        doc.AddComment(1, "Comment text for verification.");
        Assert.Equal(before + 1, doc.GetCommentCount());
    }

    [Fact]
    public void AddComment_Then_GetComments_HasEntry()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Unique comment sentinel XYZ999.");
        var comments = doc.GetComments();
        Assert.True(comments.Count > 0);
    }

    [Fact]
    public void AddComment_Multiple_Paragraphs()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Comment on paragraph one.");
        doc.AddComment(2, "Comment on paragraph two.");
        doc.AddComment(4, "Comment on paragraph four.");
        Assert.Equal(3, doc.GetCommentCount());
    }

    [Fact]
    public void AddComment_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "This comment must survive save-load cycle.");
        var before = doc.GetCommentCount();
        var path = TempFile("ac_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount());
    }

    [Fact]
    public void AddComment_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "HTML export comment test.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddComment(2, "Markdown export comment test.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Consistency check comment.");
        var count1 = doc.GetCommentCount();
        var count2 = doc.GetCommentCount();
        Assert.Equal(count1, count2);
    }

    // -------------------------------------------------------------------------
    // GetComments
    // -------------------------------------------------------------------------

    [Fact]
    public void GetComments_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetComments());
    }

    [Fact]
    public void GetComments_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetComments());
        Assert.Null(ex);
    }

    [Fact]
    public void GetComments_Count_Equals_GetCommentCount()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Test comment for count check.");
        doc.AddComment(2, "Second test comment.");
        Assert.Equal(doc.GetCommentCount(), doc.GetComments().Count);
    }

    [Fact]
    public void GetComments_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Consistency test comment.");
        var c1 = doc.GetComments();
        var c2 = doc.GetComments();
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void GetComments_HasCorrectText()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "ReviewNeededMarkerXYZ123");
        var comments = doc.GetComments();
        Assert.True(comments.Exists(c => c.Contains("ReviewNeededMarkerXYZ123")));
    }

    [Fact]
    public void GetComments_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Save load comment test.");
        doc.AddComment(2, "Another save load comment.");
        var before = doc.GetComments().Count;
        var path = TempFile("gc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetComments().Count);
    }

    [Fact]
    public void GetComments_AfterMultipleAddComment()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Comment A for paragraph 1.");
        doc.AddComment(2, "Comment B for paragraph 2.");
        doc.AddComment(3, "Comment C for paragraph 3.");
        doc.AddComment(4, "Comment D for paragraph 4.");
        var comments = doc.GetComments();
        Assert.Equal(4, comments.Count);
    }

    [Fact]
    public void GetComments_AllItems_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddComment(1, "Comment one.");
        doc.AddComment(2, "Comment two.");
        var comments = doc.GetComments();
        foreach (var c in comments)
            Assert.NotNull(c);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddComment_GetCommentCount_GetComments_SaveToFile_Pipeline()
    {
        // Build comprehensive document
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Board Meeting Minutes 2026", 1);
        doc.AppendParagraph("The board meeting convened at nine AM with all members present.");
        doc.AppendParagraph("Financial results for the quarter were presented by the CFO.");

        doc.InsertHeading(3, "Strategic Decisions", 2);
        doc.AppendParagraph("The board approved the acquisition strategy for three target companies.");
        doc.AppendParagraph("Capital allocation of fifty million was authorized for technology infrastructure.");

        doc.InsertHeading(6, "Risk Assessment", 2);
        doc.AppendParagraph("Supply chain risks were reviewed and mitigation plans approved.");
        doc.AppendParagraph("Regulatory compliance status confirmed as fully compliant in all jurisdictions.");

        doc.InsertHeading(9, "Action Items", 1);
        doc.AppendParagraph("CEO to present revised growth targets at next quarterly review.");
        doc.AppendParagraph("CFO to prepare detailed capital expenditure report for Q4.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetCommentCount — should be 0 initially
        Assert.Equal(0, doc.GetCommentCount());

        // GetComments — empty initially
        var emptyComments = doc.GetComments();
        Assert.NotNull(emptyComments);
        Assert.Equal(0, emptyComments.Count);

        // AddComment on multiple paragraphs
        doc.AddComment(1, "Attendance list to be attached as appendix A.");
        Assert.Equal(1, doc.GetCommentCount());

        doc.AddComment(2, "Verify Q3 figures against audited financial statements.");
        Assert.Equal(2, doc.GetCommentCount());

        doc.AddComment(4, "Legal review required before acquisition strategy is finalized.");
        Assert.Equal(3, doc.GetCommentCount());

        doc.AddComment(5, "Capital allocation subject to shareholder approval at AGM.");
        Assert.Equal(4, doc.GetCommentCount());

        doc.AddComment(6, "Supply chain mitigation plan details in Appendix C.");
        Assert.Equal(5, doc.GetCommentCount());

        // GetComments
        var comments = doc.GetComments();
        Assert.NotNull(comments);
        Assert.Equal(5, comments.Count);
        Assert.Equal(doc.GetCommentCount(), comments.Count);

        // Verify specific comment texts
        Assert.True(comments.Exists(c => c.Contains("attendance") || c.Contains("Attendance") || c.Contains("appendix")));

        // All comments non-null
        foreach (var c in comments)
            Assert.NotNull(c);

        // Consistent
        Assert.Equal(comments.Count, doc.GetComments().Count);

        // ExportToHtml still works after comments
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown still works after comments
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount and GetCharCount unaffected
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_minutes.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetCommentCount());

        // GetComments on loaded
        var loadedComments = loaded.GetComments();
        Assert.Equal(5, loadedComments.Count);
        foreach (var c in loadedComments)
            Assert.NotNull(c);

        // AddComment on loaded
        loaded.AddComment(7, "Action item deadline to be confirmed by operations team.");
        Assert.Equal(6, loaded.GetCommentCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Additional agenda item: review of sustainability targets for 2027.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // AddComment on new paragraph
        loaded.AddComment(loaded.GetParagraphCount() - 1, "Sustainability metrics to align with ESG framework.");
        Assert.Equal(7, loaded.GetCommentCount());

        // Final save
        var path2 = TempFile("dogfood_minutes_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetCommentCount());
        var loaded2Comments = loaded2.GetComments();
        Assert.Equal(7, loaded2Comments.Count);
        Assert.True(loaded2.GetParagraphCount() > 0);
    }
}
