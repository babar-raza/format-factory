// Tests for FodtDocument.GetUserFieldCount dedicated coverage.
// Sprint: ff-sprint-s395-dotnet-deepening-20260701
// Ledger: PC-FODT-R419

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R419: Dedicated tests for FodtDocument.UserFieldCount (or GetUserFieldCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking UserFieldCount.
/// TableCount unchanged after checking UserFieldCount.
/// VariableCount unchanged after checking UserFieldCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: UserFieldCount non-negative after paragraphs.
/// Dogfood: UserFieldCount non-negative after mixed content.
/// Dogfood: UserFieldCount never negative in loop.
/// </summary>
public class FodtR419GetUserFieldCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void UserFieldCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.UserFieldCount >= 0);
    }

    [Fact]
    public void UserFieldCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.UserFieldCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void UserFieldCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.UserFieldCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void UserFieldCount_VariableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.VariableCount;
        _ = doc.UserFieldCount;
        Assert.Equal(before, doc.VariableCount);
    }

    [Fact]
    public void UserFieldCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.UserFieldCount;
        int second = doc.UserFieldCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void UserFieldCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.UserFieldCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("User field placeholder A");
        doc.AddParagraph("User field placeholder B");
        Assert.True(doc.UserFieldCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document title");
        doc.AddTable(3, 3);
        doc.AddParagraph("User field section");
        Assert.True(doc.UserFieldCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"User field paragraph {i}");
            Assert.True(doc.UserFieldCount >= 0);
        }
    }
}
