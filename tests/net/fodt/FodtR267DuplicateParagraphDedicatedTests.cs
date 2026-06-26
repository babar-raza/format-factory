// Tests for FodtDocument.DuplicateParagraph dedicated coverage.
// Sprint: ff-sprint-s252-dotnet-deepening-20260630
// Ledger: PC-FODT-R267

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R267: Dedicated tests for FodtDocument.DuplicateParagraph(index).
/// DuplicateParagraph creates a copy of the paragraph at index and inserts it after.
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid index → no exception.
/// ParagraphCount increases by 1.
/// Duplicated paragraph text matches original.
/// Original paragraph at index unchanged.
/// Multiple duplications work correctly.
/// Dogfood: duplicate, verify copy follows original.
/// Dogfood: duplicate multiple times, count tracks.
/// </summary>
public class FodtR267DuplicateParagraphDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DuplicateParagraph_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Some text");
        Assert.ThrowsAny<Exception>(() => doc.DuplicateParagraph(-1));
    }

    [Fact]
    public void DuplicateParagraph_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Content");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.DuplicateParagraph(count));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DuplicateParagraph_ValidIndex_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Paragraph to duplicate");
        var ex = Record.Exception(() => doc.DuplicateParagraph(0));
        Assert.Null(ex);
    }

    [Fact]
    public void DuplicateParagraph_ParagraphCountIncreasesBy1()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Original");
        int before = doc.ParagraphCount;
        doc.DuplicateParagraph(0);
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void DuplicateParagraph_DuplicatedTextMatchesOriginal()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Unique content here");
        doc.DuplicateParagraph(0);
        // The duplicated paragraph should contain the same text
        string original = doc.GetParagraphText(0);
        string duplicate = doc.GetParagraphText(1);
        Assert.Contains("Unique content here", duplicate);
    }

    [Fact]
    public void DuplicateParagraph_OriginalParagraph_Unchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Stay as-is");
        doc.DuplicateParagraph(0);
        // Original paragraph text should remain the same
        string original = doc.GetParagraphText(0);
        Assert.Contains("Stay as-is", original);
    }

    [Fact]
    public void DuplicateParagraph_MultipleDuplications_CountGrows()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Base paragraph");
        int startCount = doc.ParagraphCount;
        doc.DuplicateParagraph(0);
        doc.DuplicateParagraph(0);
        Assert.Equal(startCount + 2, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Duplicate_VerifyCopyFollowsOriginal()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Third paragraph");
        // Duplicate the first paragraph — it should appear after index 0
        doc.DuplicateParagraph(0);
        // Now there should be 3 paragraphs
        Assert.Equal(3, doc.ParagraphCount);
        // The duplicate should contain the same text as original
        Assert.Contains("First paragraph", doc.GetParagraphText(1));
    }

    [Fact]
    public void DogfoodPipeline_DuplicateMultiple_CountTracks()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Template paragraph");
        doc.AppendParagraph("Another paragraph");
        int startCount = doc.ParagraphCount;
        doc.DuplicateParagraph(0);
        doc.DuplicateParagraph(1);
        doc.DuplicateParagraph(2);
        Assert.Equal(startCount + 3, doc.ParagraphCount);
    }
}
