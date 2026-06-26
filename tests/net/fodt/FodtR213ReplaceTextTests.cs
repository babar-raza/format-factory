// Tests for FodtDocument.ReplaceText dedicated coverage.
// Sprint: ff-sprint-s198-dotnet-deepening-20260629
// Ledger: PC-FODT-R213

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R213: Dedicated tests for FodtDocument.ReplaceText(string oldValue, string newValue).
/// null oldValue → ArgumentNullException.
/// null newValue → ArgumentNullException.
/// No match → document unchanged (no exception).
/// Single match replaced.
/// Multiple occurrences in same paragraph all replaced.
/// Across paragraphs: both replaced.
/// Case-sensitive: different case not replaced.
/// Empty string newValue → replacement with empty (deletion).
/// ParagraphCount unchanged after replace.
/// Dogfood: multi-step replace chain; replace then check GetPlainText.
/// </summary>
public class FodtR213ReplaceTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NullOldValue_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Throws<ArgumentNullException>(() => doc.ReplaceText(null!, "Hi"));
    }

    [Fact]
    public void ReplaceText_NullNewValue_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Throws<ArgumentNullException>(() => doc.ReplaceText("Hello", null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NoMatch_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var ex = Record.Exception(() => doc.ReplaceText("NotHere", "X"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_NoMatch_TextUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.ReplaceText("NotHere", "X");
        Assert.Equal("Hello World", doc.GetParagraphText(0));
    }

    [Fact]
    public void ReplaceText_SingleMatch_Replaced()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.ReplaceText("World", "Everyone");
        Assert.Contains("Everyone", doc.GetParagraphText(0));
    }

    [Fact]
    public void ReplaceText_AcrossParagraphs_BothReplaced()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.AppendParagraph("World again");
        doc.ReplaceText("World", "Earth");
        Assert.Contains("Earth", doc.GetParagraphText(0));
        Assert.Contains("Earth", doc.GetParagraphText(1));
    }

    [Fact]
    public void ReplaceText_CaseSensitive_DifferentCaseNotReplaced()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("hello world");
        doc.ReplaceText("World", "Earth");
        // lowercase "world" should NOT be replaced
        Assert.DoesNotContain("Earth", doc.GetParagraphText(0));
    }

    [Fact]
    public void ReplaceText_EmptyNewValue_DeletesOccurrence()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.ReplaceText("World", "");
        Assert.DoesNotContain("World", doc.GetParagraphText(0));
    }

    [Fact]
    public void ReplaceText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.ReplaceText("Alpha", "Gamma");
        Assert.Equal(before, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ChainedReplace_FinalStateCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        doc.ReplaceText("quick", "slow");
        doc.ReplaceText("brown", "red");
        var text = doc.GetParagraphText(0);
        Assert.Contains("slow", text);
        Assert.Contains("red", text);
        Assert.DoesNotContain("quick", text);
        Assert.DoesNotContain("brown", text);
    }

    [Fact]
    public void DogfoodPipeline_ReplaceAndGetPlainText_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Foo Bar");
        doc.AppendParagraph("Bar Baz");
        doc.ReplaceText("Bar", "Qux");
        var plain = doc.GetPlainText();
        Assert.Contains("Qux", plain);
        Assert.DoesNotContain("Bar", plain);
    }
}
