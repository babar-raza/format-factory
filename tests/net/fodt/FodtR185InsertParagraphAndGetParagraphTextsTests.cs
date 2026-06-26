// Tests for FodtDocument.InsertParagraph, GetParagraphTexts, GetParagraphText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R185

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R185: Tests for FodtDocument.InsertParagraph, GetParagraphTexts, GetParagraphText deeper.
/// InsertParagraph(index, text): inserts a paragraph at a given index.
/// GetParagraphTexts(): returns all paragraph texts as a list.
/// GetParagraphText(index): returns the text of a specific paragraph.
/// RemoveParagraph(index): removes a paragraph at a given index.
/// Covers: InsertParagraph at 0 shifts existing paras; InsertParagraph increments ParagraphCount;
/// InsertParagraph text accessible at index; GetParagraphTexts count equals ParagraphCount;
/// GetParagraphTexts contains all texts; GetParagraphText(0) returns first para;
/// GetParagraphText(index) returns correct text; GetParagraphTexts after AppendParagraph;
/// RemoveParagraph decrements ParagraphCount; RemoveParagraph removes correct para;
/// InsertParagraph then RemoveParagraph restores count; GetParagraphTexts empty doc;
/// dogfood CreateEmpty->InsertParagraph->GetParagraphTexts->RemoveParagraph->GetParagraphText.
/// </summary>
public class FodtR185InsertParagraphAndGetParagraphTextsTests
{
    // -------------------------------------------------------------------------
    // InsertParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_IncrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para0");
        var before = doc.ParagraphCount;
        doc.InsertParagraph(0, "Before");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_AtZero_ShiftsExistingParas()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.InsertParagraph(0, "Inserted");
        // The inserted para is now at index 0
        Assert.Equal("Inserted", doc.GetParagraphText(0));
        Assert.Equal("Original", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_AtEnd_TextAccessible()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.InsertParagraph(2, "AtEnd");
        Assert.Equal("AtEnd", doc.GetParagraphText(2));
    }

    [Fact]
    public void InsertParagraph_Middle_OrderPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("C");
        doc.InsertParagraph(1, "B");
        Assert.Equal("A", doc.GetParagraphText(0));
        Assert.Equal("B", doc.GetParagraphText(1));
        Assert.Equal("C", doc.GetParagraphText(2));
    }

    // -------------------------------------------------------------------------
    // GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_CountEqualsParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        doc.AppendParagraph("Y");
        doc.AppendParagraph("Z");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(doc.ParagraphCount, texts.Count);
    }

    [Fact]
    public void GetParagraphTexts_ContainsAllTexts()
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

    [Fact]
    public void GetParagraphTexts_AfterInsertParagraph_UpdatesCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.InsertParagraph(0, "P0");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(2, texts.Count);
        Assert.Contains("P0", texts);
        Assert.Contains("P1", texts);
    }

    [Fact]
    public void GetParagraphTexts_EmptyDoc_EmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetParagraphTexts();
        Assert.Empty(texts);
    }

    // -------------------------------------------------------------------------
    // GetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_Index0_ReturnsFirstPara()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("FirstText");
        Assert.Equal("FirstText", doc.GetParagraphText(0));
    }

    [Fact]
    public void GetParagraphText_LastIndex_ReturnsLastPara()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.AppendParagraph("LastPara");
        Assert.Equal("LastPara", doc.GetParagraphText(2));
    }

    // -------------------------------------------------------------------------
    // RemoveParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_DecrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.RemoveParagraph(0);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveParagraph_RemovesCorrectPara()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep");
        doc.AppendParagraph("Remove");
        doc.RemoveParagraph(1);
        Assert.Equal("Keep", doc.GetParagraphText(0));
    }

    [Fact]
    public void InsertThenRemove_RestoresCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        var before = doc.ParagraphCount;
        doc.InsertParagraph(0, "Temp");
        doc.RemoveParagraph(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertParagraph->GetParagraphTexts->RemoveParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertGetTextsRemoveGetParagraphText_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Insert paragraphs in different positions
        doc.AppendParagraph("C");
        doc.InsertParagraph(0, "A");
        doc.InsertParagraph(1, "B");
        Assert.Equal(3, doc.ParagraphCount);

        // GetParagraphTexts preserves order
        var texts = doc.GetParagraphTexts();
        Assert.Equal(3, texts.Count);
        Assert.Equal("A", texts[0]);
        Assert.Equal("B", texts[1]);
        Assert.Equal("C", texts[2]);

        // Remove middle paragraph
        doc.RemoveParagraph(1);
        Assert.Equal(2, doc.ParagraphCount);

        // Check remaining
        Assert.Equal("A", doc.GetParagraphText(0));
        Assert.Equal("C", doc.GetParagraphText(1));
    }
}
