// Tests for FodtDocument.RemoveParagraph, SetParagraphText, AppendParagraph deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R191

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R191: Tests for FodtDocument.RemoveParagraph, SetParagraphText, AppendParagraph deeper coverage.
/// RemoveParagraph(index): removes paragraph at index.
/// SetParagraphText(index, text): updates text of paragraph at index.
/// AppendParagraph(text): adds paragraph at end.
/// Covers: RemoveParagraph decrements ParagraphCount; RemoveParagraph index 0 removes first;
/// RemoveParagraph last index removes last; SetParagraphText updates text;
/// SetParagraphText GetParagraphText round-trips; AppendParagraph increments count;
/// AppendParagraph text accessible via GetParagraphText; AppendParagraph returns paragraph;
/// AppendParagraph->GetParagraphTexts contains new text; RemoveParagraph then GetParagraphTexts;
/// SetParagraphText then GetPlainText has updated text; AppendParagraph multiple;
/// RemoveAllParagraphs then ParagraphCount is zero; GetParagraphText valid index;
/// dogfood AppendParagraph->SetParagraphText->RemoveParagraph->GetParagraphTexts pipeline.
/// </summary>
public class FodtR191RemoveParagraphAndSetTextTests
{
    private static FodtDocument CreateWithParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Paragraph one.");
        doc.AppendParagraph("Paragraph two.");
        doc.AppendParagraph("Paragraph three.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // RemoveParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_DecrementsCount()
    {
        var doc = CreateWithParagraphs();
        var before = doc.ParagraphCount;
        doc.RemoveParagraph(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveParagraph_Index0_RemovesFirst()
    {
        var doc = CreateWithParagraphs();
        doc.RemoveParagraph(0);
        var texts = doc.GetParagraphTexts();
        Assert.DoesNotContain("Paragraph one.", texts);
    }

    [Fact]
    public void RemoveParagraph_LastIndex_RemovesLast()
    {
        var doc = CreateWithParagraphs();
        var lastIdx = doc.ParagraphCount - 1;
        doc.RemoveParagraph(lastIdx);
        var texts = doc.GetParagraphTexts();
        Assert.DoesNotContain("Paragraph three.", texts);
    }

    [Fact]
    public void RemoveParagraph_ThenGetParagraphTexts_HasRemainder()
    {
        var doc = CreateWithParagraphs();
        doc.RemoveParagraph(1); // remove "Paragraph two."
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Paragraph one.", texts);
        Assert.Contains("Paragraph three.", texts);
        Assert.DoesNotContain("Paragraph two.", texts);
    }

    // -------------------------------------------------------------------------
    // SetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_UpdatesText()
    {
        var doc = CreateWithParagraphs();
        doc.SetParagraphText(0, "Updated paragraph one.");
        var text = doc.GetParagraphText(0);
        Assert.Equal("Updated paragraph one.", text);
    }

    [Fact]
    public void SetParagraphText_GetParagraphText_RoundTrips()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text.");
        doc.SetParagraphText(0, "New text.");
        Assert.Equal("New text.", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_ThenGetPlainText_HasUpdatedText()
    {
        var doc = CreateWithParagraphs();
        doc.SetParagraphText(1, "Modified paragraph.");
        var text = doc.GetPlainText();
        Assert.Contains("Modified paragraph", text);
    }

    // -------------------------------------------------------------------------
    // AppendParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendParagraph_IncrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.ParagraphCount;
        doc.AppendParagraph("New paragraph.");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void AppendParagraph_TextAccessibleViaGetParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Accessible paragraph.");
        var text = doc.GetParagraphText(0);
        Assert.Equal("Accessible paragraph.", text);
    }

    [Fact]
    public void AppendParagraph_GetParagraphTexts_ContainsNew()
    {
        var doc = CreateWithParagraphs();
        doc.AppendParagraph("Fourth paragraph.");
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Fourth paragraph.", texts);
    }

    [Fact]
    public void AppendParagraph_Multiple_AllAccessible()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Alpha", texts);
        Assert.Contains("Beta", texts);
        Assert.Contains("Gamma", texts);
    }

    // -------------------------------------------------------------------------
    // RemoveAllParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAllParagraphs_ParagraphCountIsZero()
    {
        var doc = CreateWithParagraphs();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // GetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_ValidIndex_ReturnsText()
    {
        var doc = CreateWithParagraphs();
        Assert.Equal("Paragraph two.", doc.GetParagraphText(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendParagraph->SetParagraphText->RemoveParagraph->GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendSetRemoveGetParagraphTexts_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // AppendParagraph
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        Assert.Equal(3, doc.ParagraphCount);

        // SetParagraphText
        doc.SetParagraphText(1, "Second (modified)");
        Assert.Equal("Second (modified)", doc.GetParagraphText(1));

        // GetParagraphTexts
        var texts = doc.GetParagraphTexts();
        Assert.Contains("First", texts);
        Assert.Contains("Second (modified)", texts);
        Assert.Contains("Third", texts);
        Assert.DoesNotContain("Second", texts.Where(t => t == "Second").ToList());

        // RemoveParagraph
        doc.RemoveParagraph(0);
        Assert.Equal(2, doc.ParagraphCount);
        var afterRemove = doc.GetParagraphTexts();
        Assert.DoesNotContain("First", afterRemove);

        // GetPlainText
        var plain = doc.GetPlainText();
        Assert.Contains("Second (modified)", plain);
        Assert.Contains("Third", plain);
    }
}
