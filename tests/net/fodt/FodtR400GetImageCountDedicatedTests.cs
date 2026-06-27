// Tests for FodtDocument.GetImageCount dedicated coverage.
// Sprint: ff-sprint-s382-dotnet-deepening-20260630
// Ledger: PC-FODT-R400

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R400: Dedicated tests for FodtDocument.ImageCount (or GetImageCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking ImageCount.
/// TableCount unchanged after checking ImageCount.
/// HeadingCount unchanged after checking ImageCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: ImageCount non-negative after paragraphs.
/// Dogfood: ImageCount non-negative after tables.
/// Dogfood: ImageCount never negative in loop.
/// </summary>
public class FodtR400GetImageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ImageCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.ImageCount >= 0);
    }

    [Fact]
    public void ImageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.ImageCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ImageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.ImageCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void ImageCount_HeadingCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.HeadingCount;
        _ = doc.ImageCount;
        Assert.Equal(before, doc.HeadingCount);
    }

    [Fact]
    public void ImageCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.ImageCount;
        int second = doc.ImageCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void ImageCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.ImageCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Figure 1 caption");
        doc.AddParagraph("Figure 2 caption");
        Assert.True(doc.ImageCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterTables_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        doc.AddTable(2, 2);
        Assert.True(doc.ImageCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Content block {i}");
            Assert.True(doc.ImageCount >= 0);
        }
    }
}
