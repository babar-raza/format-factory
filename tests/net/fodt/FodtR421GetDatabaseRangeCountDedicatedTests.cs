// Tests for FodtDocument.GetDatabaseRangeCount dedicated coverage.
// Sprint: ff-sprint-s397-dotnet-deepening-20260701
// Ledger: PC-FODT-R421

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R421: Dedicated tests for FodtDocument.DatabaseRangeCount (or GetDatabaseRangeCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking DatabaseRangeCount.
/// TableCount unchanged after checking DatabaseRangeCount.
/// SequenceCount unchanged after checking DatabaseRangeCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: DatabaseRangeCount non-negative after paragraphs.
/// Dogfood: DatabaseRangeCount non-negative after mixed content.
/// Dogfood: DatabaseRangeCount never negative in loop.
/// </summary>
public class FodtR421GetDatabaseRangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DatabaseRangeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.DatabaseRangeCount >= 0);
    }

    [Fact]
    public void DatabaseRangeCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.DatabaseRangeCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DatabaseRangeCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.DatabaseRangeCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void DatabaseRangeCount_SequenceCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.SequenceCount;
        _ = doc.DatabaseRangeCount;
        Assert.Equal(before, doc.SequenceCount);
    }

    [Fact]
    public void DatabaseRangeCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.DatabaseRangeCount;
        int second = doc.DatabaseRangeCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void DatabaseRangeCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.DatabaseRangeCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Data import section");
        doc.AddParagraph("Database reference A");
        Assert.True(doc.DatabaseRangeCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Overview");
        doc.AddTable(4, 3);
        doc.AddParagraph("Data range section");
        Assert.True(doc.DatabaseRangeCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Database entry {i}");
            Assert.True(doc.DatabaseRangeCount >= 0);
        }
    }
}
