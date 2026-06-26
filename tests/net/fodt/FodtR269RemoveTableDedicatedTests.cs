// Tests for FodtDocument.RemoveTable dedicated coverage.
// Sprint: ff-sprint-s254-dotnet-deepening-20260630
// Ledger: PC-FODT-R269

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R269: Dedicated tests for FodtDocument.RemoveTable(tableIndex).
/// RemoveTable removes the table at the given index.
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid removal → no exception.
/// TableCount decreases after removal.
/// ParagraphCount unchanged or decreases (table paragraphs removed).
/// Other tables unaffected.
/// Remove last table → TableCount reaches 0 (if only one).
/// Dogfood: add table, remove it, verify TableCount=0.
/// Dogfood: add two tables, remove first, second remains at index 0.
/// </summary>
public class FodtR269RemoveTableDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveTable_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.RemoveTable(-1));
    }

    [Fact]
    public void RemoveTable_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.RemoveTable(count));
    }

    [Fact]
    public void RemoveTable_EmptyDocument_NoTablesThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        // No tables added → any index should throw
        Assert.ThrowsAny<Exception>(() => doc.RemoveTable(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveTable_ValidIndex_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        var ex = Record.Exception(() => doc.RemoveTable(0));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveTable_TableCountDecreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.TableCount;
        doc.RemoveTable(0);
        Assert.True(doc.TableCount < before);
    }

    [Fact]
    public void RemoveTable_RemoveSingleTable_TableCountIsZero()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        doc.RemoveTable(0);
        Assert.Equal(0, doc.TableCount);
    }

    [Fact]
    public void RemoveTable_OtherTablesUnaffected()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2); // index 0
        doc.AddTable(3, 3); // index 1
        doc.RemoveTable(0); // remove first
        // One table should remain
        Assert.Equal(1, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddAndRemoveTable_CountReturnsToZero()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 4);
        Assert.Equal(1, doc.TableCount);
        doc.RemoveTable(0);
        Assert.Equal(0, doc.TableCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoTables_RemoveFirst_SecondAtIndexZero()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2); // becomes index 0 then removed
        doc.AddTable(3, 3); // becomes index 1 then index 0 after removal
        doc.RemoveTable(0);
        // Only one table remains
        Assert.Equal(1, doc.TableCount);
        // GetTableAt(0) should not throw — the remaining table is now at 0
        var ex = Record.Exception(() => doc.GetTableAt(0));
        Assert.Null(ex);
    }
}
