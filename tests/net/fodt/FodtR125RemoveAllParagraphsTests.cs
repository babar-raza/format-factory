// Tests for FodtDocument.RemoveAllParagraphs() — clears all content.
// Sprint: FORMAT-FACTORY-FODT-REMOVE-ALL-20260626
// Ledger: R125-GOVERNED-DOTNET-FODT-REMOVE-ALL-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R125: RemoveAllParagraphs() removes every paragraph (body and heading) from the
/// document. After the call, ParagraphCount = 0, GetPlainText returns empty/whitespace,
/// and subsequent AppendParagraph adds to a clean document.
/// Tests also cover rebuild after removal and interaction with GetDocumentStats.
/// </summary>
public class FodtR125RemoveAllParagraphsTests
{
    // ---- Empty document: remove all is a no-op ----

    [Fact]
    public void RemoveAllParagraphs_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.RemoveAllParagraphs());
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveAllParagraphs_EmptyDoc_ParagraphCountStillZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    // ---- Single paragraph removed ----

    [Fact]
    public void RemoveAllParagraphs_SingleParagraph_ParagraphCountZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only paragraph");

        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    // ---- Multiple paragraphs all removed ----

    [Fact]
    public void RemoveAllParagraphs_MultipleParagraphs_AllGone()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");

        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    // ---- Plain text empty after removal ----

    [Fact]
    public void RemoveAllParagraphs_PlainTextEmptyOrWhitespace()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some content here");

        doc.RemoveAllParagraphs();

        var text = doc.GetPlainText();
        Assert.True(string.IsNullOrWhiteSpace(text),
            $"Expected empty/whitespace plain text after RemoveAllParagraphs, got: '{text}'");
    }

    // ---- Headings also removed ----

    [Fact]
    public void RemoveAllParagraphs_IncludingHeadings_AllGone()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.AppendParagraph("Body text");
        doc.InsertHeading(2, "Section 1.1", 2);

        doc.RemoveAllParagraphs();

        Assert.Equal(0, doc.ParagraphCount);
        Assert.Equal(0, doc.GetHeadingCount());
    }

    // ---- AppendParagraph after removal starts fresh ----

    [Fact]
    public void RemoveAllParagraphs_ThenAppend_StartsFromIndex0()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Old");
        doc.AppendParagraph("Content");

        doc.RemoveAllParagraphs();
        doc.AppendParagraph("New content");

        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("New content", doc.GetParagraphText(0));
    }

    // ---- GetDocumentStats after removal: all zero ----

    [Fact]
    public void RemoveAllParagraphs_GetDocumentStats_AllZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        doc.InsertHeading(1, "Title", 1);

        doc.RemoveAllParagraphs();
        var stats = doc.GetDocumentStats();

        Assert.Equal(0, stats.ParagraphCount);
        Assert.Equal(0, stats.HeadingCount);
        Assert.Equal(0, stats.WordCount);
        Assert.Equal(0, stats.CharCount);
    }

    // ---- Paragraphs collection is empty ----

    [Fact]
    public void RemoveAllParagraphs_ParagraphsCollection_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");

        doc.RemoveAllParagraphs();

        Assert.Empty(doc.Paragraphs);
    }

    // ---- Dogfood: remove all, rebuild, export ----

    [Fact]
    public void DogfoodPipeline_RemoveAndRebuild_ExportedCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Old paragraph 1");
        doc.AppendParagraph("Old paragraph 2");

        doc.RemoveAllParagraphs();

        doc.InsertHeading(0, "New Title", 1);
        doc.AppendParagraph("New body text");

        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal(1, doc.GetHeadingCount());

        var html = doc.ExportToHtml();
        Assert.Contains("New Title", html);
        Assert.Contains("New body text", html);
        Assert.DoesNotContain("Old paragraph", html);
    }
}
