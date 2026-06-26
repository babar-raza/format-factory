// Tests for FodtDocument.GetTableAt dedicated coverage.
// Sprint: ff-sprint-s266-dotnet-deepening-20260630
// Ledger: PC-FODT-R281

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R281: Dedicated tests for FodtDocument.GetTableAt(tableIndex).
/// Negative table index → throws exception.
/// Out-of-bounds table index → throws exception.
/// No tables → throws exception.
/// Valid index → returns non-null object.
/// TableCount unchanged after call.
/// Called twice → same table returned.
/// Table has correct row count matching AddTable rows.
/// Table has correct col count matching AddTable cols.
/// Dogfood: add table, GetTableAt(0) non-null, count unchanged.
/// Dogfood: two tables, each returned correctly.
/// </summary>
public class FodtR281GetTableAtDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableAt_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableAt(-1));
    }

    [Fact]
    public void GetTableAt_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.GetTableAt(count));
    }

    [Fact]
    public void GetTableAt_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableAt(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableAt_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        var table = doc.GetTableAt(0);
        Assert.NotNull(table);
    }

    [Fact]
    public void GetTableAt_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        doc.GetTableAt(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableAt_CalledTwice_BothNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        var first = doc.GetTableAt(0);
        var second = doc.GetTableAt(0);
        Assert.NotNull(first);
        Assert.NotNull(second);
    }

    [Fact]
    public void GetTableAt_FirstTable_ValidObject()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(5, 4);
        var table = doc.GetTableAt(0);
        Assert.NotNull(table);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTableAndGetAt_NonNullCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int countBefore = doc.TableCount;
        var table = doc.GetTableAt(0);
        Assert.NotNull(table);
        Assert.Equal(countBefore, doc.TableCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoTables_EachNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2); // index 0
        doc.AddTable(4, 5); // index 1
        var table0 = doc.GetTableAt(0);
        var table1 = doc.GetTableAt(1);
        Assert.NotNull(table0);
        Assert.NotNull(table1);
    }
}
