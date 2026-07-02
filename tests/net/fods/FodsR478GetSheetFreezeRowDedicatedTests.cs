// Tests for FodsDocument.GetSheetFreezeRow dedicated coverage.
// Sprint: ff-sprint-s429-dotnet-deepening-20260701
// Ledger: PC-FODS-R478

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R478: Dedicated tests for FodsDocument.GetSheetFreezeRow(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns non-negative int.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default sheet and multiple sheets both return non-negative.
/// </summary>
public class FodsR478GetSheetFreezeRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeRow_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeRow(null!));
    }

    [Fact]
    public void GetSheetFreezeRow_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeRow("   "));
    }

    [Fact]
    public void GetSheetFreezeRow_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeRow("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeRow_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        int val = doc.GetSheetFreezeRow(sheet);
        Assert.True(val >= 0);
    }

    [Fact]
    public void GetSheetFreezeRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetFreezeRow(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetFreezeRow_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        int first = doc.GetSheetFreezeRow(sheet);
        int second = doc.GetSheetFreezeRow(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetFreezeRow_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetFreezeRow(sheet);
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        Assert.True(doc.GetSheetFreezeRow(sheet) >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            Assert.True(doc.GetSheetFreezeRow(sheet) >= 0);
        }
    }
}
