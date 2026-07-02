// Tests for FodsDocument.GetSheetShowGrid dedicated coverage.
// Sprint: ff-sprint-s433-dotnet-deepening-20260701
// Ledger: PC-FODS-R482

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R482: Dedicated tests for FodsDocument.GetSheetShowGrid(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns bool.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is bool.
/// Dogfood: default sheet and multiple sheets no exception.
/// </summary>
public class FodsR482GetSheetShowGridDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetShowGrid_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetShowGrid(null!));
    }

    [Fact]
    public void GetSheetShowGrid_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetShowGrid("   "));
    }

    [Fact]
    public void GetSheetShowGrid_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetShowGrid("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetShowGrid_ValidSheet_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetShowGrid(sheet);
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetSheetShowGrid_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetShowGrid(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetShowGrid_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        bool first = doc.GetSheetShowGrid(sheet);
        bool second = doc.GetSheetShowGrid(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetShowGrid_IsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetShowGrid(sheet);
        Assert.IsType<bool>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.GetSheetShowGrid(sheet));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            var ex = Record.Exception(() => doc.GetSheetShowGrid(sheet));
            Assert.Null(ex);
        }
    }
}
