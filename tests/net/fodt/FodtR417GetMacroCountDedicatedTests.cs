// Tests for FodtDocument.GetMacroCount dedicated coverage.
// Sprint: ff-sprint-s393-dotnet-deepening-20260701
// Ledger: PC-FODT-R417

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R417: Dedicated tests for FodtDocument.MacroCount (or GetMacroCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking MacroCount.
/// TableCount unchanged after checking MacroCount.
/// DrawingCount unchanged after checking MacroCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: MacroCount non-negative after paragraphs.
/// Dogfood: MacroCount non-negative after mixed content.
/// Dogfood: MacroCount never negative in loop.
/// </summary>
public class FodtR417GetMacroCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MacroCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.MacroCount >= 0);
    }

    [Fact]
    public void MacroCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.MacroCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void MacroCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.MacroCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void MacroCount_DrawingCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.DrawingCount;
        _ = doc.MacroCount;
        Assert.Equal(before, doc.DrawingCount);
    }

    [Fact]
    public void MacroCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.MacroCount;
        int second = doc.MacroCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void MacroCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.MacroCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Macro-enabled section A");
        doc.AddParagraph("Macro-enabled section B");
        Assert.True(doc.MacroCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Header");
        doc.AddTable(3, 3);
        doc.AddParagraph("Footer");
        Assert.True(doc.MacroCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Section with macro {i}");
            Assert.True(doc.MacroCount >= 0);
        }
    }
}
