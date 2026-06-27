// Tests for FodsDocument.GetCellDataType dedicated coverage.
// Sprint: ff-sprint-s334-dotnet-deepening-20260630
// Ledger: PC-FODS-R370

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R370: Dedicated tests for FodsDocument.GetCellDataType().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellDataType.
/// Idempotent (called twice same result).
/// Dogfood: SetCellValue then GetCellDataType returns type.
/// Dogfood: Multiple cells with different types.
/// </summary>
public class FodsR370GetCellDataTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType(null!, 0, 0));
    }

    [Fact]
    public void GetCellDataType_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType("   ", 0, 0));
    }

    [Fact]
    public void GetCellDataType_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType("GhostSheet", 0, 0));
    }

    [Fact]
    public void GetCellDataType_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType("Data", -1, 0));
    }

    [Fact]
    public void GetCellDataType_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Types");
        string? dataType = doc.GetCellDataType("Types", 0, 0);
        Assert.NotNull(dataType);
    }

    [Fact]
    public void GetCellDataType_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("TypeSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellDataType("TypeSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellDataType_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Idempotent");
        doc.SetCellValue("Idempotent", 0, 0, "42.5");
        string? first = doc.GetCellDataType("Idempotent", 0, 0);
        string? second = doc.GetCellDataType("Idempotent", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellValueThenGetDataType_ReturnsType()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Values");
        doc.SetCellValue("Values", 0, 0, "Revenue");
        string? dataType = doc.GetCellDataType("Values", 0, 0);
        Assert.NotNull(dataType);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsDifferentTypes_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Mixed");
        doc.SetCellValue("Mixed", 0, 0, "Label");
        doc.SetCellValue("Mixed", 1, 0, "100");
        doc.SetCellValue("Mixed", 2, 0, "3.14");
        Assert.NotNull(doc.GetCellDataType("Mixed", 0, 0));
        Assert.NotNull(doc.GetCellDataType("Mixed", 1, 0));
        Assert.NotNull(doc.GetCellDataType("Mixed", 2, 0));
    }
}
