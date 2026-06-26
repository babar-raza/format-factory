// Tests for FodtDocument.InsertParagraph dedicated coverage.
// Sprint: ff-sprint-s247-dotnet-deepening-20260630
// Ledger: PC-FODT-R262

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R262: Dedicated tests for FodtDocument.InsertParagraph(index, text).
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid insertion → no exception.
/// ParagraphCount increases after insertion.
/// Inserted text retrievable via GetParagraphText.
/// Insert at index 0 shifts existing paragraphs.
/// Insert at end appends.
/// Dogfood: insert two paragraphs at different indices, verify order.
/// Dogfood: repeated insertions, count tracks accurately.
/// </summary>
public class FodtR262InsertParagraphDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertParagraph(-1, "Bad index"));
    }

    [Fact]
    public void InsertParagraph_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Existing para");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.InsertParagraph(count + 1, "Too far"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_ValidIndex_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First");
        var ex = Record.Exception(() => doc.InsertParagraph(0, "Before First"));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertParagraph_ParagraphCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Initial");
        int before = doc.ParagraphCount;
        doc.InsertParagraph(0, "Inserted");
        Assert.True(doc.ParagraphCount > before);
    }

    [Fact]
    public void InsertParagraph_TextRetrievable()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Existing");
        doc.InsertParagraph(0, "My Inserted Text");
        string text = doc.GetParagraphText(0);
        Assert.Contains("My Inserted Text", text);
    }

    [Fact]
    public void InsertParagraph_AtZero_ShiftsExistingParagraphs()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Original");
        doc.InsertParagraph(0, "New First");
        // "New First" should now be at index 0
        Assert.Contains("New First", doc.GetParagraphText(0));
        // "Original" should now be at index 1
        Assert.Contains("Original", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_AtEnd_Appends()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        int count = doc.ParagraphCount;
        doc.InsertParagraph(count, "Last");
        // Last should be at the new end
        int newCount = doc.ParagraphCount;
        Assert.Contains("Last", doc.GetParagraphText(newCount - 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertTwoParagraphs_VerifyOrder()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Middle");
        doc.InsertParagraph(0, "First");
        int count = doc.ParagraphCount;
        doc.InsertParagraph(count, "Last");
        Assert.Contains("First", doc.GetParagraphText(0));
        Assert.Contains("Middle", doc.GetParagraphText(1));
        Assert.Contains("Last", doc.GetParagraphText(doc.ParagraphCount - 1));
    }

    [Fact]
    public void DogfoodPipeline_RepeatedInsertions_CountTracks()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Base");
        int startCount = doc.ParagraphCount;
        doc.InsertParagraph(0, "Insert1");
        doc.InsertParagraph(0, "Insert2");
        doc.InsertParagraph(0, "Insert3");
        Assert.Equal(startCount + 3, doc.ParagraphCount);
    }
}
