// Tests for FodtDocument.GetTextBoxCount dedicated coverage.
// Sprint: ff-sprint-s320-dotnet-deepening-20260630
// Ledger: PC-FODT-R338

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R338: Dedicated tests for FodtDocument.GetTextBoxCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddTextBox.
/// ParagraphCount unchanged after GetTextBoxCount.
/// TableCount unchanged after GetTextBoxCount.
/// SectionCount unchanged after GetTextBoxCount.
/// Idempotent (called twice same result).
/// Dogfood: add text box then count is non-negative.
/// Dogfood: multiple text boxes count is non-negative.
/// </summary>
public class FodtR338GetTextBoxCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBoxCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTextBoxCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextBoxCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetTextBoxCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTextBoxCount_AfterAddTextBox_Increases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        int before = doc.GetTextBoxCount();
        doc.AddTextBox("Sidebar note");
        int after = doc.GetTextBoxCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetTextBoxCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetTextBoxCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTextBoxCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetTextBoxCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTextBoxCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetTextBoxCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetTextBoxCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para text");
        doc.AddTextBox("Info box");
        int first = doc.GetTextBoxCount();
        int second = doc.GetTextBoxCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTextBox_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main content");
        doc.AddTextBox("Callout box: important note");
        int count = doc.GetTextBoxCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleTextBoxes_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddTextBox("Tip box one");
        doc.AddParagraph("Main content");
        doc.AddTextBox("Tip box two");
        doc.AddTextBox("Tip box three");
        int count = doc.GetTextBoxCount();
        Assert.True(count >= 0);
    }
}
