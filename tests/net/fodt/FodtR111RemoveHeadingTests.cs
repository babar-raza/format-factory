// R111 Wave 5: FODT RemoveHeading tests
// Ledger: R111-GOVERNED-DOTNET-FODT-REMOVEHEADING-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR111RemoveHeadingTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void RemoveHeading_ExistingHeading_RemovesIt()
    {
        var doc = FodtDocument.Load(MinimalPath);
        // Insert a heading first, then remove it
        int beforeCount = doc.ParagraphCount;
        doc.InsertHeading(0, "Test Heading", 1);
        Assert.Equal(beforeCount + 1, doc.ParagraphCount);
        doc.RemoveHeading(0);
        Assert.Equal(beforeCount, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveHeading_NotAHeading_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        // Ensure first element is a paragraph, not heading, by appending one
        doc.AppendParagraph("regular paragraph");
        int lastIdx = doc.ParagraphCount - 1;
        // The appended paragraph is text:p, not text:h
        Assert.Throws<InvalidOperationException>(() =>
            doc.RemoveHeading(lastIdx));
    }

    [Fact]
    public void RemoveHeading_NegativeIndex_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.RemoveHeading(-1));
    }

    [Fact]
    public void RemoveHeading_IndexTooLarge_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.RemoveHeading(99999));
    }

    [Fact]
    public void RemoveHeading_MultipleHeadings_RemovesCorrectOne()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int baseCount = doc.ParagraphCount;
        doc.InsertHeading(0, "First", 1);
        doc.InsertHeading(1, "Second", 2);
        Assert.Equal(baseCount + 2, doc.ParagraphCount);

        // Remove "First" at index 0
        doc.RemoveHeading(0);
        Assert.Equal(baseCount + 1, doc.ParagraphCount);
        // "Second" should now be at index 0
        Assert.Equal("Second", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void RemoveHeading_ThenInsert_RoundTrips()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "TempHeading", 3);
        doc.RemoveHeading(0);
        doc.InsertHeading(0, "NewHeading", 2);
        Assert.Equal("NewHeading", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void RemoveHeading_SurvivesSaveRoundtrip()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "WillBeRemoved", 1);
        doc.InsertHeading(1, "WillStay", 2);
        doc.RemoveHeading(0);

        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal("WillStay", reloaded.Paragraphs[0].Text);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void RemoveHeading_EmptyDocument_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.RemoveHeading(0));
    }
}
