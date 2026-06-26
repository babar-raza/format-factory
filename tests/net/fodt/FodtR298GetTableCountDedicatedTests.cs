// Tests for FodtDocument.GetTableCount / TableCount dedicated coverage.
// Sprint: ff-sprint-s283-dotnet-deepening-20260630
// Ledger: PC-FODT-R298

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R298: Dedicated tests for FodtDocument.TableCount property.
/// Returns non-negative int.
/// Increases after AddTable.
/// ParagraphCount unchanged after accessing TableCount.
/// SectionCount unchanged after accessing TableCount.
/// Called twice returns same result.
/// Adding two tables increases count by at least 2.
/// New document count at least zero.
/// Dogfood: add table, count increases.
/// Dogfood: multiple tables accumulated correctly.
/// </summary>
public class FodtR298GetTableCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void TableCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.TableCount >= 0);
    }

    [Fact]
    public void TableCount_IncreasesAfterAddTable()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        doc.AddTable(3, 3);
        int after = doc.TableCount;
        Assert.True(after > before);
    }

    [Fact]
    public void TableCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int paraBefore = doc.ParagraphCount;
        _ = doc.TableCount;
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void TableCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int secBefore = doc.GetSectionCount();
        _ = doc.TableCount;
        Assert.Equal(secBefore, doc.GetSectionCount());
    }

    [Fact]
    public void TableCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int first = doc.TableCount;
        int second = doc.TableCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void TableCount_AddTwoTables_IncreasedByAtLeastTwo()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        doc.AddTable(2, 2);
        doc.AddTable(3, 3);
        int after = doc.TableCount;
        Assert.True(after >= before + 2);
    }

    [Fact]
    public void TableCount_NewDocument_AtLeastZero()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.TableCount >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTable_CountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        doc.AddTable(4, 4);
        Assert.True(doc.TableCount > before);
    }

    [Fact]
    public void DogfoodPipeline_MultipleTables_AccumulatedCorrectly()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        doc.AddTable(2, 2);
        doc.AddTable(3, 3);
        doc.AddTable(4, 4);
        Assert.True(doc.TableCount >= before + 3);
    }
}
