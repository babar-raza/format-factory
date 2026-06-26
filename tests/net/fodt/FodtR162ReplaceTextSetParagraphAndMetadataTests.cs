// Tests for FodtDocument.ReplaceText, SetParagraphText, RemoveAllParagraphs,
// GetParagraphTexts, MimeType, OdfVersion.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R162

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R162: Tests for FodtDocument mutation and metadata methods.
/// ReplaceText(old, new): replaces all occurrences case-sensitively by default; returns replacement count.
/// SetParagraphText(index, text): replaces paragraph text at given index; OOB throws.
/// RemoveAllParagraphs(): clears all paragraphs; ParagraphCount becomes 0.
/// GetParagraphTexts(): returns list of all paragraph text strings.
/// MimeType: returns ODF text MIME type string.
/// OdfVersion: returns ODF version string.
/// Covers: ReplaceText single occurrence returns 1; ReplaceText no match returns 0;
/// ReplaceText multiple occurrences returns count; ReplaceText updates paragraph text;
/// SetParagraphText valid index updates text; SetParagraphText OOB throws;
/// RemoveAllParagraphs after appending returns zero; RemoveAllParagraphs empty doc is noop;
/// GetParagraphTexts matches AppendParagraph order; GetParagraphTexts empty doc is empty;
/// MimeType is not null/empty; OdfVersion is not null/empty;
/// dogfood CreateEmpty->Append->Replace->SetParagraphText->GetParagraphTexts pipeline.
/// </summary>
public class FodtR162ReplaceTextSetParagraphAndMetadataTests
{
    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_SingleOccurrence_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var count = doc.ReplaceText("world", "there");
        Assert.Equal(1, count);
    }

    [Fact]
    public void ReplaceText_NoMatch_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var count = doc.ReplaceText("xyz", "abc");
        Assert.Equal(0, count);
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences_ReturnsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("foo bar foo");
        doc.AppendParagraph("foo baz");
        var count = doc.ReplaceText("foo", "qux");
        Assert.Equal(3, count);
    }

    [Fact]
    public void ReplaceText_UpdatesParagraphContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        doc.ReplaceText("world", "C#");
        Assert.Equal("Hello C#.", doc.GetParagraphText(0));
    }

    [Fact]
    public void ReplaceText_EmptyDoc_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        var count = doc.ReplaceText("anything", "nothing");
        Assert.Equal(0, count);
    }

    // -------------------------------------------------------------------------
    // SetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ValidIndex_UpdatesText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text.");
        doc.SetParagraphText(0, "Updated text.");
        Assert.Equal("Updated text.", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_DoesNotAffectOtherParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.AppendParagraph("Second.");
        doc.SetParagraphText(0, "Changed.");
        Assert.Equal("Second.", doc.GetParagraphText(1));
    }

    [Fact]
    public void SetParagraphText_OobIndex_Throws()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only.");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(5, "X"));
    }

    [Fact]
    public void SetParagraphText_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only.");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(-1, "X"));
    }

    // -------------------------------------------------------------------------
    // RemoveAllParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAllParagraphs_AfterAppending_ParagraphCountIsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One.");
        doc.AppendParagraph("Two.");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_EmptyDoc_IsNoop()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.RemoveAllParagraphs(); // Should not throw
        Assert.Equal(0, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_MatchesAppendOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha.");
        doc.AppendParagraph("Beta.");
        var texts = doc.GetParagraphTexts();
        Assert.Equal("Alpha.", texts[0]);
        Assert.Equal("Beta.", texts[1]);
    }

    [Fact]
    public void GetParagraphTexts_EmptyDoc_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetParagraphTexts());
    }

    // -------------------------------------------------------------------------
    // MimeType / OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_IsNotNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.False(string.IsNullOrEmpty(doc.MimeType));
    }

    [Fact]
    public void OdfVersion_IsNotNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.False(string.IsNullOrEmpty(doc.OdfVersion));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Append->Replace->SetParagraphText->GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendReplaceSetsGetTexts_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox.");
        doc.AppendParagraph("The lazy dog.");

        // Replace across paragraphs
        var replaced = doc.ReplaceText("The", "A");
        Assert.Equal(2, replaced);

        // Update first paragraph directly
        doc.SetParagraphText(0, "A slow red fox.");
        Assert.Equal("A slow red fox.", doc.GetParagraphText(0));

        // Get all texts
        var texts = doc.GetParagraphTexts();
        Assert.Equal(2, texts.Count);
        Assert.Contains("A slow red fox.", texts);

        // Remove all
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
        Assert.Empty(doc.GetParagraphTexts());
    }
}
