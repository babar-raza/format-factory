// Tests for FodtDocument.GetSettingCount dedicated coverage.
// Sprint: ff-sprint-s473-dotnet-deepening-20260701
// Ledger: PC-FODT-R497

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R497: Dedicated tests for FodtDocument.GetSettingCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetSettingCount.
/// TableCount unchanged after GetSettingCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR497GetSettingCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSettingCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSettingCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSettingCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetSettingCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSettingCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetSettingCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSettingCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetSettingCount();
        int second = doc.GetSettingCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSettingCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetSettingCount();
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
        Assert.True(doc.GetSettingCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetSettingCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetSettingCount() >= 0);
        }
    }
}
