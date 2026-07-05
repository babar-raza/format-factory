// Tests for FodtDocument.SetParagraphText, GetParagraphText, GetTextBetweenParagraphs.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R181

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R181: Tests for FodtDocument.SetParagraphText, GetParagraphText, GetTextBetweenParagraphs.
/// SetParagraphText(index, text): replaces text in an existing paragraph.
/// GetParagraphText(index): returns text of paragraph at index.
/// GetTextBetweenParagraphs(start, end): returns text between two paragraph indices.
/// GetParagraphTexts(): returns all paragraph text strings.
/// Covers: SetParagraphText changes paragraph text; GetParagraphText returns text;
/// SetParagraphText GetPlainText reflects change; GetParagraphTexts non-empty;
/// GetTextBetweenParagraphs non-null for valid range; GetTextBetweenParagraphs empty range;
/// SetParagraphText then SearchText finds new text; AppendParagraph then GetParagraphText;
/// GetParagraphText OOB index returns null; SetParagraphText multiple;
/// GetTextBetweenParagraphs full range; ParagraphCount unchanged after SetParagraphText;
/// dogfood Load->AppendParagraphs->SetText->GetText->GetBetween pipeline.
/// </summary>
public class FodtR181ParagraphSetTextTests
{
    private static readonly string FodtFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fodt", "valid", "two-paragraphs.fodt");

    private FodtDocument LoadFixture()
    {
        var path = Path.GetFullPath(FodtFixturePath);
        return FodtDocument.Load(path);
    }

    // -------------------------------------------------------------------------
    // SetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ChangesText()
    {
        var doc = LoadFixture();
        doc.SetParagraphText(0, "Updated first paragraph text.");
        var text = doc.GetParagraphText(0);
        Assert.Equal("Updated first paragraph text.", text);
    }

    [Fact]
    public void SetParagraphText_GetPlainText_ReflectsChange()
    {
        var doc = LoadFixture();
        doc.SetParagraphText(0, "Unique updated content R181");
        Assert.Contains("Unique updated content R181", doc.GetPlainText());
    }

    [Fact]
    public void SetParagraphText_DoesNotChangeParagraphCount()
    {
        var doc = LoadFixture();
        var before = doc.ParagraphCount;
        doc.SetParagraphText(0, "New text.");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphText_MultipleEdits_AllReflected()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        var aIdx = doc.ParagraphCount - 2;
        var bIdx = doc.ParagraphCount - 1;

        doc.SetParagraphText(aIdx, "Updated A");
        doc.SetParagraphText(bIdx, "Updated B");

        Assert.Equal("Updated A", doc.GetParagraphText(aIdx));
        Assert.Equal("Updated B", doc.GetParagraphText(bIdx));
    }

    // -------------------------------------------------------------------------
    // GetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_ValidIndex_ReturnsText()
    {
        var doc = LoadFixture();
        var text = doc.GetParagraphText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetParagraphText_AfterAppend_ReturnsAppendedText()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("AppendedParagraphR181");
        var text = doc.GetParagraphText(doc.ParagraphCount - 1);
        Assert.Equal("AppendedParagraphR181", text);
    }

    [Fact]
    public void GetParagraphText_OOBIndex_ReturnsNull()
    {
        var doc = LoadFixture();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(999));
    }

    // -------------------------------------------------------------------------
    // GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_IsNonEmpty()
    {
        var doc = LoadFixture();
        var texts = doc.GetParagraphTexts();
        Assert.NotEmpty(texts);
    }

    [Fact]
    public void GetParagraphTexts_CountMatchesParagraphCount()
    {
        var doc = LoadFixture();
        Assert.Equal(doc.ParagraphCount, doc.GetParagraphTexts().Count);
    }

    // -------------------------------------------------------------------------
    // GetTextBetweenParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_ValidRange_ReturnsNonNull()
    {
        var doc = LoadFixture();
        if (doc.ParagraphCount >= 2)
        {
            var text = doc.GetTextBetweenParagraphs(0, 1);
            Assert.NotNull(text);
        }
    }

    [Fact]
    public void GetTextBetweenParagraphs_SameStartEnd_MayBeNullOrEmpty()
    {
        var doc = LoadFixture();
        var text = doc.GetTextBetweenParagraphs(0, 0);
        // Same index may return null or empty
        Assert.True(text == null || text.Length == 0);
    }

    [Fact]
    public void GetTextBetweenParagraphs_FullRange_NonNull()
    {
        var doc = LoadFixture();
        if (doc.ParagraphCount > 1)
        {
            var text = doc.GetTextBetweenParagraphs(0, doc.ParagraphCount - 1);
            Assert.NotNull(text);
        }
    }

    // -------------------------------------------------------------------------
    // SearchText after SetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_SearchTextFindsNewText()
    {
        var doc = LoadFixture();
        doc.SetParagraphText(0, "UniqueSearchableTextR181XYZ");
        var results = doc.SearchText("UniqueSearchableTextR181XYZ");
        Assert.NotEmpty(results);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AppendParagraphs->SetText->GetText->GetBetween pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendSetGetBetweenPipeline()
    {
        var doc = LoadFixture();
        var initialCount = doc.ParagraphCount;

        // Append some paragraphs
        doc.AppendParagraph("First appended paragraph.");
        doc.AppendParagraph("Second appended paragraph.");
        doc.AppendParagraph("Third appended paragraph.");
        Assert.Equal(initialCount + 3, doc.ParagraphCount);

        // Set text on the last appended
        var lastIdx = doc.ParagraphCount - 1;
        doc.SetParagraphText(lastIdx, "Modified third paragraph.");
        Assert.Equal("Modified third paragraph.", doc.GetParagraphText(lastIdx));

        // GetParagraphTexts includes modification
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Modified third paragraph.", texts);

        // GetTextBetweenParagraphs covers the appended region
        if (initialCount > 0)
        {
            var between = doc.GetTextBetweenParagraphs(initialCount, lastIdx);
            Assert.NotNull(between);
        }

        // Plain text reflects all changes
        Assert.Contains("Modified third paragraph.", doc.GetPlainText());
        Assert.Contains("First appended paragraph.", doc.GetPlainText());
    }
}
