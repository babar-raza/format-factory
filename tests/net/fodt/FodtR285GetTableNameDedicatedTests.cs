// Tests for FodtDocument.GetTableName dedicated coverage.
// Sprint: ff-sprint-s270-dotnet-deepening-20260630
// Ledger: PC-FODT-R285

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R285: Dedicated tests for FodtDocument.GetTableName(tableIndex).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Valid table returns non-null string.
/// TableCount unchanged after GetTableName.
/// Called twice returns same result.
/// Dogfood: two tables have different names.
/// Dogfood: name is non-empty string.
/// </summary>
public class FodtR285GetTableNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableName_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableName(-1));
    }

    [Fact]
    public void GetTableName_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.GetTableName(count));
    }

    [Fact]
    public void GetTableName_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableName(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableName_ValidTable_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        string name = doc.GetTableName(0);
        Assert.NotNull(name);
    }

    [Fact]
    public void GetTableName_ValidTable_ReturnsNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        string name = doc.GetTableName(0);
        Assert.NotEmpty(name);
    }

    [Fact]
    public void GetTableName_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        _ = doc.GetTableName(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableName_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        string first = doc.GetTableName(0);
        string second = doc.GetTableName(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoTables_HaveDifferentNames()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        doc.AddTable(4, 5);
        string name0 = doc.GetTableName(0);
        string name1 = doc.GetTableName(1);
        Assert.NotEqual(name0, name1);
    }

    [Fact]
    public void DogfoodPipeline_TableName_IsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        string name = doc.GetTableName(0);
        Assert.False(string.IsNullOrWhiteSpace(name));
    }
}
