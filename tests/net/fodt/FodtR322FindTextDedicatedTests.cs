// Tests for FodtDocument.FindText dedicated coverage.
// Sprint: ff-sprint-s307-dotnet-deepening-20260630
// Ledger: PC-FODT-R322

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R322: Dedicated tests for FodtDocument.FindText(searchText).
/// Null search text throws exception.
/// Empty search returns false or throws.
/// Text that exists returns true.
/// Text that does not exist returns false.
/// ParagraphCount unchanged after FindText.
/// TableCount unchanged after FindText.
/// Case-consistent: same text found twice.
/// Dogfood: add paragraphs and find contained text.
/// Dogfood: find text absent from document returns false.
/// </summary>
public class FodtR322FindTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindText_NullSearchText_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        Assert.ThrowsAny<Exception>(() => doc.FindText(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindText_ExistingText_ReturnsTrue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox");
        bool found = doc.FindText("quick");
        Assert.True(found);
    }

    [Fact]
    public void FindText_NonExistingText_ReturnsFalse()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        bool found = doc.FindText("xyz_not_here_999");
        Assert.False(found);
    }

    [Fact]
    public void FindText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int before = doc.ParagraphCount;
        _ = doc.FindText("Hello");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void FindText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int before = doc.TableCount;
        _ = doc.FindText("Hello");
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void FindText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Sample text content");
        bool first = doc.FindText("Sample");
        bool second = doc.FindText("Sample");
        Assert.Equal(first, second);
    }

    [Fact]
    public void FindText_FullParagraphText_ReturnsTrue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Exact match paragraph");
        bool found = doc.FindText("Exact match paragraph");
        Assert.True(found);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FindTextInMultipleParagraphs_ReturnsTrue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction section");
        doc.AddParagraph("Main body with important content");
        doc.AddParagraph("Conclusion with summary");
        bool found = doc.FindText("important");
        Assert.True(found);
        Assert.Equal(3, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_FindAbsentText_ReturnsFalse()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        bool found = doc.FindText("xyzzy_absent_text_42");
        Assert.False(found);
    }
}
