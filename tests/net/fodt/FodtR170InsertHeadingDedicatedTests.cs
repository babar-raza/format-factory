// Tests for FodtDocument.InsertHeading dedicated coverage.
// Sprint: ff-sprint-s161-dotnet-deepening-20260628
// Ledger: PC-FODT-R170

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R170: Dedicated tests for FodtDocument.InsertHeading(int index, string text, int level).
/// InsertHeading inserts a heading at the given position (before the element at index).
/// Level must be between 1 and 6 (throws ArgumentOutOfRangeException otherwise).
/// Index must be in range [0, ParagraphCount] (throws ArgumentOutOfRangeException otherwise).
/// Returns the created FodtParagraph.
/// Covers: level=0 throws ArgumentOutOfRangeException; level=7 throws ArgumentOutOfRangeException;
/// negative index throws ArgumentOutOfRangeException; index beyond count throws;
/// valid level=1 insert no-throw; valid level=6 insert no-throw;
/// count increases after insert; inserted heading appears in GetHeadingTexts;
/// insert at 0 places before first; dogfood AppendParagraph->InsertHeading;
/// dogfood insert at end appends correctly.
/// </summary>
public class FodtR170InsertHeadingDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_LevelZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertHeading(0, "Title", 0));
    }

    [Fact]
    public void InsertHeading_LevelSeven_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertHeading(0, "Title", 7));
    }

    [Fact]
    public void InsertHeading_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertHeading(-1, "Title", 1));
    }

    [Fact]
    public void InsertHeading_IndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertHeading(5, "Title", 1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_Level1_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertHeading_Level6_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Deep Heading", 6);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertHeading_ValidCall_IncreasesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Existing", 1);
        var before = doc.ParagraphCount;
        doc.InsertHeading(0, "New First", 1);
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertHeading_InsertedHeading_AppearsInGetHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter A", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Contains("Chapter A", texts);
    }

    [Fact]
    public void InsertHeading_InsertAtZero_PlacesBeforeFirst()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Second", 1);
        doc.InsertHeading(0, "First", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Equal("First", texts[0]);
        Assert.Equal("Second", texts[1]);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_InsertHeadingAtZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text");
        doc.InsertHeading(0, "Title", 1);
        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal("Title", doc.GetHeadingTexts()[0]);
    }

    [Fact]
    public void DogfoodPipeline_InsertHeadingAtEnd_AppendsCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Start", 1);
        doc.AppendParagraph("Middle");
        doc.InsertHeading(doc.ParagraphCount, "End Heading", 2);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(2, texts.Count);
        Assert.Equal("End Heading", texts[1]);
    }
}
