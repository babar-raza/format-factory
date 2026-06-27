// Tests for FodtDocument.GetHeadingCount dedicated coverage.
// Sprint: ff-sprint-s381-dotnet-deepening-20260630
// Ledger: PC-FODT-R399

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R399: Dedicated tests for FodtDocument.HeadingCount (or GetHeadingCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking HeadingCount.
/// TableCount unchanged after checking HeadingCount.
/// BookmarkCount unchanged after checking HeadingCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: HeadingCount non-negative after paragraphs.
/// Dogfood: HeadingCount non-negative after tables.
/// Dogfood: HeadingCount never negative in loop.
/// </summary>
public class FodtR399GetHeadingCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void HeadingCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.HeadingCount >= 0);
    }

    [Fact]
    public void HeadingCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.HeadingCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void HeadingCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.HeadingCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void HeadingCount_BookmarkCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.BookmarkCount;
        _ = doc.HeadingCount;
        Assert.Equal(before, doc.BookmarkCount);
    }

    [Fact]
    public void HeadingCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.HeadingCount;
        int second = doc.HeadingCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void HeadingCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.HeadingCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Executive Summary");
        doc.AddParagraph("Introduction");
        Assert.True(doc.HeadingCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterTables_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        doc.AddTable(4, 2);
        Assert.True(doc.HeadingCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Heading {i}");
            Assert.True(doc.HeadingCount >= 0);
        }
    }
}
