// Tests for FodtDocument.Tables, FodtTable model, FodtParagraph model.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R174

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R174: Tests for FodtDocument.Tables, FodtTable, FodtParagraph model properties.
/// Tables: IReadOnlyList of FodtTable found in document.
/// FodtTable.RowCount: number of rows in the table.
/// FodtTable.ColumnCount: number of columns.
/// FodtTable.GetCellText(row, col): returns cell text.
/// FodtParagraph.Text: text content of paragraph.
/// FodtParagraph.StyleName: style associated with paragraph.
/// Covers: Tables empty for no-table doc; Paragraphs has correct count;
/// AppendParagraph text accessible via Paragraphs[n].Text;
/// SetParagraphText updates Paragraphs[n].Text; GetParagraphText by index;
/// GetParagraphStyleName returns style name; ParagraphCount matches Paragraphs.Count;
/// InsertParagraph at index 0 shifts; RemoveParagraph decreases count;
/// dogfood CreateEmpty->AppendParagraph->SetText->GetText->ParagraphCount pipeline.
/// </summary>
public class FodtR174TablesAndParagraphModelTests
{
    // -------------------------------------------------------------------------
    // Tables
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_EmptyDoc_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.Tables);
    }

    [Fact]
    public void Tables_DocWithParagraphs_IsStillEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just text, no tables");
        Assert.Empty(doc.Tables);
    }

    // -------------------------------------------------------------------------
    // Paragraphs model
    // -------------------------------------------------------------------------

    [Fact]
    public void Paragraphs_EmptyDoc_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.Paragraphs);
    }

    [Fact]
    public void Paragraphs_AfterAppend_HasCorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        Assert.Equal(3, doc.Paragraphs.Count);
    }

    [Fact]
    public void Paragraphs_TextAccessibleViaIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello from paragraph");
        Assert.Contains("Hello", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void SetParagraphText_UpdatesParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.SetParagraphText(0, "Updated");
        Assert.Contains("Updated", doc.Paragraphs[0].Text);
    }

    // -------------------------------------------------------------------------
    // GetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_ValidIndex_ReturnsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("My paragraph text");
        var text = doc.GetParagraphText(0);
        Assert.NotNull(text);
        Assert.Contains("My paragraph", text!);
    }

    [Fact]
    public void GetParagraphText_OobIndex_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        var text = doc.GetParagraphText(999);
        Assert.Null(text);
    }

    // -------------------------------------------------------------------------
    // GetParagraphStyleName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyleName_ParagraphStyle_NotNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        var style = doc.GetParagraphStyleName(0);
        // Normal paragraph should have some style
        Assert.NotNull(style);
    }

    [Fact]
    public void GetParagraphStyleName_HeadingStyle_ContainsHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", 1);
        var style = doc.GetParagraphStyleName(0);
        Assert.NotNull(style);
        Assert.Contains("Heading", style);
    }

    [Fact]
    public void GetParagraphStyleName_OobIndex_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var style = doc.GetParagraphStyleName(999);
        Assert.Null(style);
    }

    // -------------------------------------------------------------------------
    // ParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ParagraphCount_MatchesParagraphsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");
        doc.AppendParagraph("Two");
        Assert.Equal(doc.Paragraphs.Count, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // InsertParagraph / RemoveParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_AtZero_ShiftsExistingDown()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        doc.InsertParagraph(0, "Inserted");
        Assert.Contains("Inserted", doc.GetParagraphText(0)!);
        Assert.Contains("Existing", doc.GetParagraphText(1)!);
    }

    [Fact]
    public void RemoveParagraph_DecreasesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        var before = doc.ParagraphCount;
        doc.RemoveParagraph(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendParagraph->SetText->GetText->ParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendSetGetTextParagraphCount_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Append 3 paragraphs
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        Assert.Equal(3, doc.ParagraphCount);
        Assert.Equal(doc.ParagraphCount, doc.Paragraphs.Count);

        // Check text
        Assert.Contains("Alpha", doc.GetParagraphText(0)!);
        Assert.Contains("Beta", doc.GetParagraphText(1)!);

        // Update text
        doc.SetParagraphText(2, "Delta");
        Assert.Contains("Delta", doc.GetParagraphText(2)!);
        Assert.Contains("Delta", doc.Paragraphs[2].Text);

        // Insert at beginning
        doc.InsertParagraph(0, "Prologue");
        Assert.Equal(4, doc.ParagraphCount);
        Assert.Contains("Prologue", doc.GetParagraphText(0)!);
        Assert.Contains("Alpha", doc.GetParagraphText(1)!);

        // Remove first
        doc.RemoveParagraph(0);
        Assert.Equal(3, doc.ParagraphCount);
        Assert.Contains("Alpha", doc.GetParagraphText(0)!);

        // Tables are still empty (no table-capable paragraphs)
        Assert.Empty(doc.Tables);
    }
}
