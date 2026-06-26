// Tests for FodtDocument.ReplaceParagraphText dedicated coverage.
// Sprint: ff-sprint-s224-dotnet-deepening-20260629
// Ledger: PC-FODT-R239

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R239: Dedicated tests for FodtDocument.ReplaceParagraphText(index, newText).
/// Negative index → throws exception.
/// OOB index → throws exception.
/// Valid replace → no exception.
/// Text updated after replace.
/// ParagraphCount unchanged after replace.
/// Replace with empty string → no exception.
/// Second paragraph replaceable independently.
/// Called twice: latest value preserved.
/// Dogfood: add paragraphs, replace all, verify.
/// Dogfood: replace and retrieve round-trip.
/// </summary>
public class FodtR239ReplaceParagraphTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceParagraphText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        Assert.ThrowsAny<Exception>(() => doc.ReplaceParagraphText(-1, "New"));
    }

    [Fact]
    public void ReplaceParagraphText_OobIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        Assert.ThrowsAny<Exception>(() => doc.ReplaceParagraphText(10, "New"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceParagraphText_ValidReplace_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text");
        var ex = Record.Exception(() => doc.ReplaceParagraphText(0, "Replaced text"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceParagraphText_TextUpdated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Before");
        doc.ReplaceParagraphText(0, "After");
        var text = doc.GetParagraphText(0);
        Assert.Contains("After", text);
    }

    [Fact]
    public void ReplaceParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");
        doc.AppendParagraph("Two");
        int before = doc.ParagraphCount;
        doc.ReplaceParagraphText(0, "Replaced");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ReplaceParagraphText_WithEmptyString_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        var ex = Record.Exception(() => doc.ReplaceParagraphText(0, ""));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceParagraphText_SecondParagraphIndependent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.ReplaceParagraphText(1, "Replaced Second");
        Assert.Contains("First", doc.GetParagraphText(0));
        Assert.Contains("Replaced Second", doc.GetParagraphText(1));
    }

    [Fact]
    public void ReplaceParagraphText_ReplaceTwice_LatestValuePreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial");
        doc.ReplaceParagraphText(0, "Middle");
        doc.ReplaceParagraphText(0, "Final");
        Assert.Contains("Final", doc.GetParagraphText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ReplaceAll_VerifyAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P0");
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.ReplaceParagraphText(0, "New P0");
        doc.ReplaceParagraphText(1, "New P1");
        doc.ReplaceParagraphText(2, "New P2");
        Assert.Contains("New P0", doc.GetParagraphText(0));
        Assert.Contains("New P1", doc.GetParagraphText(1));
        Assert.Contains("New P2", doc.GetParagraphText(2));
    }

    [Fact]
    public void DogfoodPipeline_ReplaceAndRetrieve_RoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.ReplaceParagraphText(0, "Round-trip text");
        var retrieved = doc.GetParagraphText(0);
        Assert.Contains("Round-trip text", retrieved);
    }
}
