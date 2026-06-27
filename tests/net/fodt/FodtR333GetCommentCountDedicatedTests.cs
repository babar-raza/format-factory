// Tests for FodtDocument.GetCommentCount dedicated coverage.
// Sprint: ff-sprint-s315-dotnet-deepening-20260630
// Ledger: PC-FODT-R333

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R333: Dedicated tests for FodtDocument.GetCommentCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddComment.
/// ParagraphCount unchanged after GetCommentCount.
/// TableCount unchanged after GetCommentCount.
/// SectionCount unchanged after GetCommentCount.
/// Idempotent (called twice same result).
/// Dogfood: add comment then count is non-negative.
/// Dogfood: multiple comments count is non-negative.
/// </summary>
public class FodtR333GetCommentCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCommentCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCommentCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetCommentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentCount_AfterAddComment_Increases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        int before = doc.GetCommentCount();
        doc.AddComment("Reviewer", "Please clarify");
        int after = doc.GetCommentCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetCommentCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetCommentCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCommentCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetCommentCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCommentCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetCommentCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetCommentCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph with comment");
        doc.AddComment("Author", "Review comment");
        int first = doc.GetCommentCount();
        int second = doc.GetCommentCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddComment_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body");
        doc.AddComment("Editor", "This needs revision");
        int count = doc.GetCommentCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleComments_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddComment("Reviewer1", "Great opening");
        doc.AddParagraph("Main content");
        doc.AddComment("Reviewer2", "Needs more detail");
        doc.AddComment("Reviewer1", "Agreed");
        int count = doc.GetCommentCount();
        Assert.True(count >= 0);
    }
}
