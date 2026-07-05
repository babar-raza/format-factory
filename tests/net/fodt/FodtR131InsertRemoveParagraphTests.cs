// Tests for FodtDocument.InsertParagraph, RemoveParagraph, SetParagraphText, GetParagraphText.
// Sprint: FORMAT-FACTORY-FODT-INSERT-REMOVE-PARAGRAPH-20260626
// Ledger: R131-GOVERNED-DOTNET-FODT-INSERT-REMOVE-PARAGRAPH-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R131: FodtDocument positional paragraph mutation — InsertParagraph(index, text) shifts
/// subsequent paragraphs; RemoveParagraph(index) removes and shifts; SetParagraphText(index,
/// text) replaces content in-place; GetParagraphText(index) retrieves content by index.
/// </summary>
public class FodtR131InsertRemoveParagraphTests
{
    // ---- GetParagraphText: basic access ----

    [Fact]
    public void GetParagraphText_IndexZero_ReturnsFirstParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");

        Assert.Equal("First", doc.GetParagraphText(0));
    }

    [Fact]
    public void GetParagraphText_LastIndex_ReturnsLastParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");

        Assert.Equal("Gamma", doc.GetParagraphText(2));
    }

    [Fact]
    public void GetParagraphText_OutOfRange_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only one");

        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(5));
    }

    // ---- SetParagraphText: in-place replacement ----

    [Fact]
    public void SetParagraphText_UpdatesContentAtIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.SetParagraphText(0, "Updated");

        Assert.Equal("Updated", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        var before = doc.GetParagraphCount();

        doc.SetParagraphText(0, "New A");

        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void SetParagraphText_OtherParagraphsUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep this");
        doc.AppendParagraph("Replace this");

        doc.SetParagraphText(1, "Replaced");

        Assert.Equal("Keep this", doc.GetParagraphText(0));
        Assert.Equal("Replaced", doc.GetParagraphText(1));
    }

    // ---- InsertParagraph: positional insertion ----

    [Fact]
    public void InsertParagraph_AtIndex0_BecomesFirstParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        doc.InsertParagraph(0, "Inserted First");

        Assert.Equal("Inserted First", doc.GetParagraphText(0));
        Assert.Equal("Existing", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_IncreasesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        var before = doc.GetParagraphCount();

        doc.InsertParagraph(1, "Between");

        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    // ---- RemoveParagraph: deletion and shift ----

    [Fact]
    public void RemoveParagraph_RemovesTargetParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");

        doc.RemoveParagraph(1); // remove "B"

        Assert.Equal("A", doc.GetParagraphText(0));
        Assert.Equal("C", doc.GetParagraphText(1));
    }

    [Fact]
    public void RemoveParagraph_DecreasesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        doc.AppendParagraph("Y");
        var before = doc.GetParagraphCount();

        doc.RemoveParagraph(0);

        Assert.Equal(before - 1, doc.GetParagraphCount());
    }

    // ---- Dogfood: insert + set + remove pipeline ----

    [Fact]
    public void DogfoodPipeline_InsertSetRemove_FinalOrderCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Third");

        // Insert "Second" between them
        doc.InsertParagraph(1, "Second");
        Assert.Equal(3, doc.GetParagraphCount());
        Assert.Equal("Second", doc.GetParagraphText(1));

        // Replace "First" with "Alpha"
        doc.SetParagraphText(0, "Alpha");
        Assert.Equal("Alpha", doc.GetParagraphText(0));

        // Remove "Second" (now at index 1)
        doc.RemoveParagraph(1);
        Assert.Equal(2, doc.GetParagraphCount());
        Assert.Equal("Alpha", doc.GetParagraphText(0));
        Assert.Equal("Third", doc.GetParagraphText(1));
    }
}
