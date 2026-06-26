// Tests for FodtDocument.GetParagraphText dedicated coverage.
// Sprint: ff-sprint-s260-dotnet-deepening-20260630
// Ledger: PC-FODT-R275

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R275: Dedicated tests for FodtDocument.GetParagraphText(index).
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid index → returns non-null string.
/// Text matches what was added via AddParagraph.
/// After SetParagraphText, returns the new text.
/// ParagraphCount unchanged after call.
/// Called twice → same result.
/// Dogfood: add paragraph, verify retrieved text matches.
/// Dogfood: multiple paragraphs, each returns correct text.
/// </summary>
public class FodtR275GetParagraphTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello World");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(-1));
    }

    [Fact]
    public void GetParagraphText_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello World");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(count));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        string text = doc.GetParagraphText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetParagraphText_MatchesAddedText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox");
        string text = doc.GetParagraphText(0);
        Assert.Equal("The quick brown fox", text);
    }

    [Fact]
    public void GetParagraphText_AfterSetParagraphText_ReturnsNewText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Original text");
        doc.SetParagraphText(0, "Updated text");
        string text = doc.GetParagraphText(0);
        Assert.Equal("Updated text", text);
    }

    [Fact]
    public void GetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content");
        int before = doc.ParagraphCount;
        doc.GetParagraphText(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Consistent text");
        string first = doc.GetParagraphText(0);
        string second = doc.GetParagraphText(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddAndRetrieve_TextMatches()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Format Factory is great");
        string retrieved = doc.GetParagraphText(0);
        Assert.Equal("Format Factory is great", retrieved);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        doc.AddParagraph("Third paragraph");
        Assert.Equal("First paragraph", doc.GetParagraphText(0));
        Assert.Equal("Second paragraph", doc.GetParagraphText(1));
        Assert.Equal("Third paragraph", doc.GetParagraphText(2));
    }
}
