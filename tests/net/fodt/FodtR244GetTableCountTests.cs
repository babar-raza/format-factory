// Tests for FodtDocument.GetTableCount dedicated coverage.
// Sprint: ff-sprint-s229-dotnet-deepening-20260629
// Ledger: PC-FODT-R244

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R244: Dedicated tests for FodtDocument.GetTableCount().
/// Empty document: no exception.
/// Empty document: count is 0.
/// ParagraphCount unchanged after get.
/// Called twice: same result.
/// After adding paragraphs: count still 0 (no tables).
/// After adding headings: count still 0 (no tables).
/// Returns non-negative integer.
/// After adding table: count increases.
/// Two tables: count is 2.
/// Dogfood: add mixed content, table count correct.
/// </summary>
public class FodtR244GetTableCountTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        int before = doc.ParagraphCount;
        doc.GetTableCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_ParagraphsOnly_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No tables here");
        doc.AppendParagraph("Still no tables");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_HeadingsOnly_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Heading 1", 1);
        doc.AppendHeading("Heading 2", 2);
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_AfterAddTable_CountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        int before = doc.GetTableCount();
        doc.AddTable(2, 2);
        int after = doc.GetTableCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetTableCount_TwoTables_CountIsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.AddTable(3, 3);
        Assert.Equal(2, doc.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedContent_TableCountCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Report", 1);
        doc.AppendParagraph("Introduction text");
        doc.AddTable(2, 3);
        doc.AppendParagraph("More text");
        Assert.Equal(1, doc.GetTableCount());
    }
}
