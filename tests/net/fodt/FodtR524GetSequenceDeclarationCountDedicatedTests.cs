// Tests for FodtDocument.GetSequenceDeclarationCount dedicated coverage.
// Sprint: ff-sprint-s500-dotnet-deepening-20260701
// Ledger: PC-FODT-R524

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R524: Dedicated tests for FodtDocument.GetSequenceDeclarationCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetSequenceDeclarationCount.
/// TableCount unchanged after GetSequenceDeclarationCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR524GetSequenceDeclarationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSequenceDeclarationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSequenceDeclarationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSequenceDeclarationCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetSequenceDeclarationCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSequenceDeclarationCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetSequenceDeclarationCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSequenceDeclarationCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetSequenceDeclarationCount();
        int second = doc.GetSequenceDeclarationCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSequenceDeclarationCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetSequenceDeclarationCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        Assert.True(doc.GetSequenceDeclarationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetSequenceDeclarationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetSequenceDeclarationCount() >= 0);
        }
    }
}
