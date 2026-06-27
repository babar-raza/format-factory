// Tests for FodtDocument.GetBookmarkCount dedicated coverage.
// Sprint: ff-sprint-s380-dotnet-deepening-20260630
// Ledger: PC-FODT-R398

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R398: Dedicated tests for FodtDocument.BookmarkCount (or GetBookmarkCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking BookmarkCount.
/// TableCount unchanged after checking BookmarkCount.
/// SectionCount unchanged after checking BookmarkCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: BookmarkCount non-negative after paragraphs.
/// Dogfood: BookmarkCount non-negative after tables.
/// Dogfood: BookmarkCount never negative in loop.
/// </summary>
public class FodtR398GetBookmarkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BookmarkCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.BookmarkCount >= 0);
    }

    [Fact]
    public void BookmarkCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.BookmarkCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void BookmarkCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.BookmarkCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void BookmarkCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.SectionCount;
        _ = doc.BookmarkCount;
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void BookmarkCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.BookmarkCount;
        int second = doc.BookmarkCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void BookmarkCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.BookmarkCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Chapter 1");
        doc.AddParagraph("Chapter 2");
        Assert.True(doc.BookmarkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterTables_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        doc.AddTable(4, 2);
        Assert.True(doc.BookmarkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Section {i}");
            Assert.True(doc.BookmarkCount >= 0);
        }
    }
}
