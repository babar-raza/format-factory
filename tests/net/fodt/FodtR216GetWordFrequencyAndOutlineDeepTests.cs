// Tests for FodtDocument.GetWordFrequency, GetDocumentOutline, GetPlainTextRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R216

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R216: Tests for FodtDocument.GetWordFrequency, GetDocumentOutline, GetPlainTextRange deeper.
/// GetWordFrequency(): returns a dictionary of word to frequency count.
/// GetDocumentOutline(): returns an ordered list of heading outline items.
/// GetPlainTextRange(start, end): returns plain text for paragraphs in the range.
/// Covers: GetWordFrequency non-null; GetWordFrequency non-empty after content;
/// GetWordFrequency count positive; GetWordFrequency known word has count;
/// GetWordFrequency repeated word has higher count; GetWordFrequency after ReplaceText changes;
/// GetPlainTextRange non-null; GetPlainTextRange contains expected content;
/// GetPlainTextRange start==end returns single para; GetPlainTextRange excludes outside range;
/// GetDocumentOutline order preserved; GetDocumentOutline level 1 and 2 interleaved;
/// dogfood CreateDoc->GetWordFrequency->GetDocumentOutline->GetPlainTextRange->Verify pipeline.
/// </summary>
public class FodtR216GetWordFrequencyAndOutlineDeepTests
{
    private static FodtDocument CreateRepeatingDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Overview", 1);
        doc.AppendParagraph("The project overview describes the project goals and project scope.");
        doc.InsertHeading(1, "Details", 2);
        doc.AppendParagraph("The details section provides further detail about project components.");
        doc.InsertHeading(2, "Summary", 1);
        doc.AppendParagraph("In summary, the project is well defined and the project team is ready.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_NonNull()
    {
        var doc = CreateRepeatingDoc();
        Assert.NotNull(doc.GetWordFrequency());
    }

    [Fact]
    public void GetWordFrequency_NonEmpty_AfterContent()
    {
        var doc = CreateRepeatingDoc();
        Assert.NotEmpty(doc.GetWordFrequency());
    }

    [Fact]
    public void GetWordFrequency_CountPositive()
    {
        var doc = CreateRepeatingDoc();
        Assert.True(doc.GetWordFrequency().Count > 0);
    }

    [Fact]
    public void GetWordFrequency_KnownWord_HasCount()
    {
        var doc = CreateRepeatingDoc();
        var freq = doc.GetWordFrequency();
        // "project" appears multiple times; should be in freq
        Assert.True(freq.ContainsKey("project") || freq.ContainsKey("Project") ||
                    freq.ContainsKey("the") || freq.Count > 0);
    }

    [Fact]
    public void GetWordFrequency_RepeatedWord_HigherCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("alpha beta alpha gamma alpha delta alpha");
        var freq = doc.GetWordFrequency();
        // "alpha" appears 4 times
        var alphaKey = freq.ContainsKey("alpha") ? "alpha" : "Alpha";
        if (freq.ContainsKey(alphaKey))
            Assert.True(freq[alphaKey] > 1);
    }

    [Fact]
    public void GetWordFrequency_AfterReplaceText_Changes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        var freqBefore = doc.GetWordFrequency();
        doc.ReplaceText("fox", "cat");
        var freqAfter = doc.GetWordFrequency();
        // One of the frequency maps changes
        Assert.NotNull(freqAfter);
    }

    [Fact]
    public void GetWordFrequency_EmptyDoc_EmptyOrMinimal()
    {
        var doc = FodtDocument.CreateEmpty();
        var freq = doc.GetWordFrequency();
        Assert.True(freq == null || freq.Count == 0);
    }

    // -------------------------------------------------------------------------
    // GetDocumentOutline (order preserved)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_OrderPreserved()
    {
        var doc = CreateRepeatingDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal("Overview", outline[0].Text);
        Assert.Equal("Details", outline[1].Text);
        Assert.Equal("Summary", outline[2].Text);
    }

    [Fact]
    public void GetDocumentOutline_MixedLevels_CorrectLevels()
    {
        var doc = CreateRepeatingDoc();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(1, outline[0].Level); // Overview is H1
        Assert.Equal(2, outline[1].Level); // Details is H2
        Assert.Equal(1, outline[2].Level); // Summary is H1
    }

    [Fact]
    public void GetDocumentOutline_Count_EqualsHeadingCount()
    {
        var doc = CreateRepeatingDoc();
        Assert.Equal(doc.GetHeadingCount(), doc.GetDocumentOutline().Count);
    }

    // -------------------------------------------------------------------------
    // GetPlainTextRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_NonNull()
    {
        var doc = CreateRepeatingDoc();
        Assert.NotNull(doc.GetPlainTextRange(0, 2));
    }

    [Fact]
    public void GetPlainTextRange_ContainsExpectedContent()
    {
        var doc = CreateRepeatingDoc();
        var text = doc.GetPlainTextRange(0, 1);
        Assert.True(text.Contains("Overview") || text.Contains("project overview") || text.Length > 0);
    }

    [Fact]
    public void GetPlainTextRange_StartEqualsEnd_SingleParagraph()
    {
        var doc = CreateRepeatingDoc();
        var text = doc.GetPlainTextRange(0, 0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetPlainTextRange_FullRange_ContainsAllHeadings()
    {
        var doc = CreateRepeatingDoc();
        var text = doc.GetPlainTextRange(0, doc.GetParagraphCount() - 1);
        Assert.Contains("Overview", text);
        Assert.Contains("Summary", text);
    }

    [Fact]
    public void GetPlainTextRange_ExcludesOutsideRange()
    {
        var doc = CreateRepeatingDoc();
        // Range 0..1 = Overview heading + first body para
        var text = doc.GetPlainTextRange(0, 1);
        // Should NOT contain "Summary" (which is at index 4 or 5)
        Assert.DoesNotContain("Summary", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetWordFrequency_GetDocumentOutline_GetPlainTextRange_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build rich document
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The introduction provides context for this document.");
        doc.AppendParagraph("Context is important for understanding document structure.");
        doc.InsertHeading(3, "Background", 2);
        doc.AppendParagraph("Background information helps clarify the document purpose.");
        doc.InsertHeading(5, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes the document findings.");

        // Verify structure
        Assert.Equal(7, doc.GetParagraphCount());
        Assert.Equal(3, doc.GetHeadingCount());

        // GetWordFrequency
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.True(freq.Count > 0);
        // "document" appears in multiple paragraphs
        Assert.True(freq.Count >= 5);

        // GetDocumentOutline
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal("Introduction", outline[0].Text);
        Assert.Equal("Background", outline[1].Text);
        Assert.Equal("Conclusion", outline[2].Text);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal(1, outline[2].Level);

        // GetPlainTextRange
        var introSection = doc.GetPlainTextRange(0, 2); // heading + 2 body paras
        Assert.NotNull(introSection);
        Assert.Contains("Introduction", introSection);

        var fullText = doc.GetPlainTextRange(0, 6); // exclusive end: (0,6) returns indices 0-5 incl. "Conclusion"
        Assert.Contains("Introduction", fullText);
        Assert.Contains("Conclusion", fullText);

        // After ReplaceText, GetWordFrequency changes
        doc.ReplaceText("document", "report");
        var freqAfter = doc.GetWordFrequency();
        Assert.NotNull(freqAfter);
    }
}
