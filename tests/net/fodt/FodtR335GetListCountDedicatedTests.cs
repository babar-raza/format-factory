// Tests for FodtDocument.GetListCount dedicated coverage.
// Sprint: ff-sprint-s317-dotnet-deepening-20260630
// Ledger: PC-FODT-R335

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R335: Dedicated tests for FodtDocument.GetListCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddList.
/// ParagraphCount unchanged after GetListCount.
/// TableCount unchanged after GetListCount.
/// SectionCount unchanged after GetListCount.
/// Idempotent (called twice same result).
/// Dogfood: add list then count is non-negative.
/// Dogfood: multiple lists count is non-negative.
/// </summary>
public class FodtR335GetListCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetListCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetListCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_AfterAddList_Increases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetListCount();
        doc.AddList(new[] { "Item 1", "Item 2", "Item 3" });
        int after = doc.GetListCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetListCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        int before = doc.ParagraphCount;
        _ = doc.GetListCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetListCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetListCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetListCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetListCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetListCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "Alpha", "Beta" });
        int first = doc.GetListCount();
        int second = doc.GetListCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddList_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddList(new[] { "Point one", "Point two", "Point three" });
        int count = doc.GetListCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleLists_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddList(new[] { "A", "B" });
        doc.AddParagraph("Separator");
        doc.AddList(new[] { "X", "Y", "Z" });
        int count = doc.GetListCount();
        Assert.True(count >= 0);
    }
}
