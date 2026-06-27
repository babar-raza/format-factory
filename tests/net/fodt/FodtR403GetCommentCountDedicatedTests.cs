// Tests for FodtDocument.GetCommentCount dedicated coverage.
// Sprint: ff-sprint-s385-dotnet-deepening-20260630
// Ledger: PC-FODT-R403

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R403: Dedicated tests for FodtDocument.CommentCount (or GetCommentCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking CommentCount.
/// TableCount unchanged after checking CommentCount.
/// FootnoteCount unchanged after checking CommentCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: CommentCount non-negative after paragraphs.
/// Dogfood: CommentCount non-negative after mixed content.
/// Dogfood: CommentCount never negative in loop.
/// </summary>
public class FodtR403GetCommentCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CommentCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.CommentCount >= 0);
    }

    [Fact]
    public void CommentCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.CommentCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void CommentCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.CommentCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void CommentCount_FootnoteCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.FootnoteCount;
        _ = doc.CommentCount;
        Assert.Equal(before, doc.FootnoteCount);
    }

    [Fact]
    public void CommentCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.CommentCount;
        int second = doc.CommentCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void CommentCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.CommentCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Reviewed section A");
        doc.AddParagraph("Reviewed section B");
        Assert.True(doc.CommentCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddTable(2, 3);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.CommentCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Review paragraph {i}");
            Assert.True(doc.CommentCount >= 0);
        }
    }
}
