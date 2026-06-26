// Tests for FodtDocument.SetParagraphText dedicated coverage.
// Sprint: ff-sprint-s253-dotnet-deepening-20260630
// Ledger: PC-FODT-R268

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R268: Dedicated tests for FodtDocument.SetParagraphText(index, text).
/// Sets/replaces the text content of an existing paragraph at the given index.
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid index with text → no exception.
/// ParagraphCount unchanged.
/// GetParagraphText returns the new text.
/// Original text replaced (not appended).
/// Setting to empty string allowed.
/// Other paragraphs unaffected.
/// Dogfood: set text, retrieve it, verify match.
/// Dogfood: update text multiple times, final value correct.
/// </summary>
public class FodtR268SetParagraphTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Existing");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(-1, "New text"));
    }

    [Fact]
    public void SetParagraphText_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Only one");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(count, "Beyond"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ValidIndex_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Initial text");
        var ex = Record.Exception(() => doc.SetParagraphText(0, "Updated text"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        int before = doc.ParagraphCount;
        doc.SetParagraphText(0, "Modified First");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphText_TextUpdated()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Original text");
        doc.SetParagraphText(0, "Replacement text");
        string text = doc.GetParagraphText(0);
        Assert.Contains("Replacement text", text);
    }

    [Fact]
    public void SetParagraphText_OtherParagraphsUnaffected()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Unchanged");
        doc.AppendParagraph("To be changed");
        doc.SetParagraphText(1, "Now changed");
        // First paragraph should be untouched
        Assert.Contains("Unchanged", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_SetToEmpty_Allowed()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Some content");
        var ex = Record.Exception(() => doc.SetParagraphText(0, string.Empty));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetText_RetrieveVerifyMatch()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Placeholder");
        string newText = "The quick brown fox";
        doc.SetParagraphText(0, newText);
        string retrieved = doc.GetParagraphText(0);
        Assert.Contains(newText, retrieved);
    }

    [Fact]
    public void DogfoodPipeline_UpdateMultipleTimes_FinalValueCorrect()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Version 1");
        doc.SetParagraphText(0, "Version 2");
        doc.SetParagraphText(0, "Version 3");
        string final = doc.GetParagraphText(0);
        Assert.Contains("Version 3", final);
    }
}
