// Tests for FodtDocument.GetDocumentPropertyCount dedicated coverage.
// Sprint: ff-sprint-s475-dotnet-deepening-20260701
// Ledger: PC-FODT-R499

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R499: Dedicated tests for FodtDocument.GetDocumentPropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetDocumentPropertyCount.
/// TableCount unchanged after GetDocumentPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR499GetDocumentPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetDocumentPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDocumentPropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentPropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentPropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetDocumentPropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentPropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetDocumentPropertyCount();
        int second = doc.GetDocumentPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentPropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetDocumentPropertyCount();
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
        Assert.True(doc.GetDocumentPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetDocumentPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetDocumentPropertyCount() >= 0);
        }
    }
}
