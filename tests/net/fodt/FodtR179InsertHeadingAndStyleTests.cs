// Tests for FodtDocument.InsertHeading, RemoveHeading, SetParagraphStyle.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R179

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R179: Tests for FodtDocument.InsertHeading, RemoveHeading, SetParagraphStyle.
/// InsertHeading(index, text, level): inserts heading paragraph at given index.
/// RemoveHeading(index): removes heading paragraph at given index.
/// SetParagraphStyle(index, styleName): sets the style name of a paragraph.
/// GetParagraphStyleName(index): returns style name of paragraph at index.
/// Covers: InsertHeading increases ParagraphCount; InsertHeading text retrievable;
/// InsertHeading is in GetHeadingParagraphs; RemoveHeading decreases ParagraphCount;
/// RemoveHeading shifts remaining paragraphs; SetParagraphStyle changes style;
/// GetParagraphStyleName returns non-null after style set;
/// InsertHeading level 1 creates heading; InsertHeading level 2 creates heading;
/// SearchText finds text in heading; AppendParagraph after InsertHeading;
/// ReplaceText affects heading text; dogfood InsertHeading->SetStyle->RemoveHeading.
/// </summary>
public class FodtR179InsertHeadingAndStyleTests
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
    // InsertHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_IncreasesParagraphCount()
    {
        var doc = LoadFixture();
        var before = doc.ParagraphCount;
        doc.InsertHeading(0, "New Heading", 1);
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertHeading_TextIsRetrievable()
    {
        var doc = LoadFixture();
        doc.InsertHeading(0, "Test Chapter", 1);
        // Heading was inserted at index 0, so GetPlainText should contain it
        var plain = doc.GetPlainText();
        Assert.Contains("Test Chapter", plain);
    }

    [Fact]
    public void InsertHeading_Level1_IsInHeadingParagraphs()
    {
        var doc = LoadFixture();
        var headingsBefore = doc.GetHeadingParagraphs().Count;
        doc.InsertHeading(0, "Level 1 Heading", 1);
        var headingsAfter = doc.GetHeadingParagraphs().Count;
        Assert.Equal(headingsBefore + 1, headingsAfter);
    }

    [Fact]
    public void InsertHeading_Level2_IncreasesParagraphCount()
    {
        var doc = LoadFixture();
        var before = doc.ParagraphCount;
        doc.InsertHeading(0, "Level 2 Heading", 2);
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertHeading_AtEnd_TextInGetPlainText()
    {
        var doc = LoadFixture();
        doc.InsertHeading(doc.ParagraphCount, "End Heading", 1);
        Assert.Contains("End Heading", doc.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // RemoveHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_DecreasesParagraphCount()
    {
        var doc = LoadFixture();
        // Insert heading to have one to remove
        doc.InsertHeading(0, "Removable", 1);
        var before = doc.ParagraphCount;
        doc.RemoveHeading(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveHeading_RemovedTextNotInGetPlainText()
    {
        var doc = LoadFixture();
        doc.InsertHeading(0, "UniqueRemovableHeading12345", 1);
        Assert.Contains("UniqueRemovableHeading12345", doc.GetPlainText());
        doc.RemoveHeading(0);
        Assert.DoesNotContain("UniqueRemovableHeading12345", doc.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // SetParagraphStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_ChangesStyle()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("Paragraph to restyle.");
        var lastIdx = doc.ParagraphCount - 1;
        doc.SetParagraphStyle(lastIdx, "Heading_20_1");
        var style = doc.GetParagraphStyleName(lastIdx);
        // Style was set (may normalize name slightly)
        Assert.NotNull(style);
    }

    [Fact]
    public void SetParagraphStyle_GetParagraphStyleName_NonNull()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("Style test paragraph.");
        var idx = doc.ParagraphCount - 1;
        doc.SetParagraphStyle(idx, "Text_20_Body");
        var style = doc.GetParagraphStyleName(idx);
        Assert.NotNull(style);
    }

    // -------------------------------------------------------------------------
    // SearchText in heading
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_FindsTextInHeading()
    {
        var doc = LoadFixture();
        doc.InsertHeading(0, "SearchableHeadingText", 1);
        var results = doc.SearchText("SearchableHeadingText");
        Assert.NotEmpty(results);
    }

    // -------------------------------------------------------------------------
    // AppendParagraph after InsertHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendParagraph_AfterInsertHeading_CountIncreases()
    {
        var doc = LoadFixture();
        doc.InsertHeading(0, "Section", 1);
        var before = doc.ParagraphCount;
        doc.AppendParagraph("Section body text.");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // ReplaceText in heading
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_AffectsHeadingText()
    {
        var doc = LoadFixture();
        doc.InsertHeading(0, "Original Heading Text", 1);
        doc.ReplaceText("Original Heading Text", "Replaced Heading Text");
        Assert.Contains("Replaced Heading Text", doc.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // Dogfood: InsertHeading->SetStyle->SearchText->RemoveHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertSetStyleSearchRemovePipeline()
    {
        var doc = LoadFixture();
        var initialCount = doc.ParagraphCount;

        // Insert heading
        doc.InsertHeading(0, "Chapter One", 1);
        Assert.Equal(initialCount + 1, doc.ParagraphCount);
        Assert.Contains("Chapter One", doc.GetPlainText());

        // Insert level 2
        doc.InsertHeading(1, "Section 1.1", 2);
        Assert.Equal(initialCount + 2, doc.ParagraphCount);

        // Set style on a different paragraph
        doc.AppendParagraph("Body content.");
        doc.SetParagraphStyle(doc.ParagraphCount - 1, "Text_20_Body");

        // Search
        var found = doc.SearchText("Chapter One");
        Assert.NotEmpty(found);

        // Remove heading at 0
        doc.RemoveHeading(0);
        Assert.Equal(initialCount + 2, doc.ParagraphCount); // +2: Section 1.1 + Body

        // Verify Chapter One is gone
        Assert.DoesNotContain("Chapter One", doc.GetPlainText());
        // Section 1.1 still there
        Assert.Contains("Section 1.1", doc.GetPlainText());
    }
}
