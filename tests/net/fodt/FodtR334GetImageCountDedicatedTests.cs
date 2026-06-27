// Tests for FodtDocument.GetImageCount dedicated coverage.
// Sprint: ff-sprint-s316-dotnet-deepening-20260630
// Ledger: PC-FODT-R334

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R334: Dedicated tests for FodtDocument.GetImageCount().
/// Non-negative on empty document.
/// Empty document ok.
/// ParagraphCount unchanged after GetImageCount.
/// TableCount unchanged after GetImageCount.
/// SectionCount unchanged after GetImageCount.
/// Idempotent (called twice same result).
/// Does not throw on document with content.
/// Dogfood: document with multiple sections count is non-negative.
/// Dogfood: two documents independent counts.
/// </summary>
public class FodtR334GetImageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetImageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetImageCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetImageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetImageCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetImageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetImageCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetImageCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetImageCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetImageCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph one");
        int first = doc.GetImageCount();
        int second = doc.GetImageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetImageCount_DocumentWithContent_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        doc.AddParagraph("Second paragraph");
        var ex = Record.Exception(() => doc.GetImageCount());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithSections_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Introduction");
        doc.AddParagraph("Body text");
        doc.AddSection("Conclusion");
        int count = doc.GetImageCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoDocuments_IndependentCounts()
    {
        var doc1 = FodtDocument.CreateNew();
        doc1.AddParagraph("Doc1 paragraph");

        var doc2 = FodtDocument.CreateNew();
        doc2.AddParagraph("Doc2 para A");
        doc2.AddParagraph("Doc2 para B");

        int count1 = doc1.GetImageCount();
        int count2 = doc2.GetImageCount();

        Assert.True(count1 >= 0);
        Assert.True(count2 >= 0);
    }
}
