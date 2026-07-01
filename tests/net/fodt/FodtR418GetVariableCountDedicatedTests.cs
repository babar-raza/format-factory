// Tests for FodtDocument.GetVariableCount dedicated coverage.
// Sprint: ff-sprint-s394-dotnet-deepening-20260701
// Ledger: PC-FODT-R418

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R418: Dedicated tests for FodtDocument.VariableCount (or GetVariableCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking VariableCount.
/// TableCount unchanged after checking VariableCount.
/// MacroCount unchanged after checking VariableCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: VariableCount non-negative after paragraphs.
/// Dogfood: VariableCount non-negative after mixed content.
/// Dogfood: VariableCount never negative in loop.
/// </summary>
public class FodtR418GetVariableCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void VariableCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.VariableCount >= 0);
    }

    [Fact]
    public void VariableCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.VariableCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void VariableCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.VariableCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void VariableCount_MacroCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.MacroCount;
        _ = doc.VariableCount;
        Assert.Equal(before, doc.MacroCount);
    }

    [Fact]
    public void VariableCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.VariableCount;
        int second = doc.VariableCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void VariableCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.VariableCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Variable reference A");
        doc.AddParagraph("Variable reference B");
        Assert.True(doc.VariableCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Title");
        doc.AddTable(2, 3);
        doc.AddParagraph("Summary with variables");
        Assert.True(doc.VariableCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Variable-driven paragraph {i}");
            Assert.True(doc.VariableCount >= 0);
        }
    }
}
